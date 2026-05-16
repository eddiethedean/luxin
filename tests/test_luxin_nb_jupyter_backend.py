"""Tests for luxin_nb jupyter_backend wrapper."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest


@pytest.mark.notebook
def test_display_jupyter_forwards_to_display_drill_table():
    with patch("luxin_nb.jupyter_backend.display_drill_table") as mock_disp:
        from luxin_nb.jupyter_backend import display_jupyter

        agg = pd.DataFrame({"x": [1]})
        detail = pd.DataFrame({"x": [1], "y": [2]})
        mapping = {("a",): [0]}
        display_jupyter(agg, detail, mapping, ["x"], extra_opt=1)

        mock_disp.assert_called_once()
        args, kwargs = mock_disp.call_args
        assert args[0] is agg
        assert args[1] is detail
        assert args[2] == mapping
        assert args[3] == ["x"]
        assert kwargs.get("extra_opt") == 1
