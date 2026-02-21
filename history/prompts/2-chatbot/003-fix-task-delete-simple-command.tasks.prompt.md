---
id: 3
title: fix-task-delete-simple-command
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

Fix the issue where the chatbot doesn't properly handle simple deletion commands like "delete buy milk" where the task title directly follows the verb.

## Response snapshot

Updated the _extract_task_title_from_command method in agents.py to add a new pattern that handles simple commands like "delete buy milk". Added Pattern 5 that specifically looks for commands where a verb (delete, remove, complete, etc.) is directly followed by the task title.

## Outcome

- ✅ Impact: Fixed handling of simple command patterns like "delete buy milk"
- 🧪 Tests: No tests added yet
- 📁 Files: Updated apps/server/mcp/agents.py with enhanced pattern matching
- 🔁 Next prompts: Testing the functionality and verifying all command patterns work
- 🧠 Reflection: The solution now handles multiple command patterns including simple direct commands

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add comprehensive tests for all command patterns