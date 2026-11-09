#!/usr/bin/env python3
"""Derive every vLLM architecture's LoRA / pipeline-parallel support from source.

Purely via AST — never imports vLLM. model_architectures.json's `supports_lora` / `supports_pipeline_parallelism` must
equal vLLM's own `supports_lora()` / `supports_pp()` on the class the CUDA image
loads. Those change for EXISTING archs too (v0.32.0 added SupportsLoRA to
BertEmbeddingModel, so 7 BERT/RoBERTa embedding archs gained LoRA), so re-derive
them for every arch on every upgrade, not only for the new ones.

Reproduces the runtime checks in vllm/model_executor/models/interfaces.py:
  - LoRA: `supports_lora`, `packed_modules_mapping` and `embedding_modules` are all
    present in the class's MRO (runtime_checkable protocols test presence only;
    SupportsLoRA itself provides all three).
  - PP: `supports_pp` and `make_empty_intermediate_tensors` are present in the MRO
    (SupportsPP provides both), and the first `forward` in the MRO accepts
    `intermediate_tensors` (or **kwargs, which supports_kw allows).
The MRO is the real C3 linearisation. Bases resolve through imports, imports inside
module-level if/try blocks (per-platform branches), and module-level aliases such as
`_Base = as_embedding_model(LlamaForCausalLM)`. Per-device `vllm.models.<pkg>` archs
resolve to the nvidia/ implementation, which is what the CUDA image loads.

Calibration: on v0.31.0 this reproduces all 387 flags that the 0.10.0 seed took from
runtime calls inside the image. If you change the resolver, re-calibrate: run it on
the previous release's tag and diff against the model_architectures.json that release
shipped with (`git show <commit>:budconnect/seeders/data/model_architectures.json`);
the diff must be empty.

Usage:
    python derive_lora_pp.py <vllm_dir> [--arch-json model_architectures.json] [--out flags.json]

With --arch-json it prints every native arch whose stored flags differ from the
derived ones, and exits 1 if any do. Transformers-backend survivors (outside the
native registry) take the flags of the `Transformers*` backend classes, which are
derived here as well.
"""
import argparse
import ast
import json
import os
import pathlib
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_vllm_registry import VLLM_COMPONENT_DICTS, _top_level_dicts  # noqa: E402


PROTOCOL_ATTRS = {
    "SupportsLoRA": {"supports_lora", "packed_modules_mapping", "embedding_modules"},
    "SupportsPP": {"supports_pp", "make_empty_intermediate_tensors", "forward"},
}
LORA_ATTRS = {"supports_lora", "packed_modules_mapping", "embedding_modules"}
PP_ATTRS = {"supports_pp", "make_empty_intermediate_tensors"}
OTHER_PLATFORMS = (".amd.", ".xpu.", ".cpu.")


class _Index:
    """Classes and import aliases of vllm/model_executor/models and vllm/models."""

    def __init__(self, root):
        self.root = root
        self.classes = {}  # (module, name) -> {"bases": [...], "attrs": {...}, "fwd": bool | None}
        self.imports = {}  # module -> {local_name: (module, name)}
        self._mro = {}
        for d in ("vllm/model_executor/models", "vllm/models"):
            for path in (root / d).rglob("*.py"):
                self._index_file(path)

    def _index_file(self, path):
        parts = list(path.relative_to(self.root).with_suffix("").parts)
        is_pkg = parts[-1] == "__init__"
        mod = ".".join(parts[:-1] if is_pkg else parts)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            return
        imp = {}
        top = [n for n in tree.body if isinstance(n, ast.ImportFrom)]
        nested = [n for b in tree.body if isinstance(b, (ast.If, ast.Try))
                  for n in ast.walk(b) if isinstance(n, ast.ImportFrom)]
        for node in top + nested:
            src = self._absolute(mod, is_pkg, node.level, node.module)
            for a in node.names:
                imp.setdefault(a.asname or a.name, (src, a.name))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                value = node.value
                if isinstance(value, ast.Call) and value.args and isinstance(value.args[0], ast.Name):
                    value = value.args[0]
                if isinstance(value, ast.Name) and value.id != node.targets[0].id:
                    imp.setdefault(node.targets[0].id, (mod, value.id))
        self.imports[mod] = imp
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                self.classes[(mod, node.name)] = self._class_info(node)

    @staticmethod
    def _absolute(mod, is_pkg, level, target):
        if level == 0:
            return target
        base = mod.split(".") if is_pkg else mod.split(".")[:-1]
        base = base[: len(base) - (level - 1)]
        return ".".join(base + ([target] if target else []))

    @staticmethod
    def _class_info(node):
        attrs, fwd = set(), None
        for b in node.body:
            if isinstance(b, (ast.Assign, ast.AnnAssign)):
                targets = b.targets if isinstance(b, ast.Assign) else [b.target]
                attrs.update(t.id for t in targets if isinstance(t, ast.Name))
            elif isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                attrs.add(b.name)
                if b.name == "forward":
                    names = {a.arg for a in b.args.args + b.args.kwonlyargs}
                    fwd = "intermediate_tensors" in names or b.args.kwarg is not None
        return {"bases": [ast.unparse(x) for x in node.bases], "attrs": attrs, "fwd": fwd}

    def find(self, mod, name, seen=None):
        seen = seen if seen is not None else set()
        if (mod, name) in seen:
            return None
        seen.add((mod, name))
        if (mod, name) in self.classes:
            return (mod, name)
        target = self.imports.get(mod, {}).get(name)
        return self.find(*target, seen) if target else None

    def _base(self, mod, expr):
        if "." in expr:  # nn.Module, module.Class
            head, _, tail = expr.rpartition(".")
            src = self.imports.get(mod, {}).get(head)
            return (src and self.find(f"{src[0]}.{src[1]}", tail)) or ("<ext>", expr)
        expr = expr.split("[")[0]
        return self.find(mod, expr) or ("<ext>", expr)

    def mro(self, key, _stack=()):
        if key in self._mro:
            return self._mro[key]
        if key not in self.classes or key in _stack:
            return [key]
        bases = [self._base(key[0], b) for b in self.classes[key]["bases"]]
        seqs = [list(self.mro(b, _stack + (key,))) for b in bases] + [list(bases)]
        out = [key]
        while True:
            seqs = [q for q in seqs if q]
            if not seqs:
                break
            head = next((q[0] for q in seqs if not any(q[0] in r[1:] for r in seqs)), seqs[0][0])
            out.append(head)
            for q in seqs:
                if q and q[0] == head:
                    del q[0]
        self._mro[key] = out
        return out

    def flags(self, key):
        attrs, names, fwd = set(), set(), None
        for k in self.mro(key):
            names.add(k[1].split("[")[0])
            if k in self.classes:
                attrs |= self.classes[k]["attrs"]
                if fwd is None:
                    fwd = self.classes[k]["fwd"]
        for proto, pattrs in PROTOCOL_ATTRS.items():
            if proto in names:
                attrs |= pattrs
        pp_fwd = fwd if fwd is not None else "SupportsPP" in names
        return attrs >= LORA_ATTRS, attrs >= PP_ATTRS and bool(pp_fwd)

    def locate(self, module, cls):
        if module.startswith("vllm.models."):
            cands = sorted(k for k in self.classes if k[1] == cls and k[0].startswith(module + "."))
            for pref in (".nvidia.", ".common.", ""):
                hit = [k for k in cands
                       if pref in k[0] + "." and not any(p in k[0] + "." for p in OTHER_PLATFORMS)]
                if hit:
                    return hit[0]
            return self.find(module, cls)
        return self.find(f"vllm.model_executor.models.{module}", cls)


