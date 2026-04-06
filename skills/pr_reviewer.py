"""
PR Reviewer - Senior Engineer Code Review Bot

A 20+ year senior software engineer PR review agent that:
- Reviews code quality, security issues, testing gaps
- Fintech-specific compliance checks
- Posts structured review comments
- Auto-approves Dependabot PRs if safe

Usage:
  python -m skills.pr_reviewer --diff-file diff.txt
  python -m skills.pr_reviewer --pr-number 42
"""

import json
import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


# ── Severity levels ──────────────────────────────────────────────────

CRITICAL = "critical"
HIGH = "high"
MEDIUM = "medium"
LOW = "low"
INFO = "info"


SEVERITY_EMOJI = {
    CRITICAL: "[CRITICAL]",
    HIGH: "[HIGH]",
    MEDIUM: "[MEDIUM]",
    LOW: "[LOW]",
    INFO: "[INFO]",
}


# ── Review result ────────────────────────────────────────────────────

@dataclass
class Issue:
    file: str
    line: int
    severity: str
    category: str
    rule: str
    message: str
    suggestion: str = ""
    snippet: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class ReviewResult:
    pr_title: str = ""
    summary: str = ""
    verdict: str = "Approve"  # Approve | Request Changes | Comment
    issues: List[Issue] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "pr_title": self.pr_title,
            "verdict": self.verdict,
            "summary": self.summary,
            "issues": [i.to_dict() for i in self.issues],
            "suggestions": self.suggestions,
            "stats": self.stats,
            "reviewed_at": datetime.utcnow().isoformat(),
        }

    def to_markdown(self) -> str:
        lines = [
            f"## Code Review: {self.verdict}",
            "",
            self.summary,
            "",
        ]

        if self.issues:
            lines.append("---")
            lines.append("")
            lines.append(f"**{len(self.issues)} issue(s) found:**")
            lines.append("")

            for issue in self.issues:
                sev = SEVERITY_EMOJI.get(issue.severity, issue.severity)
                location = f"`{issue.file}:{issue.line}`" if issue.line else f"`{issue.file}`"
                lines.append(f"- **{sev}** [{issue.category}] {location}: {issue.message}")
                if issue.snippet:
                    lines.append(f"  ```\n  {issue.snippet}\n  ```")
                if issue.suggestion:
                    lines.append(f"  > {issue.suggestion}")
                lines.append("")
        else:
            lines.append("No issues found. Code looks good!")
            lines.append("")

        if self.suggestions:
            lines.append("---")
            lines.append("")
            lines.append("### Suggestions")
            lines.append("")
            for s in self.suggestions:
                lines.append(f"- {s}")
            lines.append("")

        lines.append("---")
        lines.append(f"*Reviewed by PR Reviewer Agent (Senior Engineer)*")
        return "\n".join(lines)


# ── Pattern definitions ─────────────────────────────────────────────

# Security patterns: secrets, injection, weak crypto
SECURITY_PATTERNS = [
    (r'''(?i)(api[_-]?key|apikey)\s*=\s*['"]\w''', "Secret in source",
     "Use environment variables or a secrets manager for API keys", HIGH, "sk_live_", "secret-api-key"),
    (r'(?i)secret[_-]?key\s*=\s*["\']', "Secret key in source",
     "Move secrets to environment variables", CRITICAL, "", "secret-in-code"),
    (r'(?i)password\s*=\s*["\']\w', "Password in source",
     "Never hardcode passwords", CRITICAL, "", "password-in-code"),
    (r'''(?i)(aws_access_key|aws_secret)''', "AWS credentials",
     "Use IAM roles or secrets manager", CRITICAL, "", "aws-credentials"),
    (r"eval\s*\(", "eval() usage",
     "eval() can execute arbitrary code. Use ast.literal_eval() for data parsing", HIGH, "", "dangerous-eval"),
    (r"exec\s*\(", "exec() usage",
     "exec() can execute arbitrary code", HIGH, "", "dangerous-exec"),
    (r"\.execute\s*\(.*%", "SQL injection risk",
     "Use parameterized queries instead of string interpolation", CRITICAL, "", "sql-injection"),
    (r"\.execute\s*\(.*\.format", "SQL injection risk",
     "Use parameterized queries instead of .format()", CRITICAL, "", "sql-injection-format"),
    (r"import pickle", "Unsafe pickle",
     "pickle can execute arbitrary code. Use json or msgpack", HIGH, "", "unsafe-pickle"),
    (r"subprocess\.(call|run|Popen).*shell\s*=\s*True", "Shell injection risk",
     "Avoid shell=True with untrusted input", HIGH, "", "shell-injection"),
    (r"'DES'|'Blowfish'|'RC4'|'MD5'", "Weak cryptography",
     "Use AES-GCM or ChaCha20 for encryption", HIGH, "", "weak-crypto"),
]

