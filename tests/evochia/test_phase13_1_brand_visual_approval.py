from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
BRAND = ROOT / "company/evochia/brand"
REGISTRY = ROOT / "references/source_registry.yaml"
CURRENT_STATE = ROOT / "docs/architecture/current-state.md"

APPROVAL_REF = "owner-approval-2026-09-03-phase13.1"


def read(path: Path) -> str:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def test_visual_tokens_are_owner_approved_with_metadata_and_exact_typography():
    data = yaml.safe_load(read(BRAND / "visual_tokens.yaml"))
    assert data["status"] == "APPROVED"
    assert data["approval"]["approved_by"] == "Evochia Owner"
    assert data["approval"]["effective_date"] == "2026-09-03"
    assert data["approval"]["approval_reference"] == APPROVAL_REF
    typo = data["typography"]
    assert typo["digital_site"] == {
        "brand_heading": "Alexander",
        "body": "Bainsley",
        "accent": "Miama",
        "page_hero_fallback": "Georgia",
    }
    assert typo["portable_documents"]["display"] == "Cormorant Garamond"
    assert typo["portable_documents"]["body"] == "EB Garamond"
    assert typo["logo_family_reference"] == "Weiss Font"


def test_visual_identity_and_document_style_are_approved_not_draft():
    for name in ["visual_identity.md", "document_style_guide.md"]:
        text = read(BRAND / name)
        assert "**Status:** `APPROVED`" in text
        assert "**Approved by:** Evochia Owner" in text
        assert "**Effective date:** 2026-09-03" in text
        assert f"**Approval reference:** `{APPROVAL_REF}`" in text
        assert "**Status:** `OWNER_REVIEW_DRAFT`" not in text


def test_render_integrity_remains_fail_closed_after_owner_lock():
    data = yaml.safe_load(read(BRAND / "assets/render_integrity.yaml"))
    assert data["resolution_policy"] == "fail_closed"
    assert data["final_artifact_requires_verified_assets"] is True
    assert data["render_gate"]["missing_logo"] == "fail"
    assert data["render_gate"]["missing_required_font"] == "fail"
    assert data["render_gate"]["silent_font_substitution"] == "forbidden"
    assert data["render_gate"]["pdf_font_embedding_required"] is True
    assert data["logo"]["active_default"]["assets"]["ui_raster_mark_1x"]["git_blob_sha"] == "11676370669ef00c1ed6815300db240c5ce376f8"


def test_source_registry_contains_canonical_owner_approved_visual_system():
    data = yaml.safe_load(read(REGISTRY))
    source = next(item for item in data["sources"] if item["source_id"] == "evochia_visual_system_v1")
    assert source["source_class"] == "canonical_policy"
    assert source["authority"] == "canonical"
    assert source["path_or_external_ref"] == "company/evochia/brand/visual_tokens.yaml"
    assert source["effective_date"] == "2026-09-03"
    assert source["last_reviewed_at"] == "2026-09-03"
    assert source["owner"] == "Evochia"
    assert "typography" in source["scope"] and "document_visual_system" in source["scope"]


def test_current_state_records_visual_system_as_canonical_but_brand_voice_separately_reviewable():
    text = read(CURRENT_STATE)
    assert "Phase 13.1 visual/typography owner lock: `APPROVED`" in text
    assert "evochia_visual_system_v1" in text
    assert "brand voice remains a separate authority/review decision" in text.lower()
