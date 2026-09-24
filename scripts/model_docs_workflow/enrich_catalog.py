#!/usr/bin/env python3
"""Enrich budconnect's cloud catalog with model details.

This replaces the hand-run first phase of this workflow for catalog models. It has three steps,
and only the first and last are code:

  plan      Read the live catalog from a budconnect API, drop the URIs model_details.json already
            covers, and group the rest into distinct models. One description serves every region,
            deployment and dated snapshot of a model, so ~1,500 URIs need ~800 write-ups. No LLM.
  research  Done by a web-researching agent, outside this script. Each target is researched as
            RESEARCH_PROMPT.md describes and written to catalog/results/<slug>.json.
  merge     Validate those files, fan each one out to every URI in its group, and merge the result
            into budconnect/seeders/data/model_details.json.

Examples:
    python scripts/model_docs_workflow/enrich_catalog.py plan --api https://connect.dev.bud.studio
    python scripts/model_docs_workflow/enrich_catalog.py merge --dry-run
    python scripts/model_docs_workflow/enrich_catalog.py merge
"""

import argparse
import json
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


SCRIPT_DIR = Path(__file__).parent
CATALOG_DIR = SCRIPT_DIR / "catalog"
TARGETS_FILE = CATALOG_DIR / "targets.json"
RESULTS_DIR = CATALOG_DIR / "results"
OVERRIDES_FILE = CATALOG_DIR / "grouping_overrides.json"
DETAILS_FILE = SCRIPT_DIR.parent.parent / "budconnect" / "seeders" / "data" / "model_details.json"

# Bedrock prefixes a model id with a cross-region inference profile ("us.", "eu.", ...).
BEDROCK_REGION_PREFIXES = {"us", "eu", "jp", "apac", "global", "au", "ca", "us-gov", "in"}


# --------------------------------------------------------------------------------------------
# plan
# --------------------------------------------------------------------------------------------


def fetch_catalog(api: str, engine: str) -> List[Dict[str, Any]]:
    """Return the models budapp syncs: budconnect's compatible-models feed, active models only."""
    models: List[Dict[str, Any]] = []
    page, total_pages = 1, 1
    while page <= total_pages:
        url = f"{api.rstrip('/')}/model/get-compatible-models?engine={engine}&page={page}&limit=100"
        with urllib.request.urlopen(url, timeout=300) as response:  # noqa: S310 - operator-supplied URL
            body = json.load(response)
        total_pages = body["total_pages"]
        for provider in body["items"]:
            for model in provider["models"]:
                # The feed nests models under their provider and leaves the model's own field null.
                model["provider_type"] = provider["provider_type"]
                models.append(model)
        page += 1
    return models


def canonical_name(uri: str, provider_type: str) -> str:
    """Collapse a catalog URI to the model it serves.

    Only differences that cannot change what the model *is* are removed: the provider prefix,
    path segments for region / deployment / image size, Bedrock's inference-profile and vendor
    prefixes and its ``-v1:0`` revision, a Vertex ``@version``, and a full release date.

    Deliberately kept: Mistral's ``-2512`` style suffixes and ``-preview-09-2025`` (those name
    different generations, not snapshots of one), and ``-latest`` (an alias whose target moves).
    """
    rest = uri[len(provider_type) + 1 :] if uri.startswith(provider_type + "/") else uri.split("/", 1)[-1]
    name = rest.split("/")[-1].lower()
    name = name.split("@", 1)[0]
    if provider_type.startswith("bedrock"):
        parts = name.split(".")
        while len(parts) > 1 and parts[0] in BEDROCK_REGION_PREFIXES:
            parts = parts[1:]
        name = ".".join(parts)
        name = re.sub(r":\d+$", "", name)
        stripped = re.sub(r"-v\d+$", "", name)
        # "anthropic.claude-v2" is a model name, not a revision of "anthropic.claude".
        if re.search(r"\d", stripped.split(".", 1)[-1]):
            name = stripped
        if "." in name:
            vendor, tail = name.split(".", 1)
            name = f"{vendor}-{tail}" if re.match(r"^v\d", tail) else tail
    name = re.sub(r"-(\d{4}-\d{2}-\d{2}|\d{8})$", "", name)
    return name


def model_kind(endpoints: List[str]) -> str:
    """Name what a model is for, from the routes the catalog gives it (e.g. ``/v1/embeddings``)."""
    routes = " ".join(endpoints or []).lower()
    for kind, markers in (
        ("chat", ("chat/completions", "/v1/completions", "/v1/responses")),
        ("embedding", ("embeddings",)),
        ("image", ("images/",)),
        ("tts", ("audio/speech",)),
        ("stt", ("audio/transcriptions", "audio/translations")),
        ("rerank_moderation", ("rerank", "moderations", "classify")),
    ):
        if any(marker in routes for marker in markers):
            return kind
    return "no_route"


def slugify(name: str) -> str:
    """Return a filename-safe form of a canonical name."""
    return re.sub(r"[^a-z0-9._-]+", "-", name.lower()).strip("-")


