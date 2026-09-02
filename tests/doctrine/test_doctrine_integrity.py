from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_doctrine_integrity import validate

def read(rel):
    return (ROOT/rel).read_text(encoding='utf-8')

def test_manifest_checksums_pass():
    assert validate(ROOT)==[]

def test_non_linear_scaling_guard_survives():
    t=read('references/operations/professional_kitchen_workflows_v2_2.md')
    assert 'do not scale salt, spice, acid, yeast, gelatin, thickeners or leavening blindly' in t
    assert 'heat transfer, evaporation, mixing efficiency, cooling time and plating speed' in t

def test_safety_no_guarantee_survives():
    t=read('references/safety/food_safety_allergens_v2_5.md')
    assert 'Never guarantee that food is safe, allergen-free' in t
    assert 'May-contain and cross-contact must be separate from confirmed presence.' in t

def test_costing_ap_ep_vat_survives():
    t=read('references/costing/costing_formula_engine_v2_2.md')
    assert 'All internal costing uses net cost excluding recoverable VAT.' in t
    assert 'Q_AP_required = Q_EP_target / y_total' in t
    assert 'c_EP = c_AP / y_total' in t

def test_supplier_evidence_and_approval_survive():
    t=read('references/yields/supplier_yield_workflow_v3_2_2.md')
    assert 'Raw values are evidence. Normalized fields are separate.' in t
    assert 'The GPT must never auto-approve supplier prices into the approved master.' in t

def test_what_if_baseline_is_immutable():
    t=read('references/costing/what_if_profitability_v2_2.md')
    assert 'A what-if scenario must never overwrite baseline data.' in t

def test_doctrine_cases_cover_release_critical_regressions():
    import yaml
    data=yaml.safe_load((ROOT/'evals/legacy/doctrine_cases.yaml').read_text(encoding='utf-8'))
    cases=data['cases']
    ids={case['case_id'] for case in cases}
    assert ids == {
        'DOCTRINE-001','DOCTRINE-002','DOCTRINE-003','DOCTRINE-004',
        'DOCTRINE-005','DOCTRINE-006','DOCTRINE-007'
    }
    required={'domain','title','source','must_detect','forbidden_behavior','expected_behavior'}
    for case in cases:
        assert required <= set(case)
        assert (ROOT/case['source']).is_file()
        assert case['must_detect']
        assert case['forbidden_behavior']
        assert case['expected_behavior']
