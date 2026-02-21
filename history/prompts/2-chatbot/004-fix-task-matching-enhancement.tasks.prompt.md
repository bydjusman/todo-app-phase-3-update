---
id: 4
title: fix-task-matching-enhancement
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

Fix the issue where the chatbot isn't properly matching task titles during delete/complete operations, especially for cases where there might be case differences or phrase variations.

## Response snapshot

Enhanced the _find_task_by_title method in agents.py to be more robust in matching task titles by:
1. Adding exact match first
2. Improving partial matching logic
3. Handling common phrase variations like "the X task" vs "X"
4. Better handling of case differences between user input and stored task titles

## Outcome

- ✅ Impact: Improved task matching accuracy for completion and deletion
- 🧪 Tests: No tests added yet
- 📁 Files: Updated apps/server/mcp/agents.py with enhanced matching logic
- 🔁 Next prompts: Testing the functionality with various task titles and commands
- 🧠 Reflection: The solution now handles more variations in how users phrase their task titles vs how they're stored

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add comprehensive tests for various matching scenarios