def summarise_facts(members: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Collect what the catalog already knows about a group, for the researcher to rely on."""

    def values(key: str) -> List[Any]:
        found = {json.dumps(v, sort_keys=True) for v in (m.get(key) for m in members) if v not in (None, [], {})}
        return [json.loads(v) for v in sorted(found)]

    tokens = [m.get("tokens") or {} for m in members]
    return {
        "providers": sorted({m.get("provider_name") or m["provider_type"] for m in members}),
        "modality": sorted({x for m in members for x in (m.get("modality") or [])}),
        "endpoints": sorted({x for m in members for x in (m.get("endpoints") or [])}),
        "max_input_tokens": sorted({t["max_input_tokens"] for t in tokens if t.get("max_input_tokens")}),
        "max_output_tokens": sorted({t["max_output_tokens"] for t in tokens if t.get("max_output_tokens")}),
        "deprecation_date": values("deprecation_date"),
    }


def plan(args: argparse.Namespace) -> None:
    """Write the targets file: one entry per distinct model that still has no details."""
    catalog = fetch_catalog(args.api, args.engine)
    existing = set(json.loads(DETAILS_FILE.read_text())) if DETAILS_FILE.exists() else set()
    overrides: Dict[str, str] = json.loads(OVERRIDES_FILE.read_text()) if OVERRIDES_FILE.exists() else {}

    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for model in catalog:
        if model["uri"] in existing:
            continue
        name = overrides.get(model["uri"]) or canonical_name(model["uri"], model["provider_type"])
        groups[name].append(model)

    targets = []
    skipped_unrouted = 0
    for name, members in groups.items():
        # A model's kind comes from its most capable member: a chat model whose batch-only
        # regional copy has no route is still a chat model.
        kinds = {model_kind(m.get("endpoints") or []) for m in members}
        kind = next(
            (k for k in ("chat", "embedding", "image", "tts", "stt", "rerank_moderation") if k in kinds), "no_route"
        )
        if kind == "no_route" and not args.include_unrouted:
            # budapp hides a model with no route, so a description would never be seen.
            skipped_unrouted += 1
            continue
        targets.append(
            {
                "slug": slugify(name),
                "canonical": name,
                "kind": kind,
                "uris": sorted(m["uri"] for m in members),
                "facts": summarise_facts(members),
            }
        )
    targets.sort(key=lambda t: (t["kind"], t["canonical"]))

    slugs = [t["slug"] for t in targets]
    duplicates = {s for s in slugs if slugs.count(s) > 1}
    if duplicates:
        sys.exit(f"slug collision, add grouping overrides: {sorted(duplicates)}")

    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    TARGETS_FILE.write_text(json.dumps(targets, indent=2, sort_keys=True) + "\n")
    uri_count = sum(len(t["uris"]) for t in targets)
    by_kind: Dict[str, int] = defaultdict(int)
    for t in targets:
        by_kind[t["kind"]] += 1
    print(f"{len(catalog)} active models, {len(existing & {m['uri'] for m in catalog})} already have details")
    print(f"{len(targets)} targets covering {uri_count} URIs; {skipped_unrouted} unrouted groups skipped")
    print("by kind:", dict(sorted(by_kind.items(), key=lambda kv: -kv[1])))
    print(f"wrote {TARGETS_FILE}")


# --------------------------------------------------------------------------------------------
# merge
# --------------------------------------------------------------------------------------------


class Source(BaseModel):
    """A page the researcher opened and relied on."""

    url: str
    title: Optional[str] = None
    kind: Literal["maker", "host", "third_party"]

    @field_validator("url")
    @classmethod
    def _http(cls, value: str) -> str:
        if not re.match(r"^https?://", value):
            raise ValueError("source url must be http(s)")
        return value


# budmodel files every evaluation on the leaderboard as an accuracy score, so a rate where lower
# is better, a rating or a speed would read as a nonsense accuracy.
NOT_ACCURACY = re.compile(r"\b(wer|error rate|elo|speed|latency|time to first|tokens/s|ttft|price)\b", re.I)


class Evaluation(BaseModel):
    """A published benchmark score for this exact model: accuracy-style, higher is better, 0-100."""

    name: str = Field(min_length=1)
    score: float = Field(ge=0, le=100)
    source: str

    @field_validator("name")
    @classmethod
    def _accuracy_only(cls, value: str) -> str:
        if NOT_ACCURACY.search(value):
            raise ValueError(f"{value!r} is not an accuracy score; put it in an advantages sentence")
        return value

    @field_validator("score", mode="before")
    @classmethod
    def _number(cls, value: Any) -> Any:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("score must be a number")
        return value


def _short_items(items: List[str], limit: int = 300) -> List[str]:
    for item in items:
        if not item.strip() or len(item) > limit:
            raise ValueError(f"list items must be non-empty and at most {limit} characters")
    return items


class Details(BaseModel):
    """The fields a researcher fills in; budconnect's model_details columns."""

    description: str = Field(min_length=40, max_length=1200)
    advantages: List[str] = Field(min_length=1, max_length=8)
    disadvantages: List[str] = Field(default_factory=list, max_length=8)
    use_cases: List[str] = Field(min_length=1, max_length=8)
    evaluations: List[Evaluation] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list, max_length=120)
    website_url: Optional[str] = None
    github_url: Optional[str] = None

    _items = field_validator("advantages", "disadvantages", "use_cases")(_short_items)


