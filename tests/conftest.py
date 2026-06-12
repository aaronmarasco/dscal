from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def dsc80_html() -> str:
    return (FIXTURES / "dsc80_home.html").read_text(encoding="utf-8")
