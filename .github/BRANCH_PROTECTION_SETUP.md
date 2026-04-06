# GitHub Branch Protection Setup

This guide explains how to set up branch protection rules on GitHub to enforce our Git workflow.

## Why Branch Protection?

Branch protection ensures:
- No direct pushes to `main` (all changes via PR)
- All PRs require review
- CI/CD checks must pass before merge
- Maintains code quality and prevents accidental breaks

## Setup Instructions

### 1. Go to Repository Settings

1. Navigate to your GitHub repository: https://github.com/Aamirali7596/Payverse
2. Click **Settings** tab
3. Click **Branches** in the left sidebar
4. Click **Add rule** under "Branch protection rules"

### 2. Configure Protection for `main` Branch

**Branch name pattern:**
```
main
```

**Enable these protections:**

- [x] **Require a pull request before merging**
  - Require approvals: `1`
  - Dismiss stale PRs when new commits are pushed: ✅
  - Require review from code owners: ✅
  - Allow specific users to bypass: (leave empty for now)

- [x] **Require status checks to pass before merging**
  - Require branches to be up to date before merging: ✅
  - Add status checks:
    - `ci / test (ubuntu-latest)` or similar
    - `security`
    - `docker` (if using CI/CD)
    - Add any other checks from `.github/workflows/`

- [x] **Require linear history** (prevents merge commits)
  - Use this to enforce clean, linear history with rebase

- [x] **Require signed commits** (optional, recommended for production)
  - Enforces GPG signature on commits

- [x] **Do not allow bypassing** (for required checks)

- [x] **Restrict pushes**
  - Add users who can push directly: (typically none)
  - Allow force pushes: ❌ (Never!)
  - Allow deletions: ❌

- [x] **Restrict deletions** (Already covered above)

### 3. Save Rule

Click **Create** or **Save changes**

## Protected Branches

We recommend protecting these branches:

| Branch | Purpose | Required Reviews | Required Checks |
|--------|---------|------------------|-----------------|
| `main` | Production-ready code | 1 (code owner) | All CI checks |
| `develop` | Integration branch | 1 (optional) | All CI checks |
| `release/*` | Release candidates | 2 (senior devs) | All CI checks |

## What Happens Next?

After branch protection is enabled:

1. **Direct pushes to `main` will be rejected**
   ```bash
   # This will fail:
   git push origin main

   # Instead, use:
   git checkout -b feature/new-feature
   # make changes, commit, push
   # open PR on GitHub
   ```

2. **All PRs require at least 1 approval** from code owners (configured in `.github/CODEOWNERS`)

3. **All CI checks must pass** before merge button is enabled

4. **Squash and merge** is recommended to keep history clean

## Additional Settings (Optional)

### 1. Require Conversations Before Merge

In PR settings, enable:
- "Require conversation resolution before merging"
  - Ensures all review comments are addressed or marked as resolved

### 2. Auto-Delete Branches

Enable:
- "Automatically delete head branches after merge"
  - Clean up feature branches automatically

### 3. Required Pull Request Reviews

Configure:
- Dismiss stale PRs when new commits pushed ✅
- Require review from code owners ✅
- Require last pusher's review: ❌ (Useful for small teams)
- Allow specific users to bypass: None

## Branch Protection Status

After setup, branches will show:
- 🔒 (lock icon) - Protected
- ✅ - Checks passed
- ❌ - Checks failed
- ⏳ - Checks in progress

## Need to Bypass?

Only in emergencies:

1. For critical production hotfixes, you can temporarily:
   - Add your user to "Allow specific users to bypass"
   - Merge directly to `main` with `--no-verify`
   - Remove protection after merge

2. Document any bypass in `CHANGELOG.md`

## Troubleshooting

**"Required status check is missing"**
- GitHub hasn't detected a workflow yet. Push a commit to trigger CI, then revisit rule to select the check.

**"You're not allowed to push to this branch"**
- You're trying to push directly. Create a PR instead.

**"This branch has conflicts that must be resolved"**
- Rebase your feature branch onto latest main:
  ```bash
  git checkout feature/branch
  git fetch origin
  git rebase origin/main
  ```

## Confirm Setup

After configuration:

1. Try pushing directly to `main` (should fail):
   ```bash
   git checkout main
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test"
   git push origin main
   ```
   Expected: ❌ ERROR: rejected

2. Create a feature branch and PR (should work):
   ```bash
   git checkout -b test-pr
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test"
   git push origin test-pr
   ```
   Expected: ✅ Creates branch, PR requires review

## Support

- If branch protection breaks workflow: Temporarily remove rule, fix issue, re-enable
- For CI failures: Check Action logs in **Actions** tab
- For permission issues: Ask repository admin to adjust
