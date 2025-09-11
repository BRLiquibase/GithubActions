
import argparse
import json
import sys
import ast
from pathlib import Path
import yaml
from report_generator import render_report

_ALLOWED_FUNCS = {
    "len": len,
    "all": all,
    "any": any,
    "sum": sum,
    "min": min,
    "max": max,
    "sorted": sorted,
    "set": set,
    "abs": abs,
    "round": round,
}

_ALLOWED_NODES = (
    ast.Expression, ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.IfExp,
    ast.Compare, ast.Call, ast.Num, ast.Str, ast.Bytes, ast.NameConstant,
    ast.Constant, ast.Attribute, ast.Subscript, ast.Name, ast.Load,
    ast.List, ast.Tuple, ast.Dict, ast.Set, ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp,
    ast.And, ast.Or, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.Is, ast.IsNot,
    ast.USub, ast.UAdd, ast.Not
)

def _safe_eval(expr, ctx):
    """Safely evaluate a limited Python expression string against context 'ctx'."""
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Syntax error: {e}")
    for subnode in ast.walk(node):
        if not isinstance(subnode, _ALLOWED_NODES):
            raise ValueError(f"Disallowed expression element: {type(subnode).__name__}")
        if isinstance(subnode, ast.Call):
            if isinstance(subnode.func, ast.Name):
                if subnode.func.id not in _ALLOWED_FUNCS:
                    raise ValueError(f"Call to disallowed function '{subnode.func.id}'")
            elif isinstance(subnode.func, ast.Attribute):
                raise ValueError("Attribute calls are not allowed; use allowed helpers or inline expressions.")
    compiled = compile(node, "<expr>", "eval")
    return eval(compiled, {"__builtins__": {}}, {"ctx": ctx, **_ALLOWED_FUNCS})

def load_policies(path: Path):
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, list):
        raise ValueError("policies.yaml must be a list of checks.")
    checks = []
    for i, c in enumerate(data):
        cid = c.get("id") or f"check_{i+1}"
        checks.append({
            "id": cid,
            "title": c.get("title", cid),
            "description": c.get("description", ""),
            "severity": (c.get("severity") or "medium").lower(),
            "condition": c.get("condition"),
            "details_expr": c.get("details"),
        })
    return checks

def evaluate_checks(checks, ctx):
    results = []
    for c in checks:
        status = "ERROR"
        eval_value = None
        err = None
        details_val = None
        try:
            cond_expr = c["condition"]
            if not cond_expr:
                raise ValueError("Missing 'condition'")
            val = _safe_eval(cond_expr, ctx)
            if not isinstance(val, (bool, int)):
                raise ValueError("Condition did not resolve to a boolean/int")
            status = "PASS" if bool(val) else "FAIL"
            eval_value = str(val)
            if c["details_expr"]:
                details_val = _safe_eval(c["details_expr"], ctx)
        except Exception as e:
            err = str(e)
            status = "ERROR"
        results.append({
            "id": c["id"],
            "title": c["title"],
            "description": c["description"],
            "severity": c["severity"],
            "condition": c["condition"],
            "eval": eval_value,
            "status": status,
            "error": err,
            "details": details_val,
        })
    status_weight = {"FAIL": 0, "ERROR": 1, "PASS": 2}
    sev_weight = {"high": 0, "medium": 1, "low": 2}
    results.sort(key=lambda r: (status_weight.get(r["status"], 99), sev_weight.get(r["severity"], 99), r["id"]))
    return results

def main():
    p = argparse.ArgumentParser(description="Evaluate policies and produce an HTML report.")
    p.add_argument("--policies", required=True, help="Path to policies YAML")
    p.add_argument("--context", required=True, help="Path to context JSON")
    p.add_argument("--out", default="report.html", help="Output HTML file (default: report.html)")
    args = p.parse_args()

    policies_path = Path(args.policies)
    context_path = Path(args.context)
    out_path = Path(args.out)

    if not policies_path.exists():
        print(f"Policies file not found: {policies_path}", file=sys.stderr)
        sys.exit(2)
    if not context_path.exists():
        print(f"Context file not found: {context_path}", file=sys.stderr)
        sys.exit(2)

    checks = load_policies(policies_path)
    ctx = json.loads(context_path.read_text())

    if isinstance(ctx, dict):
        keys = ', '.join(sorted(ctx.keys()))
        ctx_info = f"{context_path.name} (keys: {keys})"
    else:
        ctx_info = type(ctx).__name__

    results = evaluate_checks(checks, ctx)
    html, report_obj = render_report(results, ctx_info, template_dir=str(policies_path.parent))

    out_path.write_text(html, encoding="utf-8")
    out_json = out_path.with_suffix(".json")
    out_json.write_text(json.dumps(report_obj, indent=2), encoding="utf-8")

    print(f"Wrote {out_path}")
    print(f"Wrote {out_json}")

if __name__ == "__main__":
    main()
