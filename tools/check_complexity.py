"""Require Radon rank A/B for functions, including closures and methods."""

import ast
import hashlib
import json
from pathlib import Path

from radon.complexity import cc_visit_ast

# Each exception identifies the measured implementation. Changing its syntax
# invalidates the exception, even when the function keeps its original name.
MAX_COMPLEXITY = 10

baseline = json.loads(Path("tools/complexity_baseline.json").read_text())
failures = []
for root in (Path("src"), Path("tools")):
    for path in sorted(root.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            score = cc_visit_ast(node)[0].complexity
            if score <= MAX_COMPLEXITY:
                continue
            digest = hashlib.sha256(ast.dump(node).encode()).hexdigest()
            key = f"{path}:{node.name}"
            if digest != baseline.get(key):
                failures.append(f"{path}:{node.lineno} {node.name} scores {score}")
if failures:
    raise SystemExit("\n".join(failures))
