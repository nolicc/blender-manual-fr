#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division

import re
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive

CONTROL_HEIGHT = 30

_re_size = re.compile("(\d+)(|%|px)$")
_re_aspect = re.compile("(\d+):(\d+)")


def get_size(d, key):
    if key not in d:
        return None
    m = _re_size.match(d[key])
    if not m:
        raise ValueError("invalid size %r" % d[key])
    return int(m.group(1)), m.group(2) or "px"


def css(d):
    return "; ".join(sorted("%s: %s" % kv for kv in d.items()))


class youtube(nodes.General, nodes.Element):
    pass


def visit_youtube_node(self, node):
    aspect = node["aspect"]
    width = node["width"]
    height = node["height"]

    if aspect is None:
        aspect = 16, 9

    if (height is None) and (width is not None) and (width[1] == "%"):
        style = {
            "padding-top": "%dpx" % CONTROL_HEIGHT,
            "padding-bottom": "%f%%" % (width[0] * aspect[1] / aspect[0]),
            "width": "%d%s" % width,
            "position": "relative",
        }
        self.body.append(self.starttag(node, "div", style=css(style)))
        style = {
            "position": "absolute",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100%",
            "border": "0",
        }
        attrs = {
            "src": "http://www.youtube.com/embed/%s" % node["id"],
            "style": css(style),
        }
        self.body.append(self.starttag(node, "iframe", **attrs))
        self.body.append("</iframe></div>")
    else:
        if width is None:
            if height is None:
                width = 560, "px"
            else:
                width = height[0] * aspect[0] / aspect[1], "px"
        if height is None:
            height = width[0] * aspect[1] / aspect[0], "px"
        style = {
            "width": "%d%s" % width,
            "height": "%d%s" % (height[0] + CONTROL_HEIGHT, height[1]),
            "border": "0",
        }
        attrs = {
            "src": "http://www.youtube.com/embed/%s" % node["id"],
            "style": css(style),
        }
        self.body.append(self.starttag(node, "iframe", **attrs))
        self.body.append("</iframe>")


def depart_youtube_node(self, node):
    pass


def nop_node(self, node):
    pass


class YouTube(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "width": directives.unchanged,
        "height": directives.unchanged,
        "aspect": directives.unchanged,
    }

    def run(self):
        if "aspect" in self.options:
            aspect = self.options.get("aspect")
            m = _re_aspect.match(aspect)
            if m is None:
                raise ValueError("invalid aspect ratio %r" % aspect)
            aspect = tuple(int(x) for x in m.groups())
        else:
            aspect = None
        width = get_size(self.options, "width")
        height = get_size(self.options, "height")
        return [
            youtube(
                id=self.arguments[0],
                aspect=aspect,
                width=width,
                height=height,
                )
            ]


def setup(app):
    app.add_node(
            youtube,
            html=(visit_youtube_node, depart_youtube_node),
            latex=(nop_node, nop_node),
            text=(nop_node, nop_node),
            )
    app.add_directive("youtube", YouTube)
