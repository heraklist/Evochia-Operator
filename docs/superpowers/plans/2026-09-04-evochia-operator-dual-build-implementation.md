# Evochia Operator Dual-Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic dual-build system that preserves the canonical 12-Skill source architecture while producing both a 12-public-Skill multi artifact and a one-public-Skill `@evochia-operator` artifact with 11 exact-byte internal module projections.

**Architecture:** The builder reads only committed Git objects from an explicit source commit. The multi target materializes the canonical Git tree; the operator target replaces the public source Skill surface with one source-controlled operator template, projects the 11 domain `SKILL.md` files byte-for-byte as `skills/<id>/MODULE.md`, preserves canonical resource paths, generates only `references/module_index.md` and provenance metadata, and writes a deterministic ZIP. A dedicated source-anchored validator checks artifact bytes against the actual Git objects at the declared source commit.

**Tech Stack:** Python 3.12, standard-library `subprocess`, `hashlib`, `zipfile`, `pathlib`, `dataclasses`, `re`; PyYAML 6.x; pytest 9.x; Git CLI; existing repository validators and GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-04-evochia-operator-dual-build-design.md`

## Global Constraints

- Canonical starting commit for the design: `9cab252e8757b35f6501b178c06943b0e82b398a`.
- Public operator ID: `evochia-operator`; public invocation target: `@evochia-operator`.
- The 12 existing source `skills/*/SKILL.md` contracts MUST NOT be semantically modified by this implementation.
- `skills/chef-ai-pro-business/references/routing.yaml` MUST remain canonical and byte-identical when projected.
- `references/source_registry.yaml` remains the only canonical source-authority precedence contract; do not add another precedence list.
- Domain projection path is exactly `skills/<id>/SKILL.md` → `skills/<id>/MODULE.md` with relation `EXACT_BYTE_COPY`; frontmatter and body remain byte-identical.
- `references/module_index.md` is generated from source frontmatter and is added to, never substituted for, the complete canonical `references/` subtree.
- The operator root `SKILL.md` comes from source-controlled `release/operator/SKILL.template.md`; the builder MUST NOT embed the behavioral prompt as a Python string.
- Builder inputs are explicit full Git commit SHAs and committed Git blobs; dirty working-tree bytes MUST NOT affect output.
- Supported build targets are exactly `multi` and `operator`.
- Output filenames are `chef-ai-pro-business-<version>-<shortsha>-multi.zip` and `evochia-operator-<version>-<shortsha>-operator.zip`.
- Deterministic ZIP output requires stable path ordering, timestamps, compression settings, Git-derived executable mode normalization, separators, filename encoding and archive metadata.
- Release-grade operator validation requires `--artifact`, `--source-repo`, and `--source-commit` and checks actual Git objects rather than trusting the artifact manifest.
- `openai_surface_install_scan` remains OPEN/release-blocking until a complete post-builder `MULTI(C1)` A→H surface run is completed; operator tests do not close it.
- The primary surface differential is router-to-router: `@chef-ai-pro-business` versus `@evochia-operator` with the same task. Direct domain-Skill runs are optional non-gating diagnostics.
- No Phase 14–16 implementation, business-policy change, supplier-policy change, FnB persistence change, or unrelated refactor belongs in this branch.

---

## File Structure

**Create**

- `release/operator/SKILL.template.md` — sole new behavioral operator instruction surface.
- `release/operator/package_policy.yaml` — generated-target configuration and pinned icon source, referencing canonical policy rather than duplicating authority.
- `scripts/contract_paths.py` — shared exact-path extractor for backticked repository-path references.
- `scripts/operator_git.py` — immutable Git-object reader and Git tree metadata model.
- `scripts/deterministic_zip.py` — deterministic ZIP serializer for in-memory artifact entries.
- `scripts/operator_index.py` — canonical frontmatter parser and generated module-index renderer.
- `scripts/build_skill_package.py` — dual-target build CLI and target composition logic.
- `scripts/validate_operator_package.py` — source-anchored operator artifact validator CLI.
- `tests/operator/test_operator_template.py` — root-template behavioral-contract tests.
- `tests/operator/test_contract_paths.py` — exact-path extractor tests, including the three paths that exposed the design bug.
- `tests/operator/test_operator_git.py` — Git-object anchoring and dirty-worktree isolation tests.
- `tests/operator/test_deterministic_zip.py` — deterministic archive primitive tests.
- `tests/operator/test_operator_index.py` — generated-index source-equivalence tests.
- `tests/operator/test_operator_policy.py` — target-policy and verified icon-source tests.
- `tests/operator/test_operator_validator.py` — structural/source-anchored validator tests on controlled fixture repositories/artifacts.
- `tests/operator/test_dual_build.py` — multi/operator end-to-end build tests.
- `tests/operator/test_release_gate_preservation.py` — release-blocker preservation tests.

**Modify**

- `scripts/validate_skill_package.py` — reuse the shared path extractor without changing its source-package semantics.
- `.github/workflows/verify.yml` — add deterministic dual-build and source-anchored operator validation smoke commands after the existing validation suite.

**Do not modify**

- Any existing `skills/*/SKILL.md`.
- `skills/chef-ai-pro-business/references/routing.yaml`.
- `references/source_registry.yaml`.
- Current policy/data/doctrine files solely to make the builder pass.
- `release/release_readiness.yaml` before surface evidence exists.

---

### Task 1: Write and lock the operator root template first

**Files:**
- Create: `release/operator/SKILL.template.md`
- Create: `tests/operator/test_operator_template.py`

**Interfaces:**
- Consumes: canonical paths `references/source_registry.yaml`, `skills/chef-ai-pro-business/references/routing.yaml`, and future generated `references/module_index.md`.
- Produces: a source-controlled `SKILL.template.md` whose bytes later become the operator artifact root `SKILL.md`.

- [ ] **Step 1: Write the failing template-contract test before creating the template**

```python
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "release/operator/SKILL.template.md"


def _frontmatter(text: str) -> dict:
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    return yaml.safe_load(text[4:end]) or {}


