#!/usr/bin/env sh
# Managed by gwinrules: edit in Gwin_Shared and re-run gwinrules, not in the project.
# Supports: Claude Code (PostToolUse hook on the Bash tool). Needs only a POSIX shell; Claude Code on Windows
# runs hooks in Git Bash, so this works there too.
#
# Claude Code sends the tool call to this script as JSON on stdin. When the Bash command was
# `gh pr create` or `gh pr merge`, the script prints a JSON message that tells Claude to rename the session.
# A hook cannot rename a session itself, so the hook only reminds Claude and Claude does the rename.
# The script never blocks a tool call and always exits 0. It does nothing for any other command.
input=$(cat 2>/dev/null || true)

case $(printf '%s' "$input" | grep -Eo 'gh pr (create|merge)' | head -n 1) in
  "gh pr create")
    msg='A pull request was just opened. Rename this session now. Do not ask first. Use the session-auto-rename skill if it is installed. If it is not, call set_session_title with session_id self. New title: PROJECT-CODE PR#NUMBER/feature words. Keep the project code and the feature words that the title already has. Say what you did in one short line.'
    ;;
  "gh pr merge")
    msg='A pull request was just merged. Rename this session now. Do not ask first. Use the session-auto-rename skill if it is installed. If it is not, call set_session_title with session_id self. Keep the current title and add (merged) at the end, once. Example: GS PR#10/Repo migration (merged). Say what you did in one short line.'
    ;;
  *) exit 0 ;;
esac

printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "$msg"
exit 0
