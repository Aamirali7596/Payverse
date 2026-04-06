"""
Pre-Commit Agent - Security & Governance Review

Runs automatically before each git commit.
Uses Security Guardian skill to scan staged files.
Blocks commit if critical/high issues found.

Usage:
  python -m agents.pre_commit_agent
  (called automatically by git pre-commit hook)
"""

import sys
import subprocess
from pathlib import Path
from skills.security_guardian import SecurityGuardian


def main():
    """Main entrypoint for pre-commit hook"""
    guardian = SecurityGuardian()

    # Get staged files
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True
        )
        staged_files = [f for f in result.stdout.strip().split('\n') if f]
    except Exception as e:
        print(f"Error getting staged files: {e}")
        sys.exit(1)

    if not staged_files:
        print("No files staged for commit.")
        sys.exit(0)

    # Scan only relevant file types
    files_to_scan = [f for f in staged_files if f.endswith(('.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yml', '.yaml'))]

    if not files_to_scan:
        sys.exit(0)

    print(f"\n🔒 Pre-Commit Security Scan")
    print(f"Scanning {len(files_to_scan)} files...\n")

    issues = []
    for filepath in files_to_scan:
        file_issues = guardian.scan_file(filepath)
        if file_issues:
            issues.extend(file_issues)

    # Generate report
    report = guardian.generate_report(issues, format='text')
    print(report)

    # Decision
    should_block, reason = guardian.should_block_commit(issues)
    if should_block:
        print(f"\n❌ COMMIT BLOCKED: {reason}")
        print("   Fix security issues before committing.")
        print("   To bypass (not recommended): git commit --no-verify\n")
        sys.exit(1)
    else:
        print("\n✅ Security scan passed - proceeding with commit\n")
        sys.exit(0)


if __name__ == '__main__':
    main()
