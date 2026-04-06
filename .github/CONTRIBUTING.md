# Contributing to Payverse

Thank you for contributing to Payverse! This document outlines our Git workflow and contribution process.

## Git Workflow

We follow the **GitHub Flow** branching model:

```
main (protected, always deployable)
  │
  ├── feature/user-auth      → PR → merge to main
  ├── fix/login-bug          → PR → merge to main
  └── docs/update-readme     → PR → merge to main
```

### Rules

1. **`main` branch is always deployable** - Never push directly to `main`
2. **Create feature branches** from `main` for each change
3. **Open Pull Request** when ready for review
4. **All checks must pass** (CI, security, formatting, tests)
5. **At least one code owner review** required
6. **Merge with squash** to keep history clean
7. **Deploy immediately** after merge

## Branch Naming Convention

Use clear, descriptive branch names:

- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/update-area` - Documentation changes
- `chore/task-name` - Maintenance tasks
- `refactor/component-name` - Code refactoring
- `hotfix/critical-issue` - Emergency production fixes (rare)

Examples:
- `feature/user-authentication`
- `fix/payment-timeout-handling`
- `docs/api-endpoint-documentation`

## Commit Messages

We use **Conventional Commits** format:

```
<type>(<scope>): <subject>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `revert`: Revert previous commit

### Examples

```
fix(auth): resolve redirect loop after login
feat(api): add user profile endpoint
docs(readme): update installation instructions
test(services): add unit tests for payment service
```

### Commit Message Template

We provide a commit template. To use it:

```bash
git config commit.template .gitmessage
```

When you run `git commit`, the template will open with guidance.

## Pull Request Process

### Before Creating a PR

1. **Update main branch**:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Resolve any conflicts** and ensure tests pass:
   ```bash
   pytest tests/ -v
   black --check app/
   flake8 app/
   mypy app/
   ```

3. **Self-review your code**:
   - Check for debug statements (`print()`, `console.log`)
   - Remove commented-out code
   - Ensure proper error handling
   - Verify documentation is updated

### Creating a PR

1. Push your branch:
   ```bash
   git push origin your-feature-branch
   ```

2. Open a PR on GitHub with:
   - **Clear title** following commit message convention
   - **Complete description** using our PR template
   - **Related issues** linked (Closes #123)
   - **Screenshots** for UI changes
   - **Test instructions** for reviewers

3. Set PR labels and assign reviewers (auto-assigned via CODEOWNERS)

### PR Review

**For Authors**:
- Be responsive to review comments
- Make requested changes or discuss alternatives
- Squash commits before merging if history is messy
- Keep PRs small (ideally <500 lines)

**For Reviewers**:
- Check if the code solves the stated problem
- Look for edge cases and potential bugs
- Ensure tests are sufficient
- Watch for security concerns
- Verify commit messages are clear

### Merge Process

When approved:

1. **Squash and merge** to keep history clean
2. **Delete the feature branch** (both locally and remotely)
3. **Verify CI/CD** completes successfully
4. **Deploy** (if applicable)

## Git Hooks

We provide pre-commit and pre-push hooks for safety:

```bash
# Install hooks
./scripts/setup-hooks.sh
```

### What the Hooks Do

- **pre-commit**: Runs Security Guardian agent to check for:
  - Hardcoded secrets
  - Suspicious patterns
  - Common vulnerabilities
  - Large files accidentally staged

- **pre-push**: Runs when pushing to protected branches:
  - Code formatting (black)
  - Type checking (mypy)
  - Linting (flake8)
  - Full test suite
  - Secret scanning

### Bypassing Hooks

Avoid bypassing hooks unless absolutely necessary:

```bash
git commit --no-verify   # Skip pre-commit
git push --no-verify     # Skip pre-push
```

## Undoing Mistakes

### Uncommitted Changes
```bash
git checkout -- file.py          # Discard changes in file
git reset --hard HEAD           # Discard all uncommitted changes
```

### Last Commit (Not Pushed)
```bash
git reset --soft HEAD~1         # Undo commit, keep changes
git commit --amend              # Edit commit message
git reset --hard HEAD~1         # Discard commit and changes
```

### Last Commit (Pushed)
```bash
git revert HEAD                 # Create new commit that undoes changes
git push origin branch-name
```

### Unpushed Branch
```bash
git checkout main
git pull origin main
git branch -D feature/bad-branch   # Delete local branch
git push origin --delete feature/bad-branch  # Delete remote branch
```

## Rebase vs Merge

### Use Rebase for:
- Updating your feature branch with latest `main`
- Cleaning up local commits before creating PR
- Single-developer branches

```bash
git checkout feature/my-branch
git fetch origin
git rebase origin/main
```

### Use Merge for:
- Merging feature branches into `main`
- Public branches others may have based work on
- Preserving exact history

## Conflict Resolution

### Prevent Conflicts
- Keep branches small and short-lived
- Rebase frequently onto `main`
- Communicate about shared files
- Review and merge PRs promptly

### Resolve Conflicts

1. Before merging, check for conflicts:
   ```bash
   git checkout main
   git merge feature/branch --no-commit --no-ff
   ```

2. If conflicts exist:
   ```bash
   git status                    # List conflicted files
   git mergetool                 # Use visual merge tool (if configured)
   # OR manually edit files and remove conflict markers (<<<<<<<, =======, >>>>>>>)
   ```

3. After resolving:
   ```bash
   git add <resolved-file>
   git commit -m "fix: resolve merge conflicts"
   ```

## Stashing Work

```bash
git stash push -m "WIP: description"   # Save changes
git stash list                         # List stashes
git stash pop                          # Apply and remove latest stash
git stash apply stash@{2}             # Apply specific stash
git stash drop stash@{0}               # Remove stash
```

## Common Aliases

Add to `~/.gitconfig`:

```ini
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --all
    amend = commit --amend --no-edit
    undo = reset --soft HEAD~1
    contributors = shortlog -sn
    save = stash push -m
    apply = stash pop
```

## Need Help?

- Check existing PRs and issues for patterns
- Review the git-workflow skill documentation
- Ask the team in Slack/Teams
- Read: [Pro Git Book](https://git-scm.com/book/en/v2)

## Key Resources

- Branch Strategy: GitHub Flow
- Commit Style: Conventional Commits
- CI/CD: GitHub Actions (.github/workflows/ci.yml)
- Branch Protection: Enabled in GitHub repository settings
- CODEOWNERS: `.github/CODEOWNERS`
- PR Template: `.github/PULL_REQUEST_TEMPLATE.md`
- Issue Templates: `.github/ISSUE_TEMPLATE/`

---

Happy coding! 🚀
