"""
CA Expert - Chartered Accountant AI for Tax Optimization

20 years experience in UK & UAE tax law.
Finds legal tax-saving loopholes and reliefs.

Usage:
  python -m skills.ca_expert --chat
  python -m skills.ca_expert --analyze data.json
"""

import json
import ollama
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class TaxRelief:
    name: str
    description: str
    potential_savings: float
    eligibility: List[str]
    evidence_required: List[str]
    priority: int = 1
    jurisdiction: str = "uk"

    def to_dict(self):
        return asdict(self)


@dataclass
class TaxAnalysis:
    user_id: str = None
    jurisdiction: str = "uk"
    total_current_tax: float = 0.0
    total_optimized_tax: float = 0.0
    potential_savings: float = 0.0
    reliefs_found: List[TaxRelief] = None
    recommendations: List[str] = None
    confidence: float = 0.85
    generated_at: datetime = None

    def __post_init__(self):
        if self.reliefs_found is None:
            self.reliefs_found = []
        if self.recommendations is None:
            self.recommendations = []
        if self.generated_at is None:
            self.generated_at = datetime.now()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'jurisdiction': self.jurisdiction,
            'total_current_tax': self.total_current_tax,
            'total_optimized_tax': self.total_optimized_tax,
            'potential_savings': self.potential_savings,
            'reliefs_found': [r.to_dict() for r in self.reliefs_found],
            'recommendations': self.recommendations,
            'confidence': self.confidence,
            'generated_at': self.generated_at.isoformat()
        }


class CAAdvisor:
    SYSTEM_PROMPT = """You are a chartered accountant with 20 years of experience in UK and UAE tax law.

UK Tax Reliefs (2024-25):
- Marriage Allowance: Transfer 10% of PA to spouse, save up to £1,260
- Pension Relief: 20% basic rate, up to 45% for higher/additional rate
- Gift Aid: 25% relief on charitable donations
- Working from Home: £6/week flat rate
- EIS: 30% income tax relief on up to £1M startup investment
- SEIS: 50% relief on up to £100K in early-stage startups
- R&D Credits: 230% enhancement on qualifying expenditure
- Bed and ISA: Transfer shares to ISA (CGT-free)
- Spouse Transfers: Split income to use lower tax band
- Capital Gains Tax: Annual exempt amount £3,000

UAE Tax:
- VAT: 5% standard, group registration available
- Corporate Tax: 9% on taxable income > AED 375,000
- Free zone benefits: 0% if substance requirements met

IMPORTANT:
- Only suggest LEGAL tax optimization
- Provide specific £/AED amounts
- Cite HMRC/FTA references
- Prioritize by savings + ease of claiming
- Include required documentation

Return structured analysis with:
1. Current tax position
2. All applicable reliefs with savings
3. Actionable recommendations
4. Disclaimer about consulting accountant
"""

    def __init__(self, model: str = "llama3:8b", temperature: float = 0.3):
        self.model = model
        self.temperature = temperature
        try:
            self.client = ollama.Client(host='http://localhost:11434')
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")
            self.client = None

    def analyze_financial_data(self, data: Dict, jurisdiction: str = "uk") -> TaxAnalysis:
        if not self.client:
            return TaxAnalysis(
                jurisdiction=jurisdiction,
                total_current_tax=0,
                potential_savings=0,
                reliefs_found=[],
                recommendations=["Ollama not available - install and run ollama serve"],
                confidence=0
            )

        prompt = f"{self.SYSTEM_PROMPT}\n\nAnalyze this tax situation:\n{json.dumps(data, indent=2)}\n\nProvide your full analysis:"

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={'temperature': self.temperature}
            )
            analysis_text = response['response']

            # Simple parsing (in production, ask for JSON output)
            savings = self._extract_savings(analysis_text)

            reliefs = [
                TaxRelief(
                    name="Potential Relief (see analysis)",
                    description="Review full analysis for specific reliefs",
                    potential_savings=savings,
                    eligibility=[],
                    evidence_required=[],
                    priority=1
                )
            ]

            return TaxAnalysis(
                user_id=str(data.get('user_id', '')),
                jurisdiction=jurisdiction,
                total_current_tax=data.get('tax_owed', 0) + data.get('ni_paid', 0),
                total_optimized_tax=max(0, data.get('tax_owed', 0) + data.get('ni_paid', 0) - savings),
                potential_savings=savings,
                reliefs_found=reliefs,
                recommendations=[analysis_text[:500] + "..."],
                confidence=0.85
            )
        except Exception as e:
            return TaxAnalysis(
                jurisdiction=jurisdiction,
                total_current_tax=0,
                potential_savings=0,
                reliefs_found=[],
                recommendations=[f"Error: {str(e)}"],
                confidence=0
            )

    def _extract_savings(self, text: str) -> float:
        import re
        matches = re.findall(r'save[s]? £([\d,]+(?:\.\d{2})?)', text, re.IGNORECASE)
        total = 0.0
        for match in matches:
            try:
                total += float(match.replace(',', ''))
            except:
                pass
        return total

    def chat(self, message: str, jurisdiction: str = "uk") -> str:
        if not self.client:
            return "Error: Ollama not available"

        response = self.client.chat(
            model=self.model,
            messages=[
                {'role': 'system', 'content': self.SYSTEM_PROMPT},
                {'role': 'user', 'content': f"Jurisdiction: {jurisdiction}\n\n{message}"}
            ],
            options={'temperature': self.temperature}
        )
        return response['message']['content']


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CA Expert - Tax Optimization Advisor")
    parser.add_argument('--model', default='llama3:8b')
    parser.add_argument('--chat', action='store_true')
    parser.add_argument('--analyze', help='JSON file with financial data')
    parser.add_argument('--jurisdiction', default='uk', choices=['uk', 'uae'])
    parser.add_argument('--output', help='Output file for analysis (JSON)')

    args = parser.parse_args()
    advisor = CAAdvisor(model=args.model)

    if args.chat:
        print("CA Expert Chat Mode - Type 'quit' to exit")
        while True:
            msg = input("\nYou: ").strip()
            if msg.lower() == 'quit':
                break
            response = advisor.chat(msg, args.jurisdiction)
            print(f"\nCA: {response}\n")
    elif args.analyze:
        with open(args.analyze, 'r') as f:
            data = json.load(f)
        analysis = advisor.analyze_financial_data(data, args.jurisdiction)
        result = analysis.to_dict()
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Analysis saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
