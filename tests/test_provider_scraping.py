import csv
from pathlib import Path

from bc_npp_database.provider_scraping import (
    build_provider_review,
    scrape_provider_sandbox,
)
from bc_npp_database.providers import validate_provider_sandbox

FIXTURES = Path("tests/fixtures/providers")


def test_scrape_provider_sandbox_generates_valid_fixture_outputs_for_each_provider(tmp_path):
    expected_species = {
        "PROV-SATIN": "Achillea millefolium",
        "PROV-NWM": "Prunella vulgaris var. lanceolata",
        "PROV-WCS": "Camassia quamash",
        "PROV-PREMIER": "Festuca rubra",
    }

    for provider_id, botanical_name in expected_species.items():
        result = scrape_provider_sandbox(
            provider_id,
            "vancouver",
            tmp_path / provider_id,
            input_dir=FIXTURES,
        )

        assert result.diagnostics == ()
        assert result.counts["candidate_species"] >= 1
        rows = _read_csv(tmp_path / provider_id / "candidate_species.csv")
        assert botanical_name in {row["botanical_name"] for row in rows}


def test_wcs_fixture_excludes_vegetable_rows(tmp_path):
    result = scrape_provider_sandbox(
        "PROV-WCS",
        "vancouver",
        tmp_path / "wcs",
        input_dir=FIXTURES,
    )

    assert result.diagnostics == ()
    rows = _read_csv(tmp_path / "wcs" / "candidate_species.csv")
    cabbage = next(row for row in rows if row["botanical_name"] == "Brassica oleracea")
    assert cabbage["vancouver_eligibility_status"] == "excluded"
    assert cabbage["candidate_status"] == "excluded"
    assert validate_provider_sandbox(tmp_path / "wcs").diagnostics == ()


def test_nwm_fixture_defaults_to_northward_review_and_mowability(tmp_path):
    result = scrape_provider_sandbox(
        "PROV-NWM",
        "vancouver",
        tmp_path / "nwm",
        input_dir=FIXTURES,
    )

    assert result.diagnostics == ()
    species = _read_csv(tmp_path / "nwm" / "candidate_species.csv")[0]
    mowability = _read_csv(tmp_path / "nwm" / "mowability.csv")[0]
    assert species["vancouver_eligibility_status"] == "needs_northward_review"
    assert mowability["mowability_score"] == "4"


def test_scrape_provider_sandbox_requires_fixture_or_live_fetch(tmp_path):
    result = scrape_provider_sandbox("PROV-SATIN", "vancouver", tmp_path / "missing")

    assert any(diagnostic.code == "provider_input_required" for diagnostic in result.diagnostics)


def test_build_provider_review_creates_static_html_and_copies_csvs(tmp_path):
    scrape_provider_sandbox(
        "PROV-SATIN",
        "vancouver",
        tmp_path / "sandbox",
        input_dir=FIXTURES,
    )
    result = build_provider_review(tmp_path / "sandbox", tmp_path / "review")

    assert result.diagnostics == ()
    assert (tmp_path / "review" / "index.html").exists()
    assert (tmp_path / "review" / "candidate_species.csv").exists()
    html = (tmp_path / "review" / "index.html").read_text(encoding="utf-8")
    assert "Provider Review Sandbox" in html
    assert "Achillea millefolium" in html


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]