def test_operator_template_has_only_orchestrator_responsibility():
    text = TEMPLATE.read_text(encoding="utf-8")
    meta = _frontmatter(text)
    assert meta["name"] == "evochia-operator"
    assert meta["description"]
    assert "smallest sufficient" in text.lower()
    assert "skills/<skill-id>/MODULE.md" in text
    assert "skills/chef-ai-pro-business/references/routing.yaml" in text
    assert "references/module_index.md" in text
    assert "references/source_registry.yaml" in text
    assert "food-safety-allergens" in text
    assert "INTERNAL" in text and "OPERATIONS" in text and "CLIENT-SAFE" in text
    assert "DRAFT_OR_HANDOFF_NO_FAKE_EXECUTION" in text
    assert "FnB Central" in text
    assert "system of record" in text.lower()
    assert "routing transcript" in text.lower()


def test_operator_template_does_not_duplicate_current_commercial_policy():
    text = TEMPLATE.read_text(encoding="utf-8")
    forbidden_policy_literals = ["15+", "6–14", "0–5", "+20%", "+40%", "6500", "6,500"]
    assert not [token for token in forbidden_policy_literals if token in text]
```

- [ ] **Step 2: Run the test and confirm the RED state is a missing template**

Run:

```bash
python -m pytest tests/operator/test_operator_template.py -q
```

Expected: FAIL because `release/operator/SKILL.template.md` does not exist.

- [ ] **Step 3: Create the template as reviewed behavioral content, not builder code**

Use this content as the implementation baseline:

```markdown
---
name: evochia-operator
description: Use when Evochia or professional F&B work needs one coordinated entrypoint across culinary, recipe engineering, menu design, event operations, food safety, costing/commercial, suppliers, company operations, brand/documents, product development, or market intelligence.
---
# Evochia Hospitality Operator

## Purpose
Act as the single public orchestrator for the packaged Evochia Operator. Classify the request, select the smallest sufficient internal domain set, preserve canonical source authority and audience boundaries, and compose one answer without becoming a monolithic source of culinary, safety, commercial, supplier or company policy.

## Authority and Routing
- `references/source_registry.yaml` remains the source-authority and supersession contract.
- `skills/chef-ai-pro-business/references/routing.yaml` remains the canonical routing contract.
- `references/module_index.md` is a generated capability lookup derived from canonical domain frontmatter; it is not a second authority.
- Within this operator package, a canonical skill ID resolves to `skills/<skill-id>/MODULE.md`.
- Use the routing contract first. Consult the generated module index when the route is not sufficiently clear. Read only the smallest sufficient module set.

## Orchestration Rules
Classify generic-F&B versus Evochia context, safety risk, freshness need, tool availability and output audience before composing the answer. Preserve distinctions among facts, approved data, external evidence, estimates, assumptions and needs-review items. Do not expose the internal routing transcript.

Safety authority outranks creativity, commercial optimization and presentation. When allergen or food-safety stakes are material, `food-safety-allergens` is a mandatory hard gate and its blocker state propagates to the final answer.

Choose exactly one audience boundary unless the user explicitly requests multiple:
- `INTERNAL`: costs, margins, assumptions, supplier evidence and strategy may be present.
- `OPERATIONS`: production, staffing, equipment, allergens, run sheets and service notes.
- `CLIENT-SAFE`: approved external concept/menu/scope/fee/terms only; never leak INTERNAL economics or strategy.

For controlled external execution, preserve the canonical execution contract. Consequential writes remain propose-then-confirm and success may be claimed only from an actual backend/tool response. If the required execution tool is unavailable, preserve `DRAFT_OR_HANDOFF_NO_FAKE_EXECUTION`; never simulate a successful write.

FnB Central remains the persistent F&B system of record. This operator does not create duplicate persistent state and does not describe mock/in-memory integration scaffolds as durable production persistence.

## Composition
Return the requested answer or artifact in the requested audience boundary. Use domain contracts and canonical resources for substantive rules; do not restate current rates, safety doctrine, supplier data or company policy here when a canonical source already owns them.
```

- [ ] **Step 4: Run the template tests**

Run:

```bash
python -m pytest tests/operator/test_operator_template.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the independently reviewable behavioral surface**

```bash
git add release/operator/SKILL.template.md tests/operator/test_operator_template.py
git commit -m "feat: define Evochia Operator root contract"
```

---

### Task 2: Extract exact repository paths as a reusable contract primitive

**Files:**
- Create: `scripts/contract_paths.py`
- Create: `tests/operator/test_contract_paths.py`
- Modify: `scripts/validate_skill_package.py`

**Interfaces:**
- Produces: `extract_contract_paths(text: str) -> tuple[str, ...]`.
- Consumers: existing source-package validator, operator closure builder, operator artifact validator.

- [ ] **Step 1: Write failing extractor tests including the paths that caused the design correction**

