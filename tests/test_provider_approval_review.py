import csv
from pathlib import Path

from bc_npp_database.provider_approval_review import build_provider_approval_review
from bc_npp_database.provider_approvals import validate_provider_approvals
from bc_npp_database.provider_scraping import scrape_provider_sandbox

FIXTURES = Path("tests/fixtures/providers")
POC_DIR = Path("data/poc/vancouver")


def test_build_provider_approval_review_groups_species_and_validates_draft(tmp_path):
    sandbox = tmp_path / "sandbox"
    scrape_provider_sandbox("PROV-SATIN", "vancouver", sandbox, input_dir=FIXTURES)

    result = build_provider_approval_review(
        sandbox,
        POC_DIR,
        tmp_path / "approval_review",
        reviewer="tester",
    )

    assert result.diagnostics == ()
    assert result.counts["review_items"] == 1
    assert (tmp_path / "approval_review" / "index.html").exists()
    assert (tmp_path / "approval_review" / "approval_manifest_draft.csv").exists()

    items = _read_csv(tmp_path / "approval_review" / "review_items.csv")
    assert items[0]["botanical_name"] == "Achillea millefolium"
    assert items[0]["species_id"] == "BCNPPD-0001"
    assert items[0]["existing_status"] == "existing"
    assert items[0]["default_target_action"] == "update_existing"
    assert items[0]["supplier_count"] == "1"

    manifest = _read_csv(tmp_path / "approval_review" / "approval_manifest_draft.csv")
    assert {row["sandbox_table"] for row in manifest} >= {
        "candidate_species.csv",
        "candidate_attributes.csv",
        "supplier_availability.csv",
    }
    assert all(row["approval_status"] in {"deferred", "needs_taxonomy_review"} for row in manifest)
    assert validate_provider_approvals(
        tmp_path / "approval_review" / "approval_manifest_draft.csv"
    ).diagnostics == ()


def test_build_provider_approval_review_flags_new_taxonomy_candidates(tmp_path):
    sandbox = _write_taxonomy_sandbox(tmp_path)

    result = build_provider_approval_review(sandbox, POC_DIR, tmp_path / "approval_review")

    assert result.diagnostics == ()
    items = _read_csv(tmp_path / "approval_review" / "review_items.csv")
    assert items[0]["botanical_name"] == "Prunella vulgaris ssp lanceolata"
    assert items[0]["species_id"] == ""
    assert items[0]["existing_status"] == "new"
    assert items[0]["default_target_action"] == "add_species"
    assert items[0]["taxonomy_flag"] == "yes"
    assert items[0]["default_approval_status"] == "needs_taxonomy_review"

    html = (tmp_path / "approval_review" / "index.html").read_text(encoding="utf-8")
    assert "Provider Approval Review" in html
    assert "Download approval_manifest.csv" in html
    assert "needs_taxonomy_review" in html
    assert "Provider source" in html


def _write_taxonomy_sandbox(tmp_path: Path) -> Path:
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    source_url = "https://satinflower.ca/products/prunella-vulgaris-ssp-lanceolata"
    _write_csv(
        sandbox / "inventory_pages.csv",
        [
            {
                "provider_id": "PROV-SATIN",
                "page_url": source_url,
                "page_type": "fixture",
                "fetch_status": "fixture",
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(
        sandbox / "candidate_species.csv",
        [
            {
                "provider_id": "PROV-SATIN",
                "botanical_name": "Prunella vulgaris ssp lanceolata",
                "common_name": "Self-heal",
                "candidate_status": "candidate",
                "vancouver_eligibility_status": "candidate",
                "source_url": source_url,
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(
        sandbox / "candidate_attributes.csv",
        [
            {
                "provider_id": "PROV-SATIN",
                "botanical_name": "Prunella vulgaris ssp lanceolata",
                "attribute_name": "tags",
                "attribute_value": "native, seed",
                "evidence_confidence": "Pending review",
                "source_url": source_url,
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(
        sandbox / "supplier_availability.csv",
        [
            {
                "provider_id": "PROV-SATIN",
                "botanical_name": "Prunella vulgaris ssp lanceolata",
                "supplier_status": "available",
                "product_url": source_url,
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(sandbox / "mowability.csv", [])
    _write_csv(
        sandbox / "diagnostics.csv",
        [{"severity": "info", "code": "fixture", "message": "Synthetic fixture."}],
    )
    (sandbox / "manifest.json").write_text(
        '{"database_instance":"vancouver","provider_ids":["PROV-SATIN"],'
        '"public_hygiene":{"raw_provider_html_tracked":false}}\n',
        encoding="utf-8",
    )
    return sandbox


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if rows:
        fieldnames = list(rows[0])
    else:
        fieldnames = [
            "provider_id",
            "botanical_name",
            "mowability_score",
            "source_url",
            "review_status",
        ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
