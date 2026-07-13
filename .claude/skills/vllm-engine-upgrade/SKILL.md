---
name: vllm-engine-upgrade
description: >-
  Upgrade the vLLM inference engine version in BudConnect end-to-end: mine a
  freshly-cloned vLLM source tree for its supported model architectures and
  tool/reasoning parsers, then propagate everything into the seed data
  (engines.json, model_architectures.json), the _VLLM_MODELS mirror script, the
  hardcoded parser menus in the seeder, and the docs. Use this whenever someone
  wants to bump the vLLM engine version, ship a new vLLM build, refresh the
  supported-model list, add a device build (CUDA/CPU/ROCM/HPU), sync BudConnect
  with a new vLLM release, or asks "what else needs updating when we upgrade
  vLLM" — even if they don't name this skill. BudConnect is a pre-deployment
  compatibility oracle, so getting the supported-architecture set exactly right
  matters: a wrong entry green-lights a deployment that fails at runtime.
---

# vLLM Engine Upgrade (BudConnect)

## Why this exists

BudConnect tells operators, **before** they deploy, whether a given model can run
on a given Bud engine build. For the vLLM engine that answer is **data-driven**:
nothing is computed at request time — it is all seeded from JSON files derived
from the vLLM source. An upgrade therefore means re-deriving that data from the
new vLLM and updating five coupled surfaces in lockstep. Miss one and BudConnect
either hides newly-supported models or advertises models the new engine rejects.

Versions track **Bud releases**, not upstream vLLM (the engine is a fork). See
`docs/engine-versioning.md`.

## Before you start — get three decisions from the user

1. **New version string** (e.g. `0.9.0`). This is a real change, not just an
   image tag — see the seeder gotcha below.
2. **Which device builds** are part of this rebuild (CUDA, CPU, ROCM, HPU). Only
   touch blocks whose image was actually rebuilt. CUDA and CPU currently ship the
   same vLLM fork, so their architecture lists are kept **identical**.
3. **The vLLM checkout path** (a fresh clone of the fork) and the **transformers
   version** its image pins (from vLLM `requirements/*.txt`) — needed for the
   backend-survivor check in Step 2.

## The five coupled surfaces

| File | What it holds | Derived from |
|---|---|---|
| `budconnect/seeders/data/engines.json` | per-device `version`, `container_image`, `architecture[]`, engine-level `parser_rules[]` | vLLM registry + parser registries |
| `budconnect/seeders/data/model_architectures.json` | per-arch `architecture_family`, tool/reasoning parser, LoRA/PP flags | vLLM registry + docs |
| `scripts/arch_support_to_seeder.py` | `_VLLM_MODELS` (hand-mirror of registry.py) | vLLM `registry.py` |
| `budconnect/seeders/engine.py` | hardcoded `supported_tool_calling` / `supported_reasoning` menus (vLLM branch, ~L130-176) | vLLM parser registries |
| `docs/engine-versioning.md` | version table + support policy | this procedure |

## Procedure

Work in `scratchpad/` for intermediates. Set `VLLM=<checkout>` and
`BUD=<repo root>`. The bundled scripts are under this skill's `scripts/`.

### Step 1 — Extract + diff (deterministic)

```bash
python scripts/extract_vllm_registry.py "$VLLM" \
    --engines "$BUD/budconnect/seeders/data/engines.json" --out scratchpad/vllm_extract.json
```

This AST-parses vLLM (never imports it) and emits the native architecture set,
the `class_name -> architecture_family` map, the tool/reasoning parser key sets,
and the natively-dropped archs (`_PREVIOUSLY_SUPPORTED_MODELS`). It prints the
added/removed diff vs the current seed. The four source-of-truth locations are
documented in the script header; if it errors that a file/dict moved, re-scout
them (they are stable but vLLM does refactor).

### Step 2 — Dropped ≠ unsupported: the Transformers-backend check

vLLM removing an architecture natively does **not** mean the model can't run.
In default `--model-impl auto`, vLLM falls back to its Transformers backend
*before* erroring (`_try_resolve_transformers` → `_raise_for_unsupported` in
`registry.py`). So a natively-dropped arch is still deployable iff HF Transformers
has a backend-compatible class for it.

```bash
python scripts/check_transformers_backend.py --from-extract scratchpad/vllm_extract.json
```

Run this with the transformers version the image pins. **KEEP** the arch in the
compatibility lists when it prints `KEEP`; only truly remove the rest. Also keep
removed the ones that are just aliases of a still-supported arch (e.g.
`InternLMForCausalLM`, `Aquila*`, `Xverse`, `TeleChat` → their real checkpoints
declare `LlamaForCausalLM`/`TeleChat2ForCausalLM`, which stay listed). See
`references/background.md` for the full reasoning and the last run's verdicts.

