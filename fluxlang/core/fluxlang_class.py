"""
FluxLang — Class and Instance runtime objects.

FluxLangClass stores the class name, optional parent, and method
dictionary.  FluxLangInstance stores per-object fields in a dict and
resolves method calls through the class (with inheritance).
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ast_nodes as ast


class FluxLangClass:
    """Runtime representation of a FluxLang class declaration."""

    def __init__(self, name: str, parent: "FluxLangClass | None", methods: dict):
        self.name = name
        self.parent = parent
        self.methods = methods  # dict[str, ast.FuncDecl]

    def find_method(self, name: str):
        """Look up a method by name, walking the inheritance chain."""
        if name in self.methods:
            return self.methods[name]
        if self.parent is not None:
            return self.parent.find_method(name)
        return None

    def __repr__(self) -> str:
        return f"<class {self.name}>"


class FluxLangInstance:
    """Runtime representation of an instance of a FluxLang class."""

    def __init__(self, klass: FluxLangClass):
        self.klass = klass
        self.fields: dict[str, object] = {}

    def get(self, name: str):
        """Get a field value, raise AttributeError if not found."""
        if name in self.fields:
            return self.fields[name]
        raise AttributeError(f"'{self.klass.name}' object has no attribute '{name}'")

    def set(self, name: str, value: object):
        """Set a field value (always succeeds)."""
        self.fields[name] = value

    def __repr__(self) -> str:
        return f"<{self.klass.name} instance>"
