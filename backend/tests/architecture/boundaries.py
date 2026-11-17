"""Static analysis of import rules between the layers and modules of the package."""

import ast
from pathlib import Path

PACKAGE = "skillmatch"


def _is_submodule(package_root: Path, package: str, module: str, member: str) -> bool:
    """Whether ``from <module> import <member>`` imports a sub-module rather than an attribute."""
    if module != package and not module.startswith(f"{package}."):
        return False
    relative = Path(*module.split(".")[1:]) / member
    target = package_root / relative
    return target.is_dir() or target.with_suffix(".py").is_file()


def _statements(path: Path, package_root: Path, package: str) -> list[list[str]]:
    """Return, for every import statement, the absolute dotted names it may import."""
    statements: list[list[str]] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            statements.append([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
            names.extend(
                f"{node.module}.{alias.name}"
                for alias in node.names
                if _is_submodule(package_root, package, node.module, alias.name)
            )
            statements.append(names)
    return statements


def find_violations(package_root: Path, package: str = PACKAGE) -> list[str]:
    """Check the layering rules and describe every violation found.

    Rules:
        1. ``core`` must not import ``api``, ``modules`` or ``app``.
        2. A module must not import ``api`` or ``app``.
        3. A module may import another module only through its package root.

    Args:
        package_root: Directory of the top-level package (e.g. ``src/skillmatch``).
        package: Name of the top-level package.

    Returns:
        One human-readable message per offending import statement; empty when the rules hold.
    """
    violations: list[str] = []
    for path in sorted(package_root.rglob("*.py")):
        parts = path.relative_to(package_root).with_suffix("").parts
        layer = parts[0]
        current_module = parts[1] if layer == "modules" and len(parts) > 1 else None
        for names in _statements(path, package_root, package):
            for name in names:
                problem = _check(name, layer, current_module, package)
                if problem:
                    violations.append(f"{path.relative_to(package_root).as_posix()}: {problem}")
                    break  # report each statement once
    return violations


def _check(name: str, layer: str, current_module: str | None, package: str) -> str | None:
    """Return a description if importing ``name`` breaks a rule, otherwise ``None``."""
    forbidden_for_core = (f"{package}.api", f"{package}.modules", f"{package}.app")
    forbidden_for_modules = (f"{package}.api", f"{package}.app")

    if layer == "core" and _is_within(name, forbidden_for_core):
        return f"core must not import {name}"
    if layer == "modules":
        if _is_within(name, forbidden_for_modules):
            return f"modules must not import {name}"
        pieces = name.split(".")
        if pieces[:2] == [package, "modules"] and len(pieces) > 3 and pieces[2] != current_module:
            return f"{name} reaches into the internals of module '{pieces[2]}'"
    return None


def _is_within(name: str, prefixes: tuple[str, ...]) -> bool:
    """Whether ``name`` equals one of ``prefixes`` or lives below it."""
    return any(name == prefix or name.startswith(f"{prefix}.") for prefix in prefixes)
