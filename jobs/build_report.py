"""Build REPORT.md from report/REPORT.template.md and the tables in results/.

Every line of the template of the form

    {{table:<name>}}

is replaced by the content of results/<name>.md. Everything else in the
template (text written by the group) is copied unchanged.

When a table is missing, a placeholder is written and the script exits with
an error (code 1), so an incomplete REPORT.md cannot be submitted by mistake.
Use --allow-missing to build a draft from a partial run (exit code 0).

Usage: python jobs/build_report.py [--allow-missing]
"""

import argparse
import re
import sys

from config import PROJECT_DIR, RESULTS_DIR

TEMPLATE = PROJECT_DIR / "report" / "REPORT.template.md"
OUTPUT = PROJECT_DIR / "REPORT.md"
PLACEHOLDER = re.compile(r"^\{\{table:([\w\-]+)\}\}\s*$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-missing", action="store_true",
                        help="exit with 0 even if some tables are missing (draft)")
    args = parser.parse_args()

    missing = []
    lines = []
    for line in TEMPLATE.read_text(encoding="utf-8").splitlines():
        match = PLACEHOLDER.match(line)
        if not match:
            lines.append(line)
            continue
        table = RESULTS_DIR / f"{match.group(1)}.md"
        if table.exists():
            lines.append(table.read_text(encoding="utf-8").rstrip("\n"))
        else:
            missing.append(match.group(1))
            lines.append(f"*Result `{match.group(1)}` not generated yet.*")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"REPORT.md written ({len(missing)} missing tables)")
    for name in missing:
        print(f"  missing: results/{name}.md", file=sys.stderr)
    if missing and not args.allow_missing:
        print("error: some result tables are missing, run the corresponding steps "
              "(or use --allow-missing for a draft)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
