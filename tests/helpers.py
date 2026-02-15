"""
helpers.py — shared utilities for the FluxLang pytest test suite.

Provides ``run_flux(source_or_path)`` which lexes, parses, and interprets
a FluxLang program and returns its stdout as a list of strings (one per
print() call), making assertions straightforward.
"""

from __future__ import annotations
import os
from typing import Union

from fluxlang.core.lexer import Lexer
from fluxlang.core.parser import Parser
from fluxlang.core.interpreter import Interpreter
from fluxlang.core.errors import FluxLangError


def run_flux(
    source: str,
    *,
    path: str = "",
) -> list[str]:
    """
    Run a FluxLang source string through the full pipeline and capture output.

    Parameters
    ----------
    source:
        FluxLang source code as a string.
    path:
        Optional absolute path; used only so the interpreter can resolve
        relative ``import`` statements.  Leave empty for self-contained tests.

    Returns
    -------
    list[str]
        Lines printed by the program (one entry per ``print()`` call,
        *without* a trailing newline).

    Raises
    ------
    FluxLangError
        Re-raised for any lexer / parser / runtime error so individual
        tests can assert on error scenarios.
    """
    captured: list[str] = []

    def _capture(*args, sep: str = " ", end: str = "\n") -> None:
        captured.append(sep.join(str(a) for a in args))

    tokens = Lexer(source).tokenize()
    tree = Parser(tokens).parse()
    interp = Interpreter(
        source=source,
        current_file=os.path.abspath(path) if path else "",
        print_fn=_capture,
    )
    interp.interpret(tree)
    return captured


def run_flux_file(path: str) -> list[str]:
    """
    Run a ``.flux`` file and capture its output.

    Parameters
    ----------
    path:
        Absolute (or CWD-relative) path to the ``.flux`` file.

    Returns
    -------
    list[str]
        Lines printed by the program.
    """
    abs_path = os.path.abspath(path)
    with open(abs_path, encoding="utf-8") as fh:
        source = fh.read()
    return run_flux(source, path=abs_path)
