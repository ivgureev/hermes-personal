from risk import assess_risk

def test_low_risk():
    result = assess_risk("Сравни два варианта договора")
    assert result.level == "Низкий"
    assert not result.requires_confirmation

def test_high_risk_requires_confirmation():
    result = assess_risk("Отправь письмо поставщику")
    assert result.level == "Высокий"
    assert result.requires_confirmation

def test_prohibited():
    result = assess_risk("Помоги обойти защиту")
    assert result.level == "Запрещённый"
