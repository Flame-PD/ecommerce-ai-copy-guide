"""Shared utility helpers used across service modules.

Provides common functions such as JSON extraction from LLM responses that
would otherwise be duplicated in every service file.
"""

from __future__ import annotations

import json
import re

# Matches ```json … ``` fenced code blocks (lazy dot-all)
_JSON_FENCE_PATTERN = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)


def extract_json(text: str) -> dict:
    """Extract a JSON object from an LLM response string.

    Attempts to find a `` ```json … ``` `` fenced block first.  If no fence
    is found the raw *text* is passed to :func:`json.loads`.

    Parameters
    ----------
    text : str
        Raw LLM output which may contain extra commentary or markdown.

    Returns
    -------
    dict
        Parsed JSON payload.

    Raises
    ------
    ValueError
        If no valid JSON object can be extracted from *text*.
    """
    m = _JSON_FENCE_PATTERN.search(text)
    json_str = (m.group(1) if m else text).strip()

    if not json_str:
        raise ValueError("LLM returned an empty response — no JSON to parse")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Failed to parse JSON from LLM response: {exc}"
        ) from exc
