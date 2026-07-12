#!/usr/bin/env python3
"""Verify an applied vLLM engine upgrade in BudConnect.

Usage:
    python verify_upgrade.py <vllm_dir> <budconnect_root> [vllm_extract.json]

Checks (exits non-zero on any failure):
  1. Every parser reference in engine.py menus, engines.json parser_rules, and
     model_architectures.json is a valid vLLM registry name.
  2. All vLLM device blocks share one architecture list (lockstep) and it equals
     the model_architectures.json class set.
  3. engines.json (indent=4) and model_architectures.json (indent=2) still
     round-trip (minimal-diff guarantee held).
  4. The re-mirrored _VLLM_MODELS composes to the native count; the compatibility
     set == native ∪ (extra survivors), i.e. only Transformers-backend survivors
     sit on top of the native registry.
"""
import ast
import importlib.util
import json
import os
import sys

FAIL = []


def check(cond, msg):
    print(("  ok  " if cond else "  FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


def main():
    vllm_dir, bud = sys.argv[1], sys.argv[2]
    extract_path = sys.argv[3] if len(sys.argv) > 3 else None

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from extract_vllm_registry import extract  # noqa: E402
    data = json.load(open(extract_path, encoding="utf-8")) if extract_path and os.path.exists(extract_path) \
        else extract(vllm_dir)
    VT, VR = set(data["tool_parsers"]), set(data["reasoning_parsers"])
    native = set(data["native_archs"])

    ep = os.path.join(bud, "budconnect/seeders/data/engines.json")
    mp = os.path.join(bud, "budconnect/seeders/data/model_architectures.json")

    # round-trip
    print("[round-trip]")
    for p, ind in ((ep, 4), (mp, 2)):
        s = open(p, encoding="utf-8").read()
        check(json.dumps(json.loads(s), indent=ind, ensure_ascii=False) + "\n" == s,
              f"{os.path.basename(p)} round-trips at indent={ind}")

    engines = json.load(open(ep, encoding="utf-8"))
    vllm = next(e for e in engines if e["name"] == "vllm")
    arch_lists = [v["compatibilities"][0]["architecture"] for v in vllm["versions"]]
    ma = json.load(open(mp, encoding="utf-8"))["architectures"]
    maset = {a["class_name"] for a in ma}

    print("\n[lockstep + consistency]")
    check(all(a == arch_lists[0] for a in arch_lists), "all device arch lists identical (lockstep)")
    check(all(a == sorted(a) for a in arch_lists), "arch lists sorted")
    check(set(arch_lists[0]) == maset, "engines arch set == model_architectures class set")
    check(native <= set(arch_lists[0]), "all native archs present")
    check(set(arch_lists[0]) - native == maset - native, "extras beyond native are consistent (survivors)")
    print(f"      native={len(native)}  listed={len(arch_lists[0])}  survivors={len(set(arch_lists[0]) - native)}")

    print("\n[parser validity]")
    bad_ma = [a["class_name"] for a in ma
              if (a["tool_calling_parser_type"] and a["tool_calling_parser_type"] not in VT)
              or (a["reasoning_parser_type"] and a["reasoning_parser_type"] not in VR)]
    check(not bad_ma, f"model_architectures parser refs all valid (bad: {bad_ma})")

    bad_rules = []
    for r in vllm.get("parser_rules", []):
        pt = (r.get("parser_type") or "").strip()
        if not pt:
            continue
        valid = VR if r.get("rule_type", "tool").lower() == "reasoning" else VT
        if pt not in valid:
            bad_rules.append(pt)
    check(not bad_rules, f"engines.json parser_rules all valid (bad: {bad_rules})")

    src = open(os.path.join(bud, "budconnect/seeders/engine.py"), encoding="utf-8").read()
    menus = {}
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id in ("supported_tool_calling", "supported_reasoning") \
                        and isinstance(n.value, ast.List):
                    v = [e.value for e in n.value.elts if isinstance(e, ast.Constant)]
                    if v:
                        menus[t.id] = set(v)
    check(menus.get("supported_tool_calling") == VT, "engine.py tool menu == registry tool set")
    check(menus.get("supported_reasoning") == VR, "engine.py reasoning menu == registry reasoning set")

    print("\n[mirror]")
    sp = os.path.join(bud, "scripts/arch_support_to_seeder.py")
    spec = importlib.util.spec_from_file_location("arch_support_to_seeder", sp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    check(len(set(mod._VLLM_MODELS)) == len(native),
          f"_VLLM_MODELS mirror composes to native count ({len(set(mod._VLLM_MODELS))} vs {len(native)})")

    print("\n" + ("ALL CHECKS PASSED" if not FAIL else f"{len(FAIL)} CHECK(S) FAILED"))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