The final compatibility set = **native archs ∪ Transformers-backend survivors**.

### Step 3 — Apply edits (keep diffs minimal)

Both JSON files round-trip **exactly** under a standard dump, so load → mutate →
dump instead of hand-editing big arrays. This keeps the diff to only real changes:

- `engines.json` → `json.dumps(data, indent=4, ensure_ascii=False) + "\n"`
- `model_architectures.json` → `json.dumps(data, indent=2, ensure_ascii=False) + "\n"`

Verify round-trip before editing (`dump(load(x)) == x`); if it ever fails, fall
back to targeted string edits.

Apply, per file:

- **engines.json** — for each rebuilt device block: set `version` to the new
  string and `container_image` to the new tag; replace `architecture[]` with
  `sorted(native ∪ survivors)`; keep CUDA and CPU **identical**. Then drop any
  `parser_rules[]` whose `parser_type` is no longer a valid tool/reasoning name
  (e.g. a rule pointing at a dropped model's parser).
- **model_architectures.json** — remove truly-dropped archs; append new native
  archs with `architecture_family` from the extract and **null parsers / false
  flags** (the established default); restore Transformers-backend survivors from
  git HEAD, **scrubbing any now-invalid parser value to null**. Keep the class
  set identical to engines.json.
- **arch_support_to_seeder.py** — `python scripts/remirror_seeder.py "$VLLM"
  "$BUD/scripts/arch_support_to_seeder.py" --commit <hash>`. This mirrors the
  **native** registry only, so engines.json / model_architectures.json are an
  intentional superset (they also carry the survivors) — note that in the docs.
- **engine.py** — replace the `supported_tool_calling` and `supported_reasoning`
  list literals (vLLM branch) with the full extracted key sets. These menus are
  hardcoded, not derived — the single easiest file to forget.

### Step 4 — Enrich parser assignments (conservative)

The authoritative arch→parser source is vLLM's own docs:
`docs/features/tool_calling.md` and `docs/features/reasoning_outputs.md`
("Recommended flags: `--tool-call-parser X`" / `--reasoning-parser X`). Bridge
model family → arch class via `architecture_family`. Rules:

- Only **fill nulls** where the doc clearly names the parser. Do **not** overwrite
  an existing curated value silently — flag it for the user.
- Most archs stay null. Draft/MTP/Eagle heads, audio/speech, OCR, vision-only,
  embedding, and token-classification models have **no** tool/reasoning parser.
- Never invent a parser name — every value must be in the extracted key sets.
- LoRA / PP flags for new archs come from vLLM's `docs/.../supported_models.md`
  (LoRA and PP columns) or the model class's `Supports*` interfaces.

### Step 5 — Verify (run every check)

```bash
python scripts/verify_upgrade.py "$VLLM" "$BUD" scratchpad/vllm_extract.json
```

It asserts: every parser reference across engine.py, engines.json `parser_rules`,
and model_architectures.json is a valid registry name; CUDA arch list == CPU ==
model_architectures class set; both JSONs still round-trip; the re-mirrored
`_VLLM_MODELS` composes to the native count and downstream scripts import; and the
compatibility set == native ∪ survivors. For a heavier upgrade, additionally have
independent agents re-derive the numbers from vLLM and diff the applied files.

### Step 6 — Ship

- Update `docs/engine-versioning.md`: the version table and the architecture-count
  / support-policy note (native + Transformers-backend counts).
- Re-run the `EngineSeeder` to load the rows, then smoke-test
  `GET /engine/get-latest-engine-version?engine=vllm&device_architecture=CUDA`
  and `GET /engine/get-compatible-engines`.

## Seeder gotchas (read before shipping)

- **The `version` string MUST change**, not just the image tag. The seeder is
  insert-only on `(engine, version, device_architecture)` and never updates an
  existing row's `container_image`; reusing the version leaves the old image in
  the DB and runtimes keep pulling it.
- **"Latest" = most recently seeded (`created_at DESC`), not highest semver.**
- **CUDA and CPU architecture lists must stay in lockstep** — they ship the same
  fork.
- **Dropped ≠ unsupported** — always run the Step 2 Transformers-backend check.
- No Alembic migration is needed — all vLLM data lives in these JSON seed files.

## Reference

`references/background.md` — the vLLM resolution order (why the backend check is
correct), the categories of why vLLM drops architectures, and the verdicts /
counts from the last upgrade (native 354, tool 43, reasoning 27, +9 survivors →
363) as a worked example.
