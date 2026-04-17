from __future__ import annotations

import argparse
import calendar
import datetime as dt
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
HOME_PAGE = DOCS_DIR / "index.md"
NEXT_PAGE = DOCS_DIR / "next.md"
HISTORY_DIR = DOCS_DIR / "History"
HISTORY_INDEX = HISTORY_DIR / "index.md"
DATE_HEADER_RE = re.compile(r"^# .*Date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
CHECKBOX_RE = re.compile(r"^([ \t]*- \[)(?:x|X)(\])", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PlanStack automation utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_template = subparsers.add_parser("new-template", help="Create a new daily template")
    new_template.add_argument("--date", required=True, help="Target date in YYYY-MM-DD format")
    new_template.add_argument("--output", required=True, help="Output markdown file path")

    derive_template = subparsers.add_parser(
        "derive-template",
        help="Create the next daily template by copying the current home page",
    )
    derive_template.add_argument("--date", required=True, help="Target date in YYYY-MM-DD format")
    derive_template.add_argument("--output", required=True, help="Output markdown file path")

    publish = subparsers.add_parser("publish-next", help="Publish the next plan to the preview page")
    publish.add_argument("--next-plan", required=True, help="Markdown file for the next day")

    rollover = subparsers.add_parser("rollover", help="Archive current plan and activate the published next plan")
    rollover.add_argument("--force", action="store_true", help="Overwrite existing history file if content differs")

    rebuild = subparsers.add_parser("rebuild-history", help="Rebuild History/index.md from archived files")

    sync_dates = subparsers.add_parser(
        "sync-dates",
        help="Sync docs/index.md to today and docs/next.md to tomorrow",
    )
    sync_dates.add_argument(
        "--base-date",
        default=dt.date.today().isoformat(),
        help="Base date in YYYY-MM-DD format; home becomes this date and next becomes base date + 1 day",
    )
    return parser.parse_args()


def parse_iso_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid date '{value}', expected YYYY-MM-DD") from exc


def extract_plan_date(content: str) -> dt.date:
    match = DATE_HEADER_RE.search(content)
    if not match:
        raise SystemExit("Could not find a '# Date: YYYY-MM-DD' header in the plan markdown")
    return parse_iso_date(match.group(1))


def replace_plan_date(content: str, target_date: dt.date) -> str:
    if not DATE_HEADER_RE.search(content):
        raise SystemExit("Could not find a '# Date: YYYY-MM-DD' header in the plan markdown")
    return DATE_HEADER_RE.sub(f"# 📅 Date: {target_date.isoformat()}", content, count=1)


def reset_review_sections(content: str) -> str:
    for section_name in ("Finished", "Feeling", "Tomorrow"):
        pattern = re.compile(rf"(^## {section_name}\s*$)(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
        content = pattern.sub(r"\1\n", content, count=1)
    return content


def reset_checkboxes(content: str) -> str:
    return CHECKBOX_RE.sub(r"\1 \2", content)


def derive_template_from_home(target_date: dt.date) -> str:
    home_content = read_text(HOME_PAGE)
    derived_content = replace_plan_date(home_content, target_date)
    derived_content = reset_checkboxes(derived_content)
    derived_content = reset_review_sections(derived_content)
    return derived_content


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def ensure_layout() -> None:
    if not HOME_PAGE.exists():
        raise SystemExit(f"Homepage not found: {HOME_PAGE}")
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    if not NEXT_PAGE.exists():
        write_text(NEXT_PAGE, render_next_placeholder())


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


def render_next_placeholder() -> str:
    return """# Next Plan

还没有发布下一天的计划。

运行发布脚本后，这里会显示下一天的计划预览。
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


def render_history_index(dates: list[dt.date]) -> str:
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

    return "\n".join(lines).rstrip() + "\n"


def rebuild_history_index() -> None:
    dates = list_history_dates()
    write_text(HISTORY_INDEX, render_history_index(dates))


def load_published_next_plan() -> str:
    next_content = read_text(NEXT_PAGE)
    if "# 📅 Date:" not in next_content:
        raise SystemExit("No published next plan found in docs/next.md")
    return next_content


def archive_current_plan(force: bool) -> dt.date:
    current_content = read_text(HOME_PAGE)
    current_date = extract_plan_date(current_content)
    archive_path = HISTORY_DIR / f"{current_date.isoformat()}.md"

    if archive_path.exists():
        existing = read_text(archive_path)
        if existing != current_content:
            if not force:
                raise SystemExit(
                    f"History file already exists with different content: {archive_path}. Use --force to overwrite."
                )
            write_text(archive_path, current_content)
    else:
        write_text(archive_path, current_content)

    return current_date


def command_new_template(target_date: str, output: str) -> None:
    date_value = parse_iso_date(target_date)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_text(output_path, render_template(date_value))


def command_derive_template(target_date: str, output: str) -> None:
    ensure_layout()
    date_value = parse_iso_date(target_date)
    current_date = extract_plan_date(read_text(HOME_PAGE))
    if date_value <= current_date:
        raise SystemExit(
            f"Derived plan date {date_value.isoformat()} must be after current home page date {current_date.isoformat()}"
        )

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_text(output_path, derive_template_from_home(date_value))


def command_publish_next(next_plan: str) -> None:
    ensure_layout()
    next_plan_path = Path(next_plan)
    if not next_plan_path.exists():
        raise SystemExit(f"Next plan file not found: {next_plan_path}")

    next_content = read_text(next_plan_path)
    next_date = extract_plan_date(next_content)
    current_date = extract_plan_date(read_text(HOME_PAGE))

    if next_date <= current_date:
        raise SystemExit(
            f"Next plan date {next_date.isoformat()} must be after current home page date {current_date.isoformat()}"
        )

    write_text(NEXT_PAGE, next_content)


def command_rollover(force: bool) -> None:
    ensure_layout()
    next_content = load_published_next_plan()
    next_date = extract_plan_date(next_content)
    current_date = extract_plan_date(read_text(HOME_PAGE))

    if next_date <= current_date:
        raise SystemExit(
            f"Published next plan date {next_date.isoformat()} must be after current home page date {current_date.isoformat()}"
        )

    archive_current_plan(force=force)
    write_text(HOME_PAGE, next_content)
    write_text(NEXT_PAGE, render_next_placeholder())
    rebuild_history_index()


def command_sync_dates(base_date: str) -> None:
    ensure_layout()
    current_date = parse_iso_date(base_date)
    next_date = current_date + dt.timedelta(days=1)

    home_content = read_text(HOME_PAGE)
    write_text(HOME_PAGE, replace_plan_date(home_content, current_date))

    next_content = read_text(NEXT_PAGE)
    if "# 📅 Date:" in next_content:
        write_text(NEXT_PAGE, replace_plan_date(next_content, next_date))
    else:
        write_text(NEXT_PAGE, render_template(next_date))


def main() -> None:
    args = parse_args()
    if args.command == "new-template":
        command_new_template(args.date, args.output)
        return
    if args.command == "derive-template":
        command_derive_template(args.date, args.output)
        return
    if args.command == "publish-next":
        command_publish_next(args.next_plan)
        return
    if args.command == "rollover":
        command_rollover(args.force)
        return
    if args.command == "rebuild-history":
        ensure_layout()
        rebuild_history_index()
        return
    if args.command == "sync-dates":
        command_sync_dates(args.base_date)
        return
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()