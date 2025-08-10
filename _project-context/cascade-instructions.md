# Cascade AI Assistant Instructions

*Created: January 27, 2025*  
*Purpose: Guidelines for Cascade AI when working within this project context*

---

## 🎯 Core Principles

### Always Start with PROJECT-CONTEXT.md
Before making any suggestions, recommendations, or taking actions within this project:

1. **ALWAYS** reference `PROJECT-CONTEXT.md` first
2. **CHECK** the current project structure and external system links
3. **VERIFY** stakeholder information and project status
4. **UNDERSTAND** the project phase and current sprint context

### Context-Aware Responses
- Use the project structure defined in `PROJECT-CONTEXT.md` when suggesting file locations
- Reference existing folders and organization patterns
- Maintain consistency with established naming conventions
- Consider the project's current phase (planning vs. delivery)

---

## 📋 Pre-Action Checklist

Before providing suggestions or making changes, Cascade should:

- [ ] Review `PROJECT-CONTEXT.md` for current project state
- [ ] Check relevant `_project-context/` subfolders for existing documentation
- [ ] Identify appropriate external systems for the task at hand
- [ ] Consider impact on existing project structure
- [ ] Verify alignment with project goals and stakeholder needs

---

## 🔗 External Resource References

### When to Reference External Systems

**ClickUp References:**
- For task management, sprint planning, and backlog discussions
- When suggesting work item creation or status updates
- For team capacity and velocity discussions

**Figma References:**
- For design-related tasks, UI/UX discussions
- When suggesting design reviews or prototype creation
- For component library and design system references

**Azure DevOps References:**
- For development workflow, CI/CD pipeline discussions
- When suggesting code repository actions
- For build, test, and deployment processes

**GitHub References:**
- For code review processes and pull request workflows
- When discussing issue tracking and bug management
- For documentation and wiki references

### How to Reference External Resources

1. **Always use the links from PROJECT-CONTEXT.md** - don't create new placeholder links
2. **Provide context** - explain why the external resource is relevant
3. **Suggest specific actions** - don't just mention the tool, suggest what to do with it
4. **Update PROJECT-CONTEXT.md** - if new external resources are discovered, suggest updating the master index

---

## 📁 File Organization Guidelines

### When Suggesting New Files or Folders

**Check Existing Structure First:**
- Review current folder organization in `PROJECT-CONTEXT.md`
- Identify the most appropriate existing folder for new content
- Only suggest new folders if existing structure is insufficient

**Naming Conventions:**
- Follow established patterns (kebab-case for folders, descriptive names)
- Use prefixes like `_` for meta/context folders
- Maintain consistency with existing file naming

**Documentation Placement:**
- Requirements → `_project-context/requirements/` or `requirements/`
- Architecture → `_project-context/architecture/`
- Client information → `_project-context/client-info/`
- Status tracking → `_project-context/status-tracking/`
- Meeting notes → `meetings/`
- Design assets → `designs/`

---

## 🚀 Workflow Integration

### Project Phase Awareness

**Planning Phase Focus:**
- Prioritize `requirements/`, `research/`, `meetings/`, `designs/` folders
- Reference ClickUp for backlog and planning activities
- Emphasize Figma for design and prototyping work

**Development Phase Focus:**
- Prioritize `_project-context/architecture/` and technical documentation
- Reference Azure DevOps and GitHub for development workflows
- Focus on `Project/Documentation/` for technical specs

**Delivery Phase Focus:**
- Prioritize `Project/` delivery folders (Documentation, Onboarding, Training, Release Notes)
- Reference deployment and release processes
- Focus on user-facing documentation and training materials

### Status Updates and Tracking

When project status changes:
1. **Update PROJECT-CONTEXT.md** with new information
2. **Document changes** in `_project-context/status-tracking/`
3. **Notify relevant stakeholders** using contact information from PROJECT-CONTEXT.md
4. **Update external systems** as appropriate

---

## 🎨 Communication Style

### When Working with This Project

**Be Specific:**
- Reference exact folder paths from the project structure
- Use stakeholder names and roles from PROJECT-CONTEXT.md
- Mention specific external system features and workflows

**Be Contextual:**
- Consider current sprint information and deadlines
- Reference team velocity and capacity constraints
- Align suggestions with stated project goals

**Be Proactive:**
- Suggest updates to PROJECT-CONTEXT.md when new information emerges
- Recommend documentation in appropriate `_project-context/` subfolders
- Identify opportunities to improve project organization

---

## 🔄 Maintenance and Updates

### Keeping Context Current

**Regular Updates:**
- Suggest updating PROJECT-CONTEXT.md when project phases change
- Recommend archiving completed sprint information
- Propose new external system integrations as they become relevant

**Documentation Hygiene:**
- Suggest moving outdated information to appropriate archive folders
- Recommend consolidating duplicate information
- Propose improvements to project structure as it evolves

### Memory and Learning

**Remember Project Patterns:**
- Learn from user preferences for file organization
- Adapt to team-specific workflows and terminology
- Build understanding of project-specific constraints and requirements

---

## ⚠️ Important Reminders

1. **Never bypass PROJECT-CONTEXT.md** - it's the single source of truth for project organization
2. **Always consider external system integration** - don't work in isolation
3. **Maintain project structure integrity** - don't create chaos with ad-hoc organization
4. **Update documentation proactively** - keep the project context current
5. **Respect established workflows** - work within the team's existing processes

---

*These instructions should be followed consistently to maintain project organization and ensure effective collaboration within the established project ecosystem.*
