# Evochia Operator Dual-Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic dual-build system that preserves the canonical 12-Skill source architecture while producing both a 12-public-Skill multi artifact and a one-public-Skill `@evochia-operator` artifact with 11 exact-byte internal module projections.

**Architecture:** The builder reads committed Git objects from an explicit source commit. The multi target materializes the canonical Git tree; the operator target uses one source-controlled root template, projects the 11 domain `SKILL.md` files byte-for-byte as `skills/<id>/MODULE.md`, preserves canonical paths, generates only the module index and provenance metadata, and writes a deterministic ZIP. A dedicated source-anchored validator independently compares artifact bytes and manifest hashes with the real Git objects at the declared source commit.

**Tech Stack:** Python 3.12; standard-library `subprocess`, `hashlib`, `zipfile`, `pathlib`, `dataclasses`, `re`; PyYAML 6.x; pytest 9.x; Git CLI; existing repository validators and GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-04-evochia-operator-dual-build-design.md`

## Global Constraints

- Canonical design base: `9cab252e8757b35f6501b178c06943b0e82b398a`.
- Public operator ID: `evochia-operator`; invocation: `@evochia-operator`.
- Existing `skills/*/SKILL.md`, canonical routing, source registry, policies, data and doctrine are not changed to make the operator build work.
- Domain projection is exactly `skills/<id>/SKILL.md` → `skills/<id>/MODULE.md`, relation `EXACT_BYTE_COPY`, including frontmatter and line endings.
- `references/module_index.md` is generated from canonical `name` + `description` frontmatter and is added to the complete canonical `references/` subtree.
- Root `SKILL.md` comes only from `release/operator/SKILL.template.md`.
- Supported targets are exactly `multi` and `operator`.
- Builder source inputs are Git objects at an explicit full commit SHA; ordinary dirty-worktree changes must not change the artifact.
- Release-grade validation requires `--artifact`, `--source-repo`, and `--source-commit` and verifies actual Git objects.
- `openai_surface_install_scan` remains release-blocking until a complete post-builder `MULTI(C1)` A→H surface run is reviewed.
- Primary differential is router-to-router: `@chef-ai-pro-business` vs `@evochia-operator`; direct domain-Skill runs are optional `DIRECT` diagnostics only.
- No Phase 14–16 implementation or unrelated refactor belongs here.

## File Map

**Create**
- `release/operator/SKILL.template.md` — only new behavioral instruction surface.
- `release/operator/package_policy.yaml` — operator target config; references canonical authorities.
- `scripts/operator_support/__init__.py` — makes shared build primitives importable in tests and direct CLI wrappers.
- `scripts/operator_support/contract_paths.py` — exact Markdown path extraction.
- `scripts/operator_support/git_source.py` — immutable Git-object access.
- `scripts/operator_support/deterministic_zip.py` — reproducible ZIP writer.
- `scripts/operator_support/module_index.py` — frontmatter parser/index renderer.
- `scripts/build_skill_package.py` — dual-target build CLI.
- `scripts/validate_operator_package.py` — source-anchored operator validator CLI.
- `tests/operator/test_operator_template.py`
- `tests/operator/test_contract_paths.py`
- `tests/operator/test_git_source.py`
- `tests/operator/test_deterministic_zip.py`
- `tests/operator/test_module_index.py`
- `tests/operator/test_operator_policy.py`
- `tests/operator/test_operator_validator.py`
- `tests/operator/test_dual_build.py`
- `tests/operator/test_release_gate_preservation.py`

**Modify**
- `scripts/validate_skill_package.py` — import the shared extractor while preserving current source-package path-resolution behavior.
- `.github/workflows/verify.yml` — deterministic dual-build/validation smoke steps.

**Do not modify**
- Existing `skills/*/SKILL.md`.
- `skills/chef-ai-pro-business/references/routing.yaml`.
- `references/source_registry.yaml`.
- `release/release_readiness.yaml` before surface evidence exists.

---

### Task 1: Define and review the operator root template before any builder code

**Files:**
- Create: `release/operator/SKILL.template.md`
- Create: `tests/operator/test_operator_template.py`

**Interfaces:**
- Produces the exact bytes later materialized as operator root `SKILL.md`.
- References canonical routing, source authority and generated module index; owns orchestration only.

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "release/operator/SKILL.template.md"


def frontmatter(text: str) -> dict:
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    return yaml.safe_load(text[4:end]) or {}


def test_operator_template_is_router_not_policy_monolith():
    text = TEMPLATE.read_text(encoding="utf-8")
    meta = frontmatter(text)
    assert meta["name"] == "evochia-operator"
    assert meta["description"]
    assert "smallest sufficient" in text.lower()
    assert "skills/<skill-id>/MODULE.md" in text
    assert "skills/chef-ai-pro-business/references/routing.yaml" in text
    assert "references/module_index.md" in text
    assert "references/source_registry.yaml" in text
    assert "food-safety-allergens" in text
    assert all(token in text for token in ("INTERNAL", "OPERATIONS", "CLIENT-SAFE"))
    assert "DRAFT_OR_HANDOFF_NO_FAKE_EXECUTION" in text
    assert "FnB Central" in text
    assert "system of record" in text.lower()
    assert "routing transcript" in text.lower()


def test_operator_template_does_not_duplicate_rate_policy():
    text = TEMPLATE.read_text(encoding="utf-8")
    forbidden = ["15+", "6–14", "0–5", "+20%", "+40%", "6500", "6,500"]
    assert not [token for token in forbidden if token in text]
```

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_operator_template.py -q
```

Expected: FAIL because the template is absent.

- [ ] **Step 3: Create `release/operator/SKILL.template.md` with this reviewed baseline**

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
- Use canonical routing first. Consult the generated module index only when the route is not sufficiently clear. Read only the smallest sufficient module set.

## Orchestration Rules
Classify generic-F&B versus Evochia context, safety risk, freshness need, tool availability and output audience. Preserve distinctions among facts, approved data, external evidence, estimates, assumptions and needs-review items. Do not expose the internal routing transcript.

Safety authority outranks creativity, commercial optimization and presentation. When allergen or food-safety stakes are material, `food-safety-allergens` is a mandatory hard gate and its blocker state propagates.

Choose exactly one audience boundary unless explicitly asked for multiple:
- `INTERNAL`: costs, margins, assumptions, supplier evidence and strategy may be present.
- `OPERATIONS`: production, staffing, equipment, allergens, run sheets and service notes.
- `CLIENT-SAFE`: approved external concept/menu/scope/fee/terms only; never leak INTERNAL economics or strategy.

For controlled external execution, preserve the canonical execution contract. Consequential writes remain propose-then-confirm and success may be claimed only from an actual backend/tool response. If the required execution tool is unavailable, preserve `DRAFT_OR_HANDOFF_NO_FAKE_EXECUTION`; never simulate a successful write.

FnB Central remains the persistent F&B system of record. This operator does not create duplicate persistent state and does not describe mock/in-memory integration scaffolds as durable production persistence.

## Composition
Return the requested answer or artifact in the requested audience boundary. Use domain contracts and canonical resources for substantive rules; do not restate current rates, safety doctrine, supplier data or company policy here when a canonical source already owns them.
```

