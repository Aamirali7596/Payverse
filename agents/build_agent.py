"""
Build Agent - Provides CA Tax Advice During Development

Usage scenarios:
1. While building frontend, ask: "What tax reliefs should I highlight for a £45k earner?"
2. Get sample CA advice JSON for mock UI
3. Validate financial data scenarios

Usage:
  python -m agents.build_agent --advice '{"annual_income": 45000, "employment_type": "employee"}'
  python -m agents.build_agent --sample-ui  # Generate sample advice for UI mock
"""

import json
import sys
from skills.ca_expert import CAAdvisor


def generate_sample_advice():
    """Generate sample CA advice for UI development"""
    advisor = CAAdvisor()

    sample_scenarios = [
        {"annual_income": 45000, "employment_type": "employee", "marital_status": "married", "spouse_income": 10000},
        {"annual_income": 65000, "employment_type": "self-employed", "pension_contributions": 5000},
        {"annual_income": 120000, "employment_type": "employee", "has_dividends": True},
    ]

    print("Sample CA Advice for UI Development:\n")
    for scenario in sample_scenarios:
        print(f"Scenario: {scenario}")
        analysis = advisor.analyze_financial_data(scenario, jurisdiction='uk')
        result = analysis.to_dict()
        print(f"  Potential Savings: £{result['potential_savings']:.2f}")
        print(f"  Reliefs Found: {len(result['reliefs_found'])}")
        for relief in result['reliefs_found'][:3]:  # Show top 3
            print(f"    - {relief['name']}: £{relief['potential_savings']:.2f}")
        print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build Agent - CA Advice for Development")
    parser.add_argument('--advice', help='JSON string with financial_data to analyze')
    parser.add_argument('--jurisdiction', default='uk', choices=['uk', 'uae'])
    parser.add_argument('--sample-ui', action='store_true', help='Generate sample advice for UI mock')
    parser.add_argument('--output', help='Save to JSON file')

    args = parser.parse_args()
    advisor = CAAdvisor()

    if args.sample_ui:
        generate_sample_advice()
    elif args.advice:
        try:
            data = json.loads(args.advice)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            sys.exit(1)

        analysis = advisor.analyze_financial_data(data, jurisdiction=args.jurisdiction)
        result = analysis.to_dict()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Advice saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
