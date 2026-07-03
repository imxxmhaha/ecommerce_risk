from app.services.decision_service import DecisionService


def test_only_highest_priority_hits_contribute_to_score():
    service = DecisionService()
    hits = [
        {
            "rule_code": "NEW_USER_AMOUNT_GT_3000",
            "rule_name": "new user amount greater than 3000",
            "priority": 20,
            "hit_score": 35,
        },
        {
            "rule_code": "NEW_USER_AMOUNT_GT_5000",
            "rule_name": "new user amount greater than 5000",
            "priority": 30,
            "hit_score": 60,
        },
    ]

    assert service.effective_hits(hits) == [hits[1]]
    assert service.calculate_score(hits) == 60.0
    assert service.calculate_level(service.calculate_score(hits)) == "medium"
    marked_hits = service.mark_effective_hit(hits)
    assert marked_hits[0]["is_effective"] is False
    assert marked_hits[1]["is_effective"] is True


def test_same_priority_uses_highest_score_as_effective_hit():
    service = DecisionService()
    hits = [
        {"rule_code": "A", "priority": 10, "hit_score": 40},
        {"rule_code": "B", "priority": 10, "hit_score": 50},
        {"rule_code": "C", "priority": 5, "hit_score": 90},
    ]

    assert service.effective_hits(hits) == [hits[1]]
    assert service.calculate_score(hits) == 50.0
