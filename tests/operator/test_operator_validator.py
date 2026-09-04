from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile

import yaml

from scripts.operator_support.git_source import GitSource, sha256_bytes
from scripts.operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts/validate_operator_package.py"
MANIFEST_PATH = "provenance/build_manifest.yaml"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def write_zip(path: Path, files: dict[str, bytes]) -> None:
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for name in sorted(files):
            archive.writestr(name, files[name])


def read_zip(path: Path) -> dict[str, bytes]:
    with ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist() if not name.endswith("/")}


def dump_yaml(data: dict) -> bytes:
    return yaml.safe_dump(data, sort_keys=True, allow_unicode=True).encode("utf-8")


def manifest_file(
    projected_path: str,
    projected: bytes,
    *,
    source_path: str | None,
    source: bytes | None,
    relation: str,
) -> dict:
    return {
        "projected_path": projected_path,
        "relation": relation,
        "source_path": source_path,
        "source_sha256": sha256_bytes(source) if source is not None else None,
        "projected_sha256": sha256_bytes(projected),
    }


@dataclass(frozen=True)
class Fixture:
    repo: Path
    commit: str
    artifact: Path


def make_source_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "source"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")

    files: dict[str, bytes] = {
        "VERSION": b"4.0.0-alpha.0\n",
        "release/package_policy.yaml": dump_yaml(
            {
                "schema_version": 1,
                "required_skills": ["chef-ai-pro-business", "alpha", "beta"],
                "required_skill_file": "SKILL.md",
                "required_frontmatter_fields": ["name", "description"],
                "forbidden_patterns": [".env", "*.pem", "__pycache__"],
                "allowed_exception_files": [".env.example"],
                "font_binaries_in_package": False,
                "backend_source_in_package": False,
            }
        ),
        "release/operator/SKILL.template.md": (
            b"---\nname: evochia-operator\ndescription: Fixture operator.\n---\n"
            b"# Operator\n"
            b"Use `references/source_registry.yaml`, "
            b"`skills/chef-ai-pro-business/references/routing.yaml`, and "
            b"`references/module_index.md`.\n"
        ),
        "references/source_registry.yaml": b"schema_version: 1\nsources: []\n",
        "skills/chef-ai-pro-business/SKILL.md": (
            b"---\nname: chef-ai-pro-business\ndescription: Fixture orchestrator.\n---\n# Orchestrator\n"
        ),
        "skills/chef-ai-pro-business/references/routing.yaml": (
            b"schema_version: 1\nroutes:\n  - id: alpha\n    required_skills: [alpha]\n"
        ),
        "skills/alpha/SKILL.md": (
            b"---\nname: alpha\ndescription: Alpha module.\n---\n"
            b"# Alpha\nUse `skills/alpha/references/a.md`.\n"
        ),
        "skills/alpha/references/a.md": b"# Alpha resource\n",
        "skills/beta/SKILL.md": (
            b"---\nname: beta\ndescription: Beta module.\n---\n# Beta\n"
        ),
        "company/evochia/brand/assets/logo-mark-42.png": b"\x89PNG\r\n\x1a\nfixture-icon",
        "scripts/build_skill_package.py": b"# committed fixture builder\n",
    }

    for rel, data in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    icon_blob = git(repo, "hash-object", "company/evochia/brand/assets/logo-mark-42.png")
    operator_policy = {
        "schema_version": 1,
        "source_package_policy": "release/package_policy.yaml",
        "operator_name": "evochia-operator",
        "orchestrator_skill": "chef-ai-pro-business",
        "template": "release/operator/SKILL.template.md",
        "routing": "skills/chef-ai-pro-business/references/routing.yaml",
        "module_index_path": "references/module_index.md",
        "icon": {
            "source_path": "company/evochia/brand/assets/logo-mark-42.png",
            "artifact_path": "assets/evochia-operator-icon.png",
            "expected_git_blob": icon_blob,
        },
        "provenance_manifest_path": MANIFEST_PATH,
    }
    policy_path = repo / "release/operator/package_policy.yaml"
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_bytes(dump_yaml(operator_policy))

    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture source")
    return repo, git(repo, "rev-parse", "HEAD")


