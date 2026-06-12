# dscal

A command-line tool that aggregates deadlines from DSC course websites
(like dsc80.com and other dsc-courses.github.io sites). UCSD course
deadlines are scattered across each course's own website -- dscal pulls
them into one place: a weekly "what's due" checkup in your terminal, and
an `.ics` file you can import into Google Calendar.

## Usage

Install it with `uv`:

```
uv add "git+https://github.com/aaronmarasco/dscal.git"
```

Or run it without adding it to a project:

```
uvx --from "git+https://github.com/aaronmarasco/dscal.git" dscal --help
```

Register the course websites you're taking. Vanity domains and
dsc-courses.github.io addresses both work -- these four (Spring 2026)
are all verified live:

```
dscal add "DSC 80" https://dsc80.com
dscal add "DSC 106" https://dsc106.com
dscal add "DSC 10" https://dsc10.com
dscal add "DSC 152" https://dsc152.com
dscal list
```

See what's due in the next 7 days, across all your courses:

```
dscal week
```

This prints a table of upcoming deliverables -- labs, homeworks,
quizzes, projects, and exams -- sorted by date. Use `--days 14` for a
longer horizon, `--all` to include lectures and discussions, and
`--refresh` to bypass the one-hour page cache.

Export every deadline in the quarter to a calendar file:

```
dscal export --out my-quarter.ics
```

Then import the file at calendar.google.com -> Settings -> Import &
export. Event titles are deliberately simple ("DSC 80: LAB 1") and
events get deterministic IDs, so re-importing after a schedule change
updates events instead of duplicating them.

How it works: most DSC course sites use the same Jekyll template
(just-the-class), which dscal parses precisely -- including reading each
site's quarter (e.g. "Spring 2026") off the page to resolve dates like
"Tue Apr 14" that have no year. Only deliverables make the calendar
(LAB, HW, QUIZ, PROJ, FINAL PROJ, EXAM); lectures, discussions, surveys,
and solutions/practice rows are filtered out, and duplicate rows collapse
to one event. Sites not using the template go through a heuristic parser;
sites that can't be parsed are reported, never silently dropped. If you want to try the
tool without live course sites, `dscal add` also accepts a local HTML
file in place of a URL (there's a sample page in `tests/fixtures/`).

## Development

```
uv sync          # install dependencies
uv run pytest    # run tests (offline, against fixture HTML)
uv run mypy src  # type check
uv run ruff check src tests
```