class Result(BaseModel):
    """One file in catalog/results/."""

    slug: str
    canonical: str
    status: Literal["ok", "insufficient_sources"]
    researched_on: date
    method: str
    maker: Optional[str] = None
    details: Optional[Details] = None
    sources: List[Source] = Field(default_factory=list)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _sourced(self) -> "Result":
        if self.status == "ok":
            if self.details is None:
                raise ValueError("status ok needs details")
            if not self.sources:
                raise ValueError("status ok needs at least one source")
            opened = {s.url for s in self.sources}
            for evaluation in self.details.evaluations:
                if evaluation.source not in opened:
                    raise ValueError(f"evaluation {evaluation.name!r} cites a page not listed in sources")
        return self


def to_seeder_entry(result: Result) -> Dict[str, Any]:
    """Shape a validated result as a model_details.json value."""
    details = result.details
    assert details is not None
    return {
        "description": details.description,
        "advantages": details.advantages,
        "disadvantages": details.disadvantages,
        "use_cases": details.use_cases,
        "evaluations": [{"name": e.name, "score": e.score} for e in details.evaluations],
        "languages": details.languages,
        # budapp stores tags and tasks as {name, color} objects; leave them to budapp.
        "tags": [],
        "tasks": [],
        "papers": [],
        "github_url": details.github_url,
        "website_url": details.website_url,
        "logo_url": None,
        "architecture": None,
        "model_tree": None,
        "extraction_metadata": {
            "extraction_date": result.researched_on.isoformat(),
            "method": result.method,
            "provider": result.maker,
            "canonical": result.canonical,
            "sources": [s.model_dump(exclude_none=True) for s in result.sources],
            "evaluation_sources": {e.name: e.source for e in details.evaluations},
            "model_metadata": {},
        },
    }


def merge(args: argparse.Namespace) -> None:
    """Validate research results and merge them into model_details.json."""
    targets = {t["slug"]: t for t in json.loads(TARGETS_FILE.read_text())}
    details: Dict[str, Any] = json.loads(DETAILS_FILE.read_text()) if DETAILS_FILE.exists() else {}

    invalid, insufficient, unknown = [], [], []
    added = kept = replaced = 0
    for path in sorted(RESULTS_DIR.glob("*.json")):
        try:
            result = Result.model_validate_json(path.read_text())
        except ValidationError as exc:
            invalid.append((path.name, str(exc).replace("\n", " ")[:300]))
            continue
        target = targets.get(result.slug)
        if target is None:
            unknown.append(path.name)
            continue
        if result.status != "ok":
            insufficient.append(result.slug)
            continue
        entry = to_seeder_entry(result)
        for uri in target["uris"]:
            if uri in details and not args.refresh:
                kept += 1
                continue
            replaced += uri in details
            added += uri not in details
            details[uri] = json.loads(json.dumps(entry, sort_keys=True))

    print(f"results: {len(list(RESULTS_DIR.glob('*.json')))} files")
    print(f"URIs added: {added}, replaced: {replaced}, kept (already had details): {kept}")
    for slug in insufficient:
        print(f"  insufficient sources, left without details: {slug}")
    for name in unknown:
        print(f"  not in targets.json (re-run plan?): {name}")
    for name, error in invalid:
        print(f"  INVALID {name}: {error}")

    if args.dry_run:
        print("dry run: model_details.json not written")
    elif invalid and not args.allow_invalid:
        sys.exit("refusing to write with invalid results; fix them or pass --allow-invalid")
    else:
        # Sort URIs, but keep each existing entry's key order so the diff shows only what changed.
        DETAILS_FILE.write_text(json.dumps({uri: details[uri] for uri in sorted(details)}, indent=2))
        print(f"wrote {DETAILS_FILE} ({len(details)} entries)")


def main() -> None:
    """Parse arguments and run a step."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    steps = parser.add_subparsers(dest="step", required=True)

    plan_parser = steps.add_parser("plan", help="list the distinct models that still need details")
    plan_parser.add_argument("--api", required=True, help="budconnect base URL, e.g. https://connect.dev.bud.studio")
    plan_parser.add_argument("--engine", default="tensorzero", help="engine whose catalog budapp syncs")
    plan_parser.add_argument(
        "--include-unrouted", action="store_true", help="also target models with no route (budapp hides them)"
    )
    plan_parser.set_defaults(func=plan)

    merge_parser = steps.add_parser("merge", help="validate results and merge them into model_details.json")
    merge_parser.add_argument("--dry-run", action="store_true", help="validate and report, write nothing")
    merge_parser.add_argument("--refresh", action="store_true", help="replace URIs that already have details")
    merge_parser.add_argument("--allow-invalid", action="store_true", help="write even if some results are invalid")
    merge_parser.set_defaults(func=merge)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
