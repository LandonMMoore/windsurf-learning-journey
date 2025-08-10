# Git Commands Reference Guide

*Comprehensive Git reference for PMs learning version control*

## Quick Command Index

| Command | Purpose | Example |
|---------|---------|---------|
| `git init` | Initialize repository | `git init` |
| `git status` | Check repository status | `git status` |
| `git add` | Stage changes | `git add .` |
| `git commit` | Save changes | `git commit -m "message"` |
| `git log` | View commit history | `git log --oneline` |
| `git diff` | See changes | `git diff` |
| `git clone` | Copy remote repository | `git clone <url>` |
| `git push` | Upload to remote | `git push origin main` |
| `git pull` | Download from remote | `git pull origin main` |

## Essential Daily Commands

### Check Status
```bash
git status
# Shows: modified files, staged changes, untracked files
```

### Stage Changes
```bash
git add filename.md          # Stage specific file
git add .                    # Stage all changes
git add *.md                 # Stage all markdown files
```

### Commit Changes
```bash
git commit -m "Add new feature"           # Commit with message
git commit -m "Fix bug" -m "Details..."  # Commit with description
git commit --amend                        # Modify last commit
```

### View History
```bash
git log                      # Full commit history
git log --oneline           # Condensed one-line format
git log --graph             # Visual branch representation
git log -n 5                # Show last 5 commits
```

## Repository Setup

### Initialize New Repository
```bash
git init                     # Create new Git repository
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Clone Existing Repository
```bash
git clone https://github.com/username/repo.git
git clone <url> foldername   # Clone into specific folder
```

## Working with Changes

### See What Changed
```bash
git diff                     # Unstaged changes
git diff --staged           # Staged changes
git diff HEAD~1             # Compare with previous commit
git diff filename.md        # Changes in specific file
```

### Undo Changes
```bash
git checkout filename.md     # Discard unstaged changes
git reset filename.md        # Unstage file
git reset --soft HEAD~1     # Undo last commit (keep changes)
git reset --hard HEAD~1     # Undo last commit (lose changes)
```

## Remote Repository Commands

### Connect to Remote
```bash
git remote add origin https://github.com/username/repo.git
git remote -v               # View remote connections
git remote remove origin    # Remove remote connection
```

### Push and Pull
```bash
git push origin main         # Upload changes to remote
git push -u origin main      # Set upstream and push
git pull origin main         # Download changes from remote
git fetch origin            # Download without merging
```

## Branching (Advanced)

### Create and Switch Branches
```bash
git branch feature-name      # Create new branch
git checkout feature-name    # Switch to branch
git checkout -b feature-name # Create and switch in one command
git branch -d feature-name   # Delete branch
```

### Merge Branches
```bash
git checkout main           # Switch to main branch
git merge feature-name      # Merge feature branch into main
```

## Configuration

### User Setup
```bash
git config --global user.name "Landon Moore"
git config --global user.email "landonmoore913@gmail.com"
git config --global init.defaultBranch main
```

### View Configuration
```bash
git config --list           # Show all configuration
git config user.name        # Show specific setting
```

## Commit Message Best Practices

### Format
```
Type: Brief description (50 chars max)

Longer explanation if needed (wrap at 72 chars)
- Bullet points for details
- Reference issues: Fixes #123
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Formatting changes
- **refactor**: Code restructuring
- **test**: Adding tests
- **chore**: Maintenance tasks

### Examples
```bash
git commit -m "feat: Add user authentication system"
git commit -m "fix: Resolve login button alignment issue"
git commit -m "docs: Update README with setup instructions"
git commit -m "chore: Clean up unused files"
```

## Common Workflows

### Daily Development Workflow
1. `git status` - Check current state
2. `git add .` - Stage changes
3. `git commit -m "message"` - Commit changes
4. `git push origin main` - Upload to remote

### Starting New Feature
1. `git checkout main` - Switch to main branch
2. `git pull origin main` - Get latest changes
3. `git checkout -b feature-name` - Create feature branch
4. Make changes and commit
5. `git push origin feature-name` - Push feature branch

## Troubleshooting

### Common Issues

**"Nothing to commit"**
- Solution: Make sure files are saved and use `git add .`

**"Please tell me who you are"**
- Solution: Set up user configuration (see Configuration section)

**"Repository not found"**
- Solution: Check remote URL with `git remote -v`

**Merge conflicts**
- Solution: Edit conflicted files, then `git add .` and `git commit`

**Accidentally committed wrong files**
- Solution: Use `git reset --soft HEAD~1` to undo last commit

### COMMIT_EDITMSG Editor
If Git opens a text editor for commit messages:
1. Type your commit message
2. Press `Esc`
3. Type `:wq` and press `Enter`
4. Or use `git commit -m "message"` to avoid editor

## Git Aliases (Time Savers)

Add to your Git configuration:
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm commit
git config --global alias.lg "log --oneline --graph"
```

Then use:
- `git st` instead of `git status`
- `git co main` instead of `git checkout main`
- `git lg` for pretty log display

## Integration with Windsurf

### Using Source Control Panel
- **View changes**: Modified files appear in Source Control panel
- **Stage files**: Click `+` next to filename
- **Commit**: Write message and click checkmark
- **View diff**: Click filename to see changes

### Best Practices for PMs
- **Commit frequently**: Small, logical changes
- **Write clear messages**: Future you will thank you
- **Use .gitignore**: Keep repository clean
- **Review before committing**: Check what you're committing
- **Pull before pushing**: Stay in sync with team

## Next Steps

After mastering these commands:
1. **Connect to GitHub**: Set up remote repository
2. **Learn collaboration**: Pull requests and code reviews
3. **Explore branching**: Feature branches and Git Flow
4. **Advanced features**: Rebasing, cherry-picking, hooks

---

*Reference guide created during Week 2 knowledge base building*
