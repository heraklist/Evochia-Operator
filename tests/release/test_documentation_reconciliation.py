from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/superpowers/specs/2026-09-02-chef-ai-pro-business-vnext-design.md"
PLAN = ROOT / "docs/superpowers/plans/2026-09-02-chef-ai-pro-business-vnext-implementation.md"
CURRENT = ROOT / "docs/architecture/current-state.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_current_state_distinguishes_static_contract_evals_from_live_surface_behavioral_evals():
    content = text(CURRENT)
    assert "STATIC_CONTRACT_EVALS" in content
    assert "LIVE_SURFACE_BEHAVIORAL_EVALS" in content
    assert "do not execute model/tool calls" in content


def test_phase13_is_documented_as_parallel_during_build_but_required_before_final_release():
    content = text(CURRENT)
    assert "parallel during early implementation" in content
    assert "mandatory before final commercial release" in content


def test_typography_is_documented_as_technically_specified_but_owner_review_draft():
    content = text(CURRENT)
    assert "technically specified candidate" in content
    assert "OWNER_REVIEW_DRAFT" in content
    assert "not yet canonical" in content


def test_current_state_declares_actual_policy_path_and_implementation_tree_authority():
    current = text(CURRENT)
    assert "company/evochia/policies/" in current
    assert "implemented repository tree is authoritative" in current


def test_historical_design_and_plan_are_preserved_as_records_not_silently_rewritten():
    assert "# Chef AI Pro Business vNext — Skill Suite Architecture Design" in text(DESIGN)
    assert "# Chef AI Pro Business vNext — Implementation Plan" in text(PLAN)
    current = text(CURRENT)
    assert "historical design/plan records" in current
    assert "earlier directory sketches" in current
