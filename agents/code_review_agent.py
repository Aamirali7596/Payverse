"""
Code Review Agent - Governance & Best Practices

Reviews code changes for:
- Code quality (PEP8, type hints, docstrings)
- Architecture compliance
- Security patterns
- Performance issues
- Test coverage gaps

Usage:
  python -m agents.code_review_agent --files backend/app/main.py frontend/src/page.jsx
  python -m agents.code_review_agent --diff  # Review git diff
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any


class CodeReviewAgent:
    """Reviews code for quality, security, compliance"""

    CHECKS = {
        'security': {
            'description': 'Security vulnerabilities',
            'patterns': [
                (r'eval\(', 'dangerous-eval', 'Avoid eval()'),
                (r'\.execute\(.*\+.*\)', 'sql-injection', 'Use parameterized queries'),
                (r'DEBUG\s*=\s*True', 'debug-mode', 'Disable DEBUG in production'),
                (r'password\s*=', 'password-in-code', 'Never hardcode passwords'),
                (r'api_key\s*=', 'api-key-in-code', 'Use environment variables'),
            ]
        },
        'quality': {
            'description': 'Code quality',
            'patterns': [
                (r'import \*', 'wildcard-import', 'Avoid star imports'),
                (r'^\s*pass\s*$', 'empty-pass', 'Implement or remove pass'),
                (r'^\s*raise\s+Exception\s*\(', 'generic-exception', 'Use specific exception'),
            ]
        },
        'fintech': {
            'description': 'Fintech-specific checks',
            'patterns': [
                (r'card.*=.*\d+', 'card-data', 'Never store card data'),
                (r'bank.*account', 'bank-data', 'Encrypt bank details'),
                (r'decrypt\(', 'decryption', 'Use secure KMS'),
            ]
        }
    }

    def review_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Review a single file"""
        issues = []
        path = Path(filepath)

        if not path.exists():
            return issues

        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
        except Exception:
            return issues

        for line_num, line in enumerate(lines, start=1):
            for category, config in self.CHECKS.items():
                for pattern, rule_id, message in config['patterns']:
                    import re
                    if re.search(pattern, line):
                        issues.append({
                            'file': str(path),
                            'line': line_num,
                            'category': category,
                            'rule': rule_id,
                            'message': message,
                            'snippet': line.strip()[:80]
                        })

        return issues

    def review_diff(self) -> List[Dict[str, Any]]:
        """Review git diff (staged changes)"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--unified=0'],
                capture_output=True, text=True
            )
            diff = result.stdout
        except Exception as e:
            print(f"Error getting diff: {e}")
            return []

        issues = []
        current_file = None
        for line in diff.split('\n'):
            if line.startswith('+++ b/'):
                current_file = line[6:]
            elif line.startswith('+') and not line.startswith('+++'):
                # This is an added line
                line_content = line[1:]
                for category, config in self.CHECKS.items():
                    for pattern, rule_id, message in config['patterns'].items():
                        import re
                        if re.search(pattern, line_content):
                            issues.append({
                                'file': current_file,
                                'line': 0,  # diff doesn't give line numbers easily
                                'category': category,
                                'rule': rule_id,
                                'message': message,
                                'snippet': line_content[:80]
                            })
        return issues


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Code Review Agent")
    parser.add_argument('--files', nargs='+', help='Files to review')
    parser.add_argument('--diff', action='store_true', help='Review git diff')
    parser.add_argument('--format', choices=['text', 'json'], default='text')

    args = parser.parse_args()
    agent = CodeReviewAgent()

    if args.diff:
        issues = agent.review_diff()
    elif args.files:
        issues = []
        for filepath in args.files:
            issues.extend(agent.review_file(filepath))
    else:
        parser.print_help()
        sys.exit(1)

    if args.format == 'json':
        print(json.dumps({'issues': issues, 'count': len(issues)}, indent=2))
    else:
        print(f"\nCode Review: {len(issues)} issues found\n")
        for issue in issues:
            print(f"{issue['file']}:{issue['line']}")
            print(f"  [{issue['category']}] {issue['message']}")
            if issue['snippet']:
                print(f"  Code: {issue['snippet']}")
            print()

    # Exit with non-zero if issues found (for CI)
    sys.exit(1 if issues else 0)


if __name__ == '__main__':
    main()