def derive_flags(vllm_dir):
    """Return {arch: {"lora", "pp", "class"}} for every arch in vLLM's native registry."""
    root = pathlib.Path(vllm_dir)
    index = _Index(root)
    dicts = _top_level_dicts(str(root / "vllm/model_executor/models/registry.py"))
    out = {}
    for name in VLLM_COMPONENT_DICTS:
        node = dicts.get(name)
        if node is None:
            continue
        for k, v in zip(node.keys, node.values):
            if not (isinstance(k, ast.Constant) and isinstance(v, ast.Tuple) and len(v.elts) >= 2):
                continue
            module, cls = v.elts[0].value, v.elts[1].value
            key = index.locate(module, cls)
            if key is None:
                out[k.value] = {"error": f"unresolved {module}.{cls}"}
                continue
            lora, pp = index.flags(key)
            out[k.value] = {"lora": lora, "pp": pp, "class": f"{key[0]}.{key[1]}"}
    return out


def diff_flags(derived, arch_json):
    """Native archs whose stored flags differ from the derived ones: [(arch, derived, stored, class)]."""
    with open(arch_json, encoding="utf-8") as f:
        stored = {a["class_name"]: a for a in json.load(f)["architectures"]}
    out = []
    for arch, r in sorted(derived.items()):
        if arch not in stored or "error" in r:
            continue
        s = stored[arch]
        have = (s["supports_lora"], s["supports_pipeline_parallelism"])
        if (r["lora"], r["pp"]) != have:
            out.append((arch, (r["lora"], r["pp"]), have, r["class"]))
    return out


def main():
    """Print the derived flags; with --arch-json, diff them and exit 1 on any mismatch."""
    ap = argparse.ArgumentParser()
    ap.add_argument("vllm_dir")
    ap.add_argument("--arch-json", help="model_architectures.json to diff against")
    ap.add_argument("--out", help="write the derived flags here")
    args = ap.parse_args()

    derived = derive_flags(args.vllm_dir)
    unresolved = sorted(a for a, r in derived.items() if "error" in r)
    print(f"derived LoRA/PP for {len(derived) - len(unresolved)} of {len(derived)} native archs")
    if unresolved:
        print(f"  UNRESOLVED (fix the resolver, or check these by hand): {unresolved}")
    backend = sorted({(r["lora"], r["pp"]) for a, r in derived.items() if a.startswith("Transformers")
                      and "error" not in r})
    print(f"  Transformers* backend classes (lora, pp): {backend}")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(derived, f, indent=1, sort_keys=True)
        print(f"[written] {args.out}")
    if args.arch_json:
        mismatches = diff_flags(derived, args.arch_json)
        print(f"\n{len(mismatches)} arch(s) whose stored (lora, pp) differ from vLLM's classes:")
        for arch, want, have, cls in mismatches:
            print(f"  {arch}: stored {have} -> derived {want}   ({cls})")
        sys.exit(1 if mismatches or unresolved else 0)


if __name__ == "__main__":
    main()
