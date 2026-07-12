#!/usr/bin/env python3
"""Extract the vLLM support surface (model architectures + tool/reasoning parsers)
from a vLLM source checkout, purely via AST — never imports vLLM.

Usage:
    python extract_vllm_registry.py <vllm_dir> [--engines <engines.json>] [--out <out.json>]

Prints a diff of native architectures / parser keys against the current
budconnect engines.json (the "vllm" engine), and writes the derived data to
--out (default: vllm_extract.json) for the apply step.

Sources of truth inside vLLM (stable across releases):
  - architectures: union of the 10 dicts that compose _VLLM_MODELS in
    vllm/model_executor/models/registry.py (excludes _PREVIOUSLY_SUPPORTED_MODELS
    and _OOT_SUPPORTED_MODELS).
  - tool parsers: keys of _TOOL_PARSERS_TO_REGISTER in vllm/tool_parsers/__init__.py
  - reasoning parsers: keys of _REASONING_PARSERS_TO_REGISTER in vllm/reasoning/__init__.py
  - dropped archs: _PREVIOUSLY_SUPPORTED_MODELS in registry.py (arch -> last version)
"""
import argparse
import ast
import json
import os
import sys

# The 10 component dicts that registry.py merges into _VLLM_MODELS. If a future
# vLLM renames/adds one, update this list (check the `_VLLM_MODELS = {**...}` block).
VLLM_COMPONENT_DICTS = [
    "_TEXT_GENERATION_MODELS", "_EMBEDDING_MODELS", "_LATE_INTERACTION_MODELS",
    "_REWARD_MODELS", "_TOKEN_CLASSIFICATION_MODELS", "_SEQUENCE_CLASSIFICATION_MODELS",
    "_MULTIMODAL_MODELS", "_SPECULATIVE_DECODING_MODELS",
    "_TRANSFORMERS_SUPPORTED_MODELS", "_TRANSFORMERS_BACKEND_MODELS",
]


def _top_level_dicts(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = node.value
    return out


def _dict_keys(dnode):
    return [k.value for k in dnode.keys if isinstance(k, ast.Constant)]


def _first_tuple_elt(vnode):
    if isinstance(vnode, ast.Tuple) and vnode.elts and isinstance(vnode.elts[0], ast.Constant):
        return vnode.elts[0].value
    return None


def extract(vllm_dir):
    registry = os.path.join(vllm_dir, "vllm/model_executor/models/registry.py")
    tool_init = os.path.join(vllm_dir, "vllm/tool_parsers/__init__.py")
    reason_init = os.path.join(vllm_dir, "vllm/reasoning/__init__.py")
    for p in (registry, tool_init, reason_init):
        if not os.path.exists(p):
            sys.exit(f"ERROR: expected file not found: {p}\n"
                     "vLLM layout changed — re-scout the source-of-truth locations (see SKILL.md).")

    reg = _top_level_dicts(registry)
    missing = [d for d in VLLM_COMPONENT_DICTS if d not in reg]
    if missing:
        sys.exit(f"ERROR: registry.py missing expected dicts {missing}. "
                 "Re-check the `_VLLM_MODELS = {**...}` composition and update VLLM_COMPONENT_DICTS.")

    family = {}  # class_name -> architecture_family (first tuple elt); later dict wins (mirrors ** merge)
    for dname in VLLM_COMPONENT_DICTS:
        for k, v in zip(reg[dname].keys, reg[dname].values):
            if isinstance(k, ast.Constant):
                fam = _first_tuple_elt(v)
                if fam is not None:
                    family[k.value] = fam
    native_archs = sorted(family)

    dropped = {}
    if "_PREVIOUSLY_SUPPORTED_MODELS" in reg:
        d = reg["_PREVIOUSLY_SUPPORTED_MODELS"]
        for k, v in zip(d.keys, d.values):
            if isinstance(k, ast.Constant):
                dropped[k.value] = v.value if isinstance(v, ast.Constant) else None

    tool = _dict_keys(_top_level_dicts(tool_init)["_TOOL_PARSERS_TO_REGISTER"])

    reason = []
    for node in ast.walk(ast.parse(open(reason_init, encoding="utf-8").read())):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "_REASONING_PARSERS_TO_REGISTER":
                    reason = _dict_keys(node.value)

    return {
        "native_archs": native_archs,
        "arch_family": family,
        "tool_parsers": tool,
        "reasoning_parsers": reason,
        "dropped_archs": dropped,
    }


def _diff(label, old, new):
    olds, news = set(old), set(new)
    added, removed = sorted(news - olds), sorted(olds - news)
    print(f"\n== {label}: {len(olds)} -> {len(news)}  (+{len(added)} / -{len(removed)}) ==")
    if added:
        print(f"  ADDED   ({len(added)}): {added}")
    if removed:
        print(f"  REMOVED ({len(removed)}): {removed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vllm_dir")
    ap.add_argument("--engines", help="path to budconnect engines.json for diffing")
    ap.add_argument("--out", default="vllm_extract.json")
    args = ap.parse_args()

    data = extract(args.vllm_dir)
    print(f"vLLM native architectures: {len(data['native_archs'])}")
    print(f"tool parsers: {len(data['tool_parsers'])}  reasoning parsers: {len(data['reasoning_parsers'])}")
    print(f"natively-dropped archs (_PREVIOUSLY_SUPPORTED_MODELS): {len(data['dropped_archs'])}")

    if args.engines and os.path.exists(args.engines):
        engines = json.load(open(args.engines, encoding="utf-8"))
        vllm = next((e for e in engines if e.get("name") == "vllm"), None)
        if vllm and vllm.get("versions"):
            cur = vllm["versions"][0]["compatibilities"][0]["architecture"]
            _diff("architectures (vs current engines.json block 0)", cur, data["native_archs"])
            print("\n  NOTE: current list may include Transformers-backend survivors on top of the\n"
                  "  native set — run check_transformers_backend.py before removing anything.")

    json.dump(data, open(args.out, "w", encoding="utf-8"), indent=2)
    print(f"\n[written] {args.out}")


if __name__ == "__main__":
    main()
