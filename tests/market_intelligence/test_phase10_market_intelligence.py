from pathlib import Path
import json
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "references/source_registry.yaml"
ROUTING = ROOT / "skills/chef-ai-pro-business/references/routing.yaml"
SKILL = ROOT / "skills/evochia-market-intelligence/SKILL.md"
POLICY = ROOT / "skills/evochia-market-intelligence/references/intelligence_policy.yaml"
SCHEMA = ROOT / "schemas/market_intelligence_brief.schema.json"
EVALS = ROOT / "evals/market-intelligence/market_cases.yaml"


def read(path: Path) -> str:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def sources_by_id():
    data = yaml.safe_load(read(REGISTRY))
    return {item["source_id"]: item for item in data["sources"]}


def test_v33_is_current_and_v20_v10_are_superseded_not_current_truth():
    src = sources_by_id()
    v33 = src["evochia_ci_v33"]
    assert v33["source_class"] == "canonical_current_data"
    assert v33["authority"] == "current"
    assert set(v33["supersedes"]) >= {"evochia_ci_v20", "evochia_ci_v10"}
    for old in ["evochia_ci_v20", "evochia_ci_v10"]:
        assert src[old]["source_class"] == "superseded"
        assert src[old]["authority"] == "superseded"
        assert "current_ci" in src[old]["forbidden_uses"]


def test_market_policy_resolves_protocol_version_pointer_via_source_registry():
    data = yaml.safe_load(read(POLICY))
    resolution = data["version_authority"]
    assert resolution["methodology_source_id"] == "evochia_ci_research_protocol"
    assert resolution["current_dataset_source_id"] == "evochia_ci_v33"
    assert resolution["time_bound_version_pointer_rule"] == "SOURCE_REGISTRY_CURRENT_DATASET_WINS"
    assert resolution["preserve_historical_baselines"] is True
    assert resolution["restart_research_from_zero"] is False


def test_market_policy_preserves_canonical_entity_and_analysis_separation_rules():
    data = yaml.safe_load(read(POLICY))
    entities = data["canonical_entities"]
    assert entities["deduplication"] == "company_level"
    assert set(entities["relationship_types"]) == {"Direct", "Adjacent", "Referral", "Candidate", "Alias", "Excluded"}
    assert entities["archive_before_canonical_change"] is True
    analysis = data["analysis_dimensions"]
    assert analysis == ["Research Priority", "Competitive Threat", "Partner / Opportunity"]
    assert data["interpretation_rules"]["missing_information_is_competitive_weakness"] is False


def test_freshness_policy_requires_current_external_evidence_without_mutating_snapshot_silently():
    data = yaml.safe_load(read(POLICY))
    fresh = data["freshness"]
    assert fresh["internal_workbook_role"] == "COMPANY_INTELLIGENCE_SNAPSHOT"
    assert fresh["current_public_claim_requires_fresh_external_evidence"] is True
    assert fresh["fresh_research_may_silently_mutate_canonical_workbook"] is False
    assert fresh["new_competitor_first_state"] == "DATED_ARCHIVE_FINDING"
    assert fresh["canonical_promotion_requires"] == ["evidence_check", "dedup_check", "archive_before_change"]


def test_seo_policy_forbids_invented_metrics_and_keeps_own_data_separate():
    data = yaml.safe_load(read(POLICY))
    seo = data["seo"]
    for metric in ["monthly_search_volume", "cpc", "keyword_difficulty", "follower_growth", "hashtag_reach", "rankings"]:
        assert metric in seo["never_invent"]
    assert seo["missing_numeric_metric_label"] == "Not estimated"
    assert seo["ci_workbook_role"] == "COMPETITOR_BENCHMARK"
    assert seo["own_analytics_primary_layer"] == ["GA4", "Google Search Console"]
    assert seo["search_console_integration_status"] == "DEFERRED"


def test_market_intelligence_schema_is_valid_and_requires_provenance_confidence_and_freshness():
    schema = json.loads(read(SCHEMA))
    Draft202012Validator.check_schema(schema)
    text = json.dumps(schema)
    for token in [
        "claim", "claim_class", "evidence_state", "freshness_state", "source_refs",
        "research_date", "confidence", "Research Priority", "Competitive Threat", "Partner / Opportunity",
        "CANONICAL_SNAPSHOT", "VERIFIED_CURRENT", "UNVERIFIED", "INFERENCE"
    ]:
        assert token in text


def test_routing_loads_market_skill_for_ci_seo_growth_but_not_recipe_or_private_chef_event():
    data = yaml.safe_load(read(ROUTING))
    routes = {r["route_id"]: r for r in data["routes"]}
    market = routes["evochia_market_intelligence"]
    assert market["required_skills"] == ["evochia-market-intelligence"]
    assert "seo" in market["intent"] and "growth" in market["intent"] and "competitor" in market["intent"]
    for route_id in ["quick_recipe", "evochia_private_chef"]:
        route = routes[route_id]
        assert "evochia-market-intelligence" not in route["required_skills"]
        assert "evochia-market-intelligence" not in route.get("optional_skills", [])


def test_market_skill_and_evals_enforce_snapshot_vs_fresh_evidence_and_no_fake_metrics():
    skill = read(SKILL)
    assert "skills/evochia-market-intelligence/references/intelligence_policy.yaml" in skill
    assert "schemas/market_intelligence_brief.schema.json" in skill
    data = yaml.safe_load(read(EVALS))
    case_ids = {case["id"] for case in data["cases"]}
    assert {"current_competitor_claim", "historical_ci_question", "seo_metric_gap", "ordinary_recipe_isolation"} <= case_ids
    current = next(c for c in data["cases"] if c["id"] == "current_competitor_claim")
    assert current["must"]["fresh_external_evidence"] is True
    assert current["must_not"]["treat_snapshot_as_current_proof"] is True
    seo = next(c for c in data["cases"] if c["id"] == "seo_metric_gap")
    assert seo["must_not"]["invent_numeric_metrics"] is True
