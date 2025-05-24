# Security Guidelines for llmstruct

## Git Security Configuration

### Automatic Secret Detection

The project uses built-in Git mechanisms to prevent secret leakage:

#### 1. Pre-commit Hook (`.git/hooks/pre-commit`)
Automatically scans staged files for:
- API keys (xai-*, sk-*, ghp-*, etc.)
- Authentication tokens
- Password patterns
- Private key files
- Secret configuration files

#### 2. Commit Message Hook (`.git/hooks/commit-msg`)
Validates commit messages to prevent:
- Accidental inclusion of secrets in commit descriptions
- Too short or empty commit messages
- Suspicious patterns in commit text

#### 3. Enhanced .gitignore
Excludes sensitive files:
- Environment files (*.env, .env.*)
- API key files (*api_key*, *_token*)
- Private keys (*.key, *.pem)
- Secret configuration (secrets/, *_secret*)
- Hybrid logs with potential API keys

#### 4. Git Attributes
Configures special handling for:
- Secret files (marked with filter=secret)
- Binary files proper detection
- Documentation files exclusion from stats

## Best Practices

### For Developers

1. **Never commit secrets directly**
   ```bash
   # Use environment variables instead
   export GROK_API_KEY="your-key-here"
   export ANTHROPIC_API_KEY="your-key-here"
   ```

2. **Use local environment files**
   ```bash
   # Create .env.local (already in .gitignore)
   echo "GROK_API_KEY=xai-..." > .env.local
   ```

3. **Check your commits before pushing**
   ```bash
   # The pre-commit hook will automatically run, but you can test manually:
   git diff --cached | grep -i "api.*key\|secret\|token\|password"
   ```

4. **Use git-crypt for encrypted secrets** (optional)
   ```bash
   # Install git-crypt for team secret sharing
   sudo apt install git-crypt
   git-crypt init
   ```

### For CI/CD

1. **Use GitHub Secrets** for automation:
   - Repository Settings → Secrets and variables → Actions
   - Add secrets like `GROK_API_KEY`, `ANTHROPIC_API_KEY`

2. **Use environment variables in workflows**:
   ```yaml
   env:
     GROK_API_KEY: ${{ secrets.GROK_API_KEY }}
   ```

### For Production

1. **Use external secret management**:
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Secret Manager

2. **Rotate secrets regularly**
3. **Monitor for secret exposure** using tools like:
   - GitHub Advanced Security
   - GitLeaks
   - TruffleHog

## Recovery from Secret Exposure

If secrets are accidentally committed:

1. **Immediately rotate the exposed secret**
2. **Remove from Git history**:
   ```bash
   # For recent commits
   git reset --soft HEAD~1
   git reset HEAD .
   
   # For older commits (use with caution)
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/secret/file' \
     --prune-empty --tag-name-filter cat -- --all
   ```

3. **Force push after cleanup**:
   ```bash
   git push --force-with-lease origin main
   ```

4. **Verify removal**:
   ```bash
   git log --all --full-history -- path/to/secret/file
   ```

## Testing the Security Setup

Test the pre-commit hook:
```bash
# Create a test file with a fake secret
echo 'api_key = "xai-fake12345678901234567890123456789012345678901234567890123456789012"' > test_secret.py

# Try to commit it
git add test_secret.py
git commit -m "test: adding secret (should fail)"

# Clean up
rm test_secret.py
```

## Current Issues Found

The project logs contain exposed API keys in `docs/hybrid_log.md`. This file:
- Is now excluded from commits via .gitignore
- Should be cleaned from Git history
- Contains real Grok API keys that should be rotated

## Reporting Security Issues

For security vulnerabilities, contact: kpblcaoo@gmail.com

Do not create public GitHub issues for security problems.
