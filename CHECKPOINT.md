# CHECKPOINT.md

Durable, append-only session log for AI-agent work on this AiNiee fork. Read this before
touching anything (see `AGENTS.md` §1). Append new entries below; never delete history.

This file is the record of **how this fork diverges from upstream `NEKOparapa/AiNiee`** — every
entry describes a change that makes this fork different (localization, bug fixes, etc.), in
English. Commit and update this file after each important, verified unit of work.

## 2026-09-05 — fork setup
- Done: wrote `AGENTS.md` for this fork (operating rules, doc-drift note on stale contribution-
  guide paths, autonomy/git/API-cost guardrails, checkpoint discipline).
- Deviated from expected behavior: none — no code changes made yet.
- Blocked / open question: none.
- Next: pick a first bug/improvement (check upstream Issues for known problems, or run the app
  against a small sample file to look for one), then open the first real checkpoint entry for it.

## 2026-09-05 — docs/ secret-handling rule + start of English/Thai localization
- Done:
  - Documented the `docs/` folder in `AGENTS.md` §0 and §8: it is the **exported exe's** settings +
    runtime folder; `docs/ainiee_profile.json` holds the user's real `api_settings`/`platforms`
    API keys and `docs/ProjectCache/` holds large caches. Marked as never-commit / never-paste.
  - Added `/docs/` to `.gitignore` and verified with `git check-ignore` that `docs/ainiee_profile.json`
    and `docs/ProjectCache/**` are now ignored. (docs/ was untracked but previously NOT ignored, so a
    `git add .` could have leaked the API-key profile into a commit.)
  - Scoped the localization task by evidence (see plan below).
- Fork divergence started: goal is a **full English + Thai UI** with no Chinese leaking. Root cause
  of the leak identified: `ConfigMixin.tra()` (ModuleFolders/Config/Config.py:25) returns the raw
  Chinese source string whenever a key is missing. Measured gaps: 106 `tra()` keys absent from the
  Localization JSONs; 291 hardcoded Chinese literals bypassing `tra()` (upper bound); 848 existing
  keys have English but none have Thai; the language selector (AppSettingsPage.py:314) offers no Thai.
- Deviated from expected behavior: none yet (this entry is docs/gitignore only).
- Blocked / open question: none. Keeping 简中/繁中 as selectable options (upstream parity) and
  *adding* Thai rather than removing Chinese — tell me if you actually want Chinese removed entirely.
- Next: (1) make `tra()` fall back to English before raw Chinese so missing keys never leak Chinese
  in en/th mode; (2) add "ไทย" to the language selector; (3) fill the 106 missing keys; (4) bulk-add
  Thai to the 848 entries; (5) sweep the hardcoded-Chinese files. Commit each when verified.
