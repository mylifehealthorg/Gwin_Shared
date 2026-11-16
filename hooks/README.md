# hooks

See the root [README](../README.md) for what belongs here.

| Hook | Use |
| --- | --- |
| [`session-rename-reminder.sh`](session-rename-reminder.sh) | Claude Code `PostToolUse` hook on Bash. After `gh pr create` or `gh pr merge` it prints a message that tells Claude to rename the session (use the `session-auto-rename` skill, or `set_session_title`). A hook cannot rename a session itself, so it only reminds. It never blocks a tool call. |

`gwinrules` installs this hook into a project: it copies the script to `.claude/gwin-shared/hooks/` and adds
the entry to `.claude/settings.json`. Do not copy it by hand. Edit it here and re-run `gwinrules`.
