"""Chartered Accountant AI service using local Ollama AI."""

from skills.ca_expert import CAAdvisor
from app.core.config import settings


class CAService:
    """Wraps the CA Expert skill for tax advice."""

    def __init__(self):
        self.advisor = CAAdvisor(model=settings.DEFAULT_MODEL_CA)

    async def get_advice(self, financial_data: dict, jurisdiction: str = "uk") -> dict:
        """Get tax optimization advice for given financial data."""
        analysis = self.advisor.analyze_financial_data(financial_data, jurisdiction)
        return analysis.to_dict()

    async def chat(self, message: str, jurisdiction: str = "uk") -> str:
        """Chat with the CA expert."""
        return self.advisor.chat(message, jurisdiction)


ca_service = CAService()
