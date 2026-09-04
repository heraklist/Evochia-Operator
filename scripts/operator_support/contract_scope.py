from __future__ import annotations

from collections.abc import Iterable


def operator_contract_paths(paths: Iterable[str]) -> tuple[str, ...]:
    """Return the packaged Markdown paths that define operator path authority.

    Only the public root contract and projected domain module contracts may create
    backticked runtime-path obligations. Packaged references, READMEs, evidence and
    other documentation remain content, not path-discovery authority.
    """
    return tuple(
        sorted(
            path
            for path in paths
            if path == "SKILL.md" or path.endswith("/MODULE.md")
        )
    )
