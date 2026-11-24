---
inclusion: always
---
# Task tracking conventions

- Our sprint lives in the Smartsheet sheet **"Backend API — Sprint"**. Columns: `Task ID`, `Title`, `Owner`, `Status` (Not Started / In Progress / Blocked / Complete), `Blocked By`, `PR`.
- Branch names start with the task id: `TASK-123-short-title`. Commit messages reference the task id.
- Read freely from the sheet. **Writes** are limited to: `Status`, `PR` link and a discussion comment explaining every change ("why, by whom, which commit").
- Never change `Owner`, dates or other people's rows without asking.
