"""Bounded contexts of the modular monolith.

Each sub-package owns a business capability, its data and its HTTP router. Recommended internal
layout for a module (create files only when needed)::

    <module>/
    ├── __init__.py     # public API: the only thing other modules may import
    ├── router.py       # APIRouter, HTTP concerns only
    ├── schemas.py      # Pydantic request/response models
    ├── service.py      # use cases and business rules
    ├── repository.py   # persistence access
    └── models.py       # ORM entities (introduced by task B-01)

Rules (enforced by ``tests/architecture``):

* A module never imports ``skillmatch.api`` or ``skillmatch.app``.
* A module imports another module only through its package root, never its internals.
* Data owned by a module is changed only by that module.
"""
