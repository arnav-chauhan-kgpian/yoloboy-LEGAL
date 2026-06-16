import json
from pathlib import Path
from app.schemas.contract import ContractIn


def test_nexus_meridian_loads_and_has_four_gaps_by_design():
    p = Path(__file__).parent.parent.parent / "data" / "contracts" / "nexus_meridian.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    contract = ContractIn(**data)
    assert contract.contract_id == "nexus_meridian"
    assert len(contract.clauses) == 10

    mapped = set()
    for cl in contract.clauses:
        for r in cl.maps_to_requirements:
            mapped.add(r)

    expected_present = {
        "gdpr_art_5", "gdpr_art_6", "gdpr_art_9", "gdpr_art_13",
        "gdpr_art_28", "gdpr_art_32", "gdpr_art_33",
    }
    assert expected_present.issubset(mapped)

    expected_gaps = {"gdpr_art_17", "gdpr_art_25", "gdpr_art_35", "gdpr_art_44"}
    for g in expected_gaps:
        assert g not in mapped, f"{g} should be a gap in nexus_meridian"


def test_orion_payments_covers_all_demo_requirements():
    p = Path(__file__).parent.parent.parent / "data" / "contracts" / "orion_payments.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    contract = ContractIn(**data)

    mapped = set()
    for cl in contract.clauses:
        for r in cl.maps_to_requirements:
            mapped.add(r)

    for r in [
        "gdpr_art_5", "gdpr_art_6", "gdpr_art_9", "gdpr_art_13",
        "gdpr_art_17", "gdpr_art_25", "gdpr_art_28", "gdpr_art_32",
        "gdpr_art_33", "gdpr_art_35", "gdpr_art_44",
    ]:
        assert r in mapped, f"{r} must be covered by orion_payments"
