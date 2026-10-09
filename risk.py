from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RiskAssessment:
    level: str
    requires_confirmation: bool
    reason: str

PROHIBITED = ("взлом", "укради", "обойти защит", "вредонос", "подделать подпись")
HIGH = ("отправ", "оплат", "куп", "удал", "опубли", "подпис", "подать", "изменить права", "раскрыть данные")
MEDIUM = ("изменить файл", "финальная версия", "заявк", "письмо адресату", "уведомление")


def assess_risk(text: str) -> RiskAssessment:
    value = text.lower()
    if any(x in value for x in PROHIBITED):
        return RiskAssessment("Запрещённый", True, "Запрос может быть незаконным, опасным или нарушать права.")
    if any(x in value for x in HIGH):
        return RiskAssessment("Высокий", True, "Возможны внешние или необратимые последствия.")
    if any(x in value for x in MEDIUM):
        return RiskAssessment("Средний", True, "Нужно проверить результат до значимого шага.")
    return RiskAssessment("Низкий", False, "Чтение, анализ, расчёт или подготовка черновика.")
