"""
Perform basic testing of the qrcode module
"""


import pytest
import urwid


import lookatme.contrib.qrcode as qrcode


def test_ignores(mocker):
    """Test that metadata is parsed and set correctly
    """
    mocker.patch.object(qrcode, "qrcode_ex")

    with pytest.raises(qrcode.IgnoredByContrib):
        qrcode.render_code({"lang": "notqrcode"}, None, None, None)


def test_metadata_qrcode(mocker):
    """Test that metadata is parsed and set correctly
    """
    ex_fn = mocker.patch.object(qrcode, "qrcode_ex")

    token = {
        "lang": "qrcode",
        "text": "data",
    }
    res = qrcode.render_code(token, None, None, None)

    assert isinstance(res[0], urwid.Divider)
    assert isinstance(res[-1], urwid.Divider)

    assert ex_fn.call_count == 1

    ex_data = ex_fn.call_args[0][0]
    assert len(ex_data["columns"]) == 1
    assert ex_data["columns"][0] == {
        "data": "data",
        "autocaption": True,
        "caption": None,
    }


def test_metadata_qrcode_ex(mocker):
    """Test that metadata is parsed and set correctly
    """
    ex_fn = mocker.patch.object(qrcode, "qrcode_ex")

    token = {
        "lang": "qrcode-ex",
        "text": """
columns:
  - data: new data
    autocaption: false
    caption: A different caption
        """
    }
    res = qrcode.render_code(token, None, None, None)

    assert isinstance(res[0], urwid.Divider)
    assert isinstance(res[-1], urwid.Divider)

    assert ex_fn.call_count == 1

    ex_data = ex_fn.call_args[0][0]
    assert len(ex_data["columns"]) == 1
    assert ex_data["columns"][0] == {
        "data": "new data",
        "autocaption": False,
        "caption": "A different caption",
    }


def test_render_single_column(mocker):
    """Test that metadata is parsed and set correctly
    """
    token = {
        "lang": "qrcode",
        "text": "qr",
    }
    res = qrcode.render_code(token, None, None, None)

    assert isinstance(res[0], urwid.Divider)
    assert isinstance(res[1], urwid.Columns)
    assert isinstance(res[2], urwid.Divider)


def test_render_multiple_column(mocker):
    """Test that metadata is parsed and set correctly
    """
    token = {
        "lang": "qrcode",
        "text": """
columns:
  - data: column1
    autocaption: false
    caption: A different caption
  - data: column2
    autocaption: false
    caption: Some caption
        """
    }
    res = qrcode.render_code(token, None, None, None)

    assert isinstance(res[0], urwid.Divider)
    assert isinstance(res[1], urwid.Columns)
    assert isinstance(res[2], urwid.Divider)