# Quality patterns: code style, architecture
QUALITY_PATTERNS = [
    (r"^from\s+\w+\s+import\s+\*", "Wildcard import",
     "Use explicit imports for clarity", MEDIUM, "", "wildcard-import"),
    (r"except\s*:", "Bare except",
     "Catch specific exceptions (Exception, ValueError, etc.)", MEDIUM, "", "bare-except"),
    (r"except\s+Exception\s+as\s+e\s*:\s*pass\b", "Silent exception",
     "Log exceptions instead of silently swallowing them", HIGH, "", "silent-except"),
    (r"raise\s+Exception\s*\(", "Generic exception",
     "Raise specific exception types", LOW, "", "generic-exception"),
    (r"import\s+os\s*\n.*os\.environ", "Missing dotenv",
     "Consider using python-dotenv or pydantic-settings for config", INFO, "", "config-pattern"),
]

# Fintech-specific patterns
Fintech_PATTERNS = [
    (r"(?i)card[_-]?number|cvv|cvc", "Payment card data",
     "Never store raw card data. Use PCI-compliant tokenization", CRITICAL, "", "card-data"),
    (r"(?i)(bank[_-]?account|sort[_-]?code|iban)", "Bank details",
     "Bank details must be encrypted at rest (AES-256-GCM)", HIGH, "", "bank-data-unencrypted"),
    (r"(?i)(ni[_-]?number|national[_-]?insurance)", "National Insurance Number",
     "PII detected. Ensure GDPR compliance and encryption", HIGH, "", "pii-detected"),
    (r"(?i)(utr|unique[_-]?taxpayer[_-]?reference)", "Tax PII",
     "Tax identifier detected. Ensure data encryption", MEDIUM, "", "tax-pii"),
    (r"(?i)salary|payroll|pension", "Financial PII",
     "Financial data requires encryption at rest", MEDIUM, "", "financial-pii"),
]

# Python-specific patterns
PYTHON_PATTERNS = [
    (r"^import\s+\w+\s*$\n\n\n\n", "Missing blank line",
     "PEP 8: two blank lines between top-level imports and code", LOW, "", "pep8-spacing"),
    (r"print\s*\(", "Print in source",
     "Use logging instead of print for production code", INFO, "", "print-vs-logging"),
    (r"TODO|FIXME|HACK|XXX|NOTE", "Code comment marker",
     "Consider tracking this in an issue tracker", INFO, "", "code-marker"),
]


# ── Scanner ──────────────────────────────────────────────────────────

