from pathlib import PurePosixPath
import re

_BACKTICK = re.compile(r"`([^`\n]+)`")
_META = set("*{}<>|")


def extract_contract_paths(text: str) -> tuple[str, ...]:
    """Return sorted exact repository paths referenced in Markdown backticks.

    This extractor is intentionally stricter than the canonical multi-package
    validator's historical `_path_refs()` behavior. It is operator-specific so
    release-candidate validation semantics remain untouched.
    """
    found: set[str] = set()
    for match in _BACKTICK.finditer(text):
        token = match.group(1).strip().rstrip(".,;:")
        if "/" not in token or token.startswith(("http://", "https://", "/", "-")):
            continue
        if " " in token or any(ch in token for ch in _META):
            continue
        path = PurePosixPath(token)
        if any(part in {".", ".."} for part in path.parts):
            continue
        found.add(path.as_posix())
    return tuple(sorted(found))