- [ ] **Step 4: Verify GREEN**

```bash
python -m pytest tests/operator/test_operator_template.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add release/operator/SKILL.template.md tests/operator/test_operator_template.py
git commit -m "feat: define Evochia Operator root contract"
```

---

### Task 2: Implement the exact contract-path extractor as its own tested unit

**Files:**
- Create: `scripts/operator_support/__init__.py`
- Create: `scripts/operator_support/contract_paths.py`
- Create: `tests/operator/test_contract_paths.py`
- Modify: `scripts/validate_skill_package.py`

**Interfaces:**
- Produces `extract_contract_paths(text: str) -> tuple[str, ...]`.
- Used by source validator, operator closure logic and operator validator.

- [ ] **Step 1: Write failing regression tests for the three paths that exposed the design bug**

```python
from scripts.operator_support.contract_paths import extract_contract_paths


def test_extracts_exact_repo_paths_without_rewriting():
    text = """
`skills/culinary-rnd/references/research_protocol.md`
`skills/kitchen-event-operations/references/event_lifecycle.md`
`skills/evochia-market-intelligence/references/intelligence_policy.yaml`
`references/operations/output_router_templates_v2_1.md`
"""
    assert extract_contract_paths(text) == (
        "references/operations/output_router_templates_v2_1.md",
        "skills/culinary-rnd/references/research_protocol.md",
        "skills/evochia-market-intelligence/references/intelligence_policy.yaml",
        "skills/kitchen-event-operations/references/event_lifecycle.md",
    )


def test_rejects_non_repository_tokens():
    text = "`https://x/a/b` `templates/*/x.md` `skills/<skill-id>/MODULE.md` `../secret/x` `plain-token`"
    assert extract_contract_paths(text) == ()
```

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_contract_paths.py -q
```

Expected: import failure.

- [ ] **Step 3: Implement `extract_contract_paths`**