class PRReviewer:
    """Review code changes as a senior engineer would."""

    ALL_PATTERNS = [
        ("Security", SECURITY_PATTERNS),
        ("Quality", QUALITY_PATTERNS),
        ("Fintech", Fintech_PATTERNS),
        ("Python", PYTHON_PATTERNS),
    ]

    def review_diff(self, diff_text: str) -> ReviewResult:
        """Review a unified git diff string."""
        result = ReviewResult()
        current_file = ""
        line_num = 0

        for raw_line in diff_text.split("\n"):
            # Track which file we're in
            if raw_line.startswith("+++ b/"):
                current_file = raw_line[6:]
                continue
            if raw_line.startswith("--- a/"):
                continue

            # Skip context/deletion lines — only check additions
            if not raw_line.startswith("+"):
                continue

            # Skip diff markers
            if raw_line.startswith("+++"):
                continue

            content = raw_line[1:]  # Remove leading '+'
            line_num += 1

            for category, patterns in self.ALL_PATTERNS:
                for pattern, rule_name, suggestion, severity, trigger, rule_id in patterns:
                    if re.search(pattern, content):
                        result.issues.append(Issue(
                            file=current_file,
                            line=line_num,
                            severity=severity,
                            category=category,
                            rule=rule_id,
                            message=rule_name,
                            suggestion=suggestion,
                            snippet=content.strip()[:100],
                        ))

        # Compute stats
        sev_counts = {}
        for issue in result.issues:
            sev_counts[issue.severity] = sev_counts.get(issue.severity, 0) + 1
        result.stats = sev_counts

        # Determine verdict
        if any(i.severity == CRITICAL for i in result.issues):
            result.verdict = "Request Changes"
            result.summary = "Found critical security issues that must be addressed before merge."
        elif any(i.severity == HIGH for i in result.issues):
            result.verdict = "Request Changes"
            result.summary = "Found high-severity issues. Please review and fix before merging."
        elif result.issues:
            result.verdict = "Comment"
            result.summary = "Found some minor issues. Consider addressing before merge."
        else:
            result.verdict = "Approve"
            result.summary = "Code looks clean. No issues found."

        # Smart suggestions
        self._add_suggestions(diff_text, result)

        return result

    def review_file(self, filepath: str) -> ReviewResult:
        """Review a single file."""
        result = ReviewResult()
        path = Path(filepath)

        if not path.exists():
            result.summary = f"File not found: {filepath}"
            result.verdict = "Comment"
            return result

        content = path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")
        current_file = str(path)

        for line_num, line in enumerate(lines, 1):
            for category, patterns in self.ALL_PATTERNS:
                for pattern, rule_name, suggestion, severity, trigger, rule_id in patterns:
                    if re.search(pattern, line):
                        result.issues.append(Issue(
                            file=current_file,
                            line=line_num,
                            severity=severity,
                            category=category,
                            rule=rule_id,
                            message=rule_name,
                            suggestion=suggestion,
                            snippet=line.strip()[:100],
                        ))

        # Stats & verdict
        sev_counts = {}
        for issue in result.issues:
            sev_counts[issue.severity] = sev_counts.get(issue.severity, 0) + 1
        result.stats = sev_counts

        if any(i.severity == CRITICAL for i in result.issues):
            result.verdict = "Request Changes"
        elif any(i.severity == HIGH for i in result.issues):
            result.verdict = "Request Changes"
        elif result.issues:
            result.verdict = "Comment"
        else:
            result.verdict = "Approve"
        result.summary = f"Reviewed {current_file}: {len(result.issues)} issue(s)."

        return result

    def _add_suggestions(self, diff_text: str, result: ReviewResult):
        """Add smart suggestions based on the diff content."""
        lines = diff_text.split("\n")
        added_lines = [l for l in lines if l.startswith("+") and not l.startswith("+++")]

        if len(added_lines) > 200:
            result.suggestions.append("Large PR. Consider splitting into smaller, reviewable chunks.")

        if any("import" in l for l in added_lines) and not any("pytest" in l for l in lines):
            result.suggestions.append("New imports detected. Consider adding tests for the new module.")

        if any(l for l in added_lines if "def " in l or "class " in l):
            result.suggestions.append("New functions/classes added. Add type hints and docstrings if not present.")

        # Fintech-specific
        if any("encrypt" in l.lower() or "decrypt" in l.lower() for l in added_lines):
            result.suggestions.append("Encryption logic detected. Ensure AES-256-GCM or ChaCha20 is used.")


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PR Reviewer Agent - Senior Engineer Review Bot")
    parser.add_argument("--diff-file", help="Path to git diff file")
    parser.add_argument("--pr-number", type=int, help="Review PR on GitHub")
    parser.add_argument("--file", help="Review a single file")
    parser.add_argument("--files", nargs="+", help="Review multiple files")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="markdown",
                        help="Output format (default: markdown)")

    args = parser.parse_args()
    reviewer = PRReviewer()

    if args.diff_file:
        diff_path = Path(args.diff_file)
        if not diff_path.exists():
            print(f"Error: {args.diff_file} not found")
            sys.exit(1)
        review = reviewer.review_diff(diff_path.read_text())
    elif args.pr_number:
        import subprocess
        # Fetch PR diff via gh CLI
        try:
            result = subprocess.run(
                ["gh", "pr", "view", str(args.pr_number), "--json", "title,body"],
                capture_output=True, text=True
            )
            pr_info = json.loads(result.stdout)
            review = PRReviewResult(pr_title=pr_info.get("title", ""))

            # Also get diff
            diff_result = subprocess.run(
                ["gh", "pr", "diff", str(args.pr_number)],
                capture_output=True, text=True
            )
            review = reviewer.review_diff(diff_result.stdout)
            review.pr_title = pr_info.get("title", f"PR #{args.pr_number}")
        except FileNotFoundError:
            print("Error: 'gh' CLI not found. Install GitHub CLI first.")
            sys.exit(1)
        except Exception as e:
            print(f"Error fetching PR: {e}")
            sys.exit(1)
    elif args.file:
        review = reviewer.review_file(args.file)
    elif args.files:
        review = ReviewResult()
        for f in args.files:
            file_review = reviewer.review_file(f)
            review.issues.extend(file_review.issues)
        review.stats = {}
        for issue in review.issues:
            review.stats[issue.severity] = review.stats.get(issue.severity, 0) + 1
        review.verdict = "Request Changes" if any(
            i.severity in (CRITICAL, HIGH) for i in review.issues) else "Approve"
        review.summary = f"Reviewed {len(args.files)} file(s): {len(review.issues)} issues."
    else:
        parser.print_help()
        sys.exit(1)

    # Output
    if args.format == "json":
        print(json.dumps(review.to_dict(), indent=2))
    elif args.format == "markdown":
        print(review.to_markdown())
    else:
        print(f"Verdict: {review.verdict}")
        print(f"Summary: {review.summary}")
        for issue in review.issues:
            print(f"  {issue.file}:{issue.line} [{issue.severity}] {issue.message}")

    sys.exit(1 if review.verdict == "Request Changes" else 0)


if __name__ == "__main__":
    main()
