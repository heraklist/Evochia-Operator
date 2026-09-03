from pathlib import Path
import importlib.util
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_VALIDATOR = ROOT / "scripts/validate_skill_package.py"
PARITY_VALIDATOR = ROOT / "scripts/validate_parity_coverage.py"
SOURCE_VALIDATOR = ROOT / "scripts/validate_source_registry.py"


def load_package_validator():
    spec = importlib.util.spec_from_file_location("validate_skill_package", PACKAGE_VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_package_validator_ignores_generated_cache_files_in_fallback_filesystem_mode(tmp_path):
    (tmp_path / "release").mkdir()
    (tmp_path / "references").mkdir()
    (tmp_path / "release/package_policy.yaml").write_text(
        "required_skills: []\n"
        "forbidden_patterns: [__pycache__, .pytest_cache]\n"
        "allowed_exception_files: []\n"
        "font_binaries_in_package: false\n"
        "max_repository_candidate_bytes: 26214400\n",
        encoding="utf-8",
    )
    (tmp_path / "release/runtime_resource_ownership.yaml").write_text(
        "resource_roots: []\nexact_resources: []\nnon_runtime_tooling: []\n",
        encoding="utf-8",
    )
    (tmp_path / "references/source_registry.yaml").write_text(
        "sources:\n  - source_id: test-source\n",
        encoding="utf-8",
    )
    cache = tmp_path / "pkg/__pycache__"
    cache.mkdir(parents=True)
    (cache / "generated.pyc").write_bytes(b"generated")
    pytest_cache = tmp_path / ".pytest_cache"
    pytest_cache.mkdir()
    (pytest_cache / "CACHEDIR.TAG").write_text("generated", encoding="utf-8")

    validator = load_package_validator()
    issues = validator.validate(tmp_path)
    assert not [issue for issue in issues if "__pycache__" in issue or ".pytest_cache" in issue]


def test_parity_validator_accepts_repo_root_dot_cli():
    result = subprocess.run(
        [sys.executable, str(PARITY_VALIDATOR), "."],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_source_registry_validator_accepts_repo_root_dot_cli():
    result = subprocess.run(
        [sys.executable, str(SOURCE_VALIDATOR), "."],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout
