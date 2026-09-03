from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
ROUTING = ROOT / "skills/chef-ai-pro-business/references/routing.yaml"


def test_evochia_market_intelligence_has_one_canonical_route():
    data = yaml.safe_load(ROUTING.read_text(encoding="utf-8"))
    routes = {item["route_id"]: item for item in data["routes"]}
    assert "competitor_intelligence" not in routes
    assert "evochia_market_intelligence" in routes
    market = routes["evochia_market_intelligence"]
    assert market["required_skills"] == ["evochia-market-intelligence"]
    assert "competitor" in market["intent"]
    assert "seo" in market["intent"]
    assert "growth" in market["intent"]
    assert market["freshness"] == "snapshot_plus_current_evidence_when_claim_is_mutable"
