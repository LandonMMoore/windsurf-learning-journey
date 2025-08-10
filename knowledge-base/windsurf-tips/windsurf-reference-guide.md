# Windsurf Tips & Tricks Reference Guide

*Quick reference for Windsurf mastery - searchable and organized for fast lookup*

## Keyboard Shortcuts

### Essential Shortcuts
- **Cmd + S** - Save current file (ALWAYS do this before committing!)
- **Cmd + Shift + P** - Open command palette (search for any action)
- **Tab** - Accept Windsurf's auto-complete suggestions
- **Cmd + /** - Toggle line comment
- **Cmd + Shift + /** - Toggle block comment

### Navigation
- **Cmd + P** - Quick file open
- **Cmd + Shift + E** - Focus on Explorer panel
- **Cmd + `** - Toggle terminal
- **Cmd + B** - Toggle sidebar visibility

### File Management
- **Cmd + N** - New file
- **Cmd + Shift + N** - New folder
- **Cmd + W** - Close current tab
- **Cmd + Shift + T** - Reopen closed tab

## Cascade AI Best Practices

### Effective Communication
- **Be specific about which file** you're working on
- **Provide context** - tell Cascade what you're trying to achieve
- **Ask for explanations** when you don't understand something
- **Request step-by-step guidance** for complex tasks

### Getting Better Results
- **Use descriptive language** - "Create a professional PRD template" vs "Make a document"
- **Ask for alternatives** - "Show me 2-3 ways to organize this"
- **Request examples** - "Include an example of how to use this"
- **Be clear about format preferences** - "Use markdown format" or "Make it a table"

### Conversation Tips
- **Start conversations with your goal** - "I want to create a project structure for..."
- **Ask follow-up questions** - Don't hesitate to dig deeper
- **Request modifications** - "Can you make this more concise?" or "Add more detail here"
- **Save important conversations** - Copy useful responses to your knowledge base

## File Management Tips

### File Organization
- **Use clear, descriptive filenames** - `project-requirements.md` not `doc1.md`
- **Include dates when relevant** - `2025-01-10-meeting-notes.md`
- **Group related files in folders** - Keep projects organized
- **Use consistent naming conventions** - Pick a style and stick to it

### File Extensions Matter
- **.md** - Markdown files (great for documentation)
- **.txt** - Plain text files (simple notes)
- **.py** - Python files (code)
- **.html** - Web pages
- **.json** - Data files

### Visual Cues
- **Dot (•) in tab** = Unsaved changes
- **Modified files** appear in Source Control panel
- **Preview mode** shows formatted markdown
- **Diff view** shows before/after changes in red/green

## Source Control Workflow

### Git Setup (One-time)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Daily Git Workflow
1. **Make changes** to your files
2. **Save files** (Cmd + S) - Critical step!
3. **Stage changes** - Click + next to files in Source Control
4. **Write commit message** - Be descriptive
5. **Commit** - Click checkmark or Cmd + Enter

### Commit Message Best Practices
- **Use present tense** - "Add new feature" not "Added new feature"
- **Be descriptive** - "Create PRD template with voice notes section"
- **Keep first line under 50 characters**
- **Add details in body if needed**

### Git Commands (Terminal)
```bash
git status          # See what's changed
git add .           # Stage all changes
git commit -m "message"  # Commit with message
git log --oneline   # See commit history
git diff            # See changes
```

## Common Issues & Solutions

### File Not Appearing in Explorer
**Problem**: Created a file but don't see it in the left panel
**Solution**: Make sure you saved the file (Cmd + S)

### Can't Commit Changes
**Problem**: Commit button is grayed out
**Solution**: 
1. Make sure files are saved
2. Stage the changes (click + in Source Control)
3. Write a commit message

### COMMIT_EDITMSG Editor
**Problem**: Terminal opened a text editor for commit message
**Solution**: 
1. Type your commit message
2. Press Esc, then type `:wq` and press Enter
3. Or use Windsurf's Source Control panel instead

### Cascade Not Understanding Context
**Problem**: Cascade gives generic responses
**Solution**: 
1. Tell Cascade which file you're working on
2. Provide more context about your goal
3. Be specific about what you want

### Lost Work
**Problem**: Accidentally closed a file or lost changes
**Solution**: 
1. Check Recent files (Cmd + P)
2. Look in Source Control for uncommitted changes
3. Use Git history if you committed earlier

### Preview Not Working
**Problem**: Markdown preview not showing formatted version
**Solution**: 
1. Make sure file has .md extension
2. Click the preview icon in the editor
3. Use Cmd + Shift + V for preview

## Pro Tips

### Productivity Hacks
- **Use auto-complete** - Let Windsurf suggest as you type
- **Preview markdown** - Always check formatting
- **Commit frequently** - Small, regular commits are better
- **Name files clearly** - Future you will thank you
- **Use the command palette** - Cmd + Shift + P for everything

### Organization Strategies
- **Create folder structures first** - Plan before you build
- **Use README files** - Document what each folder contains
- **Keep templates** - Save reusable formats
- **Regular cleanup** - Delete files you no longer need

### Learning Approach
- **Experiment safely** - Git lets you undo anything
- **Ask Cascade questions** - It's there to help
- **Document what you learn** - Build your knowledge base
- **Practice regularly** - Skills improve with use

## Quick Troubleshooting Checklist

When something isn't working:
1. ✅ Did you save the file? (Cmd + S)
2. ✅ Is the file extension correct?
3. ✅ Are you in the right folder?
4. ✅ Did you provide enough context to Cascade?
5. ✅ Check the Source Control panel for issues
6. ✅ Try the command palette (Cmd + Shift + P)

## Advanced Features to Explore

### Coming Up in Your Learning Journey
- **GitHub integration** - Remote repositories
- **Extensions** - Additional functionality
- **Themes** - Customize appearance
- **Multi-cursor editing** - Edit multiple lines at once
- **Find and replace** - Bulk text changes
- **Terminal integration** - Command line access

---

*Last Updated: After Week 1 completion | Keep this guide updated as you learn new tricks!*
