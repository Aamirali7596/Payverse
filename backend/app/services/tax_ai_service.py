"""PayVerse Tax MVP - Services Layer"""

import os
import sys
import json
import io
from pathlib import Path
from typing import Dict, Any, List

# Ensure UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app.core.config import settings
from app.services.hmrc_service import HMRCService
from skills.tax_processor import TaxDocumentProcessor
from skills.ca_expert import CAAdvisor

hmrc_service = HMRCService()


class TaxAIService:
    """Combines document processing with CA advice."""

    def __init__(self):
        self.processor = TaxDocumentProcessor(model=settings.DEFAULT_MODEL_EXTRACTION)
        self.advisor = CAAdvisor(model=settings.DEFAULT_MODEL_CA)

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Extract structured data from tax document."""
        return self.processor.process_file(file_path)

    def get_ca_advice(self, financial_data: Dict[str, Any], jurisdiction: str = "uk") -> Dict[str, Any]:
        """Get chartered accountant advice."""
        analysis = self.advisor.analyze_financial_data(financial_data, jurisdiction)
        return analysis.to_dict()

    def calculate_tax(self, income_data: Dict[str, Any], tax_year: str = "2024-25") -> Dict[str, Any]:
        """
        Calculate UK income tax for 2024-25.

        Income bands:
        - Personal Allowance: 12,570 (tax-free)
        - Basic rate (20%): 12,571 - 50,270
        - Higher rate (40%): 50,271 - 125,140
        - Additional rate (45%): 125,141+

        National Insurance:
        - 8%: 12,570 - 50,270
        - 2%: 50,271+
        """
        total_income = (
            income_data.get("employment_income", 0)
            + income_data.get("selfEmploymentIncome", 0)
            + income_data.get("dividendIncome", 0)
            + income_data.get("savingsInterest", 0)
            + income_data.get("propertyIncome", 0)
        )

        personal_allowance = 12570.0
        # Taper PA for income > 100k
        if total_income > 100000:
            reduction = (total_income - 100000) / 2
            personal_allowance = max(0, personal_allowance - reduction)

        taxable_income = max(0, total_income - personal_allowance)

        # Income tax calculation
        basic_rate_limit = 50270 - personal_allowance
        higher_rate_limit = 125140 - personal_allowance

        tax_basic = 0.0
        tax_higher = 0.0
        tax_additional = 0.0

        if taxable_income <= basic_rate_limit:
            tax_basic = taxable_income * 0.20
        elif taxable_income <= higher_rate_limit:
            tax_basic = basic_rate_limit * 0.20
            tax_higher = (taxable_income - basic_rate_limit) * 0.40
        else:
            tax_basic = basic_rate_limit * 0.20
            tax_higher = (higher_rate_limit - basic_rate_limit) * 0.40
            tax_additional = (taxable_income - higher_rate_limit) * 0.45

        income_tax = tax_basic + tax_higher + tax_additional

        # National Insurance (employee)
        ni_threshold = 12570.0
        ni_upper = 50270.0
        national_insurance = 0.0
        if total_income > ni_threshold:
            ni_income = min(total_income, ni_upper) - ni_threshold
            national_insurance += ni_income * 0.08
            if total_income > ni_upper:
                national_insurance += (total_income - ni_upper) * 0.02

        total_tax = income_tax + national_insurance
        effective_rate = (total_tax / total_income * 100) if total_income > 0 else 0

        return {
            "incomeBreakdown": {
                "employmentIncome": income_data.get("employmentIncome", 0),
                "selfEmploymentIncome": income_data.get("selfEmploymentIncome", 0),
                "dividendIncome": income_data.get("dividendIncome", 0),
                "savingsInterest": income_data.get("savingsInterest", 0),
                "propertyIncome": income_data.get("propertyIncome", 0),
                "totalIncome": total_income,
            },
            "taxResult": {
                "taxAllowance": personal_allowance,
                "taxableIncome": taxable_income,
                "taxBasic": round(tax_basic, 2),
                "taxHigher": round(tax_higher, 2),
                "taxAdditional": round(tax_additional, 2),
                "incomeTax": round(income_tax, 2),
                "nationalInsurance": round(national_insurance, 2),
                "totalTax": round(total_tax, 2),
                "effectiveTaxRate": round(effective_rate, 2),
            },
        }


tax_ai_service = TaxAIService()
