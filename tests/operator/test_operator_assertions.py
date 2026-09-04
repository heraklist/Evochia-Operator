from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import shutil
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

import pytest
import yaml

from scripts.operator_support.contract_paths import extract_contract_paths
from scripts.operator_support.contract_scope import operator_contract_paths
from scripts.operator_support.deterministic_zip import ArchiveEntry, write_deterministic_zip
from scripts.operator_support.git_source import GitSource, sha256_bytes
from scripts.operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "scripts/build_skill_package.py"
VALIDATOR = ROOT / "scripts/validate_operator_package.py"
MANIFEST_PATH = "provenance/build_manifest.yaml"


@dataclass(frozen=True)
class BuiltOperator:
    repo: Path
    commit: str
    artifact: Path


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def clone_repo(parent: Path) -> tuple[Path, str]:
    repo = parent / "source"
    subprocess.run(
        ["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(repo)],
        check=True,
        capture_output=True,
    )
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    return repo, git(repo, "rev-parse", "HEAD")


def run_builder(
    repo: Path,
    commit: str,
    output_dir: Path,
    *,
    builder: Path = BUILDER,
    cwd: Path = ROOT,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            str(builder),
            "--target",
            "operator",
            "--source-repo",
            str(repo),
            "--source-commit",
            commit,
            "--output-dir",
            str(output_dir),
        ],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    matches = list(output_dir.glob("evochia-operator-*-operator.zip"))
    assert len(matches) == 1
    return matches[0]


def run_validator(artifact: Path, repo: Path, commit: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--artifact",
            str(artifact),
            "--source-repo",
            str(repo),
            "--source-commit",
            commit,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def read_archive(path: Path) -> tuple[dict[str, bytes], dict[str, int]]:
    files: dict[str, bytes] = {}
    modes: dict[str, int] = {}
    with ZipFile(path) as archive:
        for info in archive.infolist():
            if info.filename.endswith("/"):
                continue
            files[info.filename] = archive.read(info.filename)
            modes[info.filename] = info.external_attr >> 16
    return files, modes


def rewrite_archive(path: Path, files: dict[str, bytes], modes: dict[str, int]) -> None:
    entries = [
        ArchiveEntry(name, data, modes.get(name, 0o100644))
        for name, data in files.items()
    ]
    write_deterministic_zip(path, entries)


def copy_artifact(base: BuiltOperator, tmp_path: Path) -> Path:
    target = tmp_path / "mutated.zip"
    shutil.copyfile(base.artifact, target)
    return target


def load_manifest(files: dict[str, bytes]) -> dict:
    return yaml.safe_load(files[MANIFEST_PATH])


def store_manifest(files: dict[str, bytes], manifest: dict) -> None:
    files[MANIFEST_PATH] = yaml.safe_dump(
        manifest,
        sort_keys=True,
        allow_unicode=True,
    ).encode("utf-8")


def manifest_row(manifest: dict, projected_path: str) -> dict:
    return next(
        row
        for row in manifest["files"]
        if row["projected_path"] == projected_path
    )


def remove_manifest_row(manifest: dict, projected_path: str) -> None:
    manifest["files"] = [
        row for row in manifest["files"] if row["projected_path"] != projected_path
    ]


def add_source_copy_row(
    manifest: dict,
    source: GitSource,
    *,
    projected_path: str,
    source_path: str,
    projected: bytes,
    relation: str = "EXACT_BYTE_COPY",
) -> None:
    source_bytes = source.read_bytes(source_path)
    manifest["files"].append(
        {
            "projected_path": projected_path,
            "relation": relation,
            "source_path": source_path,
            "source_sha256": sha256_bytes(source_bytes),
            "projected_sha256": sha256_bytes(projected),
        }
    )
    manifest["files"].sort(key=lambda row: row["projected_path"])


def add_generated_row(
    manifest: dict,
    *,
    projected_path: str,
    projected: bytes,
    relation: str = "GENERATED_TEST_ONLY",
) -> None:
    manifest["files"].append(
        {
            "projected_path": projected_path,
            "relation": relation,
            "source_path": None,
            "source_sha256": None,
            "projected_sha256": sha256_bytes(projected),
        }
    )
    manifest["files"].sort(key=lambda row: row["projected_path"])


def domain_ids(source: GitSource) -> tuple[str, ...]:
    package_policy = yaml.safe_load(source.read_bytes("release/package_policy.yaml"))
    operator_policy = yaml.safe_load(source.read_bytes("release/operator/package_policy.yaml"))
    return tuple(
        skill
        for skill in package_policy["required_skills"]
        if skill != operator_policy["orchestrator_skill"]
    )


def expected_index(source: GitSource, domains: tuple[str, ...]) -> bytes:
    descriptors = []
    for skill_id in domains:
        meta = parse_frontmatter(source.read_bytes(f"skills/{skill_id}/SKILL.md"))
        descriptors.append(ModuleDescriptor(meta["name"], meta["description"]))
    return render_module_index(descriptors)


def assert_validation_fails(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 1, result.stdout + result.stderr
    assert "Operator package validation: FAIL" in result.stderr


@pytest.fixture(scope="module")
def built_operator(tmp_path_factory) -> BuiltOperator:
    root = tmp_path_factory.mktemp("operator-a01-a19")
    repo, commit = clone_repo(root)
    artifact = run_builder(repo, commit, root / "artifact")
    return BuiltOperator(repo=repo, commit=commit, artifact=artifact)


def test_a01_exactly_one_skill_md_exists(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    source = GitSource(built_operator.repo, built_operator.commit)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)

    extra_path = "skills/rogue/SKILL.md"
    extra = source.read_bytes("release/operator/SKILL.template.md")
    files[extra_path] = extra
    modes[extra_path] = 0o100644
    add_source_copy_row(
        manifest,
        source,
        projected_path=extra_path,
        source_path="release/operator/SKILL.template.md",
        projected=extra,
        relation="TEMPLATE_EXACT_COPY",
    )
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a02_root_skill_is_evochia_operator(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    tampered = files["SKILL.md"].replace(b"name: evochia-operator", b"name: rogue-operator", 1)
    files["SKILL.md"] = tampered
    manifest_row(manifest, "SKILL.md")["projected_sha256"] = sha256_bytes(tampered)
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a03_exactly_11_expected_modules_exist(built_operator: BuiltOperator, tmp_path):
    source = GitSource(built_operator.repo, built_operator.commit)
    assert len(domain_ids(source)) == 11

    artifact = copy_artifact(built_operator, tmp_path)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    missing = f"skills/{domain_ids(source)[0]}/MODULE.md"
    files.pop(missing)
    modes.pop(missing)
    remove_manifest_row(manifest, missing)
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a04_no_missing_or_unexpected_module_ids(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    source = GitSource(built_operator.repo, built_operator.commit)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)

    extra_path = "skills/rogue-domain/MODULE.md"
    source_path = "skills/recipe-engineering/SKILL.md"
    extra = source.read_bytes(source_path)
    files[extra_path] = extra
    modes[extra_path] = 0o100644
    add_source_copy_row(
        manifest,
        source,
        projected_path=extra_path,
        source_path=source_path,
        projected=extra,
    )
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a05_every_module_is_exact_byte_copy(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    source = GitSource(built_operator.repo, built_operator.commit)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    module = f"skills/{domain_ids(source)[0]}/MODULE.md"
    tampered = files[module] + b"\nTAMPERED\n"
    files[module] = tampered
    manifest_row(manifest, module)["projected_sha256"] = sha256_bytes(tampered)
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a06_skill_local_resources_preserve_canonical_paths(tmp_path):
    repo, _ = clone_repo(tmp_path)
    extra_source = "skills/recipe-engineering/references/unreferenced-a06-proof.txt"
    source_file = repo / extra_source
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("unreferenced local resource\n", encoding="utf-8")
    git(repo, "add", extra_source)
    git(repo, "commit", "-m", "test fixture: add unreferenced skill resource")
    commit = git(repo, "rev-parse", "HEAD")

    artifact = run_builder(repo, commit, tmp_path / "built")
    files, modes = read_archive(artifact)
    assert extra_source in files
    manifest = load_manifest(files)

    relocated = "relocated/unreferenced-a06-proof.txt"
    data = files.pop(extra_source)
    modes.pop(extra_source)
    remove_manifest_row(manifest, extra_source)
    files[relocated] = data
    modes[relocated] = 0o100644
    add_source_copy_row(
        manifest,
        GitSource(repo, commit),
        projected_path=relocated,
        source_path=extra_source,
        projected=data,
    )
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, repo, commit)
    assert_validation_fails(result)


def test_a07_routing_is_exact_copy(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    source = GitSource(built_operator.repo, built_operator.commit)
    operator_policy = yaml.safe_load(source.read_bytes("release/operator/package_policy.yaml"))
    routing = operator_policy["routing"]
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    tampered = files[routing] + b"\n# tampered routing\n"
    files[routing] = tampered
    manifest_row(manifest, routing)["projected_sha256"] = sha256_bytes(tampered)
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a08_module_index_equals_source_frontmatter_render(built_operator: BuiltOperator, tmp_path):
    source = GitSource(built_operator.repo, built_operator.commit)
    operator_policy = yaml.safe_load(source.read_bytes("release/operator/package_policy.yaml"))
    index_path = operator_policy["module_index_path"]
    canonical = expected_index(source, domain_ids(source))
    reversed_render = render_module_index(
        list(
            reversed(
                [
                    ModuleDescriptor(
                        parse_frontmatter(source.read_bytes(f"skills/{skill}/SKILL.md"))["name"],
                        parse_frontmatter(source.read_bytes(f"skills/{skill}/SKILL.md"))["description"],
                    )
                    for skill in domain_ids(source)
                ]
            )
        )
    )
    assert canonical == reversed_render

    artifact = copy_artifact(built_operator, tmp_path)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    assert files[index_path] == canonical
    tampered = render_module_index([ModuleDescriptor("forged", "Forged index.")])
    files[index_path] = tampered
    manifest["module_index"]["sha256"] = sha256_bytes(tampered)
    manifest_row(manifest, index_path)["projected_sha256"] = sha256_bytes(tampered)
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a09_packaged_file_hashes_match_complete_manifest_inventory(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    files, modes = read_archive(artifact)
    files["extra/unmanifested.txt"] = b"not in manifest\n"
    modes["extra/unmanifested.txt"] = 0o100644
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a10_every_contract_runtime_path_resolves_exactly(built_operator: BuiltOperator, tmp_path):
    source = GitSource(built_operator.repo, built_operator.commit)
    operator_policy = yaml.safe_load(source.read_bytes("release/operator/package_policy.yaml"))
    icon_source = operator_policy["icon"]["source_path"]
    files, _ = read_archive(built_operator.artifact)

    for contract_path in operator_contract_paths(files):
        text = files[contract_path].decode("utf-8")
        for ref in extract_contract_paths(text):
            if ref == icon_source:
                continue
            assert ref in files or any(
                path.startswith(ref.rstrip("/") + "/") for path in files
            ), (contract_path, ref)

    artifact = copy_artifact(built_operator, tmp_path)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    referenced = "skills/culinary-rnd/references/research_protocol.md"
    relocated = "relocated/research_protocol.md"
    data = files.pop(referenced)
    modes.pop(referenced)
    row = manifest_row(manifest, referenced)
    remove_manifest_row(manifest, referenced)
    files[relocated] = data
    modes[relocated] = 0o100644
    row["projected_path"] = relocated
    manifest["files"].append(row)
    manifest["files"].sort(key=lambda item: item["projected_path"])
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a11_forbidden_files_and_secrets_are_rejected(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    forbidden = b"SECRET=operator-test-only\n"
    files[".env"] = forbidden
    modes[".env"] = 0o100644
    add_generated_row(manifest, projected_path=".env", projected=forbidden)
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a12_package_font_and_backend_source_restrictions_are_preserved(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)

    font = b"fake-font-binary"
    backend = b"print('unintended backend source')\n"
    files["assets/rogue.ttf"] = font
    files["backend/server.py"] = backend
    modes["assets/rogue.ttf"] = 0o100644
    modes["backend/server.py"] = 0o100644
    add_generated_row(manifest, projected_path="assets/rogue.ttf", projected=font)
    add_generated_row(manifest, projected_path="backend/server.py", projected=backend)
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a13_source_commit_and_version_are_accurate(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    tampered_version = b"999.0.0-forged\n"
    files["VERSION"] = tampered_version
    manifest["source_commit"] = "0" * 40
    manifest["source_version"] = "999.0.0-forged"
    manifest_row(manifest, "VERSION")["projected_sha256"] = sha256_bytes(tampered_version)
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a14_same_commit_produces_same_zip_sha256(built_operator: BuiltOperator, tmp_path):
    first = run_builder(built_operator.repo, built_operator.commit, tmp_path / "first")
    second = run_builder(built_operator.repo, built_operator.commit, tmp_path / "second")
    assert first.read_bytes() == second.read_bytes()
    assert sha256(first.read_bytes()).hexdigest() == sha256(second.read_bytes()).hexdigest()


def test_a15_any_projected_module_routing_or_resource_byte_mutation_fails(built_operator: BuiltOperator, tmp_path):
    source = GitSource(built_operator.repo, built_operator.commit)
    operator_policy = yaml.safe_load(source.read_bytes("release/operator/package_policy.yaml"))
    targets = (
        "skills/recipe-engineering/MODULE.md",
        operator_policy["routing"],
        "references/source_registry.yaml",
    )

    for index, target in enumerate(targets):
        artifact = tmp_path / f"mutation-{index}.zip"
        shutil.copyfile(built_operator.artifact, artifact)
        files, modes = read_archive(artifact)
        manifest = load_manifest(files)
        tampered = files[target] + b"\nBYTE-MUTATION\n"
        files[target] = tampered
        manifest_row(manifest, target)["projected_sha256"] = sha256_bytes(tampered)
        store_manifest(files, manifest)
        rewrite_archive(artifact, files, modes)
        result = run_validator(artifact, built_operator.repo, built_operator.commit)
        assert_validation_fails(result)


def test_a16_manifest_source_sha256_is_recomputed_from_git_objects(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    target = "skills/recipe-engineering/MODULE.md"
    row = manifest_row(manifest, target)
    row["source_sha256"] = "0" * 64
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a17_exact_byte_copy_compares_git_bytes_directly_not_only_manifest_hashes(built_operator: BuiltOperator, tmp_path):
    artifact = copy_artifact(built_operator, tmp_path)
    source = GitSource(built_operator.repo, built_operator.commit)
    files, modes = read_archive(artifact)
    manifest = load_manifest(files)
    target = "skills/recipe-engineering/MODULE.md"
    row = manifest_row(manifest, target)
    canonical_source = source.read_bytes(row["source_path"])
    tampered = files[target] + b"\nDIRECT-BYTE-COMPARISON-PROOF\n"
    files[target] = tampered
    row["source_sha256"] = sha256_bytes(canonical_source)
    row["projected_sha256"] = sha256_bytes(tampered)
    store_manifest(files, manifest)
    rewrite_archive(artifact, files, modes)

    result = run_validator(artifact, built_operator.repo, built_operator.commit)
    assert_validation_fails(result)


def test_a18_manual_index_or_provenance_mutation_fails_without_source_change(built_operator: BuiltOperator, tmp_path):
    source = GitSource(built_operator.repo, built_operator.commit)
    operator_policy = yaml.safe_load(source.read_bytes("release/operator/package_policy.yaml"))
    index_path = operator_policy["module_index_path"]

    index_artifact = tmp_path / "index-mutation.zip"
    shutil.copyfile(built_operator.artifact, index_artifact)
    files, modes = read_archive(index_artifact)
    manifest = load_manifest(files)
    forged_index = render_module_index([ModuleDescriptor("forged", "Forged.")])
    files[index_path] = forged_index
    manifest["module_index"]["sha256"] = sha256_bytes(forged_index)
    manifest_row(manifest, index_path)["projected_sha256"] = sha256_bytes(forged_index)
    store_manifest(files, manifest)
    rewrite_archive(index_artifact, files, modes)
    assert_validation_fails(run_validator(index_artifact, built_operator.repo, built_operator.commit))

    provenance_artifact = tmp_path / "provenance-mutation.zip"
    shutil.copyfile(built_operator.artifact, provenance_artifact)
    files, modes = read_archive(provenance_artifact)
    manifest = load_manifest(files)
    manifest["root_template_sha256"] = "0" * 64
    store_manifest(files, manifest)
    rewrite_archive(provenance_artifact, files, modes)
    assert_validation_fails(run_validator(provenance_artifact, built_operator.repo, built_operator.commit))


def test_a19_dirty_worktree_does_not_change_explicit_commit_artifact_and_dirty_builder_is_rejected(tmp_path):
    repo, commit = clone_repo(tmp_path)
    clean = run_builder(repo, commit, tmp_path / "clean")
    clean_bytes = clean.read_bytes()

    dirty_skill = repo / "skills/recipe-engineering/SKILL.md"
    dirty_skill.write_bytes(dirty_skill.read_bytes() + b"\nDIRTY-WORKTREE-A19\n")
    dirty = run_builder(repo, commit, tmp_path / "dirty")
    assert dirty.read_bytes() == clean_bytes

    builder_path = repo / "scripts/build_skill_package.py"
    builder_path.write_bytes(builder_path.read_bytes() + b"\n# DIRTY BUILDER A19\n")
    dirty_builder_artifact = run_builder(
        repo,
        commit,
        tmp_path / "dirty-builder",
        builder=builder_path,
        cwd=repo,
    )
    result = run_validator(dirty_builder_artifact, repo, commit)
    assert_validation_fails(result)