def make_valid_artifact(tmp_path: Path) -> Fixture:
    repo, commit = make_source_repo(tmp_path)
    source = GitSource(repo, commit)

    descriptors = []
    for skill_id in ("alpha", "beta"):
        meta = parse_frontmatter(source.read_bytes(f"skills/{skill_id}/SKILL.md"))
        descriptors.append(ModuleDescriptor(meta["name"], meta["description"]))
    module_index = render_module_index(descriptors)

    source_map = {
        "SKILL.md": ("release/operator/SKILL.template.md", "TEMPLATE_EXACT_COPY"),
        "VERSION": ("VERSION", "EXACT_BYTE_COPY"),
        "references/source_registry.yaml": ("references/source_registry.yaml", "EXACT_BYTE_COPY"),
        "skills/chef-ai-pro-business/references/routing.yaml": (
            "skills/chef-ai-pro-business/references/routing.yaml",
            "EXACT_BYTE_COPY",
        ),
        "skills/alpha/MODULE.md": ("skills/alpha/SKILL.md", "EXACT_BYTE_COPY"),
        "skills/alpha/references/a.md": ("skills/alpha/references/a.md", "EXACT_BYTE_COPY"),
        "skills/beta/MODULE.md": ("skills/beta/SKILL.md", "EXACT_BYTE_COPY"),
        "assets/evochia-operator-icon.png": (
            "company/evochia/brand/assets/logo-mark-42.png",
            "RENAMED_EXACT_BYTE_COPY",
        ),
    }

    artifact_files: dict[str, bytes] = {}
    inventory: list[dict] = []
    for projected_path, (source_path, relation) in source_map.items():
        data = source.read_bytes(source_path)
        artifact_files[projected_path] = data
        inventory.append(
            manifest_file(
                projected_path,
                data,
                source_path=source_path,
                source=data,
                relation=relation,
            )
        )

    artifact_files["references/module_index.md"] = module_index
    inventory.append(
        manifest_file(
            "references/module_index.md",
            module_index,
            source_path=None,
            source=None,
            relation="GENERATED_FRONTMATTER_INDEX",
        )
    )

    builder_source = source.read_bytes("scripts/build_skill_package.py")
    manifest = {
        "schema_version": 1,
        "source_commit": commit,
        "source_version": source.read_bytes("VERSION").decode("utf-8").strip(),
        "target": "operator",
        "builder": {
            "path": "scripts/build_skill_package.py",
            "runtime_sha256": sha256_bytes(builder_source),
            "source_commit_sha256": sha256_bytes(builder_source),
        },
        "root_template_sha256": sha256_bytes(source.read_bytes("release/operator/SKILL.template.md")),
        "module_index": {
            "path": "references/module_index.md",
            "generation_method": "frontmatter-name-description-v1",
            "sha256": sha256_bytes(module_index),
        },
        "files": sorted(inventory, key=lambda item: item["projected_path"]),
    }
    artifact_files[MANIFEST_PATH] = dump_yaml(manifest)

    artifact = tmp_path / "operator.zip"
    write_zip(artifact, artifact_files)
    return Fixture(repo=repo, commit=commit, artifact=artifact)


def rewrite_artifact(artifact: Path, mutate) -> None:
    files = read_zip(artifact)
    mutate(files)
    write_zip(artifact, files)


def run_validator(fixture: Fixture, *, source_commit: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--artifact",
            str(fixture.artifact),
            "--source-repo",
            str(fixture.repo),
            "--source-commit",
            source_commit or fixture.commit,
        ],
        text=True,
        capture_output=True,
    )


def test_valid_handcrafted_operator_passes_without_canonical_icon_path_in_artifact(tmp_path):
    fixture = make_valid_artifact(tmp_path)
    files = read_zip(fixture.artifact)
    assert "assets/evochia-operator-icon.png" in files
    assert "company/evochia/brand/assets/logo-mark-42.png" not in files

    result = run_validator(fixture)

    assert result.returncode == 0, result.stderr
    assert "Operator package validation: PASS" in result.stdout


def test_rejects_module_and_manifest_tampered_together_against_git_source(tmp_path):
    fixture = make_valid_artifact(tmp_path)
    tampered = b"---\nname: alpha\ndescription: Tampered.\n---\n# Alpha\n"

    def mutate(files: dict[str, bytes]) -> None:
        files["skills/alpha/MODULE.md"] = tampered
        manifest = yaml.safe_load(files[MANIFEST_PATH])
        row = next(item for item in manifest["files"] if item["projected_path"] == "skills/alpha/MODULE.md")
        forged = sha256(tampered).hexdigest()
        row["source_sha256"] = forged
        row["projected_sha256"] = forged
        files[MANIFEST_PATH] = dump_yaml(manifest)

    rewrite_artifact(fixture.artifact, mutate)
    result = run_validator(fixture)

    assert result.returncode == 1
    assert "Git source bytes differ: skills/alpha/MODULE.md" in result.stderr


def test_requires_exact_written_contract_path_even_when_same_bytes_exist_elsewhere(tmp_path):
    fixture = make_valid_artifact(tmp_path)

    def mutate(files: dict[str, bytes]) -> None:
        data = files.pop("skills/alpha/references/a.md")
        files["relocated/a.md"] = data

    rewrite_artifact(fixture.artifact, mutate)
    result = run_validator(fixture)

    assert result.returncode == 1
    assert "broken referenced path skills/alpha/references/a.md" in result.stderr


def test_rejects_generated_index_and_manifest_tampered_together(tmp_path):
    fixture = make_valid_artifact(tmp_path)
    tampered = b"<!-- GENERATED — DO NOT EDIT -->\n# Internal Capability Index\n\n- `alpha`\n  Forged.\n"

    def mutate(files: dict[str, bytes]) -> None:
        files["references/module_index.md"] = tampered
        manifest = yaml.safe_load(files[MANIFEST_PATH])
        manifest["module_index"]["sha256"] = sha256(tampered).hexdigest()
        row = next(item for item in manifest["files"] if item["projected_path"] == "references/module_index.md")
        row["projected_sha256"] = sha256(tampered).hexdigest()
        files[MANIFEST_PATH] = dump_yaml(manifest)

    rewrite_artifact(fixture.artifact, mutate)
    result = run_validator(fixture)

    assert result.returncode == 1
    assert "generated module index differs from canonical source frontmatter" in result.stderr


def test_missing_source_commit_is_clean_validation_failure_not_traceback(tmp_path):
    fixture = make_valid_artifact(tmp_path)
    missing = "0" * 40

    result = run_validator(fixture, source_commit=missing)

    assert result.returncode == 1
    assert "Operator package validation: FAIL" in result.stderr
    assert "source commit unavailable" in result.stderr
    assert missing in result.stderr
    assert "Traceback" not in result.stderr