```python
from pathlib import PurePosixPath
import re

_BACKTICK = re.compile(r"`([^`\n]+)`")
_META = set("*{}<>|")


def extract_contract_paths(text: str) -> tuple[str, ...]:
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
```

- [ ] **Step 4: Reuse it in `validate_skill_package.py` without breaking direct CLI or importlib tests**

At the top of the existing script use a dual-context import:

```python
try:
    from scripts.operator_support.contract_paths import extract_contract_paths
except ModuleNotFoundError:  # direct: python scripts/validate_skill_package.py
    from operator_support.contract_paths import extract_contract_paths
```

Replace only the private extraction loop; preserve the existing source-validator resolution behavior:

```python
for ref in extract_contract_paths(text):
    candidates = [root / ref, skill_dir / ref]
    if not any(path.exists() for path in candidates):
        issues.append(f"{skill_name}: broken referenced path {ref}")
```

- [ ] **Step 5: Run focused plus existing validator tests**

```bash
python -m pytest tests/operator/test_contract_paths.py tests/release/test_validator_hardening.py tests/release/test_runtime_resource_ownership.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/operator_support/__init__.py scripts/operator_support/contract_paths.py scripts/validate_skill_package.py tests/operator/test_contract_paths.py
git commit -m "test: enforce exact contract path extraction"
```

---

### Task 3: Prove Git-object anchoring and dirty-worktree isolation before builder implementation

**Files:**
- Create: `scripts/operator_support/git_source.py`
- Create: `tests/operator/test_git_source.py`

**Interfaces:**
- `GitEntry(path: str, mode: int, blob_sha: str)`
- `GitSource(repo, commit).full_commit() -> str`
- `GitSource.entries(prefix=None) -> tuple[GitEntry, ...]`
- `GitSource.read_bytes(path) -> bytes`
- `sha256_bytes(data) -> str`

This establishes the foundations for assertions 16, 17 and 19 before builder code exists.

- [ ] **Step 1: Write tests using a real temporary Git repository**

```python
from pathlib import Path
import subprocess
from scripts.operator_support.git_source import GitSource, sha256_bytes


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True, capture_output=True).stdout.strip()


def make_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    (repo / "contract.md").write_bytes(b"canonical\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture")
    return repo, git(repo, "rev-parse", "HEAD")


def test_reads_committed_blob_not_dirty_worktree(tmp_path):
    repo, commit = make_repo(tmp_path)
    source = GitSource(repo, commit)
    (repo / "contract.md").write_bytes(b"dirty\r\n")
    assert source.read_bytes("contract.md") == b"canonical\n"


def test_blob_identity_matches_git_object(tmp_path):
    repo, commit = make_repo(tmp_path)
    source = GitSource(repo, commit[:8])
    assert source.full_commit() == commit
    entry = next(e for e in source.entries() if e.path == "contract.md")
    assert entry.blob_sha == git(repo, "rev-parse", f"{commit}:contract.md")
    assert sha256_bytes(source.read_bytes("contract.md")) == sha256_bytes(b"canonical\n")
```

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_git_source.py -q
```

- [ ] **Step 3: Implement immutable Git reads with subprocess argument arrays only**

```python
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

    def _run(self, *args: str, text: bool = False):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, text=text)

    def full_commit(self) -> str:
        return self._run("rev-parse", f"{self.commit}^{{commit}}", text=True).stdout.strip()

    def entries(self, prefix: str | None = None) -> tuple[GitEntry, ...]:
        args = ["ls-tree", "-r", "-z", self.full_commit()]
        if prefix:
            args += ["--", prefix]
        raw = self._run(*args).stdout
        out = []
        for record in raw.split(b"\0"):
            if not record:
                continue
            meta, path = record.split(b"\t", 1)
            mode, kind, blob = meta.decode("ascii").split()
            if kind == "blob":
                out.append(GitEntry(path.decode("utf-8"), int(mode, 8), blob))
        return tuple(sorted(out, key=lambda item: item.path))

    def read_bytes(self, path: str) -> bytes:
        return self._run("show", f"{self.full_commit()}:{path}").stdout
```

- [ ] **Step 4: Verify GREEN**

```bash
python -m pytest tests/operator/test_git_source.py -q
```

- [ ] **Step 5: Commit**

```bash
git add scripts/operator_support/git_source.py tests/operator/test_git_source.py
git commit -m "feat: add immutable Git object source"
```

---

### Task 4: Prove deterministic ZIP serialization before builder implementation

**Files:**
- Create: `scripts/operator_support/deterministic_zip.py`
- Create: `tests/operator/test_deterministic_zip.py`

**Interfaces:**
- `ArchiveEntry(path: str, data: bytes, mode: int = 0o100644)`
- `write_deterministic_zip(path, entries) -> str` returning lowercase SHA-256.

This establishes assertion 14 at the archive primitive level before builder code exists.

- [ ] **Step 1: Write failing determinism tests**

```python
from scripts.operator_support.deterministic_zip import ArchiveEntry, write_deterministic_zip


def test_same_entries_same_bytes_and_hash_regardless_of_input_order(tmp_path):
    a = [ArchiveEntry("b.txt", b"B\n"), ArchiveEntry("a.txt", b"A\n", 0o100755)]
    b = list(reversed(a))
    ha = write_deterministic_zip(tmp_path / "a.zip", a)
    hb = write_deterministic_zip(tmp_path / "b.zip", b)
    assert ha == hb
    assert (tmp_path / "a.zip").read_bytes() == (tmp_path / "b.zip").read_bytes()


def test_content_change_changes_hash(tmp_path):
    assert write_deterministic_zip(tmp_path / "a.zip", [ArchiveEntry("a", b"A")]) != write_deterministic_zip(tmp_path / "b.zip", [ArchiveEntry("a", b"B")])
```

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_deterministic_zip.py -q
```

- [ ] **Step 3: Implement fixed ZIP metadata**

```python
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


def write_deterministic_zip(path: Path, entries: Iterable[ArchiveEntry]) -> str:
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
        for entry in sorted(entries, key=lambda item: item.path):
            info = ZipInfo(entry.path, date_time=_FIXED_TIME)
            info.create_system = 3
            perm = 0o755 if entry.mode & 0o111 else 0o644
            info.external_attr = (0o100000 | perm) << 16
            info.compress_type = ZIP_DEFLATED
            info.flag_bits |= 0x800
            info.extra = b""
            info.comment = b""
            archive.writestr(info, entry.data, compress_type=ZIP_DEFLATED, compresslevel=9)
    return sha256(path.read_bytes()).hexdigest()
```

- [ ] **Step 4: Verify GREEN twice**

```bash
python -m pytest tests/operator/test_deterministic_zip.py -q
python -m pytest tests/operator/test_deterministic_zip.py -q
```

- [ ] **Step 5: Commit**

```bash
git add scripts/operator_support/deterministic_zip.py tests/operator/test_deterministic_zip.py
git commit -m "feat: add deterministic ZIP primitive"
```

---

### Task 5: Generate the capability index only from canonical frontmatter

**Files:**
- Create: `scripts/operator_support/module_index.py`
- Create: `tests/operator/test_module_index.py`

**Interfaces:**
- `parse_frontmatter(data: bytes) -> dict[str, str]`
- `ModuleDescriptor(name: str, description: str)`
- `render_module_index(modules) -> bytes`

- [ ] **Step 1: Write failing source-equivalence tests**

```python
from scripts.operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index


def test_frontmatter_requires_name_and_description():
    raw = b"---\nname: recipe-engineering\ndescription: Exact description.\n---\n# Body\n"
    assert parse_frontmatter(raw) == {"name": "recipe-engineering", "description": "Exact description."}


def test_render_is_sorted_and_does_not_paraphrase():
    raw = render_module_index([
        ModuleDescriptor("recipe-engineering", "Exact recipe description."),
        ModuleDescriptor("culinary-rnd", "Exact culinary description."),
    ])
    assert raw == (
        "<!-- GENERATED — DO NOT EDIT -->\n"
        "# Internal Capability Index\n\n"
        "- `culinary-rnd`\n  Exact culinary description.\n\n"
        "- `recipe-engineering`\n  Exact recipe description.\n"
    ).encode()
```

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_module_index.py -q
```

- [ ] **Step 3: Implement strict parsing/rendering**

Use `yaml.safe_load`; raise `ValueError` for missing/empty fields. Sort by `name`; never summarize descriptions.

- [ ] **Step 4: Verify GREEN**

```bash
python -m pytest tests/operator/test_module_index.py -q
```

- [ ] **Step 5: Commit**

```bash
git add scripts/operator_support/module_index.py tests/operator/test_module_index.py
git commit -m "feat: derive operator module index from source"
```

---

### Task 6: Define the operator build policy and pin the verified icon source

**Files:**
- Create: `release/operator/package_policy.yaml`
- Create: `tests/operator/test_operator_policy.py`

**Interfaces:**
- References canonical `release/package_policy.yaml`; does not duplicate the 11 domain IDs.
- Maps verified `company/evochia/brand/assets/logo-mark-42.png` to artifact `assets/evochia-operator-icon.png`.

- [ ] **Step 1: Write failing policy tests**

```python
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "release/operator/package_policy.yaml"


def test_policy_references_canonical_authorities_not_domain_copy_list():
    data = yaml.safe_load(POLICY.read_text())
    assert data["source_package_policy"] == "release/package_policy.yaml"
    assert data["operator_name"] == "evochia-operator"
    assert data["orchestrator_skill"] == "chef-ai-pro-business"
    assert data["template"] == "release/operator/SKILL.template.md"
    assert data["icon"]["source_path"] == "company/evochia/brand/assets/logo-mark-42.png"
    assert data["icon"]["artifact_path"] == "assets/evochia-operator-icon.png"
    assert "domain_skills" not in data


def test_icon_source_is_verified_git_blob():
    blob = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD:company/evochia/brand/assets/logo-mark-42.png"], check=True, text=True, capture_output=True).stdout.strip()
    assert blob == "11676370669ef00c1ed6815300db240c5ce376f8"
```

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_operator_policy.py -q
```

- [ ] **Step 3: Create the minimal policy**

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

- [ ] **Step 4: Verify GREEN**

```bash
python -m pytest tests/operator/test_operator_policy.py -q
```

- [ ] **Step 5: Commit**

```bash
git add release/operator/package_policy.yaml tests/operator/test_operator_policy.py
git commit -m "chore: define operator build target policy"
```

---

### Task 7: Implement the source-anchored validator against handcrafted fixtures before the real builder

**Files:**
- Create: `scripts/validate_operator_package.py`
- Create: `tests/operator/test_operator_validator.py`

**Interfaces:**
- `validate_operator_artifact(artifact: Path, source_repo: Path, source_commit: str) -> list[str]`
- CLI: `python scripts/validate_operator_package.py --artifact ... --source-repo ... --source-commit ...`

**Import rule:** direct CLI wrappers use dual-context imports, exactly as Task 2 does, so both `python scripts/...` and pytest imports work.

- [ ] **Step 1: Build a real temporary Git fixture in tests**

Commit a minimal source graph containing `VERSION`, canonical package policy, operator policy/template, source registry, routing, two domain `SKILL.md` files, one `skills/alpha/references/a.md`, and the verified-icon fixture path.

- [ ] **Step 2: Write failing adversarial tests**

Required tests:

```python
def test_rejects_module_and_manifest_tampered_together(...):
    # mutate MODULE bytes and both manifest hashes to agree
    # expected: still FAIL against source_commit Git bytes
    ...


def test_requires_exact_written_path(...):
    # remove skills/alpha/references/a.md, place same bytes elsewhere
    # expected issue contains exact missing canonical path
    ...


def test_rejects_manual_generated_index(...):
    # mutate module_index only
    # expected: mismatch against render(extract_frontmatter(source))
    ...
```

Also test: exactly one root `SKILL.md`; exact expected modules; routing exact copy; source commit/version match; forbidden patterns absent; manifest file hashes accurate.

- [ ] **Step 3: Verify RED**

```bash
python -m pytest tests/operator/test_operator_validator.py -q
```

- [ ] **Step 4: Implement ZIP loading and canonical domain derivation**

```python
from zipfile import ZipFile
import yaml


def zip_files(path):
    with ZipFile(path) as zf:
        return {name: zf.read(name) for name in zf.namelist() if not name.endswith("/")}


def canonical_domain_ids(source):
    package = yaml.safe_load(source.read_bytes("release/package_policy.yaml")) or {}
    operator = yaml.safe_load(source.read_bytes("release/operator/package_policy.yaml")) or {}
    return tuple(skill for skill in package["required_skills"] if skill != operator["orchestrator_skill"])
```

- [ ] **Step 5: Implement source anchoring, exact-byte checks, generated-index check and exact-path assertion**

For each domain:

```python
source_path = f"skills/{skill_id}/SKILL.md"
projected_path = f"skills/{skill_id}/MODULE.md"
if files.get(projected_path) != source.read_bytes(source_path):
    issues.append(f"Git source bytes differ: {projected_path}")
```

Recompute every manifest `source_sha256` from `source.read_bytes(source_path)`. Never trust a manifest source hash merely because its projected hash matches. For path assertion 10, scan only behavioral/authoritative contract Markdown included in the artifact: root `SKILL.md`, all `MODULE.md`, and Markdown inside canonical `references/`; each extracted token must exist at exactly that artifact path.

- [ ] **Step 6: Implement CLI return codes**

PASS prints `Operator package validation: PASS` and exits 0; any issue prints `FAIL`, one issue per line, and exits 1.

- [ ] **Step 7: Verify GREEN**

```bash
python -m pytest tests/operator/test_operator_validator.py -q
```

- [ ] **Step 8: Commit**

```bash
git add scripts/validate_operator_package.py tests/operator/test_operator_validator.py
git commit -m "feat: add source-anchored operator validator"
```

---

### Task 8: Implement `multi` target first and prove package preservation

**Files:**
- Create: `scripts/build_skill_package.py`
- Create: `tests/operator/test_dual_build.py`

**Interfaces:**
- `BuildResult(target, source_commit, version, artifact_path, sha256)`
- `build_package(repo, source_commit, target, output_dir) -> BuildResult`
- CLI: `--target {multi,operator} --source-repo --source-commit --output-dir`.

- [ ] **Step 1: Write failing `multi` tests before builder implementation**

Test that two builds from one explicit commit are byte-identical, contain 12 `SKILL.md`, contain no `MODULE.md`, preserve `VERSION`, and are unaffected by a dirty tracked CSV when source commit is unchanged.

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_dual_build.py -k multi -q
```

- [ ] **Step 3: Implement result/filename logic**

```python
@dataclass(frozen=True)
class BuildResult:
    target: str
    source_commit: str
    version: str
    artifact_path: Path
    sha256: str


def artifact_name(target, version, commit):
    short = commit[:7]
    if target == "multi":
        return f"chef-ai-pro-business-{version}-{short}-multi.zip"
    if target == "operator":
        return f"evochia-operator-{version}-{short}-operator.zip"
    raise ValueError(f"unsupported target: {target}")
```

- [ ] **Step 4: Implement `multi` as committed-tree materialization**

Use `GitSource.entries()` + `read_bytes()` only. Normalize archive mode from Git mode through `deterministic_zip`. Before writing, enforce canonical forbidden patterns from `release/package_policy.yaml`; do not silently omit forbidden tracked files.

- [ ] **Step 5: Validate an extracted multi artifact with the existing validator**

The integration test extracts the ZIP and runs:

```bash
python scripts/validate_skill_package.py <extracted-root>
```

Expected: exit 0 and `Skill package validation: PASS`.

- [ ] **Step 6: Verify GREEN**

```bash
python -m pytest tests/operator/test_dual_build.py -k multi -q
```

- [ ] **Step 7: Commit**

```bash
git add scripts/build_skill_package.py tests/operator/test_dual_build.py
git commit -m "feat: add deterministic multi-skill build target"
```

---

### Task 9: Implement operator projection, closure, icon, index and provenance

**Files:**
- Modify: `scripts/build_skill_package.py`
- Modify: `tests/operator/test_dual_build.py`

**Interfaces:**
- Consumes all previous primitives.
- Produces one root `SKILL.md`, 11 exact-byte modules, canonical resource closure, generated index, verified icon and provenance manifest.

- [ ] **Step 1: Write failing operator topology tests**

Assert exactly one `SKILL.md` at root, exactly 11 `skills/<id>/MODULE.md`, no projected orchestrator module, every module equals `git show <commit>:skills/<id>/SKILL.md`, full canonical `references/` is present, routing remains at its canonical path and byte-identical, and icon bytes equal the pinned source asset.

- [ ] **Step 2: Verify RED**

```bash
python -m pytest tests/operator/test_dual_build.py -k operator -q
```

Expected: explicit unsupported/not-implemented operator path.

- [ ] **Step 3: Derive domain IDs from canonical policy**

`required_skills` minus `orchestrator_skill`; assert the real source yields 11 domains. Do not write an 11-ID list into operator policy.

- [ ] **Step 4: Derive runtime resource closure**

Seed with:
1. `VERSION`.
2. Entire canonical `references/` subtree.
3. Every domain skill-local subtree; omit source `SKILL.md` at its old path and project its bytes to `MODULE.md`.
4. Canonical routing at unchanged path.
5. `resource_roots` and `exact_resources` from `release/runtime_resource_ownership.yaml`.
6. Exact paths extracted from root template, domain contracts and included authoritative Markdown; iterate newly included Markdown to a fixed point.
7. Pinned icon source mapped to `assets/evochia-operator-icon.png`.

If an extracted exact path does not exist in the Git commit, fail. Do not search by basename or rewrite it.

- [ ] **Step 5: Generate only the approved generated files**

- `SKILL.md` = template bytes.
- `references/module_index.md` = deterministic frontmatter render.
- `provenance/build_manifest.yaml` = deterministic manifest.

Everything else is Git-object copy except the domain filename projection.

- [ ] **Step 6: Make builder identity itself provenance-safe**

Manifest builder block records both running code hash and source-commit builder hash:

```yaml
builder:
  path: scripts/build_skill_package.py
  runtime_sha256: <sha256(Path(__file__).read_bytes())>
  source_commit_sha256: <sha256(GitSource.read_bytes(path))>
```

Release-grade validation requires equality. This prevents a dirty/uncommitted builder from claiming that an artifact was produced by the committed builder at `source_commit`. Ordinary dirty input files remain irrelevant because source content still comes from Git objects.

- [ ] **Step 7: Write deterministic manifest**

For every projected file include `projected_path`, `relation`, `source_path` where applicable, `source_sha256`, and `projected_sha256`. Sort entries by `projected_path`; use deterministic `yaml.safe_dump(..., sort_keys=True, allow_unicode=True)`. Do not embed ZIP hash in the ZIP.

- [ ] **Step 8: Verify GREEN**

```bash
python -m pytest tests/operator/test_dual_build.py -k operator -q
```

- [ ] **Step 9: Commit**

```bash
git add scripts/build_skill_package.py tests/operator/test_dual_build.py
git commit -m "feat: build deterministic Evochia Operator package"
```

---

### Task 10: Verify all 19 design assertions end-to-end

**Files:**
- Modify: `tests/operator/test_operator_validator.py`
- Modify: `tests/operator/test_dual_build.py`
- Modify: `scripts/validate_operator_package.py` only for a demonstrated missing assertion.

- [ ] **Step 1: Name one test per design assertion**

Use visible names such as:

```python
def test_a01_exactly_one_public_skill(...): ...
def test_a05_modules_equal_git_source_bytes(...): ...
def test_a08_index_equals_source_frontmatter_render(...): ...
def test_a10_exact_written_paths_resolve(...): ...
def test_a14_two_builds_same_zip_sha(...): ...
def test_a16_manifest_source_hashes_match_git_objects(...): ...
def test_a17_exact_copy_bytes_match_git_objects(...): ...
def test_a19_dirty_worktree_does_not_change_explicit_commit_build(...): ...
```

- [ ] **Step 2: Add adversarial assertion 16/17 mutation**

Mutate a `MODULE.md` and mutate both corresponding manifest hashes to agree with the tampered bytes. Validation must still fail against the Git source object.

- [ ] **Step 3: Add assertion 10 regression using all three real problematic paths**

For each of:
- `skills/culinary-rnd/references/research_protocol.md`
- `skills/kitchen-event-operations/references/event_lifecycle.md`
- `skills/evochia-market-intelligence/references/intelligence_policy.yaml`

remove the exact path from a copied artifact and put identical bytes elsewhere. Validation must fail on the missing exact path.

- [ ] **Step 4: Add full assertion 14 and 19 integration tests**

Build operator twice from one commit into two directories and compare bytes + hash. For dirty-worktree coverage, use a temporary clone/worktree fixture, modify a tracked non-builder file without committing it, build from the same commit, and require unchanged artifact hash.

- [ ] **Step 5: Add dirty-builder negative test**

Run builder from a modified `scripts/build_skill_package.py` worktree against its old source commit and require source-anchored validation to reject the runtime/source builder hash mismatch. This closes the provenance gap without weakening normal dirty-worktree isolation.

- [ ] **Step 6: Run all operator tests**

```bash
python -m pytest tests/operator -q
```

Expected: PASS; no xfail/skip used to hide an unimplemented assertion.

- [ ] **Step 7: Run source-package regressions**

```bash
python -m pytest tests/release tests/routing tests/parity -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add scripts/validate_operator_package.py tests/operator/test_operator_validator.py tests/operator/test_dual_build.py
git commit -m "test: verify operator provenance and determinism end to end"
```

---

### Task 11: Preserve the open surface blocker and add CI dual-build verification

**Files:**
- Create: `tests/operator/test_release_gate_preservation.py`
- Modify: `.github/workflows/verify.yml`

- [ ] **Step 1: Write release-gate preservation test**

```python
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_builder_does_not_close_surface_blocker():
    data = yaml.safe_load((ROOT / "release/release_readiness.yaml").read_text())
    blocker = next(x for x in data["blockers"] if x["id"] == "openai_surface_install_scan")
    assert blocker["status"] == "NOT_RUN"
    assert blocker["required_before_final_release"] is True
    assert data["final_release_status"] == "BLOCKED"
    assert data["may_claim_production_ready"] is False
```

- [ ] **Step 2: Verify it passes without editing readiness**

```bash
python -m pytest tests/operator/test_release_gate_preservation.py -q
```

- [ ] **Step 3: Add CI smoke commands after existing validators**

```yaml
      - name: Build deterministic multi and operator packages
        run: |
          mkdir -p /tmp/build-a /tmp/build-b
          python scripts/build_skill_package.py --target multi --source-repo . --source-commit "$GITHUB_SHA" --output-dir /tmp/build-a
          python scripts/build_skill_package.py --target operator --source-repo . --source-commit "$GITHUB_SHA" --output-dir /tmp/build-a
          python scripts/build_skill_package.py --target operator --source-repo . --source-commit "$GITHUB_SHA" --output-dir /tmp/build-b

      - name: Validate operator package against Git source
        run: |
          test "$(find /tmp/build-a -maxdepth 1 -name 'evochia-operator-*-operator.zip' | wc -l)" -eq 1
          OPERATOR_ZIP=$(find /tmp/build-a -maxdepth 1 -name 'evochia-operator-*-operator.zip' -print -quit)
          python scripts/validate_operator_package.py --artifact "$OPERATOR_ZIP" --source-repo . --source-commit "$GITHUB_SHA"

      - name: Verify repeat build hash
        run: |
          test "$(find /tmp/build-b -maxdepth 1 -name 'evochia-operator-*-operator.zip' | wc -l)" -eq 1
          A=$(sha256sum /tmp/build-a/evochia-operator-*-operator.zip | awk '{print $1}')
          B=$(sha256sum /tmp/build-b/evochia-operator-*-operator.zip | awk '{print $1}')
          test "$A" = "$B"
```

- [ ] **Step 4: Run the full local CI-equivalent suite**

```bash
python -m pytest -q
python evals/run_evals.py
python scripts/validate_skill_package.py
python scripts/validate_repo_hygiene.py .
python scripts/validate_parity_coverage.py
python scripts/validate_source_registry.py
python scripts/validate_doctrine_integrity.py
```

Expected: every command exits 0.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/verify.yml tests/operator/test_release_gate_preservation.py
git commit -m "ci: verify deterministic dual skill builds"
```

---

### Task 12: Produce `C1` artifacts and stop at surface-test handoff

**Files:**
- No source modifications unless verification exposes a concrete implementation defect.
- Artifacts are local/untracked output.

- [ ] **Step 1: Verify clean implementation state and record `C1`**

```bash
git status --short
git rev-parse HEAD
```

Expected: no unintended source changes; record full SHA as `C1`.

- [ ] **Step 2: Build both artifacts from exactly `C1`**

```bash
mkdir -p dist
python scripts/build_skill_package.py --target multi --source-repo . --source-commit "$(git rev-parse HEAD)" --output-dir dist
python scripts/build_skill_package.py --target operator --source-repo . --source-commit "$(git rev-parse HEAD)" --output-dir dist
```

Expected names:

```text
chef-ai-pro-business-4.0.0-alpha.0-<short-C1>-multi.zip
evochia-operator-4.0.0-alpha.0-<short-C1>-operator.zip
```

- [ ] **Step 3: Validate the operator artifact against `C1`**

```bash
python scripts/validate_operator_package.py \
  --artifact dist/evochia-operator-4.0.0-alpha.0-$(git rev-parse --short=7 HEAD)-operator.zip \
  --source-repo . \
  --source-commit "$(git rev-parse HEAD)"
```

Expected: `Operator package validation: PASS`.

- [ ] **Step 4: Record both SHA-256 values**

```bash
sha256sum dist/*-multi.zip dist/*-operator.zip
```

Do not edit `release/release_readiness.yaml` from build success.

- [ ] **Step 5: Perform surface testing in the mandatory order**

1. Install `MULTI(C1)`; confirm 12 visible Skills and record scan/install evidence.
2. Run complete A→H through `@chef-ai-pro-business`. This is mandatory; sampling does not close the blocker.
3. Install `OPERATOR(C1)`; require exactly one visible `evochia-operator`, zero exposed module names, and record icon/scan behavior.
4. Run the same complete A→H tasks through `@evochia-operator`.
5. Compare router-to-router transcripts. Optional direct-domain runs are labeled `DIRECT` and excluded from gating thresholds.

Thresholds:

```text
BLOCKING failures:              0
new MAJOR regressions:          0
new PASS_WITH_CONCERN:         <= 2
new NEAR_MISS in B1:            0
new NEAR_MISS in D2:            0
new NEAR_MISS in Block F:       0
```

If `MULTI(C1)` fails Block F, classify it first as multi-skill baseline failure; do not attribute it to the operator without differential evidence.

- [ ] **Step 6: Stop before any release-readiness mutation**

No production-ready claim and no blocker-status change until install evidence and transcripts are separately reviewed.

---

## Final Verification Checklist

Before claiming implementation readiness for surface testing, retain fresh output for:

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

Then:

```bash
git diff <implementation-base>..HEAD -- skills references/source_registry.yaml
git diff <implementation-base>..HEAD -- skills/chef-ai-pro-business/references/routing.yaml
```

Expected: no changes to existing Skill contracts, source registry or routing. Build both targets twice from the same explicit commit, confirm repeated hashes, and run the release-grade operator validator with source anchoring. Command output and artifact hashes—not agent summaries—are the completion evidence.
