# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| develop | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Payverse seriously. If you believe you have found a security vulnerability, please report it to us as detailed below.

### How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please email your findings to: **security@payverse.com**

Or contact directly: **Aamir Ali** (project maintainer)

### What to Include

When reporting a security issue, please include:

1. **Description**: Clear description of the vulnerability
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Impact**: Potential impact of the vulnerability
4. **Environment**: Version, OS, deployment details
5. **Proof of Concept**: If possible, provide a minimal proof of concept

### Response Timeline

- **Initial Response**: We'll acknowledge receipt within 48 hours
- **Status Update**: We'll provide an update within 7 days
- **Fix Timeline**: Depends on severity, but we aim to address critical issues within 30 days

### Severity Classification

**Critical**: Remote code execution, SQL injection, authentication bypass
**High**: Information disclosure, privilege escalation
**Medium**: DoS, missing security headers
**Low**: Minor information leaks, security configuration issues

### Security Best Practices

Before deploying Payverse, ensure:

1. **Environment Variables**: All secrets stored in `.env` file (not committed to git)
2. **HTTPS**: All external communication over TLS
3. **Authentication**: Use strong passwords and enable 2FA where available
4. **Network**: Firewall rules restrict database and admin access
5. **Updates**: Regularly update dependencies to patch vulnerabilities
6. **Monitoring**: Set up audit logging and regular security scans

### git Security

We enforce strict Git practices:

- **Branch Protection**: `main` branch protected, requires PR reviews and passing CI
- **Pre-commit Hooks**: Security agent scans code for secrets and vulnerabilities
- **Pre-push Hooks**: Formatting, type-checking, and tests must pass
- **Commit Signing**: Optional but recommended for production deployments
- **Secret Scanning**: GitHub's secret scanning enabled (configurable in settings)

### Code of Conduct

Security researchers are expected to:

- Follow responsible disclosure
- Not exploit discovered vulnerabilities
- Not disclose publicly until a fix is available
- Only interact with systems they own or have explicit permission to test

We appreciate responsible disclosure and may offer recognition for valid security findings.
