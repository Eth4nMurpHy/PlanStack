from __future__ import annotations

import argparse
import calendar
import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
HOME_PAGE = DOCS_DIR / "index.md"
HISTORY_DIR = DOCS_DIR / "History"
HISTORY_INDEX = HISTORY_DIR / "index.md"
DATE_HEADER_RE = re.compile(r"^# .*Date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
CHECKBOX_RE = re.compile(r"^([ \t]*- \[)(?:x|X)(\])", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manually archive docs/index.md and advance the home page date"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing history file if content differs",
    )
    parser.add_argument(
        "--blank-template",
        action="store_true",
        help="Use a blank template for next day instead of deriving from current home page",
    )
    return parser.parse_args()


def parse_iso_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid date '{value}', expected YYYY-MM-DD") from exc


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def extract_plan_date(content: str) -> dt.date:
    match = DATE_HEADER_RE.search(content)
    if not match:
        raise SystemExit("Could not find a '# Date: YYYY-MM-DD' header in docs/index.md")
    return parse_iso_date(match.group(1))


def replace_plan_date(content: str, target_date: dt.date) -> str:
    if not DATE_HEADER_RE.search(content):
        raise SystemExit("Could not find a '# Date: YYYY-MM-DD' header in docs/index.md")
    return DATE_HEADER_RE.sub(f"# 📅 Date: {target_date.isoformat()}", content, count=1)


def reset_checkboxes(content: str) -> str:
    return CHECKBOX_RE.sub(r"\1 \2", content)


def reset_review_sections(content: str) -> str:
    for section_name in ("Finished", "Feeling", "Tomorrow"):
        pattern = re.compile(rf"(^## {section_name}\s*$)(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
        content = pattern.sub(r"\1\n", content, count=1)
    return content


def render_template(target_date: dt.date) -> str:
    return f"""# 📅 Date: {target_date.isoformat()}
# 待处理
## Q1 - 重要 & 紧急
- [ ]
- [ ]
- [ ]

## Q2 - 重要 & 不急
- [ ]
- [ ]
- [ ]

## Q3 - 不重要 & 不急
- [ ]
- [ ]
- [ ]

## Q4 - 不重要 & 紧急 (容易忘记&错过的事件)
- [ ]
- [ ]
- [ ]

## Q5 - 慢性压力源
- [ ]
- [ ]
---

# ⏰ Time Blocking

| Time        | Task |
| ----------- | ---- |
| 06:00-07:00 |      |
| 07:00-08:00 |      |
| 08:00-09:00 |      |
| 09:00-10:00 |      |
| 10:00-11:00 |      |
| 11:00-12:00 |      |
| 12:00-13:00 |      |
| 13:00-14:00 |      |
| 14:00-15:00 |      |
| 15:00-16:00 |      |
| 16:00-17:00 |      |
| 17:00-18:00 |      |
| 18:00-19:00 |      |
| 19:00-20:00 |      |
| 20:00-21:00 |      |
| 21:00-22:00 |      |
| 22:00-23:00 |      |
---

# 📊 Review

## Finished

## Feeling

## Tomorrow
"""


def list_history_dates() -> list[dt.date]:
    dates: list[dt.date] = []
    for path in HISTORY_DIR.glob("*.md"):
        if path.name == "index.md":
            continue
        try:
            dates.append(parse_iso_date(path.stem))
        except SystemExit:
            continue
    return sorted(dates)


def rebuild_history_index() -> None:
    dates = list_history_dates()
    lines = ["# 📅 Plans Index", ""]
    grouped: dict[tuple[int, int], list[dt.date]] = {}
    for item in dates:
        grouped.setdefault((item.year, item.month), []).append(item)

    for year, month in sorted(grouped):
        month_name = calendar.month_name[month]
        lines.append(f"## {month_name} {year}")
        lines.append("")
        for item in grouped[(year, month)]:
            lines.append(f"- [{item.isoformat()}]({item.isoformat()}.md)")
        lines.append("")

    write_text(HISTORY_INDEX, "\n".join(lines).rstrip() + "\n")


def ensure_layout() -> None:
    if not HOME_PAGE.exists():
        raise SystemExit(f"Homepage not found: {HOME_PAGE}")
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def archive_current_plan(content: str, force: bool) -> tuple[dt.date, Path]:
    current_date = extract_plan_date(content)
    archive_path = HISTORY_DIR / f"{current_date.isoformat()}.md"

    if archive_path.exists():
        existing = read_text(archive_path)
        if existing != content:
            if not force:
                raise SystemExit(
                    f"History file already exists with different content: {archive_path}. Use --force to overwrite."
                )
            write_text(archive_path, content)
    else:
        write_text(archive_path, content)

    return current_date, archive_path


def main() -> None:
    args = parse_args()
    ensure_layout()

    current_content = read_text(HOME_PAGE)
    current_date, archive_path = archive_current_plan(current_content, force=args.force)
    next_date = current_date + dt.timedelta(days=1)

    if args.blank_template:
        next_home = render_template(next_date)
    else:
        next_home = replace_plan_date(current_content, next_date)
        next_home = reset_checkboxes(next_home)
        next_home = reset_review_sections(next_home)

    write_text(HOME_PAGE, next_home)
    rebuild_history_index()

    print(f"Archived: {archive_path}")
    print(f"Home page advanced to: {next_date.isoformat()}")


if __name__ == "__main__":
    main()
