---
id: 7
title: add-bulk-delete-feature
stage: tasks
date: 2026-02-21
surface: agent
model: if/qwen3-coder-plus
feature: 2-chatbot
branch: main
user: User
command: feature
labels: [agent,openai,mcp,feature]
links:
  spec: D:/todo-app/todo-app-phase-3-update/specs/2-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - D:/todo-app/todo-app-phase-3-update/apps/server/mcp/server.py
  - D:/todo-app/todo-app-phase-3-update/apps/server/mcp/agents.py
tests:
  -
---

## Prompt

Add bulk deletion functionality to allow users to delete all their tasks with commands like "delete all tasks" or "remove all my tasks".

## Response snapshot

Added bulk deletion functionality by:
1. Creating a new delete_all_tasks MCP tool in server.py with confirmation requirement
2. Updating the agents.py deletion logic to detect bulk deletion intents like "all tasks", "all my tasks", etc.
3. Implementing proper security measures to ensure only authenticated user's tasks are deleted
4. Adding confirmation step to prevent accidental bulk deletion

## Outcome

- ✅ Impact: Users can now delete all tasks with commands like "delete all tasks"
- 🧪 Tests: No tests added yet
- 📁 Files: Updated server.py with new tool and agents.py with bulk detection
- 🔁 Next prompts: Testing bulk deletion functionality
- 🧠 Reflection: The solution includes safety measures like confirmation to prevent accidental data loss

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add tests for bulk deletion