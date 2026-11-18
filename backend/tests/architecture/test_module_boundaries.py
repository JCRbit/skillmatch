from pathlib import Path

from tests.architecture.boundaries import find_violations

PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "src" / "skillmatch"


def _write(root: Path, relative: str, source: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def test_the_real_package_respects_the_layering_rules() -> None:
    assert find_violations(PACKAGE_ROOT) == []


def test_core_importing_modules_is_reported(tmp_path: Path) -> None:
    _write(tmp_path, "core/bad.py", "from skillmatch.modules import jobs\n")

    violations = find_violations(tmp_path)

    assert violations == ["core/bad.py: core must not import skillmatch.modules"]


def test_modules_importing_the_api_layer_is_reported(tmp_path: Path) -> None:
    _write(tmp_path, "modules/jobs/service.py", "import skillmatch.api.deps\n")

    assert find_violations(tmp_path) == [
        "modules/jobs/service.py: modules must not import skillmatch.api.deps"
    ]


def test_reaching_into_another_module_is_reported(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "modules/jobs/service.py",
        "from skillmatch.modules.candidates.models import Candidate\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "internals of module 'candidates'" in violations[0]


def test_public_api_of_other_modules_and_own_internals_are_allowed(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "modules/jobs/service.py",
        "from skillmatch.modules.candidates import CandidateRef\n"
        "from skillmatch.modules.jobs.models import Job\n"
        "from skillmatch.core.config import Settings\n",
    )

    assert find_violations(tmp_path) == []


def test_importing_an_internal_submodule_of_another_module_is_reported(tmp_path: Path) -> None:
    _write(tmp_path, "modules/candidates/models.py", "")
    source = "from skillmatch.modules.candidates import models\n"
    _write(tmp_path, "modules/jobs/service.py", source)

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "internals of module 'candidates'" in violations[0]
