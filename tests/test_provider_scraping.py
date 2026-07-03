import csv
import json
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


def test_scrape_provider_sandbox_parses_shopify_product_json_fixture(tmp_path):
    fixture_dir = tmp_path / "fixtures" / "PROV-SATIN"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "products.json").write_text(
        json.dumps(
            {
                "products": [
                    {
                        "title": "Achillea millefolium (Yarrow)",
                        "handle": "achillea-millefolium",
                        "body_html": (
                            "<p>Useful full-sun meadow species.</p>"
                            "<button>Plant Details</button>"
                            "<table><tr><th>habitat</th><td>Meadow</td></tr>"
                            "<tr><th>light</th><td>Full sun</td></tr></table>"
                            "<button>Seed Details</button>"
                            "<table><tr><th>seeds/ packet</th><td>184</td></tr>"
                            "<tr><th>sowing time</th><td>Sow in fall</td></tr></table>"
                        ),
                        "product_type": "Seed Packet",
                        "tags": ["native", "pollinator"],
                        "variants": [{"available": True}],
                    },
                    {
                        "title": "Gift Card",
                        "handle": "gift-card",
                        "product_type": "Gift Card",
                        "tags": [],
                        "variants": [{"available": True}],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = scrape_provider_sandbox(
        "PROV-SATIN",
        "vancouver",
        tmp_path / "sandbox",
        input_dir=tmp_path / "fixtures",
    )

    assert result.diagnostics == ()
    rows = _read_csv(tmp_path / "sandbox" / "candidate_species.csv")
    assert [row["botanical_name"] for row in rows] == ["Achillea millefolium"]
    assert rows[0]["source_url"] == "https://satinflower.ca/products/achillea-millefolium"
    attributes = _read_csv(tmp_path / "sandbox" / "candidate_attributes.csv")
    values = {row["attribute_name"]: row["attribute_value"] for row in attributes}
    assert set(values) >= {
        "product title",
        "tags",
        "description",
        "plant details habitat",
        "plant details light",
        "seed details seeds packet",
        "seed details sowing time",
    }
    assert values["description"] == "Useful full-sun meadow species."
    assert values["plant details habitat"] == "Meadow"
    assert values["seed details seeds packet"] == "184"
    supplier = _read_csv(tmp_path / "sandbox" / "supplier_availability.csv")
    assert supplier[0]["supplier_status"] == "available"


def test_nwm_shopify_titles_use_botanical_parentheses_and_skip_non_species(tmp_path):
    fixture_dir = tmp_path / "fixtures" / "PROV-NWM"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "products.json").write_text(
        json.dumps(
            {
                "products": [
                    {
                        "title": "Western Yarrow Seeds (Achillea millefolium)",
                        "handle": "western-yarrow-achillea-millefolium",
                        "body_html": "<p>Mowable eco-lawn component.</p>",
                        "product_type": "",
                        "tags": [],
                        "variants": [{"available": True}],
                    },
                    {
                        "title": "Roemer's Fescue Seeds (Festuca idahoensis ssp. romeri)",
                        "handle": "roemers-fescue-seed",
                        "body_html": "<p>Low native bunchgrass.</p>",
                        "product_type": "",
                        "tags": [],
                        "variants": [{"available": True}],
                    },
                    {
                        "title": (
                            "Common Camas Bulbs Pre Order for Nov 2026 Shipping "
                            "(Camassia quamash)"
                        ),
                        "handle": "common-camas-bulbs-camassia-quamash",
                        "body_html": "<p>Bulb product.</p>",
                        "product_type": "",
                        "tags": [],
                        "variants": [{"available": True}],
                    },
                    {
                        "title": "Cocozella di Napoli Seeds",
                        "handle": "cocozella-di-napoli-seeds",
                        "body_html": "<p>Vegetable squash.</p>",
                        "product_type": "",
                        "tags": [],
                        "variants": [{"available": True}],
                    },
                    {
                        "title": (
                            "Farming with Native Beneficial Insects "
                            "(A Xerces Society Guide Book)"
                        ),
                        "handle": (
                            "farming-with-native-beneficial-insects-a-xerces-society-guide-book"
                        ),
                        "body_html": "<p>Book.</p>",
                        "product_type": "",
                        "tags": [],
                        "variants": [{"available": True}],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = scrape_provider_sandbox(
        "PROV-NWM",
        "vancouver",
        tmp_path / "sandbox",
        input_dir=tmp_path / "fixtures",
    )

    assert result.diagnostics == ()
    species = _read_csv(tmp_path / "sandbox" / "candidate_species.csv")
    names = {row["botanical_name"]: row for row in species}
    assert set(names) == {
        "Achillea millefolium",
        "Camassia quamash",
        "Festuca idahoensis ssp romeri",
    }
    assert names["Achillea millefolium"]["common_name"] == "Western Yarrow"
    assert names["Camassia quamash"]["common_name"] == "Common Camas"
    assert names["Festuca idahoensis ssp romeri"]["common_name"] == "Roemer's Fescue"
    assert all(row["vancouver_eligibility_status"] == "needs_northward_review" for row in species)


def test_wcs_shopify_body_extracts_single_species_and_blend_components(tmp_path):
    fixture_dir = tmp_path / "fixtures" / "PROV-WCS"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "products.json").write_text(
        json.dumps(
            {
                "products": [
                    {
                        "title": "Common Woolly Sunflower",
                        "handle": "common-woolly-sunflower",
                        "body_html": (
                            "<p>Eriophyllum lanatum. Height to 30-60cm. "
                            "Blooms May to August.</p>"
                        ),
                        "product_type": "Flower Seeds",
                        "tags": ["wildflower"],
                        "variants": [{"available": True}],
                    },
                    {
                        "title": "Cut Flower Blend",
                        "handle": "cut-flower-blend",
                        "body_html": (
                            "<p>Blend Ingredients. [Blanketflower "
                            "(Gaillardia aristata), Clarkia "
                            "(Clarkia unguiculata)]</p>"
                        ),
                        "product_type": "Flower Seeds",
                        "tags": ["wildflower"],
                        "variants": [{"available": True}],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = scrape_provider_sandbox(
        "PROV-WCS",
        "vancouver",
        tmp_path / "sandbox",
        input_dir=tmp_path / "fixtures",
    )

    assert result.diagnostics == ()
    species = _read_csv(tmp_path / "sandbox" / "candidate_species.csv")
    names = {row["botanical_name"]: row for row in species}
    assert set(names) == {
        "Clarkia unguiculata",
        "Eriophyllum lanatum",
        "Gaillardia aristata",
    }
    assert names["Eriophyllum lanatum"]["common_name"] == "Common Woolly Sunflower"
    assert all(row["vancouver_eligibility_status"] == "needs_review" for row in species)

    suppliers = _read_csv(tmp_path / "sandbox" / "supplier_availability.csv")
    supplier_statuses = {
        row["botanical_name"]: row["supplier_status"] for row in suppliers
    }
    assert supplier_statuses["Eriophyllum lanatum"] == "available"
    assert supplier_statuses["Gaillardia aristata"] == "mix_component"
    assert supplier_statuses["Clarkia unguiculata"] == "mix_component"

    attributes = _read_csv(tmp_path / "sandbox" / "candidate_attributes.csv")
    observation_types = {
        (row["botanical_name"], row["attribute_value"])
        for row in attributes
        if row["attribute_name"] == "provider observation type"
    }
    assert ("Eriophyllum lanatum", "product_body") in observation_types
    assert ("Gaillardia aristata", "blend_ingredient") in observation_types


def test_provider_sandbox_deduplicates_species_but_keeps_supplier_rows(tmp_path):
    fixture_dir = tmp_path / "fixtures" / "PROV-NWM"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "products.json").write_text(
        json.dumps(
            {
                "products": [
                    {
                        "title": "Common Camas Seeds (Camassia quamash)",
                        "handle": "common-camas-seeds",
                        "body_html": "<p>Packet.</p>",
                        "product_type": "",
                        "tags": [],
                        "variants": [{"available": True}],
                    },
                    {
                        "title": "Common Camas Bulbs (Camassia quamash)",
                        "handle": "common-camas-bulbs",
                        "body_html": "<p>Bulbs.</p>",
                        "product_type": "",
                        "tags": [],
                        "variants": [{"available": False}],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = scrape_provider_sandbox(
        "PROV-NWM",
        "vancouver",
        tmp_path / "sandbox",
        input_dir=tmp_path / "fixtures",
    )

    assert result.diagnostics == ()
    species = _read_csv(tmp_path / "sandbox" / "candidate_species.csv")
    suppliers = _read_csv(tmp_path / "sandbox" / "supplier_availability.csv")
    assert [row["botanical_name"] for row in species] == ["Camassia quamash"]
    assert [row["supplier_status"] for row in suppliers] == ["available", "unavailable"]


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
