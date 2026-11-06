"""Execute the actual browser extractor on DOM/style/Range doubles, not layout."""
import json
from pathlib import Path
import subprocess
import pytest
from test_sorting_empty_jpeg_regression import _assert_complete_geometry


def _bounds(mutation="valid"):
    result = subprocess.run(["node", str(Path(__file__).with_name("export_dom_probe_controls.cjs")), mutation],
                            check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def test_complete_geometry_accepts_full_content():
    bounds = _bounds()
    assert any(text["text"].startswith("Arreglo vacío") and text["fontSize"] == 16
               for box in bounds for text in box["text"])
    _assert_complete_geometry([1000, 800], 500, 400, 500, bounds)


@pytest.mark.parametrize("mutation", ["zero_area", "missing_memory", "hidden_memory", "hidden_narration",
    "hidden_visual", "ancestor_opacity", "ancestor_visibility", "closed_details", "transparent_text",
    "empty_memory", "hidden_terminal", "zero_font", "crop_left", "crop_top", "crop_right", "crop_bottom", "text_crop"])
def test_actual_dom_probe_rejects_hidden_or_clipped_content(mutation):
    with pytest.raises(AssertionError):
        _assert_complete_geometry([1000, 800], 500, 400, 500, _bounds(mutation))


@pytest.mark.parametrize("size,width,height,live_width", [([500,400],500,400,500),
    ([1000,800],500,400,600), ([1000,38],500,19,500)])
def test_geometry_rejects_scale_width_and_raw_only(size, width, height, live_width):
    with pytest.raises(AssertionError):
        _assert_complete_geometry(size, width, height, live_width, _bounds())
