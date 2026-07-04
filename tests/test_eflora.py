import csv
from pathlib import Path

from bc_npp_database.eflora import (
    apply_eflora_boost,
    build_eflora_boost,
    eflora_atlas_url,
    eflora_external_id,
    has_error_diagnostics,
    normalize_botanical_name,
    parse_eflora_atlas_page,
    resolve_eflora_species,
    validate_eflora_boost,
)

FIXTURES = Path("tests/fixtures/eflora")


def test_eflora_url_and_external_id_are_deterministic():
    assert normalize_botanical_name("achillea  millefolium") == "Achillea millefolium"
    assert eflora_atlas_url("Achillea millefolium").endswith(
        "Atlas.aspx?sciname=Achillea+millefolium"
    )
    assert eflora_external_id("Achillea millefolium") == "eflora:atlas:achillea_millefolium"


def test_resolve_eflora_species_from_fixture():
    result = resolve_eflora_species("Achillea millefolium", input_dir=FIXTURES)

    assert result.match_status == "exact"
    assert not has_error_diagnostics(result.diagnostics)
    assert "Achillea millefolium" in result.source_text


def test_parse_eflora_atlas_fixture_extracts_boost_values():
    page = (FIXTURES / "achillea_millefolium.html").read_text(encoding="utf-8")
    parsed = parse_eflora_atlas_page(
        page,
        input_name="Achillea millefolium",
        species_id="BCNPPD-9991",
        atlas_url=eflora_atlas_url("Achillea millefolium"),
        access_date="2026-07-03",
    )

    values = {
        row["attribute_name"]: row["attribute_value"] for row in parsed["attributes"]
    }
    assert values["family"] == "Asteraceae"
    assert values["origin_status"] == "Native"
    assert values["bc_list_status"] == "Yellow"
    assert values["modal_bec_zone_class"] == "IDF"
    assert values["soil_moisture_regime_min_avg_max"] == "3 / 4 / 8"
    assert values["blooming_period"] == "Early Summer"
    assert {row["synonym"] for row in parsed["synonyms"]} == {
        "Achillea borealis",
        "Achillea magna",
    }
    assert parsed["attributions"][0]["source_id"] == "SRC-9001"


def test_build_and_validate_eflora_boost_from_fixtures(tmp_path):
    out_dir = tmp_path / "boost"
    result = build_eflora_boost(
        FIXTURES / "species.csv",
        out_dir,
        input_dir=FIXTURES,
        access_date="2026-07-03",
    )

    assert result.counts["resolved_species"] == 1
    assert result.counts["candidate_attributes"] >= 6
    assert not has_error_diagnostics(result.diagnostics)
    validation = validate_eflora_boost(out_dir)
    assert not has_error_diagnostics(validation.diagnostics)
    rows = _read_csv(out_dir / "candidate_attributes.csv")
    assert {row["attribute_name"] for row in rows} >= {"family", "origin_status"}


def test_missing_eflora_fixture_emits_error_without_candidate_facts(tmp_path):
    species_csv = tmp_path / "species.csv"
    _write_csv(
        species_csv,
        [{"Species ID": "BCNPPD-9992", "Botanical Name": "Unknown missing"}],
    )

    result = build_eflora_boost(
        species_csv,
        tmp_path / "boost",
        input_dir=FIXTURES,
        access_date="2026-07-03",
    )

    assert has_error_diagnostics(result.diagnostics)
    assert result.counts["resolved_species"] == 0
    assert any(diagnostic.code == "eflora_fixture_missing" for diagnostic in result.diagnostics)


def test_apply_eflora_boost_fills_missing_values_only(tmp_path):
    poc_dir = tmp_path / "poc"
    poc_dir.mkdir()
    _write_csv(
        poc_dir / "plant_list.csv",
        [
            {
                "Species ID": "BCNPPD-9991",
                "Botanical Name": "Achillea millefolium",
                "Common Name": "",
                "Family": "",
                "Native Status": "Already reviewed",
                "Soil Moisture": "Unknown",
                "evidence_status": "reviewed",
            }
        ],
    )
    for filename in ("sources.csv", "source_attribution.csv"):
        _write_csv(poc_dir / filename, [])

    boost_dir = tmp_path / "boost"
    build_eflora_boost(
        FIXTURES / "species.csv",
        boost_dir,
        input_dir=FIXTURES,
        access_date="2026-07-03",
    )
    result = apply_eflora_boost(boost_dir, poc_dir, tmp_path / "preview")

    assert not has_error_diagnostics(result.diagnostics)
    plant = _read_csv(tmp_path / "preview" / "plant_list.csv")[0]
    assert plant["Family"] == "Asteraceae"
    assert plant["Common Name"] == "common yarrow"
    assert plant["Native Status"] == "Already reviewed"
    assert plant["Soil Moisture"] == "3 / 4 / 8"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = list(rows[0]) if rows else ["placeholder"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
