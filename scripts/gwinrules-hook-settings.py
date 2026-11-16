#!/usr/bin/env python3
"""Supports: Claude Code. Helper for gwinrules.sh and gwinrules.ps1 (one copy serves both).

Adds or removes the Gwin session-rename hook in a project's .claude/settings.json. It touches only the
handler whose command contains MARK. Every other setting and hook stays as it is.

Usage: gwinrules-hook-settings.py SETTINGS_JSON install|uninstall COMMAND OUT_FILE
Prints one word on stdout: create, update, same, remove or none.
  create / update: the new settings text is written to OUT_FILE (the caller copies it in place).
  same / none:     nothing to write.
  remove:          the file would be left empty ({}); the caller deletes it.
Exit code 3 means SETTINGS_JSON is not valid JSON or has an unexpected shape. The file is not touched.
"""
import copy
import json
import os
import sys

MARK = 'gwin-shared/hooks/session-rename-reminder'


def load(path):
    if not os.path.exists(path):
        return None, False
    with open(path, encoding='utf-8-sig', newline='') as f:
        raw = f.read()
    crlf = '\r\n' in raw
    if not raw.strip():
        return {}, crlf
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError('settings.json is not a JSON object')
    return data, crlf


def strip_ours(data):
    """Return a copy of data without our handler. Empty groups, and an empty hooks object, are dropped."""
    out = copy.deepcopy(data)
    hooks = out.get('hooks')
    if hooks is None:
        return out
    if not isinstance(hooks, dict):
        raise ValueError('"hooks" is not an object')
    groups = hooks.get('PostToolUse')
    if groups is not None:
        if not isinstance(groups, list):
            raise ValueError('"hooks.PostToolUse" is not a list')
        kept = []
        for g in groups:
            if isinstance(g, dict) and isinstance(g.get('hooks'), list):
                g['hooks'] = [h for h in g['hooks'] if not (isinstance(h, dict) and MARK in str(h.get('command', '')))]
                if not g['hooks']:
                    continue
            kept.append(g)
        if kept:
            hooks['PostToolUse'] = kept
        else:
            del hooks['PostToolUse']
    if not hooks:
        del out['hooks']
    return out


def main():
    path, mode, command, out_file = sys.argv[1:5]
    try:
        old, crlf = load(path)
        base = strip_ours(old if old is not None else {})
    except (ValueError, json.JSONDecodeError) as e:
        print('invalid: %s' % e, file=sys.stderr)
        return 3

    if mode == 'uninstall':
        if old is None or base == old:
            print('none')
            return 0
        if not base:
            print('remove')
            return 0
        new, kind = base, 'update'
    else:
        new = copy.deepcopy(base)
        new.setdefault('hooks', {}).setdefault('PostToolUse', []).append(
            {'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': command}]})
        if old is None:
            kind = 'create'
        elif new == old:
            print('same')
            return 0
        else:
            kind = 'update'

    text = json.dumps(new, indent=2, ensure_ascii=False) + '\n'
    if crlf:
        text = text.replace('\n', '\r\n')
    with open(out_file, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    print(kind)
    return 0


if __name__ == '__main__':
    sys.exit(main())
