# AGENTS.md — AiNiee (fork)

Operating rules for any AI agent working in this repository, a personal fork of
[NEKOparapa/AiNiee](https://github.com/NEKOparapa/AiNiee). Read this file at the start of every
session before touching anything. This file governs *how you work*; it never overrides the
actual source in this repo, or upstream's own docs, on *what AiNiee does* — see §2.

## 0. What this repo is

AiNiee is a Python desktop app (PyQt5 + PyQt-Fluent-Widgets GUI, entry point `AiNiee.py`) that
automates AI-based translation of games (via export tools like Mtool/Translator++/ParaTranz/
RenPy/SExtraction), novels (Epub/TXT), documents (Word/PDF/MD/PPT), and subtitles
(Srt/Ass/Vtt/Lrc) by calling LLM APIs (OpenAI, Anthropic, Google Gemini, AWS Bedrock via
`boto3`, local models via Sakura/LM Studio/ollama, etc.).

This fork's purpose right now is general improvement and bug-hunting, not a from-scratch port —
so §9 ("milestones") looks different here than it would on a structured rewrite project.

Core layout:

- `ModuleFolders/Domain/` — the actual translation pipeline: `FileReader` / `FileOutputer` /
  `FileAccessor` (per-format accessors: `DocxAccessor.py`, `EpubAccessor.py`,
  `WolfXlsxAccessor.py`, `BabeldocPdfAccessor.py`, `ZipUtil.py`), `FileConverter`,
  `PromptBuilder`, `ResponseChecker`, `ResponseExtractor`, `TextFilter`, `TextNormalizer`,
  `TextProcessor`, `TextSymbolRepair`, `TranslationResultCheck`. Most file-parsing and
  translation-pipeline bugs live here.
- `ModuleFolders/{Base,Config,Infrastructure,Log,Service}` — supporting layers.
- `UserInterface/` — the PyQt GUI (`Settings/`, `EditView/`, `Table/`, `PromptSettings/`,
  `VersionManager/`, etc.).
- `Resource/Regex/regex.json` — the regex library used for in-game text embedding/extraction.
- `Resource/Localization/` — UI translation strings.
- `Resource/config.json` — runtime config, **gitignored** (holds the user's own LLM API keys —
  never commit it, never paste its contents into a commit message, PR, or chat log).
- `docs/` — the **exported exe's** settings + runtime folder, **gitignored**. `docs/ainiee_profile.json`
  is the profile the packaged app loads and contains the user's real `api_settings` / `platforms`
  **API keys**; `docs/ProjectCache/` holds large per-project translation caches. Treat the whole
  folder as secret + bulky: never commit it, never force-add it, never paste its contents anywhere.
  This is distinct from `Resource/config.json` (the source-run config) — *both* hold live secrets.
- `tests/` — currently one test, `test_version_manager_portable_update.py`, covering the
  self-update/portable-update logic. There is no broader automated suite, and CI
  (`.github/workflows/main.yml`) never runs `tests/` at all — it only builds Windows/macOS
  packages and auto-publishes a "Beta" prerelease on every push to `main`. A green CI run means
  "it packaged," nothing about correctness.

**Known doc drift (found, not yet fixed):** the project's own contribution guide in
`README.md`/`README_EN.md` says format-reading code lives in `ModuleFolders\FileReader` /
`FileOutputer`, and per-format UI toggles live in `UserInterface\Setting\ProjectSettingsPage`.
Neither path is current — the real paths are `ModuleFolders/Domain/FileReader` /
`ModuleFolders/Domain/FileOutputer`, and UI settings live under `UserInterface/Settings/`
(plural — `ExtractionSettingsPage.py`, `OutputSettingsPage.py`, etc.; there is no single
`ProjectSettingsPage`). Trust the source tree, not that doc text, when adding format support.

## 1. Start of every session

1. Read `CHECKPOINT.md` — the actual current state, not this file and not memory. If it doesn't
   exist yet, this is session 1: create it (shape in §6) instead of silently assuming a clean
   slate.
2. Skim `README.md` / `README_EN.md` once per fork-lifetime (not every session) for the current
   feature/format list — upstream adds format support over time.
3. Resume from the "Next" line of the latest checkpoint entry unless something in the repo
   (failing test, half-finished diff, an open question logged there) says otherwise.
4. Only after that, start work under the autonomy rules in §3.

## 2. Authority order (when sources disagree)

1. The actual code and observed behavior in this repo — always wins.
2. Upstream `NEKOparapa/AiNiee` `main` branch. This is a fork of an actively maintained project
   (2,400+ commits, ~6k stars) — before fixing something, check whether upstream already fixed
   it. Duplicating a landed fix wastes effort and complicates a future rebase/merge. Note
   anywhere this fork intentionally diverges from upstream.
3. In-repo docs: `README.md` / `README_EN.md`, and per-module `README.md` files (e.g.
   `ModuleFolders/Domain/FileAccessor/README.md`, the reader/writer development guide) — for
   intended behavior and extension points, checked against the doc-drift note in §0.
4. Upstream Issues/Discussions/Wiki — background on known bugs and feature requests; useful
   context, not authoritative on its own, and mostly in Chinese.

Never re-derive how a file format or prompt-building step is supposed to work from general LLM
knowledge when the relevant `Domain/` module already defines it.

## 3. Autonomy: run full-auto, ask only when it's a real human decision

Work through bugs/improvements one at a time without pausing for routine engineering choices —
anything answerable by reading the source or running the app/tests is yours to decide and act on.

Stop and hand back to a human only when:

- the decision isn't answerable from the repo, upstream, or a tool you can run;
- the next step is irreversible or outward-facing — see §5, always gated no matter how
  "obviously correct" it seems;
- you need credentials, secrets, or access outside this working tree — **this explicitly
  includes a real LLM API key.** Verifying a translation-pipeline fix by actually calling
  OpenAI/Anthropic/Gemini/Bedrock costs the user's own money and quota; treat that as an
  outward-facing action needing a fresh go-ahead each time, not something to do just because a
  key happens to be sitting in `Resource/config.json`. Prefer a mocked response, a recorded
  fixture, or a unit test around the parsing/formatting logic instead.
- you've hit 3 failed fix→verify cycles on the same defect, or you're blocked by something
  outside your control;
- doing the "obvious" next thing would contradict an instruction already given (about to push,
  about to weaken a check, about to widen a tolerance instead of finding the cause).

When you do stop: say exactly what you tried, what you observed, and the specific decision or
input needed — never a vague "let me know how you'd like to proceed."

## 4. How to work each task (apply every time; don't narrate it)

1. **Classify and define done.** A crash/parsing bug has an observable done state (it no longer
   throws; a round-tripped file matches expectations). A *translation-quality* complaint ("the
   output reads badly") usually doesn't — see §11. Say which kind of task this is before acting.
2. **Gather evidence before acting.** Open the actual `Domain/` module (and its README, if any)
   before writing a line of code — not the README's stale path claims (§0).
3. **Decide one approach.** If you seriously weighed an alternative, say why it lost, in one
   line.
4. **Act with the smallest correct diff**, matching existing style — this codebase mixes Chinese
   and English identifiers/comments in places; match whichever the surrounding file already
   uses, don't "clean up" language as a drive-by. Don't rewrite a whole file unless you've read
   all of it this session.
5. **Verify by observation.** Run `tests/` if the change touches version-manager/update logic;
   otherwise run the app (or the smallest reproducible script) against a small sample input file
   of the relevant format. Don't infer correctness from re-reading your own diff. For every bug
   fixed, check sibling format-handlers for the same pattern before calling it done — each
   format has its own accessor/reader/writer class, so an edge-case bug in one often exists in
   others.
6. **Report outcome-first.** Checkpoint entries lead with what happened and what proved it.

## 5. Git discipline

- Commit freely and often on a local/feature branch — after every bug fixed and verified, every
  meaningful improvement.
- **Never `git push`, force-push, open/merge a PR, create a tag/release, or touch anything
  remote — regardless of framing.** This matters more than usual here: `.github/workflows/main.yml`
  triggers a Windows + macOS build **and auto-publishes a "Beta" prerelease** on every push to
  `main`. If Actions are enabled on this fork, an unauthorized push to `main` doesn't just risk a
  bad commit — it can kick off a public-looking release build. Act only if the human's own words
  in this session say to push, and quote them before doing it.
- Never commit secrets, API keys, or `Resource/config.json` (already gitignored — keep it that
  way, don't force-add it).
- Never rewrite already-shared history.

## 6. Checkpoint file (mandatory)

Maintain `CHECKPOINT.md` at repo root — a durable, append-only record separate from commit
messages. Update it immediately when a bug is fixed and verified, when you find something worth
flagging but not fixing yet, or when you're about to stop for any reason (§3).

Entry shape:

```
## <ISO date> — <short label, e.g. "EpubAccessor: encoding bug" or "PromptBuilder cleanup">
- Done: <concrete, observed completions, and what verified each>
- Deviated from expected behavior: <what/why, or "none">
- Blocked / open question: <or "none">
- Next: <one line>
```

Append; never delete history.

## 7. Resource safety

Nothing here needs GPU/build-cluster-scale caution, but two things accumulate:

- Launching the app (`AiNiee.py`) or a translation run to reproduce/verify a bug writes to
  `ProjectCache/` and `Logs/` (both gitignored). Clean those up before ending the session unless
  the user wants them kept for inspection.
- Building the actual installers (`Tools/pyinstall.py`, `Tools/pyinstall_macos.py`) is the one
  genuinely heavy operation in this repo — that's what CI is for, not a casual local
  verification step.

## 8. Standing prohibitions (absent explicit instruction otherwise)

- Never weaken, skip, or fake a check to make it pass.
- Never touch secrets, credentials, `.env`, `Resource/config.json`, `docs/` (exported-exe profile
  with API keys — see §0), or CI config (`.github/workflows/`).
- Never add a dependency without a concrete, repo-specific need — `requirements.txt` is already
  large (LLM SDKs, OCR/PDF stack, PyQt, BabelDOC, etc.); don't grow it casually.
- Never delete or overwrite a file without reading what's actually in it first.
- Never call a real, paid LLM API or spend the user's API quota as part of routine verification
  — see §3.

## 9. Scope / milestones

This fork has no fixed milestone list — it's ongoing bug-hunting and improvement, not a port
with a defined end state. If the user later gives a specific priority list or roadmap, put it in
its own doc and reference it here; until then, each `CHECKPOINT.md` entry is its own unit of
work, tackled and verified independently.

## 10. Licensing note

AiNiee is AGPL-3.0-licensed (inherited by this fork). If you bring in code from somewhere else —
another project, a snippet adapted from a specific external source — beyond what you wrote
yourself, note where it came from and its license in the commit message or `CHECKPOINT.md`.
Don't let "referenced how X does it" quietly become "copied X's code" unlogged.

## 11. Bug vs. quality-judgment calls

Two different kinds of "problem" show up in this project; treat them differently:

- **Technical bugs** (crash, wrong file encoding, mangled tags/placeholders, broken regex,
  update/version-manager failure) — these have an observable correct behavior. Fix and verify
  per §4-§5 normally.
- **Translation-quality complaints** (tone, naturalness, terminology consistency) — these don't
  have a single correct answer and can't be verified by re-running code; they need a human to
  actually read the output. Don't "fix" these by guessing at a prompt tweak and calling it done —
  say what you'd change and why, and let the user judge the actual translated text before
  treating it as resolved.

# Fable family (think / act / prove)
- Before any non-trivial multi-step task, apply the fable-method loop; for tasks that will
  run unattended or fan out subagents, use fable-loop.
- After completing substantive work, or whenever any agent/tool claims work is done,
  run a fable-judge pass before presenting it as finished. "Did that actually work?" = fable-judge.
