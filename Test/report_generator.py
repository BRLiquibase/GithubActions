
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_report(results, context_info, template_dir, template_name="report_template.html"):
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tmpl = env.get_template(template_name)

    counts = {"total": len(results), "pass": 0, "fail": 0, "error": 0}
    for r in results:
        counts[r["status"].lower()] += 1

    report = {
        "title": "Checks run",
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
        "counts": counts,
        "context_info": context_info,
        "checks": results,
    }

    html = tmpl.render(report=report)
    return html, report
