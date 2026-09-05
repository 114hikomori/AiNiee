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

## 2026-09-05 — localization: English-fallback in tra() + Thai language option
- Done:
  - `ConfigMixin.tra()` (ModuleFolders/Config/Config.py) now falls back to the entry's **English**
    value when the selected language's value is missing, before returning the raw Chinese source.
    Verified by importing the real class (shimmed `rapidjson`→stdlib json) and exercising three
    cases: Thai-mode with a missing-Thai entry returns English (not Chinese); Chinese mode unchanged;
    a key absent from the dict still returns Chinese (that set is the 106 missing keys, next task).
  - Added `"ไทย"` to the interface-language selector list (UserInterface/Settings/AppSettingsPage.py:314).
    No other code enumerates the language set; the combo stores the selected text directly into
    `interface_language_setting`, so selecting ไทย now drives `tra()` lookups on a "ไทย" key.
  - Both changed files pass `python -m py_compile`.
- Fork divergence: this is the first functional change vs upstream — upstream has no Thai and no
  English-fallback (missing keys leak Chinese in any non-Chinese UI).
- Deviated from expected behavior: none.
- Blocked / open question: none.
- Next: add the 106 `tra()` keys that are absent from the Localization JSONs (with English + ไทย),
  then bulk-add ไทย values to the 848 existing entries.

## 2026-09-05 — localization: added the missing tra() keys (Supplement.json)
- Done:
  - Re-extracted the truly-missing `tra()` keys with Python `ast` (folds adjacent string literals +
    escapes into the exact runtime value) instead of regex: **94** keys were absent from the
    Localization JSONs (the earlier regex count of 106 over-counted multi-line literals).
  - Added all 94 as `Resource/Localization/Supplement.json` (flat-merged by `load_translations`, so a
    new file is functionally identical to editing existing ones and keeps the additions isolated).
    Each entry has 简中/繁中/English/日本語/ไทย. English + Thai are the fork's target; 繁中/日本語
    filled for schema parity with the other 848.
  - Verified by reloading through the real `ConfigMixin.load_translations` and re-running the ast
    missing-check: **0 remaining missing tra() keys** (637 distinct literals all covered). Spot-checked
    rendering: ไทย 确定→ตกลง, format-string key `表格已按 '{}' {}排序`→`ตารางเรียงตาม '{}' {}`
    (placeholders preserved), English and 简中 modes correct.
  - Effect: the "Chinese still shows after switching to English/Thai" bug is now fixed for **every**
    `tra()`-based UI string. Remaining Chinese leaks are only the hardcoded literals that bypass
    `tra()` (next major task) and Thai completeness on the pre-existing 848 entries (currently covered
    by the English fallback added earlier).
- Deviated from expected behavior: none.
- Blocked / open question: none.
- Next: bulk-add ไทย to the 848 pre-existing entries (so Thai mode shows Thai, not English fallback),
  then sweep the ~291 hardcoded Chinese literals to wrap user-facing ones in `tra()`.

## 2026-09-05 — localization: caught tra() alias calls (translate/bare tra)
- Done:
  - Realized the earlier ast check only matched `.tra(` and missed calls via a `translate` parameter
    alias (e.g. AnalysisPage) and bare `tra(...)` (e.g. MacOSUI). Re-ran an ast detector covering
    `.tra(`, bare `tra(`, and `translate(` across the whole repo: 640 distinct literals, only 3 were
    uncovered — `AiNiee` (proper noun, correctly left untranslated) plus `AiNiee macOS 支持` and
    `配置目录`, which I added to Supplement.json (English + Thai + parity fields).
  - Re-verified: the **entire tra()/translate() call surface now resolves to English or Thai** for
    every key except the app-name literal.
- Deviated from expected behavior: none.
- Blocked / open question: none.
- Next: (a) bulk-add ไทย to the 848 pre-existing entries so Thai mode stops relying on the English
  fallback; (b) sweep the genuinely hardcoded Chinese literals (never call tra()) — the only remaining
  source of Chinese in an English/Thai UI.
