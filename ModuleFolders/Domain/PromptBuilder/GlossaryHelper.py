from functools import lru_cache

import regex

from ModuleFolders.Domain.RegexSwitchHelper import RegexSwitchHelper


_CACHE_MAXSIZE = 8192


class GlossaryHelper:
    REGEX_KEY = RegexSwitchHelper.REGEX_KEY
    STATE_VALID = "valid"
    STATE_REGEX = "regex"
    STATE_INVALID = "invalid"
    _warned_invalid_sources = set()

    @staticmethod
    def _normalize_text(value) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    @lru_cache(maxsize=_CACHE_MAXSIZE)
    def _compile_source_text(source_text: str):
        return regex.compile(source_text)

    @classmethod
    def validate_source_text(cls, source_text: str) -> bool:
        source_text = cls._normalize_text(source_text)
        if not source_text:
            return True
        try:
            cls._compile_source_text(source_text)
            return True
        except regex.error:
            return False

    @classmethod
    def get_row_state(cls, row: dict) -> str:
        if not isinstance(row, dict):
            return cls.STATE_INVALID
        if not RegexSwitchHelper.is_regex_enabled(row):
            return cls.STATE_VALID
        if not cls.validate_source_text(row.get("src", "")):
            return cls.STATE_INVALID
        return cls.STATE_REGEX

    @classmethod
    def is_row_valid(cls, row: dict) -> bool:
        return cls.get_row_state(row) != cls.STATE_INVALID

    @classmethod
    def is_row_regex(cls, row: dict) -> bool:
        return cls.get_row_state(row) == cls.STATE_REGEX

    @classmethod
    def normalize_row(cls, row: dict) -> dict:
        return RegexSwitchHelper.normalize_glossary_row(row)

    @classmethod
    def normalize_rows(cls, rows: list[dict] | None) -> list[dict]:
        return RegexSwitchHelper.normalize_glossary_rows(rows)

    @classmethod
    @lru_cache(maxsize=_CACHE_MAXSIZE)
    def build_search_pattern(
        cls,
        source_text: str,
        regex_enabled: bool = False,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ):
        source_text = cls._normalize_text(source_text)
        if not source_text:
            return None

        try:
            if regex_enabled is True:
                return cls._compile_source_text(source_text)

            pattern_text = regex.escape(source_text)
            if whole_word:
                pattern_text = rf"(?<!\w){pattern_text}(?!\w)"

            flags = 0 if case_sensitive else regex.IGNORECASE
            return regex.compile(pattern_text, flags)
        except regex.error:
            return None

    @classmethod
    def source_matches_text(
        cls,
        source_text: str,
        full_text: str,
        regex_enabled: bool = False,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> bool:
        pattern = cls.build_search_pattern(
            source_text,
            regex_enabled,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
        )
        return bool(pattern and pattern.search(full_text or ""))

    @classmethod
    def collect_matched_rows(
        cls,
        rows: list[dict] | None,
        input_dict: dict | None,
        include_invalid: bool = False,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> list[dict]:
        full_text = "\n".join(input_dict.values()) if isinstance(input_dict, dict) else ""
        if not full_text:
            return []

        matched_rows = []
        seen_keys = set()

        for row in cls.normalize_rows(rows):
            src = row.get("src", "")
            regex_enabled = row.get(cls.REGEX_KEY) is True
            if not src:
                continue

            if regex_enabled and not cls.validate_source_text(src):
                if src not in cls._warned_invalid_sources:
                    print(f"[WARNING][GlossaryHelper] 跳过无效术语正则表达式: '{src}'")
                    cls._warned_invalid_sources.add(src)
                continue

            pattern = cls.build_search_pattern(
                src,
                regex_enabled,
                case_sensitive=case_sensitive,
                whole_word=whole_word,
            )
            if pattern is None:
                continue

            found_texts = []
            seen_texts = set()
            for match in pattern.finditer(full_text):
                match_text = match.group(0)
                if not match_text or match_text in seen_texts:
                    continue
                found_texts.append(match_text)
                seen_texts.add(match_text)

            for match_text in found_texts:
                dedupe_key = (match_text, row.get("dst", ""))
                if dedupe_key in seen_keys:
                    continue
                new_row = row.copy()
                new_row["src"] = match_text
                matched_rows.append(new_row)
                seen_keys.add(dedupe_key)

        return matched_rows

    @classmethod
    def clear_cache(cls) -> None:
        cls._compile_source_text.cache_clear()
        cls.build_search_pattern.cache_clear()
        cls._warned_invalid_sources.clear()
