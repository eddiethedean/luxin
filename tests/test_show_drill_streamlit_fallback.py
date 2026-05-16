"""Tests for show_drill_table import fallback when Streamlit (or luxin) is unavailable."""

import builtins
import subprocess
import sys
from pathlib import Path

import pytest

from luxin_core.tracked_df import (
    TrackedDataFrame,
    _inspector_import_should_fall_through,
)


def test_inspector_import_fall_through_includes_streamlit_and_submodules():
    for name in ("streamlit", "streamlit.runtime", "streamlit.runtime.scriptrunner"):
        exc = ModuleNotFoundError("missing", name=name)
        assert _inspector_import_should_fall_through(exc) is True


def test_inspector_import_fall_through_includes_luxin():
    for name in (None, "luxin", "luxin.inspector"):
        exc = ModuleNotFoundError("missing", name=name)
        assert _inspector_import_should_fall_through(exc) is True


def test_inspector_import_fall_through_rejects_other_modules():
    exc = ModuleNotFoundError("missing", name="some_other_pkg")
    assert _inspector_import_should_fall_through(exc) is False


def test_inspector_import_fall_through_rejects_non_module_not_found():
    assert _inspector_import_should_fall_through(ValueError("x")) is False


def test_show_drill_table_falls_through_when_streamlit_and_ipython_unavailable(
    monkeypatch,
):
    """Without Streamlit, skip Inspector; without IPython, luxin_nb import fails with notebook hint."""
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if isinstance(name, str):
            if name == "streamlit" or name.startswith("streamlit."):
                raise ModuleNotFoundError(
                    "No module named 'streamlit'", name="streamlit"
                )
            if name == "IPython" or name.startswith("IPython."):
                raise ModuleNotFoundError("No module named 'IPython'", name="IPython")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    for key in (
        "luxin.inspector",
        "streamlit",
        "luxin.components.table_view",
        "luxin.streamlit_backend",
    ):
        monkeypatch.delitem(sys.modules, key, raising=False)
    for key in list(sys.modules.keys()):
        if key == "luxin_nb" or key.startswith("luxin_nb."):
            monkeypatch.delitem(sys.modules, key, raising=False)

    df = TrackedDataFrame({"a": [1, 1], "b": [1, 2]})
    agg = df.groupby("a").sum()
    with pytest.raises(ImportError, match="luxin-nb|notebook|Jupyter"):
        agg.show_drill_table()


def test_show_drill_subprocess_no_streamlit_or_ipython():
    """Isolated interpreter: block streamlit + IPython imports; expect notebook-oriented ImportError."""
    root = Path(__file__).resolve().parents[1]
    script = r"""
import builtins
_real_import = builtins.__import__

def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if isinstance(name, str):
        if name == "streamlit" or name.startswith("streamlit."):
            raise ModuleNotFoundError("No module named 'streamlit'", name="streamlit")
        if name == "IPython" or name.startswith("IPython."):
            raise ModuleNotFoundError("No module named 'IPython'", name="IPython")
    return _real_import(name, globals, locals, fromlist, level)

builtins.__import__ = _guarded_import

from luxin_core.tracked_df import TrackedDataFrame

df = TrackedDataFrame({"a": [1, 1], "b": [1, 2]})
agg = df.groupby("a").sum()
try:
    agg.show_drill_table()
except ImportError as e:
    msg = str(e).lower()
    assert "luxin-nb" in msg or "notebook" in msg or "jupyter" in msg, msg
else:
    raise SystemExit("expected ImportError from show_drill_table")
"""
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(root)
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(root),
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
