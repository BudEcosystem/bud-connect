"""Static transitive module-level import walk over an image's site-packages.

Flags each registered arch whose unguarded module-level import chain reaches a
module the image does not ship. argv: <site-packages> <arch->module json>
"""

import ast
import json
import os
import sys


SP = sys.argv[1]


STDLIB = set(sys.stdlib_module_names) | set(sys.builtin_module_names)


def resolve(mod):
    if mod.split(".")[0] in STDLIB:
        return "NS"
    p = os.path.join(SP, *mod.split("."))
    for c in (p + ".py", os.path.join(p, "__init__.py")):
        if os.path.isfile(c):
            return c
    if os.path.isdir(p):
        return "NS"
    d, b = os.path.dirname(p), os.path.basename(p)
    if os.path.isdir(d) and any(f.startswith(b + ".") and f.endswith(".so") for f in os.listdir(d)):
        return "SO"
    return None


def toplevel_imports(path, mod, is_pkg):
    tree = ast.parse(open(path).read())
    out = []

    def walk(body, guarded):
        for n in body:
            if isinstance(n, ast.Import):
                for a in n.names:
                    out.append((a.name, None, guarded))
            elif isinstance(n, ast.ImportFrom):
                base = n.module or ""
                if n.level:
                    pkg = mod if is_pkg else mod.rsplit(".", 1)[0]
                    for _ in range(n.level - 1):
                        pkg = pkg.rsplit(".", 1)[0]
                    base = pkg + ("." + base if base else "")
                out.append((base, [a.name for a in n.names], guarded))
            elif isinstance(n, ast.Try):
                walk(n.body, True)
                for h in n.handlers:
                    walk(h.body, True)
                walk(n.orelse, guarded)
                walk(n.finalbody, guarded)
            elif isinstance(n, ast.If):
                t = ast.unparse(n.test)
                if "TYPE_CHECKING" in t:
                    continue
                # Conditional imports count as guarded, except the else branch of
                # a bare `if current_platform.is_rocm():`, which a CPU build always
                # takes (the per-device packages fall back to nvidia/ there).
                walk(n.body, True)
                rocm_only = "is_rocm" in t and "not" not in t
                walk(n.orelse, not rocm_only)

    walk(tree.body, False)
    return out


MEMO = {}
ACTIVE = set()


def missing_chain(mod, seen=None, chain=None):
    """Memoized: returns the import chain from mod to a missing module, or None."""
    if mod in MEMO:
        return MEMO[mod]
    if mod in ACTIVE:
        return None
    ACTIVE.add(mod)
    res = _walk(mod)
    ACTIVE.discard(mod)
    MEMO[mod] = res
    return res


def _walk(mod):
    r = resolve(mod)
    if r is None:
        return [mod]
    if r in ("NS", "SO") or not mod.startswith("vllm"):
        return None
    for base, names, guarded in toplevel_imports(r, mod, r.endswith("__init__.py")):
        if guarded:
            continue
        parts = base.split(".")
        cands = [".".join(parts[:i]) for i in range(1, len(parts))] + [base]
        for nm in names or []:
            if nm != "*" and resolve(base + "." + nm) is not None:
                cands.append(base + "." + nm)
        for c in cands:
            m = missing_chain(c)
            if m:
                return [mod] + m
    return None


arch_map = json.load(open(sys.argv[2]))
res = {a: missing_chain(m) for a, m in sorted(arch_map.items())}
print(json.dumps({a: c for a, c in res.items() if c}, indent=1))
