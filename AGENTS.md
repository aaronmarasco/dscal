# dscal

A Python CLI that aggregates deadlines from DSC course websites
(dsc-courses.github.io and friends). Two main commands:

- `dscal week`: print what's due in the next 7 days, per course.
- `dscal export`: write an .ics file importable into Google Calendar.

## Development

- Managed with uv. Install deps: `uv sync`
- Run tests: `uv run pytest`
- Type check: `uv run mypy src`
- Lint/format: `uv run ruff check src tests` and `uv run ruff format src tests`

## Architecture

- `models.py`: Event dataclass (course, title, kind, date, url). Pure data.
- `dates.py`: quarter/year inference ("Spring 2026" -> month range), date resolution.
- `parser.py`: HTML -> list[Event]. Template parser for Just-the-Docs course
  sites + heuristic fallback. Pure functions: take HTML strings, no network.
- `ics.py`: list[Event] -> ICS text. No dependencies, written by hand.
- `fetch.py`: thin network layer with on-disk cache. The ONLY module that
  does network I/O.
- `config.py`: read/write course list at ~/.config/dscal/courses.toml.
- `cli.py`: argparse subcommands wiring it together.

## Rules

- Parsing functions must be pure (no network) so tests run offline against
  fixtures in tests/fixtures/.
- All functions have type hints; mypy must pass.
- Tests are written BEFORE implementations (see tests/).
