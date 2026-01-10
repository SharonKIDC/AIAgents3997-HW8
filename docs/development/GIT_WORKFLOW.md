# Git Workflow Documentation

## Branching Strategy

This project follows a structured multi-agent workflow with dedicated branches for each phase and agent execution.

### Branch Types

1. **Phase Branches**: `phase/{phase-name}-{timestamp}`
   - Created at the start of each phase (PreProject, TaskLoop, ResearchLoop, ReleaseGate)
   - All agent work for that phase is merged into the phase branch
   - Phase branch is merged to main at phase completion

2. **Agent Branches**: `agent/{phase}/{agent-id}-{timestamp}`
   - Created before each agent executes
   - Agent performs all work on this dedicated branch
   - Merged to phase branch after agent completes and passes gates

3. **Feature Branches**: `feature/{description}` (for manual development)

### Commit Strategy

**Minimum Commit Target**: 15 commits across project lifecycle

**Per Agent**: At least 1 commit per agent execution

**Commit Message Format**:
```
[{PHASE}] {agent-id}: {Brief summary}

Agent: {agent-id}
Purpose: {agent role/purpose}
Phase: {current phase}

Changes:
- Created: {list of created files}
- Modified: {list of modified files}

Documentation: .claude/agents/{agent-id}.md
```

### Merge Strategy

All merges use `--no-ff` (no fast-forward) to preserve history and maintain clear agent boundaries.

```bash
git merge --no-ff agent/{phase}/{agent-id}
```

### Workflow Visualization

View commit history with agent flow:
```bash
git log --graph --oneline --all --decorate
```

View commits per phase:
```bash
git log --grep="\[PreProject\]" --oneline
git log --grep="\[TaskLoop\]" --oneline
```

View agent-specific history:
```bash
git log --grep="Agent: repo-scaffolder" --oneline
```

### Quality Gates

Before each commit:
- [ ] pylint src/ --score=y (must be 10/10)
- [ ] black --check src/ tests/
- [ ] isort --check-only --profile black src/ tests/
- [ ] ruff check src/ tests/
- [ ] pytest tests/ (all tests pass)
- [ ] No temp files in git status

### Current Workflow State

Track progress via `.git-workflow-state.json`:
```bash
cat .git-workflow-state.json | jq
```

## Success Criteria

A well-managed workflow shows:
- 15+ commits on main branch
- Each agent has dedicated branch and merge commit
- Clear phase boundaries in commit history
- Structured commit messages throughout
- No direct commits to main (all via agent branches)
