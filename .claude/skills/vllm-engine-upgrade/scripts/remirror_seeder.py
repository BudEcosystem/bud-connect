#!/usr/bin/env python3
"""Re-mirror scripts/arch_support_to_seeder.py's _VLLM_MODELS block verbatim from
the new vLLM registry.py, preserving the script's header + helper functions.

The seeder script's dict block is a hand-copy of registry.py lines
`_TEXT_GENERATION_MODELS = {` ... end of `_VLLM_MODELS = {...}`. This copies that
block byte-for-byte so the mirror can never silently drift from upstream.

Usage:
    python remirror_seeder.py <vllm_dir> <path/to/scripts/arch_support_to_seeder.py> [--commit <hash>]

Verify afterwards:
    (cd scripts && python -c "import arch_support_to_seeder as m; print(len(set(m._VLLM_MODELS)))")
This mirrors the NATIVE registry only. engines.json / model_architectures.json
are an intentional superset (they also carry Transformers-backend survivors).
"""
import argparse
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vllm_dir")
    ap.add_argument("seeder_script")
    ap.add_argument("--commit", default="", help="vLLM commit hash for the provenance comment")
    args = ap.parse_args()

    registry = os.path.join(args.vllm_dir, "vllm/model_executor/models/registry.py")
    lines = open(registry, encoding="utf-8").read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("_TEXT_GENERATION_MODELS = {"))
        vstart = next(i for i, l in enumerate(lines) if l.startswith("_VLLM_MODELS = {"))
        end = next(i for i in range(vstart, len(lines)) if lines[i].strip() == "}")
    except StopIteration:
        sys.exit("ERROR: could not locate the _TEXT_GENERATION_MODELS.._VLLM_MODELS block in registry.py")
    block = "\n".join(lines[start:end + 1])

    pin = f" (vLLM @ {args.commit})" if args.commit else ""
    new_script = (
        "import json\n"
        "import sys\n\n\n"
        "# yapf: disable\n"
        f"# Mirrored from {registry}{pin}\n"
        f"{block}\n"
        "# yapf: enable\n\n\n"
        "def build_arch_list() -> list:\n"
        "    return list(_VLLM_MODELS.keys())\n\n\n"
        "def write_arch_json(output_file: str) -> None:\n"
        "    model_list = build_arch_list()\n"
        "    print(model_list)\n"
        '    output_data = {"architectures": model_list}\n'
        "    output_json = json.dumps(output_data, indent=2, ensure_ascii=False)\n"
        '    with open(output_file, "w", encoding="utf-8") as f:\n'
        "        f.write(output_json)\n"
        '    print(f"Output written to: {output_file}", file=sys.stderr)\n\n\n'
        "def main() -> None:\n"
        '    write_arch_json("arch.json")\n\n\n'
        'if __name__ == "__main__":\n'
        "    main()\n"
    )
    open(args.seeder_script, "w", encoding="utf-8").write(new_script)
    print(f"re-mirrored {args.seeder_script} from registry.py lines {start + 1}-{end + 1}")


if __name__ == "__main__":
    main()
