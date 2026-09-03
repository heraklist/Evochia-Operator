from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/superpowers/specs/2026-09-02-chef-ai-pro-business-vnext-design.md"
PLAN = ROOT / "docs/superpowers/plans/2026-09-02-chef-ai-pro-business-vnext-implementation.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_distinguishes_static_contract_evals_from_live_surface_behavioral_evals():
    content = text(DESIGN)
    assert "STATIC_CONTRACT_EVALS" in content
    assert "LIVE_SURFACE_BEHAVIORAL_EVALS" in content
    assert "do not execute model/tool calls" in content


def test_phase13_is_documented_as_parallel_during_build_but_required_before_final_release():
    combined = text(DESIGN) + "\n" + text(PLAN)
    assert "parallel during early implementation" in combined
    assert "mandatory before final commercial release" in combined


def test_typography_is_documented_as_technically_specified_but_owner_review_draft():
    combined = text(DESIGN) + "\n" + text(PLAN)
    assert "technically specified candidate" in combined
    assert "OWNER_REVIEW_DRAFT" in combined
    assert "not yet canonical" in combined


def test_plan_uses_actual_evochia_policy_path():
    content = text(PLAN)
    assert "company/evochia/policies/" in content
