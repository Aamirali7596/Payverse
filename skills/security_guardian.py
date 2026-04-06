"""
Security Guardian - Fintech Security & Data Governance Expert

10+ years experience in fintech security, white-hat hacking, GDPR compliance

Scans code for:
- Secrets exposure (API keys, passwords, tokens)
- PII leakage (emails, phones, NI numbers, addresses)
- Vulnerabilities (SQL injection, XSS, weak crypto)
- GDPR compliance issues
- Fintech-specific risks (card data, bank details)

Usage as module:
  from skills.security_guardian import SecurityGuardian
  guardian = SecurityGuardian()
  issues = guardian.scan_directory('backend/')
  report = guardian.generate_report(issues)

CLI usage:
  python -m skills.security_guardian --scan .
  python -m skills.security_guardian --pre-commit
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class SecurityIssue:
    SEVERITIES = ['critical', 'high', 'medium', 'low', 'info']

    def __init__(self, filepath: str, line: int, severity: str, rule_id: str,
                 description: str, snippet: str = "", recommendation: str = ""):
        self.filepath = filepath
        self.line = line
        self.severity = severity
        self.rule_id = rule_id
        self.description = description
        self.snippet = snippet[:100]
        self.recommendation = recommendation

    def to_dict(self):
        return {
            'file': self.filepath,
            'line': self.line,
            'severity': self.severity,
            'rule_id': self.rule_id,
            'description': self.description,
            'snippet': self.snippet,
            'recommendation': self.recommendation
        }


class SecurityGuardian:
    """Scan code for security issues with fintech focus"""

    SECRET_PATTERNS = [
        (re.compile(r'(?:api[_-]?key|apikey|secret|token|password|passwd|pwd|credential)["\']?\s*[=:]\s*["\']([^"\']{8,})["\']', re.IGNORECASE), 'hardcoded-secret', 'Hardcoded API key or secret', 'Use environment variables'),
        (re.compile(r'(?:sk_live_|sk_test_|pk_live_|pk_test_|rk_live_|rk_test_)', re.IGNORECASE), 'stripe-key', 'Possible Stripe API key exposed', 'Move to STRIPE_* env vars'),
        (re.compile(r'AIza[0-9A-Za-z\\-_]{35}', re.IGNORECASE), 'google-api-key', 'Google API key exposed', 'Use secure storage'),
        (re.compile(r'(?:BEGIN|END)\s+(?:RSA\s+)?PRIVATE\s+KEY', re.IGNORECASE), 'private-key', 'Private key in code', 'Use environment or key management service'),
        (re.compile(r'ghp_[0-9a-zA-Z]{36}', re.IGNORECASE), 'github-token', 'GitHub personal access token', 'Rotate token immediately'),
        (re.compile(r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}', re.IGNORECASE), 'jwt-token', 'JWT token exposed', 'Never hardcode JWT secrets'),
        (re.compile(r'(?:mongodb|mysql|postgresql)://[^/"\'\\s]+', re.IGNORECASE), 'database-uri', 'Database connection string with credentials', 'Use environment variables'),
    ]

    PII_PATTERNS = [
        (re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'), 'email-address', 'Email address PII', 'Anonymize in logs/code'),
        (re.compile(r'(\+44|0)(\d{10,11})'), 'uk-phone', 'UK phone number PII', 'Mask or remove'),
        (re.compile(r'[A-Z]{2}\d{9}[A-Z]?'), 'ni-number', 'National Insurance number (UK)', 'Highly sensitive - remove'),
        (re.compile(r'\b\d{6}\s*\d{2}[A-Z]{2}\b', re.IGNORECASE), 'utr', 'Unique Taxpayer Reference (UK)', 'Sensitive - anonymize'),
        (re.compile(r'\b[A-Z]{2}\d{6}[A-Z]?\b'), 'nino-check', 'NI number format', 'Remove immediately'),
    ]

    VULN_PATTERNS = [
        (re.compile(r'\.execute\(.*\+.*\)'), 'sql-injection', 'Potential SQL injection', 'Use parameterized queries'),
        (re.compile(r'eval\(|exec\(', re.IGNORECASE), 'code-injection', 'Use of eval/exec (dangerous)', 'Refactor to avoid'),
        (re.compile(r'pickle\.load\(', re.IGNORECASE), 'unsafe-deserialization', 'Unpickle of untrusted data', 'Use JSON or safe deserialization'),
        (re.compile(r'(?:md5|sha1)\(', re.IGNORECASE), 'weak-hash', 'Weak cryptographic hash (MD5/SHA1)', 'Use SHA-256 or bcrypt'),
        (re.compile(r'print\(.*password|print\(.*token', re.IGNORECASE), 'info-logging', 'Logging sensitive data', 'Remove PII from logs'),
        (re.compile(r'except.*:.*pass', re.IGNORECASE), 'bare-except', 'Bare except clause', 'Log exception, re-raise'),
        (re.compile(r'DEBUG\s*=\s*True', re.IGNORECASE), 'debug-mode', 'Debug mode enabled', 'Set DEBUG=False in production'),
    ]

    FINTECH_PATTERNS = [
        (re.compile(r'(?:card|cvv|ccv|pan)\s*[=:]\s*["\']', re.IGNORECASE), 'card-data', 'Card data in code', 'PCI-DSS violation - never store'),
        (re.compile(r'bank_account|account_number|sort_code', re.IGNORECASE), 'bank-details', 'Bank details in code', 'Encrypt or remove'),
        (re.compile(r'decrypt\(.*password.*\)', re.IGNORECASE), 'weak-decryption', 'Weak decryption', 'Use KMS or vault'),
    ]

    def __init__(self):
        self.issues = []

    def scan_file(self, filepath: str) -> List[SecurityIssue]:
        issues = []
        path = Path(filepath)

        if not path.exists() or not path.is_file():
            return []

        # Skip binary files
        if path.suffix in ['.png', '.jpg', '.jpeg', '.pdf', '.exe', '.dll']:
            return []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            return []

        for line_num, line in enumerate(lines, start=1):
            line_stripped = line.strip()

            # Check secrets
            for pattern, rule_id, desc, rec in self.SECRET_PATTERNS:
                if pattern.search(line_stripped):
                    snippet = self._redact_sensitive(line_stripped)
                    issues.append(SecurityIssue(
                        filepath=str(path), line=line_num, severity='critical',
                        rule_id=rule_id, description=desc, snippet=snippet, recommendation=rec
                    ))

            # Check PII
            for pattern, rule_id, desc, rec in self.PII_PATTERNS:
                if pattern.search(line_stripped):
                    snippet = self._sanitize_for_logging(line_stripped)
                    severity = 'medium' if 'ni-number' in rule_id else 'low'
                    issues.append(SecurityIssue(
                        filepath=str(path), line=line_num, severity=severity,
                        rule_id=rule_id, description=desc, snippet=snippet, recommendation=rec
                    ))

            # Check vulnerabilities
            for pattern, rule_id, desc, rec in self.VULN_PATTERNS:
                if pattern.search(line_stripped):
                    issues.append(SecurityIssue(
                        filepath=str(path), line=line_num, severity='high',
                        rule_id=rule_id, description=desc, snippet=line_stripped[:80], recommendation=rec
                    ))

            # Check fintech-specific
            for pattern, rule_id, desc, rec in self.FINTECH_PATTERNS:
                if pattern.search(line_stripped):
                    issues.append(SecurityIssue(
                        filepath=str(path), line=line_num, severity='critical',
                        rule_id=rule_id, description=desc, snippet=line_stripped[:80], recommendation=rec
                    ))

        return issues

    def _redact_sensitive(self, text: str) -> str:
        """Redact secret values"""
        for pattern, *_ in self.SECRET_PATTERNS:
            text = pattern.sub(lambda m: m.group(0).split('=')[0] + '=***REDACTED***', text)
        return text

    def _sanitize_for_logging(self, text: str) -> str:
        """Replace PII with placeholders"""
        text = re.sub(r'([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})', r'***EMAIL***@***DOMAIN***', text)
        text = re.sub(r'(\+44|0)(\d{10,11})', r'***PHONE***', text)
        text = re.sub(r'[A-Z]{2}\d{9}[A-Z]?', r'***NI***', text)
        return text

    def scan_directory(self, directory: str) -> List[SecurityIssue]:
        all_issues = []
        path = Path(directory)

        if not path.exists():
            return all_issues

        for filepath in path.rglob('*'):
            if filepath.is_file() and filepath.suffix in ['.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yml', '.yaml', '.env']:
                issues = self.scan_file(str(filepath))
                all_issues.extend(issues)

        all_issues.sort(key=lambda x: SecurityIssue.SEVERITIES.index(x.severity))
        return all_issues

    def scan_git_changes(self) -> List[SecurityIssue]:
        """Scan staged files"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True, cwd=os.getcwd()
            )
            staged_files = [f for f in result.stdout.strip().split('\n') if f]
            all_issues = []
            for filepath in staged_files:
                if Path(filepath).exists():
                    all_issues.extend(self.scan_file(filepath))
            all_issues.sort(key=lambda x: SecurityIssue.SEVERITIES.index(x.severity))
            return all_issues
        except Exception as e:
            print(f"Error scanning git changes: {e}")
            return []

    def generate_report(self, issues: List[SecurityIssue], format: str = 'text') -> str:
        if format == 'json':
            return json.dumps({
                'scan_timestamp': datetime.now().isoformat(),
                'total_issues': len(issues),
                'issues': [i.to_dict() for i in issues]
            }, indent=2)

        lines = []
        lines.append("=" * 80)
        lines.append(f"SECURITY GUARDIAN SCAN REPORT")
        lines.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total issues: {len(issues)}")
        lines.append("=" * 80)
        lines.append("")

        if not issues:
            lines.append("[PASS] NO ISSUES FOUND")
            return "\n".join(lines)

        for severity in SecurityIssue.SEVERITIES:
            sev_issues = [i for i in issues if i.severity == severity]
            if sev_issues:
                lines.append(f"\n{severity.upper()} ({len(sev_issues)} issues):")
                lines.append("-" * 80)
                for issue in sev_issues:
                    lines.append(f"\n{issue.filepath}:{issue.line}")
                    lines.append(f"  [{issue.rule_id}] {issue.description}")
                    if issue.snippet:
                        lines.append(f"    Code: {issue.snippet}")
                    if issue.recommendation:
                        lines.append(f"    Fix: {issue.recommendation}")

        lines.append("\n" + "=" * 80)
        lines.append("SUMMARY")
        lines.append("=" * 80)
        for severity in SecurityIssue.SEVERITIES:
            count = len([i for i in issues if i.severity == severity])
            if count > 0:
                lines.append(f"  {severity}: {count}")

        return "\n".join(lines)

    def should_block_commit(self, issues: List[SecurityIssue]) -> Tuple[bool, str]:
        critical = [i for i in issues if i.severity == 'critical']
        high = [i for i in issues if i.severity == 'high']
        if critical:
            return True, f"{len(critical)} critical issue(s) found"
        if high:
            return True, f"{len(high)} high severity issue(s) found"
        return False, "No blocking issues"


# Singleton instance
security_guardian = SecurityGuardian()
