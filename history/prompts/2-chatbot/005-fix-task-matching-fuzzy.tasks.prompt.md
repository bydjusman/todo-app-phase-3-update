---
id: 5
title: fix-task-matching-fuzzy
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

Fix the task matching to handle even more variations in how task titles are stored vs how users refer to them, including fuzzy matching and word-by-word comparison.

## Response snapshot

Enhanced the _find_task_by_title method with fuzzy matching logic that:
1. Handles common word removal like 'the', 'a'
2. Implements word-by-word matching where if 50% or more words match, the task is considered a match
3. Provides more flexible matching for case and phrase variations
4. Maintains the same security and functionality while improving accuracy

## Outcome

- ✅ Impact: Much improved task matching with fuzzy logic
- 🧪 Tests: No tests added yet
- 📁 Files: Updated apps/server/mcp/agents.py with enhanced fuzzy matching
- 🔁 Next prompts: Testing with real tasks and commands
- 🧠 Reflection: The solution now handles complex variations between user input and stored task titles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add comprehensive tests for all matching scenarios