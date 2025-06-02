# Note: Cursor Automation & Enforcement (Branch Policy, AI Best Practices)

## How Automation Will Work (If Implemented)

1. **User rules/preferences** in Cursor will act as the primary enforcement point for all AI and user actions in the IDE. If a rule is violated (e.g., attempt to change develop directly), Cursor can warn, block, or require justification.

2. **.cursor/rules/** will store machine-readable and human-readable enforcement rules (branch_policy.mdc, ai_best_practices.mdc, etc.).
   - AI and CLI tools can parse these files to check compliance before allowing changes, merges, or session switches.
   - External scripts (pre-commit hooks, CI/CD, custom CLI) can use these rules for automated checks.

3. **Session discipline**: All substantial work must be done in a dedicated branch and session. If a user or AI tries to change anything outside of a session, the system will:
   - Warn the user (in the UI or CLI)
   - Log the attempt (if possible)
   - Block the action or require explicit override/justification

4. **Logging**: All key actions, errors, and mode switches are logged in event_log/meta-log. If work is done outside a session, AI must warn the user and explain the risks (loss of traceability, audit, reproducibility).

5. **Advice and hypotheses**: AI will always provide objective advice, and will clearly mark any suggestions that are not implemented or not fixed in the code/rules/docs.

6. **Best practices and onboarding**: All new rules and best practices are added to .cursor/rules/ and referenced in onboarding docs. This ensures new team members and AI always have a single source of truth.

## Limitations (Current State)
- If you do not use sessions/branches for all work, enforcement and logging will be incomplete.
- Cursor IDE and AI currently do not enforce all rules automatically — some discipline is required from the user.
- Full automation (blocking, warnings, pre-commit checks) requires integration with CLI tools, git hooks, or custom plugins.

## Recommendation
- Use sessions and branches for all substantial work.
- Keep user rules and .cursor/rules/ in sync and up to date.
- Gradually automate enforcement via CLI, pre-commit, or Cursor plugins.
- Regularly review logs and update best practices as the workflow evolves. 