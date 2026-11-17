"""Cross-cutting building blocks shared by every layer.

``core`` must stay free of business logic and must not import from ``skillmatch.api``,
``skillmatch.modules`` or ``skillmatch.app`` (enforced by ``tests/architecture``).
"""