```python
from scripts.contract_paths import extract_contract_paths


def test_extracts_exact_repo_paths_without_rewriting():
    text = """
Read `skills/culinary-rnd/references/research_protocol.md`,
`skills/kitchen-event-operations/references/event_lifecycle.md`, and
`skills/evochia-market-intelligence/references/intelligence_policy.yaml`.
Use `references/operations/output_router_templates_v2_1.md`.
"""
    assert extract_contract_paths(text) == (
        "references/operations/output_router_templates_v2_1.md",
        "skills/culinary-rnd/references/research_protocol.md",
        "skills/evochia-market-intelligence/references/intelligence_policy.yaml",
        "skills/kitchen-event-operations/references/event_lifecycle.md",
    )


def test_ignores_urls_globs_placeholders_commands_and_parent_traversal():
    text = """
`https://example.com/a/b`
`templates/*/x.md`
`skills/<skill-id>/MODULE.md`
`python scripts/tool.py --flag`
`../secret/file`
`plain-token`
"""
    assert extract_contract_paths(text) == ()
```

- [ ] **Step 2: Verify RED before the extractor exists**

Run:

```bash
python -m pytest tests/operator/test_contract_paths.py -q
```

Expected: import failure for `scripts.contract_paths`.

- [ ] **Step 3: Implement the exact-path extractor**

```python
from __future__ import annotations

from pathlib import PurePosixPath
import re

_BACKTICK = re.compile(r"`([^`\n]+)`")
_FORBIDDEN_META = set("*{}<>|")


def extract_contract_paths(text: str) -> tuple[str, ...]:
    paths: set[str] = set()
    for match in _BACKTICK.finditer(text):
        token = match.group(1).strip().rstrip(".,;:")
        if "/" not in token:
            continue
        if token.startswith(("http://", "https://", "/")):
            continue
        if token.startswith("-") or " " in token:
            continue
        if any(ch in token for ch in _FORBIDDEN_META):
            continue
        path = PurePosixPath(token)
        if ".." in path.parts or "." in path.parts:
            continue
        paths.add(path.as_posix())
    return tuple(sorted(paths))
```

- [ ] **Step 4: Reuse the extractor in the existing validator without changing its dual-candidate resolution semantics**

In `scripts/validate_skill_package.py`, replace the private regex implementation with:

```python
from contract_paths import extract_contract_paths

# ...
for ref in extract_contract_paths(text):
    candidates = [root / ref, skill_dir / ref]
    if not any(path.exists() for path in candidates):
        issues.append(f"{skill_name}: broken referenced path {ref}")
```

Keep the current source validator's `root / ref` and `skill_dir / ref` compatibility behavior. Exact-path-only semantics are enforced later by the operator validator, not retroactively imposed on the canonical source validator.

- [ ] **Step 5: Run focused and existing validator regression tests**

```bash
python -m pytest tests/operator/test_contract_paths.py tests/release/test_validator_hardening.py tests/release/test_runtime_resource_ownership.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit the shared path primitive**

```bash
git add scripts/contract_paths.py scripts/validate_skill_package.py tests/operator/test_contract_paths.py
git commit -m "test: enforce exact contract path extraction"
```

---

### Task 3: Prove Git-object anchoring and dirty-worktree isolation before builder code exists

**Files:**
- Create: `scripts/operator_git.py`
- Create: `tests/operator/test_operator_git.py`

**Interfaces:**
- Produces:
  - `GitEntry(path: str, mode: int, blob_sha: str)`
  - `GitSource(repo: Path, commit: str)`
  - `GitSource.full_commit() -> str`
  - `GitSource.entries(prefix: str | None = None) -> tuple[GitEntry, ...]`
  - `GitSource.read_bytes(path: str) -> bytes`
  - `sha256_bytes(data: bytes) -> str`
- Consumers: builder, index generator, source-anchored validator.

This task establishes the foundations for assertions 16, 17 and 19 before the builder is implemented.

- [ ] **Step 1: Write tests that create a real temporary Git repository and then dirty its working tree**

```python
from pathlib import Path
import subprocess

from scripts.operator_git import GitSource, sha256_bytes


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], check=True, text=True, capture_output=True)
    return result.stdout.strip()


def _committed_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "VERSION").write_bytes(b"4.0.0-alpha.0\n")
    (repo / "contract.md").write_bytes(b"canonical\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")
    return repo, _git(repo, "rev-parse", "HEAD")


def test_git_source_reads_committed_blob_not_dirty_worktree(tmp_path):
    repo, commit = _committed_repo(tmp_path)
    source = GitSource(repo, commit)
    (repo / "contract.md").write_bytes(b"dirty\r\n")
    assert source.read_bytes("contract.md") == b"canonical\n"


def test_git_source_resolves_full_commit_and_real_blob_identity(tmp_path):
    repo, commit = _committed_repo(tmp_path)
    source = GitSource(repo, commit[:8])
    assert source.full_commit() == commit
    entry = next(e for e in source.entries() if e.path == "contract.md")
    actual_blob = _git(repo, "rev-parse", f"{commit}:contract.md")
    assert entry.blob_sha == actual_blob
    assert sha256_bytes(source.read_bytes("contract.md")) == sha256_bytes(b"canonical\n")
```

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_operator_git.py -q
```

Expected: import failure for `scripts.operator_git`.

- [ ] **Step 3: Implement immutable Git reads**

Use subprocess argument arrays only; never shell interpolation.

```python
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class GitEntry:
    path: str
    mode: int
    blob_sha: str


def sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


class GitSource:
    def __init__(self, repo: Path | str, commit: str):
        self.repo = Path(repo).resolve()
        self.commit = commit

    def _run(self, *args: str, text: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=text,
        )

    def full_commit(self) -> str:
        return self._run("rev-parse", f"{self.commit}^{{commit}}", text=True).stdout.strip()

    def entries(self, prefix: str | None = None) -> tuple[GitEntry, ...]:
        commit = self.full_commit()
        args = ["ls-tree", "-r", "-z", commit]
        if prefix:
            args.extend(["--", prefix])
        raw = self._run(*args).stdout
        entries: list[GitEntry] = []
        for record in raw.split(b"\0"):
            if not record:
                continue
            meta, path = record.split(b"\t", 1)
            mode, kind, blob = meta.decode("ascii").split()
            if kind != "blob":
                continue
            entries.append(GitEntry(path.decode("utf-8"), int(mode, 8), blob))
        return tuple(sorted(entries, key=lambda item: item.path))

    def read_bytes(self, path: str) -> bytes:
        commit = self.full_commit()
        return self._run("show", f"{commit}:{path}").stdout
```

- [ ] **Step 4: Run the Git anchoring tests**

```bash
python -m pytest tests/operator/test_operator_git.py -q
```

Expected: PASS, including the dirty-worktree case.

- [ ] **Step 5: Commit the Git source primitive**

```bash
git add scripts/operator_git.py tests/operator/test_operator_git.py
git commit -m "feat: add immutable Git object source"
```

---

### Task 4: Prove deterministic ZIP serialization before builder code exists

**Files:**
- Create: `scripts/deterministic_zip.py`
- Create: `tests/operator/test_deterministic_zip.py`

**Interfaces:**
- Consumes: artifact entry bytes and Git-style file modes.
- Produces:
  - `ArchiveEntry(path: str, data: bytes, mode: int = 0o100644)`
  - `write_deterministic_zip(path: Path, entries: Iterable[ArchiveEntry]) -> str` returning uppercase/lowercase consistently chosen SHA-256; use lowercase in code and reports.

This task establishes the low-level proof needed by assertion 14 before the builder exists.

- [ ] **Step 1: Write deterministic archive tests**

```python
from scripts.deterministic_zip import ArchiveEntry, write_deterministic_zip


def test_same_entries_produce_same_zip_hash_regardless_of_input_order(tmp_path):
    entries_a = [
        ArchiveEntry("b.txt", b"B\n", 0o100644),
        ArchiveEntry("a.txt", b"A\n", 0o100755),
    ]
    entries_b = list(reversed(entries_a))
    hash_a = write_deterministic_zip(tmp_path / "a.zip", entries_a)
    hash_b = write_deterministic_zip(tmp_path / "b.zip", entries_b)
    assert hash_a == hash_b
    assert (tmp_path / "a.zip").read_bytes() == (tmp_path / "b.zip").read_bytes()


def test_changed_content_changes_zip_hash(tmp_path):
    first = write_deterministic_zip(tmp_path / "a.zip", [ArchiveEntry("a.txt", b"A")])
    second = write_deterministic_zip(tmp_path / "b.zip", [ArchiveEntry("a.txt", b"B")])
    assert first != second
```

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_deterministic_zip.py -q
```

Expected: import failure.

- [ ] **Step 3: Implement deterministic ZIP metadata**

```python
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

_FIXED_TIME = (1980, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class ArchiveEntry:
    path: str
    data: bytes
    mode: int = 0o100644


def _zip_info(entry: ArchiveEntry) -> ZipInfo:
    info = ZipInfo(entry.path, date_time=_FIXED_TIME)
    info.create_system = 3
    permission = 0o755 if entry.mode & 0o111 else 0o644
    info.external_attr = (0o100000 | permission) << 16
    info.compress_type = ZIP_DEFLATED
    info.flag_bits |= 0x800
    info.extra = b""
    info.comment = b""
    return info


def write_deterministic_zip(path: Path, entries: Iterable[ArchiveEntry]) -> str:
    ordered = sorted(entries, key=lambda item: item.path)
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
        for entry in ordered:
            archive.writestr(_zip_info(entry), entry.data, compress_type=ZIP_DEFLATED, compresslevel=9)
    return sha256(path.read_bytes()).hexdigest()
```

- [ ] **Step 4: Run deterministic archive tests twice**

```bash
python -m pytest tests/operator/test_deterministic_zip.py -q
python -m pytest tests/operator/test_deterministic_zip.py -q
```

Expected: PASS both times.

- [ ] **Step 5: Commit deterministic archive support**

```bash
git add scripts/deterministic_zip.py tests/operator/test_deterministic_zip.py
git commit -m "feat: add deterministic ZIP primitive"
```

---

### Task 5: Generate the module capability index only from canonical frontmatter

**Files:**
- Create: `scripts/operator_index.py`
- Create: `tests/operator/test_operator_index.py`

**Interfaces:**
- Produces:
  - `parse_frontmatter(data: bytes) -> dict[str, object]`
  - `ModuleDescriptor(name: str, description: str)`
  - `render_module_index(modules: Iterable[ModuleDescriptor]) -> bytes`
- Consumer: operator builder and validator.

- [ ] **Step 1: Write source-equivalence tests**

```python
from scripts.operator_index import ModuleDescriptor, parse_frontmatter, render_module_index


def test_parse_frontmatter_preserves_name_and_description():
    raw = b"---\nname: recipe-engineering\ndescription: Exact description.\n---\n# Body\n"
    assert parse_frontmatter(raw) == {
        "name": "recipe-engineering",
        "description": "Exact description.",
    }


def test_render_index_is_deterministic_and_does_not_paraphrase():
    modules = [
        ModuleDescriptor("recipe-engineering", "Exact recipe description."),
        ModuleDescriptor("culinary-rnd", "Exact culinary description."),
    ]
    expected = (
        "<!-- GENERATED — DO NOT EDIT -->\n"
        "# Internal Capability Index\n\n"
        "- `culinary-rnd`\n"
        "  Exact culinary description.\n\n"
        "- `recipe-engineering`\n"
        "  Exact recipe description.\n"
    ).encode("utf-8")
    assert render_module_index(modules) == expected
```

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_operator_index.py -q
```

Expected: import failure.

- [ ] **Step 3: Implement strict frontmatter parsing and deterministic rendering**

Use `yaml.safe_load`; reject missing/empty `name` or `description` with `ValueError`. Sort rendering by `name` so source iteration order cannot affect bytes.

```python
from dataclasses import dataclass
from typing import Iterable
import yaml


@dataclass(frozen=True)
class ModuleDescriptor:
    name: str
    description: str


def parse_frontmatter(data: bytes) -> dict[str, object]:
    text = data.decode("utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    meta = yaml.safe_load(text[4:end]) or {}
    name = meta.get("name")
    description = meta.get("description")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("frontmatter name missing")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("frontmatter description missing")
    return {"name": name, "description": description}


def render_module_index(modules: Iterable[ModuleDescriptor]) -> bytes:
    lines = ["<!-- GENERATED — DO NOT EDIT -->", "# Internal Capability Index", ""]
    for module in sorted(modules, key=lambda item: item.name):
        lines.extend([f"- `{module.name}`", f"  {module.description}", ""])
    return ("\n".join(lines).rstrip() + "\n").encode("utf-8")
```

- [ ] **Step 4: Run index tests**

```bash
python -m pytest tests/operator/test_operator_index.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the generated-index primitive**

```bash
git add scripts/operator_index.py tests/operator/test_operator_index.py
git commit -m "feat: derive operator module index from source"
```

---

### Task 6: Define the operator target policy and pin the verified Evochia icon source

**Files:**
- Create: `release/operator/package_policy.yaml`
- Create: `tests/operator/test_operator_policy.py`

**Interfaces:**
- Consumes canonical `release/package_policy.yaml` and verified `company/evochia/brand/assets/logo-mark-42.png`.
- Produces a small target policy; it references canonical authority rather than reproducing all 11 domain IDs.

- [ ] **Step 1: Write failing policy/icon tests**

```python
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "release/operator/package_policy.yaml"


def test_operator_policy_references_canonical_package_policy():
    data = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    assert data["source_package_policy"] == "release/package_policy.yaml"
    assert data["orchestrator_skill"] == "chef-ai-pro-business"
    assert data["operator_name"] == "evochia-operator"
    assert data["template"] == "release/operator/SKILL.template.md"
    assert data["icon"]["source_path"] == "company/evochia/brand/assets/logo-mark-42.png"
    assert data["icon"]["artifact_path"] == "assets/evochia-operator-icon.png"
    assert "domain_skills" not in data


def test_icon_source_is_the_verified_evochia_git_blob():
    blob = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD:company/evochia/brand/assets/logo-mark-42.png"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    assert blob == "11676370669ef00c1ed6815300db240c5ce376f8"
```

- [ ] **Step 2: Verify RED because the operator policy does not exist**

```bash
python -m pytest tests/operator/test_operator_policy.py -q
```

Expected: FAIL on missing policy.

- [ ] **Step 3: Create a minimal target policy**

```yaml
schema_version: 1
source_package_policy: release/package_policy.yaml
operator_name: evochia-operator
orchestrator_skill: chef-ai-pro-business
template: release/operator/SKILL.template.md
routing: skills/chef-ai-pro-business/references/routing.yaml
module_index_path: references/module_index.md
icon:
  source_path: company/evochia/brand/assets/logo-mark-42.png
  artifact_path: assets/evochia-operator-icon.png
  expected_git_blob: 11676370669ef00c1ed6815300db240c5ce376f8
provenance_manifest_path: provenance/build_manifest.yaml
```

Do not duplicate the 11 domain IDs here; derive them from canonical `required_skills` minus the orchestrator.

- [ ] **Step 4: Run target-policy tests**

```bash
python -m pytest tests/operator/test_operator_policy.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the target policy**

```bash
git add release/operator/package_policy.yaml tests/operator/test_operator_policy.py
git commit -m "chore: define operator build target policy"
```

---

### Task 7: Build the source-anchored validator against handcrafted fixtures before the real builder

**Files:**
- Create: `scripts/validate_operator_package.py`
- Create: `tests/operator/test_operator_validator.py`

**Interfaces:**
- Consumes `GitSource`, `extract_contract_paths`, `parse_frontmatter`, `render_module_index`, canonical package policy and operator policy.
- Produces:
  - `validate_operator_artifact(artifact: Path, source_repo: Path, source_commit: str) -> list[str]`
  - CLI: `python scripts/validate_operator_package.py --artifact ... --source-repo ... --source-commit ...`

The test fixture must be a real temporary Git repository so source SHA and byte checks cannot be satisfied by mutating only the ZIP/manifest.

- [ ] **Step 1: Write a fixture factory that commits a minimal canonical source graph**

In the test file, create helper `_fixture_repo(tmp_path)` that commits:

```text
VERSION
release/package_policy.yaml
release/operator/package_policy.yaml
release/operator/SKILL.template.md
references/source_registry.yaml
references/example.md
skills/chef-ai-pro-business/references/routing.yaml
skills/alpha/SKILL.md
skills/alpha/references/a.md
skills/beta/SKILL.md
```

The canonical policy fixture has required skills `[chef-ai-pro-business, alpha, beta]` and both domain contracts have valid `name`/`description` frontmatter.

- [ ] **Step 2: Write tests for source anchoring and exact-path resolution before implementing the validator**

```python
def test_validator_rejects_module_and_manifest_tampered_together(tmp_path):
    repo, commit, artifact = make_valid_fixture_artifact(tmp_path)
    rewrite_zip_entry(artifact, "skills/alpha/MODULE.md", b"tampered\n")
    rewrite_manifest_hash_to_match_artifact(artifact, "skills/alpha/MODULE.md")
    issues = validate_operator_artifact(artifact, repo, commit)
    assert any("Git source bytes differ" in issue for issue in issues)


def test_validator_requires_exact_written_contract_path(tmp_path):
    repo, commit, artifact = make_valid_fixture_artifact(tmp_path)
    remove_zip_entry(artifact, "skills/alpha/references/a.md")
    add_zip_entry(artifact, "references/a.md", b"same bytes, wrong path\n")
    issues = validate_operator_artifact(artifact, repo, commit)
    assert any("missing exact referenced path: skills/alpha/references/a.md" in issue for issue in issues)


def test_validator_rejects_generated_index_not_equal_to_source_render(tmp_path):
    repo, commit, artifact = make_valid_fixture_artifact(tmp_path)
    rewrite_zip_entry(artifact, "references/module_index.md", b"manual index\n")
    issues = validate_operator_artifact(artifact, repo, commit)
    assert any("module index differs from canonical frontmatter render" in issue for issue in issues)
```

Also cover one root `SKILL.md`, exact expected module count, routing exact copy, manifest source commit, icon source identity, and forbidden patterns.

- [ ] **Step 3: Verify RED**

```bash
python -m pytest tests/operator/test_operator_validator.py -q
```

Expected: import failure for the validator.

- [ ] **Step 4: Implement ZIP loading and source policy derivation**

Core structure:

```python
from pathlib import Path
from zipfile import ZipFile
import argparse
import yaml

from operator_git import GitSource, sha256_bytes
from contract_paths import extract_contract_paths
from operator_index import ModuleDescriptor, parse_frontmatter, render_module_index


def _zip_files(artifact: Path) -> dict[str, bytes]:
    with ZipFile(artifact, "r") as archive:
        return {name: archive.read(name) for name in archive.namelist() if not name.endswith("/")}


def _canonical_domain_ids(source: GitSource) -> tuple[str, ...]:
    policy = yaml.safe_load(source.read_bytes("release/package_policy.yaml")) or {}
    required = tuple(policy.get("required_skills", ()))
    orchestrator = yaml.safe_load(source.read_bytes("release/operator/package_policy.yaml"))["orchestrator_skill"]
    return tuple(skill for skill in required if skill != orchestrator)
```

- [ ] **Step 5: Implement source-anchored exact-copy and index checks**

For every domain ID:

```python
source_path = f"skills/{skill_id}/SKILL.md"
artifact_path = f"skills/{skill_id}/MODULE.md"
source_bytes = source.read_bytes(source_path)
if files.get(artifact_path) != source_bytes:
    issues.append(f"Git source bytes differ: {artifact_path}")
```

Re-render the index from source frontmatter and compare actual bytes directly. Recompute `source_sha256` from `source.read_bytes(source_path)`, not from manifest values.

- [ ] **Step 6: Implement exact path validation using the shared extractor**

Scan root `SKILL.md`, all `MODULE.md`, and packaged authoritative Markdown under `references/` for tokens returned by `extract_contract_paths`. For each token, require exactly that POSIX path to exist in the artifact file map. Do not search by basename and do not rewrite prefixes.

Ignore the template placeholder `skills/<skill-id>/MODULE.md` because the extractor already rejects `<`/`>` tokens.

- [ ] **Step 7: Implement CLI exit semantics**

```python
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True, type=Path)
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    issues = validate_operator_artifact(args.artifact, args.source_repo, args.source_commit)
    if issues:
        print("Operator package validation: FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Operator package validation: PASS")
    return 0
```

- [ ] **Step 8: Run the validator tests**

```bash
python -m pytest tests/operator/test_operator_validator.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit the validator before the real build implementation**

```bash
git add scripts/validate_operator_package.py tests/operator/test_operator_validator.py
git commit -m "feat: add source-anchored operator validator"
```

---

### Task 8: Implement the `multi` target first and prove current package behavior is preserved

**Files:**
- Create: `scripts/build_skill_package.py`
- Create: `tests/operator/test_dual_build.py`

**Interfaces:**
- Consumes `GitSource`, `ArchiveEntry`, `write_deterministic_zip`, canonical `VERSION` and package policy.
- Produces:
  - `BuildResult(target: str, source_commit: str, version: str, artifact_path: Path, sha256: str)`
  - `build_package(repo: Path, source_commit: str, target: str, output_dir: Path) -> BuildResult`
  - CLI with `--target {multi,operator}`, `--source-commit`, `--source-repo`, `--output-dir`.

Implement only the multi branch in this task; the operator branch may raise a clear `NotImplementedError` until Task 9.

- [ ] **Step 1: Write failing integration tests for multi determinism and source-tree identity**

```python
def test_multi_build_is_deterministic_and_contains_canonical_skill_surface(tmp_path):
    commit = git_head(ROOT)
    first = build_package(ROOT, commit, "multi", tmp_path / "one")
    second = build_package(ROOT, commit, "multi", tmp_path / "two")
    assert first.sha256 == second.sha256
    assert first.artifact_path.read_bytes() == second.artifact_path.read_bytes()
    files = zip_file_map(first.artifact_path)
    assert len([p for p in files if p.endswith("/SKILL.md")]) == 12
    assert not [p for p in files if p.endswith("/MODULE.md")]
    assert files["VERSION"] == git_show(ROOT, commit, "VERSION")
```

Also dirty one tracked CSV in the worktree between two builds and assert the artifact hash remains unchanged for the same explicit commit.

- [ ] **Step 2: Verify RED before builder implementation**

```bash
python -m pytest tests/operator/test_dual_build.py -k multi -q
```

Expected: import failure for `scripts.build_skill_package`.

- [ ] **Step 3: Implement the public result type and filename logic**

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BuildResult:
    target: str
    source_commit: str
    version: str
    artifact_path: Path
    sha256: str


def _artifact_name(target: str, version: str, commit: str) -> str:
    short = commit[:7]
    if target == "multi":
        return f"chef-ai-pro-business-{version}-{short}-multi.zip"
    if target == "operator":
        return f"evochia-operator-{version}-{short}-operator.zip"
    raise ValueError(f"unsupported target: {target}")
```

- [ ] **Step 4: Implement multi as committed Git-tree materialization**

Build `ArchiveEntry` instances from `GitSource.entries()` and `GitSource.read_bytes(entry.path)`. Validate forbidden tracked paths from canonical `release/package_policy.yaml` before writing. Do not read file contents through `Path.read_bytes()` from the worktree.

- [ ] **Step 5: Run multi integration tests including dirty-worktree isolation**

```bash
python -m pytest tests/operator/test_dual_build.py -k multi -q
```

Expected: PASS.

- [ ] **Step 6: Run the existing package validator against a materialized/extracted multi artifact in the test**

Add a test that extracts the multi ZIP to `tmp_path / "multi"` and invokes:

```bash
python scripts/validate_skill_package.py <extracted-root>
```

Expected subprocess return code: 0 and stdout contains `Skill package validation: PASS`.

- [ ] **Step 7: Commit the multi build target**

```bash
git add scripts/build_skill_package.py tests/operator/test_dual_build.py
git commit -m "feat: add deterministic multi-skill build target"
```

---

### Task 9: Implement operator resource closure, exact-byte module projection, index, icon and provenance

**Files:**
- Modify: `scripts/build_skill_package.py`
- Modify: `tests/operator/test_dual_build.py`

**Interfaces:**
- Consumes all primitives from Tasks 2–6.
- Produces the complete operator artifact and `provenance/build_manifest.yaml`.

- [ ] **Step 1: Write failing operator topology tests before operator builder code**

```python
def test_operator_build_has_one_public_skill_and_exact_domain_modules(tmp_path):
    commit = git_head(ROOT)
    result = build_package(ROOT, commit, "operator", tmp_path)
    files = zip_file_map(result.artifact_path)
    assert [p for p in files if p.endswith("/SKILL.md") or p == "SKILL.md"] == ["SKILL.md"]
    expected_ids = canonical_domain_ids(ROOT, commit)
    assert sorted(p for p in files if p.endswith("/MODULE.md")) == [
        f"skills/{skill_id}/MODULE.md" for skill_id in sorted(expected_ids)
    ]
    for skill_id in expected_ids:
        assert files[f"skills/{skill_id}/MODULE.md"] == git_show(ROOT, commit, f"skills/{skill_id}/SKILL.md")
    assert "skills/chef-ai-pro-business/SKILL.md" not in files
```

- [ ] **Step 2: Add failing tests for full canonical references, routing path, generated index and icon mapping**

```python
def test_operator_preserves_canonical_reference_topology(tmp_path):
    commit = git_head(ROOT)
    result = build_package(ROOT, commit, "operator", tmp_path)
    files = zip_file_map(result.artifact_path)
    source_reference_paths = git_paths_under(ROOT, commit, "references/")
    assert set(source_reference_paths).issubset(files)
    assert files["skills/chef-ai-pro-business/references/routing.yaml"] == git_show(
        ROOT, commit, "skills/chef-ai-pro-business/references/routing.yaml"
    )
    assert "references/module_index.md" in files
    assert files["assets/evochia-operator-icon.png"] == git_show(
        ROOT, commit, "company/evochia/brand/assets/logo-mark-42.png"
    )
```

- [ ] **Step 3: Verify RED because operator target is not implemented**

```bash
python -m pytest tests/operator/test_dual_build.py -k operator -q
```

Expected: `NotImplementedError` or explicit unsupported operator path.

- [ ] **Step 4: Implement canonical domain derivation**

Read `release/package_policy.yaml` from `GitSource`. Domain IDs are exactly `required_skills` minus `orchestrator_skill` from `release/operator/package_policy.yaml`. Assert the source policy currently yields 11 domain IDs; fail the build if it does not.

- [ ] **Step 5: Implement resource closure without a second hand-authored authority list**

Seed artifact paths from:

1. `VERSION`.
2. Entire source `references/` subtree.
3. Every canonical domain skill-local subtree except source `SKILL.md`; project that `SKILL.md` bytes to `MODULE.md`.
4. Canonical routing file at its unchanged path.
5. `resource_roots` and `exact_resources` in `release/runtime_resource_ownership.yaml`.
6. Exact backticked paths discovered from root operator template, all domain source contracts and included authoritative Markdown; if a discovered token names a directory prefix in the Git tree, include its full subtree, otherwise include the exact file.
7. Verified icon source mapped to `assets/evochia-operator-icon.png`.

Iterate exact-path discovery to a fixed point for newly included Markdown contracts. If a referenced exact path does not exist in the selected Git commit, fail the build; never search by basename or rewrite the reference.

- [ ] **Step 6: Materialize generated content only at the approved paths**

Generated files are exactly:

- root `SKILL.md` from `release/operator/SKILL.template.md` bytes,
- `references/module_index.md` from source frontmatter,
- `provenance/build_manifest.yaml`.

Every other included file is copied from Git object bytes, with the sole path projection `skills/<id>/SKILL.md` → `skills/<id>/MODULE.md` for the 11 domain contracts.

- [ ] **Step 7: Generate provenance using stable ordered YAML data**

Manifest structure:

```yaml
schema_version: 1
target: operator
source_commit: <40-char sha>
source_version: <VERSION value>
operator_name: evochia-operator
builder:
  path: scripts/build_skill_package.py
  source_sha256: <sha256 of committed builder bytes>
root_template:
  source_path: release/operator/SKILL.template.md
  source_sha256: <sha256>
  projected_path: SKILL.md
files:
  - projected_path: skills/recipe-engineering/MODULE.md
    relation: EXACT_BYTE_COPY
    source_path: skills/recipe-engineering/SKILL.md
    source_sha256: <sha256>
    projected_sha256: <same sha256>
```

Sort `files` by `projected_path` before `yaml.safe_dump(..., sort_keys=True, allow_unicode=True)`. The manifest does not contain the ZIP hash.

- [ ] **Step 8: Run operator build tests**

```bash
python -m pytest tests/operator/test_dual_build.py -k operator -q
```

Expected: PASS.

- [ ] **Step 9: Commit the operator projection**

```bash
git add scripts/build_skill_package.py tests/operator/test_dual_build.py
git commit -m "feat: build deterministic Evochia Operator package"
```

---

### Task 10: Close all 19 validator assertions end-to-end against the actual builder

**Files:**
- Modify: `tests/operator/test_operator_validator.py`
- Modify: `tests/operator/test_dual_build.py`
- Modify: `scripts/validate_operator_package.py` only where integration reveals a concrete missing assertion.

**Interfaces:**
- Consumes real operator artifact from `build_package`.
- Produces release-grade source-anchored validation evidence.

- [ ] **Step 1: Add a table-driven assertion coverage test**

Create one named test per design assertion rather than one giant test. Names must map visibly to assertions, for example:

```python
def test_a01_exactly_one_public_skill(...): ...
def test_a05_modules_are_git_source_exact_byte_copy(...): ...
def test_a08_index_equals_source_frontmatter_render(...): ...
def test_a10_exact_written_paths_resolve(...): ...
def test_a14_two_operator_builds_have_identical_zip_sha(...): ...
def test_a16_manifest_source_hashes_match_real_git_objects(...): ...
def test_a17_exact_copy_bytes_match_real_git_objects(...): ...
def test_a19_dirty_worktree_does_not_change_explicit_commit_build(...): ...
```

- [ ] **Step 2: Add the critical adversarial mutation test for assertions 16/17**

Build a valid artifact, then create a mutated copy in which both the `MODULE.md` bytes and its manifest projected/source hashes are updated to agree with each other. Validation MUST still fail because the Git object at `source_commit:source_path` did not change.

- [ ] **Step 3: Add the exact-path adversarial test for assertion 10**

Delete `skills/culinary-rnd/references/research_protocol.md` from a copy of the artifact and place identical bytes at another path. Validation MUST fail specifically on the exact written canonical path.

Repeat for:

- `skills/kitchen-event-operations/references/event_lifecycle.md`
- `skills/evochia-market-intelligence/references/intelligence_policy.yaml`

- [ ] **Step 4: Add full integration determinism tests for assertion 14 and dirty-worktree isolation for assertion 19**

Build operator twice from the same commit into different directories and compare both SHA-256 and bytes. Then modify a tracked working-tree file without committing it and build again from the same explicit commit; the hash MUST remain identical. Restore the worktree in a `finally` block or use a temporary clone/worktree fixture so the test cannot leave the developer checkout dirty.

- [ ] **Step 5: Run all operator tests**

```bash
python -m pytest tests/operator -q
```

Expected: PASS with zero xfails/skips used to conceal missing builder behavior.

- [ ] **Step 6: Run source-package regression tests**

```bash
python -m pytest tests/release tests/routing tests/parity -q
```

Expected: PASS.

- [ ] **Step 7: Commit validator integration coverage**

```bash
git add scripts/validate_operator_package.py tests/operator/test_operator_validator.py tests/operator/test_dual_build.py
git commit -m "test: verify operator provenance and determinism end to end"
```

---

### Task 11: Preserve the open surface blocker and integrate dual-build verification into CI

**Files:**
- Create: `tests/operator/test_release_gate_preservation.py`
- Modify: `.github/workflows/verify.yml`

**Interfaces:**
- Produces CI evidence that both artifacts build and the operator artifact validates against the same commit.
- Explicitly does NOT mark `openai_surface_install_scan` complete.

- [ ] **Step 1: Write a release-gate preservation test before touching CI**

```python
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
READINESS = ROOT / "release/release_readiness.yaml"


def test_operator_builder_does_not_close_surface_release_blocker():
    data = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    blocker = next(item for item in data["blockers"] if item["id"] == "openai_surface_install_scan")
    assert blocker["status"] == "NOT_RUN"
    assert blocker["required_before_final_release"] is True
    assert data["final_release_status"] == "BLOCKED"
    assert data["may_claim_production_ready"] is False
```

- [ ] **Step 2: Run the gate test and preserve the current blocker state**

```bash
python -m pytest tests/operator/test_release_gate_preservation.py -q
```

Expected: PASS without modifying `release/release_readiness.yaml`.

- [ ] **Step 3: Add CI build/validate smoke commands after the existing validators**

Add to `.github/workflows/verify.yml`:

```yaml
      - name: Build deterministic multi and operator packages
        run: |
          mkdir -p /tmp/chef-ai-build-a /tmp/chef-ai-build-b
          python scripts/build_skill_package.py --target multi --source-repo . --source-commit "$GITHUB_SHA" --output-dir /tmp/chef-ai-build-a
          python scripts/build_skill_package.py --target operator --source-repo . --source-commit "$GITHUB_SHA" --output-dir /tmp/chef-ai-build-a
          python scripts/build_skill_package.py --target operator --source-repo . --source-commit "$GITHUB_SHA" --output-dir /tmp/chef-ai-build-b

      - name: Validate operator package against Git source
        run: |
          OPERATOR_ZIP=$(find /tmp/chef-ai-build-a -maxdepth 1 -name 'evochia-operator-*-operator.zip' -print -quit)
          python scripts/validate_operator_package.py --artifact "$OPERATOR_ZIP" --source-repo . --source-commit "$GITHUB_SHA"

      - name: Verify repeated operator build hash
        run: |
          A=$(sha256sum /tmp/chef-ai-build-a/evochia-operator-*-operator.zip | awk '{print $1}')
          B=$(sha256sum /tmp/chef-ai-build-b/evochia-operator-*-operator.zip | awk '{print $1}')
          test "$A" = "$B"
```

Use the shell glob only after verifying each directory contains exactly one operator ZIP; add `test "$(find ... | wc -l)" -eq 1` before computing hashes so ambiguous output cannot pass accidentally.

- [ ] **Step 4: Run the full local CI-equivalent command set**

```bash
python -m pytest -q
python evals/run_evals.py
python scripts/validate_skill_package.py
python scripts/validate_repo_hygiene.py .
python scripts/validate_parity_coverage.py
python scripts/validate_source_registry.py
python scripts/validate_doctrine_integrity.py
```

Expected: all commands exit 0.

- [ ] **Step 5: Commit CI integration**

```bash
git add .github/workflows/verify.yml tests/operator/test_release_gate_preservation.py
git commit -m "ci: verify deterministic dual skill builds"
```

---

### Task 12: Produce the post-builder `C1` artifacts and stop at the surface-test handoff

**Files:**
- No source file changes required unless verification exposes a real implementation defect.
- Output artifacts: untracked/local `dist/` or another explicit output directory.

**Interfaces:**
- Produces the two same-commit artifacts required for the surface experiment.
- Hands off to the mandatory complete `MULTI(C1)` A→H run before operator acceptance.

- [ ] **Step 1: Verify the implementation worktree is clean and capture the exact post-builder commit**

```bash
git status --short
git rev-parse HEAD
```

Expected: no tracked/untracked implementation residue other than an intentionally ignored output directory; record the full 40-character commit as `C1`.

- [ ] **Step 2: Build both targets from exactly `C1`**

```bash
mkdir -p dist
python scripts/build_skill_package.py --target multi --source-repo . --source-commit "$(git rev-parse HEAD)" --output-dir dist
python scripts/build_skill_package.py --target operator --source-repo . --source-commit "$(git rev-parse HEAD)" --output-dir dist
```

Expected filenames:

```text
chef-ai-pro-business-4.0.0-alpha.0-<C1-short>-multi.zip
evochia-operator-4.0.0-alpha.0-<C1-short>-operator.zip
```

- [ ] **Step 3: Validate the operator artifact against the same Git commit**

```bash
python scripts/validate_operator_package.py \
  --artifact dist/evochia-operator-4.0.0-alpha.0-$(git rev-parse --short=7 HEAD)-operator.zip \
  --source-repo . \
  --source-commit "$(git rev-parse HEAD)"
```

Expected: `Operator package validation: PASS`.

- [ ] **Step 4: Record artifact hashes without changing release readiness**

```bash
sha256sum dist/*-multi.zip dist/*-operator.zip
```

Record both SHA-256 values in the execution report/PR description. Do not edit `release/release_readiness.yaml` based on build success.

- [ ] **Step 5: Perform the mandatory surface order exactly as specified**

1. Install `MULTI(C1)` and confirm 12 visible Skills / no blocking scan warning.
2. Run the **complete A→H suite** through `@chef-ai-pro-business` for the primary multi baseline. This is mandatory and closes the still-open surface blocker only if the evidence passes the release criteria.
3. Install `OPERATOR(C1)` and require exactly one visible `evochia-operator`, no exposed module names, and record icon binding/scan behavior.
4. Run the same complete A→H user tasks through `@evochia-operator`.
5. Compare router-to-router transcripts. Optional direct-domain runs are labeled `DIRECT` and excluded from gating thresholds.

Pre-committed operator differential thresholds remain:

```text
BLOCKING failures:              0
new MAJOR regressions:          0
new PASS_WITH_CONCERN:         <= 2
new NEAR_MISS in B1:            0
new NEAR_MISS in D2:            0
new NEAR_MISS in Block F:       0
```

If `MULTI(C1)` fails Block F, classify it first as a multi-skill baseline failure and do not remediate the operator builder without differential evidence.

- [ ] **Step 6: Stop before release-readiness mutation**

Do not mark `openai_surface_install_scan` complete, do not claim production readiness, and do not merge any release-status change until the surface transcripts and install evidence have been reviewed separately.

---

## Final Verification Checklist

Before presenting the implementation as ready for surface testing, execute and retain output for all of the following:

```bash
python -m pytest tests/operator -q
python -m pytest -q
python evals/run_evals.py
python scripts/validate_skill_package.py
python scripts/validate_repo_hygiene.py .
python scripts/validate_parity_coverage.py
python scripts/validate_source_registry.py
python scripts/validate_doctrine_integrity.py
```

Then build the two artifacts twice from the same explicit commit and verify repeated operator ZIP hashes are identical. Run the release-grade operator validator with `--source-repo` and `--source-commit`. Confirm via `git diff <implementation-base>..HEAD -- skills references/source_registry.yaml` that no existing source Skill contract or canonical source registry changed; separately verify the routing file hash against the implementation base.

No completion claim is valid from test summaries alone; the actual command outputs and artifact hashes are the evidence.
