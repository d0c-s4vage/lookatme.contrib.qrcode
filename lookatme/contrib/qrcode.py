#!/usr/bin/env python3

"""
Adds qrcode rendering
"""


from marshmallow import fields, Schema
import os
import pyqrcode
import sys
import urwid
import yaml


from lookatme.exceptions import IgnoredByContrib
from lookatme.utils import row_text
import lookatme.render.markdown_block as md_block


# -----------------------------------------------------------------------------


class YamlRender:
    loads = lambda data: yaml.safe_load(data)
    dumps = lambda data: yaml.safe_dump(data)


class QrColumn(Schema):
    data = fields.String()
    autocaption = fields.Boolean(default=False, missing=False)
    caption = fields.String(default=None, missing=None)


class QrSchema(Schema):
    class Meta:
        render_module = YamlRender

    columns = fields.List(fields.Nested(QrColumn))


# -----------------------------------------------------------------------------


def blocks_to_squares(blocks):
    """Returns a list of list of blocks of four squares at a time. E.g.

    .. code-block:: python

        blocks = [
            [0, 0, 1, 1],
            [1, 0, 0, 1],
        ]

        # the first yielded value would be a list of two squares:

        [ [0, 0, 1, 0], [1, 1, 0, 1] ]

    In the yielded squares, the square coords start in the top-left and move
    clockwise around the square.
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


def spec_from_square(square) -> list:
    """Create a list of urwid.Text specs from a square
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

    else:
        raise NotImplementedError(f"Unimplemented square {square}")

    if not isinstance(res, list):
        res = [res]
    return res


def add_padding(code, width=4):
    """Add ``width`` number of blocks of padding to the code
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
        caption_text = md_block.render_text(text=caption)
        caption_text.align = "center"
        items.append(caption_text)

    return urwid.Padding(urwid.Pile(items), align="center", width="pack")


def qrcode_ex(data):
    """
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


def render_code(token, body, stack, loop):
    lang = token["lang"] or ""
    # match qrcode2
    if lang not in ["qrcode", "qrcode-ex"]:
        raise IgnoredByContrib()
    
    content = token["text"]
    if lang == "qrcode-ex":
        data = QrSchema().loads(content)
    else:
        column = QrColumn().dump(QrColumn())
        column["data"] = content
        data = { "columns": [ column ] }

    res = qrcode_ex(data)

    return [
        urwid.Divider(),
        res,
        urwid.Divider(),
    ]
