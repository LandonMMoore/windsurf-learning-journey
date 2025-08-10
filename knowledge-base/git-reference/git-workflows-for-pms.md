# Git Workflows for Product Managers

*Practical Git workflows tailored for PM work and documentation management*

## PM-Specific Git Workflows

### Daily Documentation Workflow
Perfect for maintaining PRDs, meeting notes, and project documentation.

```bash
# Morning routine
git status                    # Check what changed overnight
git pull origin main         # Get latest team updates

# During the day
git add filename.md          # Stage specific document
git commit -m "Update PRD with stakeholder feedback"
git push origin main         # Share updates with team

# End of day
git status                   # Final check
git add .                    # Stage all changes
git commit -m "Daily updates: meeting notes and status"
git push origin main         # Sync everything
```

### Project Milestone Workflow
For major project phases and deliverables.

```bash
# Starting new milestone
git checkout -b milestone-v2.0
# Work on milestone documents
git add .
git commit -m "feat: Complete Phase 2 requirements documentation"
git push origin milestone-v2.0

# When milestone complete
git checkout main
git merge milestone-v2.0
git push origin main
git branch -d milestone-v2.0  # Clean up
```

### Stakeholder Review Workflow
Managing document reviews and feedback incorporation.

```bash
# Before sending for review
git add .
git commit -m "docs: Prepare PRD v1.0 for stakeholder review"
git tag v1.0-review          # Mark review version
git push origin main --tags

# After receiving feedback
git add .
git commit -m "docs: Incorporate stakeholder feedback from review"
git commit -m "- Updated success metrics per CEO feedback
- Clarified technical requirements per engineering
- Added timeline details per project sponsor"
```

## Version Control for PM Documents

### PRD Version Management
```bash
# Major PRD updates
git commit -m "feat: Add new user authentication requirements"

# Minor PRD updates  
git commit -m "docs: Clarify acceptance criteria for login flow"

# PRD fixes
git commit -m "fix: Correct user story priority in backlog section"
```

### Meeting Notes Workflow
```bash
# Before meeting
git add meeting-prep-notes.md
git commit -m "prep: Add agenda and questions for stakeholder meeting"

# After meeting
git add meeting-notes-2025-01-10.md
git commit -m "docs: Capture decisions from stakeholder alignment meeting"
```

### Status Report Workflow
```bash
# Weekly status updates
git add weekly-status.md
git commit -m "status: Week 2 progress update - GitHub integration complete"

# Monthly reports
git add monthly-report-jan.md  
git commit -m "report: January milestone achievements and February goals"
```

## Collaboration Patterns

### Working with Engineering Teams
```bash
# Sync with engineering changes
git pull origin main         # Get latest technical updates

# Add PM perspective to technical docs
git add technical-requirements.md
git commit -m "docs: Add PM context to technical requirements"
```

### Multi-stakeholder Document Management
```bash
# Create stakeholder-specific branches for sensitive docs
git checkout -b executive-summary
# Work on executive version
git commit -m "docs: Create executive summary of technical proposal"

# Merge back when approved
git checkout main
git merge executive-summary
```

## PM Git Best Practices

### Commit Message Templates for PMs

**Requirements Changes**
```bash
git commit -m "req: Update user story acceptance criteria"
git commit -m "req: Add new feature requirement for mobile app"
```

**Documentation Updates**
```bash
git commit -m "docs: Update API documentation with new endpoints"
git commit -m "docs: Clarify user flow in onboarding guide"
```

**Process Improvements**
```bash
git commit -m "process: Add new sprint planning template"
git commit -m "process: Update stakeholder communication workflow"
```

**Decision Tracking**
```bash
git commit -m "decision: Approve move to microservices architecture"
git commit -m "decision: Delay feature X to focus on core functionality"
```

### File Organization for PMs
```
project-repo/
├── requirements/
│   ├── prd-v1.0.md
│   ├── user-stories.md
│   └── acceptance-criteria.md
├── meetings/
│   ├── stakeholder-meetings/
│   └── team-standups/
├── status-reports/
│   ├── weekly/
│   └── monthly/
└── decisions/
    └── decision-log.md
```

## Integration with PM Tools

### ClickUp Integration Preparation
```bash
# Prepare for automation
git add clickup-integration-plan.md
git commit -m "plan: Document ClickUp-Git integration requirements"
```

### Stakeholder Communication
```bash
# Before stakeholder updates
git log --oneline --since="1 week ago"  # Review recent changes
git add stakeholder-update.md
git commit -m "comm: Prepare weekly stakeholder update with progress"
```

## Troubleshooting for PMs

### Common PM Git Scenarios

**"I accidentally committed sensitive information"**
```bash
git reset --soft HEAD~1      # Undo commit, keep changes
# Edit file to remove sensitive info
git add filename.md
git commit -m "docs: Update document with public information only"
```

**"I need to share a document but it's not ready"**
```bash
git stash                    # Temporarily save changes
git checkout -b draft-review # Create draft branch
# Work on shareable version
git commit -m "draft: Prepare document for initial review"
```

**"Multiple people edited the same document"**
```bash
git pull origin main         # Get latest changes
# Git will show conflicts in the file
# Edit file to resolve conflicts
git add filename.md
git commit -m "resolve: Merge stakeholder feedback with latest updates"
```

## Advanced PM Workflows

### Release Planning with Git
```bash
# Create release branch
git checkout -b release-v2.0
git add release-notes.md
git commit -m "release: Prepare v2.0 release documentation"

# Tag release
git tag v2.0.0
git push origin main --tags
```

### A/B Test Documentation
```bash
git checkout -b experiment-new-onboarding
git add experiment-plan.md
git commit -m "experiment: Document new user onboarding A/B test"
```

### Retrospective Documentation
```bash
git add retrospective-sprint-5.md
git commit -m "retro: Capture lessons learned from sprint 5"
git commit -m "- Team velocity improved 20%
- Need better stakeholder communication
- Technical debt slowing feature development"
```

## Git for Remote PM Work

### Async Collaboration
```bash
# Leave clear context for team
git commit -m "wip: Draft requirements - need engineering review"
git commit -m "question: Should we prioritize mobile or web first?"
```

### Time Zone Coordination
```bash
# End of day handoff
git add daily-handoff.md
git commit -m "handoff: Status update for APAC team review"
git push origin main
```

## Measuring Success with Git

### Track Documentation Quality
```bash
git log --grep="docs:" --oneline  # See all documentation commits
git log --since="1 month ago" --author="your-name"  # Your contributions
```

### Monitor Team Collaboration
```bash
git log --graph --oneline        # Visualize team collaboration
git shortlog -sn                 # See contributor statistics
```

---

*Workflow guide created for PM-specific Git usage patterns*
