#!/usr/bin/env python3
"""Decide which natively-dropped architectures are STILL deployable on the new
vLLM via its Transformers backend.

BudConnect is a pre-deploy compatibility oracle: an arch stays listed if the
engine can deploy it natively OR via the Transformers backend. vLLM's default
`--model-impl auto` falls back to the Transformers backend BEFORE raising the
"not supported" error (see _try_resolve_transformers / _raise_for_unsupported in
registry.py). This script reproduces vLLM's exact per-arch gate:

    getattr(transformers, ArchName).is_backend_compatible()  == True

Run it with the SAME transformers version the target image ships (check vLLM's
requirements/*.txt, e.g. `transformers==5.13.1`). Results can differ across
transformers majors, so mismatches make the verdict unreliable.

Usage:
    python check_transformers_backend.py <arch> [<arch> ...]
    python check_transformers_backend.py --from-extract vllm_extract.json   # checks all dropped archs

Prints, for each arch: whether Transformers has a class and whether it is
backend-compatible. KEEP the True ones in the compatibility lists; drop the rest.

Caveat: archs with NO Transformers class can still sometimes run per-checkpoint
via `trust_remote_code` + the model repo's `auto_map`, but that is not an
arch-level guarantee — excluding them avoids false "supported" verdicts (worse
for a pre-deploy oracle than a false negative).
"""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archs", nargs="*")
    ap.add_argument("--from-extract", help="vllm_extract.json; checks all its dropped_archs")
    args = ap.parse_args()

    try:
        import transformers
    except ImportError:
        sys.exit("ERROR: transformers not importable. Install the version the target vLLM image pins "
                 "(see vLLM requirements/*.txt) and re-run.")

    archs = list(args.archs)
    if args.from_extract:
        archs += list(json.load(open(args.from_extract, encoding="utf-8")).get("dropped_archs", {}))
    if not archs:
        sys.exit("No architectures given. Pass arch names or --from-extract vllm_extract.json")

    print(f"transformers version: {transformers.__version__}\n")
    print(f"{'architecture':50} class  backend_compatible  -> verdict")
    keep, drop = [], []
    for a in dict.fromkeys(archs):  # dedupe, preserve order
        cls = getattr(transformers, a, None)
        compat = None
        if cls is not None:
            try:
                compat = cls.is_backend_compatible()
            except Exception as e:
                compat = f"err:{e.__class__.__name__}"
        verdict = "KEEP (transformers-backend)" if compat is True else "drop"
        (keep if compat is True else drop).append(a)
        print(f"{a:50} {'Y' if cls else 'N':5}  {str(compat):18}  -> {verdict}")

    print(f"\nKEEP ({len(keep)}): {keep}")
    print(f"DROP ({len(drop)}): {drop}")


if __name__ == "__main__":
    main()
