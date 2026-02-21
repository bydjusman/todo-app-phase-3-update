---
id: 2
title: fix-task-completion-deletion
stage: tasks
date: 2026-02-21
surface: agent
model: if/qwen3-coder-plus
feature: 2-chatbot
branch: main
user: User
command: fix
labels: [agent,openai,mcp,bugfix]
links:
  spec: D:/todo-app/todo-app-phase-3-update/specs/2-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - D:/todo-app/todo-app-phase-3-update/apps/server/mcp/agents.py
tests:
  -
---

## Prompt

Fix the issue where the chatbot doesn't properly complete or delete tasks when users request these actions through natural language commands.

## Response snapshot

Updated the agents.py file to properly handle task completion and deletion by:

1. Enhanced the _recognize_intent_and_execute method to properly identify task titles in user commands
2. Added _extract_task_title_from_command method to extract specific task references from natural language
3. Added _find_task_by_title method to match user input to existing tasks
4. Properly integrated these with the existing MCP tools for completion and deletion

The fix allows the chatbot to now recognize commands like:
- "Complete the grocery shopping task"
- "Mark 'buy milk' as done"
- "Delete the meeting task"
- "Remove task called doctor appointment"

## Outcome

- ✅ Impact: Fixed task completion and deletion functionality in chatbot
- 🧪 Tests: No tests added yet
- 📁 Files: Updated apps/server/mcp/agents.py with enhanced natural language processing
- 🔁 Next prompts: Testing the functionality and adding comprehensive tests
- 🧠 Reflection: The solution properly extracts task titles from natural language and matches them to existing user tasks before calling MCP tools

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add unit tests for the new functionality