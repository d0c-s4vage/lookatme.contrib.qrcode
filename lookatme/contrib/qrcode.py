#!/usr/bin/env python3


"""
Adds qrcode rendering
"""


from marshmallow import fields, Schema
import os
import pyqrcode
import sys
from typing import List, Dict
import urwid
import yaml


from lookatme.exceptions import IgnoredByContrib
from lookatme.utils import row_text
import lookatme.render.markdown_block as md_block


def user_warnings():
    """No warnings here
    """
    return []


# -----------------------------------------------------------------------------


class YamlRender:
    loads = lambda data: yaml.safe_load(data)
    dumps = lambda data: yaml.safe_dump(data)


class QrColumn(Schema):
    data = fields.String()
    autocaption = fields.Boolean(default=True, missing=True)
    caption = fields.String(default=None, missing=None)


class QrSchema(Schema):
    class Meta:
        render_module = YamlRender

    columns = fields.List(fields.Nested(QrColumn))


# -----------------------------------------------------------------------------


def blocks_to_squares(blocks: List[List[int]]) -> List[List[List[int]]]:
    """Returns a list of list of blocks of four squares at a time. E.g.

    .. code-block:: python

        blocks = [
            [A, B, 1, 1],
            [C, D, 0, 1],
        ]

        # would return the list below containing a list of rows, with each
        # row being a list of squares

        [ [ [A, B, C, D], [1, 1, 0, 1] ] ]

    In the returned squares, the square coords go:

      * top-left
      * top-right
      * bottom-left
      * bottom-right

    :param blocks: List of blocks to transform into squares
    """
    max_row = len(blocks)
    max_col = len(blocks[0])

    def get_pos(row, col):
        if row >= len(blocks):
            return None
        if col >= len(blocks[0]):
            return None
        val = blocks[row][col]
        if val == 1:
            return None
        return val

    square_rows = []
    for row in range(0, len(blocks), 2):
        curr_square_row = []
        for col in range(0, len(blocks[0]), 2):
            tl = get_pos(row, col)
            tr = get_pos(row, col+1)
            bl = get_pos(row+1, col)
            br = get_pos(row+1, col+1)
            curr_square_row.append([tl, tr, bl, br])
        square_rows.append(curr_square_row)

    return square_rows


def spec_from_square(square: List[int]) -> list:
    """Create a list of urwid.Text specs from a square

    :param square: The square to create the specs from
    """
    fg = "white"
    bg = "black"
    normal = lambda: urwid.AttrSpec(fg, bg)
    invert = lambda: urwid.AttrSpec(bg, fg)

    X = None

    if square == [0, 0, 0, 0]:
        res = (normal(), "██")
    elif square == [X, X, X, X]:
        res = (invert(), "██")

    elif square == [X, X, 0, 0]:
        res = (normal(), "▄▄")
    elif square == [0, 0, X, X]:
        res = (invert(), "▄▄")

    elif square == [X, 0, 0, 0]:
        res = (normal(), "▄█")
    elif square == [0, 0, X, 0]:
        res = [(invert(), "▄"), (normal(), "█")]
    elif square == [0, 0, 0, X]:
        res = [(normal(), "█"), (invert(), "▄")]
    elif square == [0, X, 0, 0]:
        res = (normal(), "█▄")

    elif square == [X, 0, X, 0]:
        res = [(invert(), "█"), (normal(), "█")]
    elif square == [0, X, 0, X]:
        res = [(normal(), "█"), (invert(), "█")]

    elif square == [X, 0, 0, X]:
        res = [(normal(), "▄"), (invert(), "▄")]
    elif square == [0, X, X, 0]:
        res = [(invert(), "▄"), (normal(), "▄")]

    elif square == [0, X, X, X]:
        res = [(invert(), "▄"), (invert(), "█")]
    elif square == [X, 0, X, X]:
        res = [(invert(), "█"), (invert(), "▄")]
    elif square == [X, X, 0, X]:
        res = [(normal(), "▄"), (invert(), "█")]
    elif square == [X, X, X, 0]:
        res = [(invert(), "█"), (normal(), "▄")]

    if not isinstance(res, list):
        res = [res]
    return res


def add_padding(code: List[List[int]], width:int=4) -> List[List[int]]:
    """Add ``width`` number of blocks of padding to the code

    :param code: The qrcode on/off image
    :param width: The amount of padding to add
    """
    # add four to the left and right
    lr_padding = [0] * width
    top_padding = [0] * (len(code[0]) + (width*2))

    res = []
    # add top padding
    for _ in range(width):
        res.append(top_padding)

    for row in code:
        res.append(lr_padding + row + lr_padding)

    # add bottom padding
    for _ in range(width):
        res.append(top_padding)

    return res


def qrcode_raw_render(data: str) -> urwid.Text:
    """Render the qrcode into an urwid.Text

    :param data: The data to encode in a qrcode and render 
    """
    res = pyqrcode.create(data)

    # a list of rows of squares
    text_spec = []
    code = add_padding(res.code)

    for row_idx, row in enumerate(blocks_to_squares(code)):
        for square in row:
            square_text_spec = spec_from_square(square)
            text_spec += square_text_spec

        if row_idx < len(res.code):
            text_spec.append("\n")

    return urwid.Text(text_spec)


def qrcode_render(data: str, autocaption: bool=True, caption: str=None) -> urwid.Widget:
    """Render a qrcode.

    :param data: The data to render as a qrcode
    :param autocaption: If caption should be added automatically
    """
    items = []

    qr_text = qrcode_raw_render(data)
    items.append(
        urwid.Padding(qr_text, align="center", width="pack"),
    )

    if autocaption and caption is None:
        caption = data.split("\n")[0]
    if caption is not None:
        caption_text = md_block.render_text(text=caption)[0]
        caption_text.align = "center"
        items.append(caption_text)

    return urwid.Padding(urwid.Pile(items), align="center", width="pack")


def qrcode_ex(data: dict) -> urwid.Columns:
    """Handle the structured QR data (parsed from the YAML) to render QR
    codes for each defined column.
    """
    cols = []
    for column in data["columns"]:
        res = qrcode_render(
            data=column["data"],
            autocaption=column["autocaption"],
            caption=column["caption"],
        )
        cols.append(res)

    return urwid.Columns(cols)


def render_code(token: Dict, body: urwid.Widget, stack: List[urwid.Widget], loop: urwid.MainLoop):
    """Main extension function that has first-chance at handling the ``render_code``
    function ``lookatme.render.markdown_block``

    This extension ignores all code blocks **except** ones with the language
    ``qrcode`` or ``qrcode-ex``.

    * ``qrcode-ex`` - Expects the contents of the code block to be yaml of
      the form:

    .. code-block:: yaml

        columns:
          - data: "Data to be qr encoded"
            autocaption: true/false # optional
            caption: "Manual markdown caption" # optional

    One or more columns may defined to render QR codes side-by-side

    If ``autocaption`` is True **and** ``caption`` is None, the caption will
    be set to the data that is QR encoded.
    """
    lang = token["lang"] or ""
    # match qrcode2
    if lang not in ["qrcode", "qrcode-ex"]:
        raise IgnoredByContrib()
    
    content = token["text"]
    if lang == "qrcode-ex":
        data = QrSchema().loads(content)
    else:
        column = QrColumn().dump({})
        column["data"] = content
        data = { "columns": [ column ] }

    res = qrcode_ex(data)

    return [
        urwid.Divider(),
        res,
        urwid.Divider(),
    ]
