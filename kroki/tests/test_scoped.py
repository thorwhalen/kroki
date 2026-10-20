"""Scoped inline SVG: interactivity kept, CSS confined to the diagram (#8).

The oracle tests parse the rewritten stylesheet with an independent CSS tokenizer
(``tinycss2``) and match every selector against a page holding notebook content
next to the diagram (``cssselect`` + ``lxml``): no rule may reach outside it.
"""

from __future__ import annotations

import pytest
from IPython.display import SVG

import kroki
from kroki import bytes_to_image
from kroki.scoped_css import scope_css, scope_svg
from kroki.tests.test_rendering import LEAKY_SVG

# The shape of a PlantUML SVG with a link: an <a> with both href spellings, a
# <title> tooltip, and a stylesheet (newer PlantUML writes one) in CDATA.
PLANTUML_SVG = (
    '<?xml version="1.0" encoding="us-ascii" standalone="no"?>'
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    'contentStyleType="text/css" height="90px" width="160px" viewBox="0 0 160 90">'
    "<defs><style type=\"text/css\"><![CDATA[a:hover{text-decoration:underline} "
    "text{font-family:sans-serif} @media print{text{fill:black}}]]></style></defs>"
    '<g><a href="https://example.com/doc" target="_top" title="Docs" '
    'xlink:href="https://example.com/doc" xlink:title="Docs">'
    "<title>Docs</title><rect width=\"80\" height=\"30\"/><text x=\"5\" y=\"20\">Alice</text>"
    "</a></g></svg>"
)

# Selectors a hostile or careless diagram might ship, each written to hit the page.
TRICKY_CSS = (
    ":root{--x:1} html body p{color:red} * {margin:0} "
    'a[title="a, b {"]{x:1} :is(p, span) > em{y:2} /* } { */ '
    "@supports (display:grid){@media screen{li,dd{z:3}}} "
    "@font-face{font-family:F;src:url(f.woff)} @keyframes k{from{opacity:0}to{opacity:1}} "
    "@import url(evil.css); svg .label, svg:hover{w:4} #mermaid-9 .node{v:5}"
)


def test_the_mermaid_sample_is_scoped_and_keeps_its_markup():
    html = kroki.svg_to_scoped_html(LEAKY_SVG, scope_id="k1")
    assert html.startswith('<svg id="k1" ')
    assert "#k1 .label{color:#333;}" in html
    assert "#k1 p{margin:0;}" in html and "#k1 span{" in html
    assert "<text>Score</text>" in html  # the drawing itself is untouched


def test_the_plantuml_sample_keeps_links_tooltips_and_cdata():
    html = kroki.svg_to_scoped_html(PLANTUML_SVG, scope_id="k2")
    assert 'href="https://example.com/doc"' in html and "<title>Docs</title>" in html
    assert "<![CDATA[#k2 a:hover{" in html
    assert "#k2 text{font-family:sans-serif}" in html
    assert "@media print{#k2 text{fill:black}}" in html
    assert html.startswith('<?xml') and '<svg id="k2" xmlns=' in html


def test_the_roots_own_id_selectors_follow_the_new_id():
    svg = '<svg id="mermaid-9"><style>#mermaid-9{font:x} #mermaid-9 .node{v:5}</style></svg>'
    assert scope_svg(svg, "k3") == (
        '<svg id="k3"><style>#k3{font:x} #k3 .node{v:5}</style></svg>'
    )


def test_import_is_dropped_and_descriptor_blocks_are_kept():
    out = scope_css(TRICKY_CSS, "k", root_ids=["mermaid-9"])
    assert "@import" not in out
    assert "@font-face{font-family:F;src:url(f.woff)}" in out
    assert "@keyframes k{from{opacity:0}to{opacity:1}}" in out  # not scoped as rules
    assert "/* } { */" in out


def test_each_display_mode():
    assert type(bytes_to_image(LEAKY_SVG, svg_display="scoped")) is kroki.ScopedSVG
    assert type(bytes_to_image(LEAKY_SVG, svg_display="inline")) is SVG
    assert type(bytes_to_image(LEAKY_SVG, svg_display="isolate")) is kroki.IsolatedSVG
    with pytest.raises(ValueError, match="svg_display"):
        bytes_to_image(LEAKY_SVG, svg_display="scope")


def test_a_scoped_svg_shows_the_same_scoped_markup_everywhere():
    """Jupyter picks text/html; an exporter may inline image/svg+xml. Same id in both."""
    from IPython.core.formatters import DisplayFormatter

    obj = bytes_to_image(LEAKY_SVG, svg_display="scoped")
    bundle, _ = DisplayFormatter().format(obj)
    assert bundle["text/html"] == bundle["image/svg+xml"]
    assert f'id="{obj.scope_id}"' in bundle["text/html"]
    other = bytes_to_image(LEAKY_SVG, svg_display="scoped")
    assert other.scope_id != obj.scope_id  # two diagrams never share a scope


def test_the_magic_takes_scoped(monkeypatch):
    monkeypatch.setattr(kroki, "diagram_image_bytes", lambda src, *args: LEAKY_SVG)
    obj = kroki.KrokiMagic.kroki(None, "mermaid --scoped", "graph TD; a-->b")
    assert type(obj) is kroki.ScopedSVG
    with pytest.raises(ValueError, match="exclusive"):
        kroki.KrokiMagic.kroki(None, "mermaid --scoped --inline", "graph TD; a-->b")


# --- oracle: an independent parser says no rule reaches the page -------------------


def _qualified_preludes(css: str):
    """Every qualified rule's selector text, at any depth of rule-holding at-rules."""
    tinycss2 = pytest.importorskip("tinycss2")
    for rule in tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True):
        if rule.type == "qualified-rule":
            yield tinycss2.serialize(rule.prelude).strip()
        elif rule.type == "at-rule" and rule.lower_at_keyword in ("media", "supports"):
            yield from _qualified_preludes(tinycss2.serialize(rule.content))


@pytest.mark.parametrize(
    "css", [TRICKY_CSS, LEAKY_SVG.decode().split("<style>")[1].split("</style>")[0]]
)
def test_no_rule_matches_anything_outside_the_scope(css):
    cssselect = pytest.importorskip("cssselect")
    lxml_html = pytest.importorskip("lxml.html")

    scoped = scope_css(css, "k", root_ids=["mermaid-9"])
    page = lxml_html.fromstring(
        "<html><body><p class='label'>notebook <span>text</span> <em>x</em></p>"
        "<ul><li>item</li></ul><a title='a, b {'>link</a>"
        "<div id='k'><p class='label'>in <span>scope</span> <em>y</em></p>"
        "<ul><li>i</li></ul><a title='a, b {'>l</a><g class='node'></g></div>"
        "</body></html>"
    )
    scope = page.get_element_by_id("k")
    inside = set(scope.iter())
    translator = cssselect.HTMLTranslator()
    preludes = list(_qualified_preludes(scoped))
    assert preludes, "the oracle saw no rules"
    for prelude in preludes:
        for selector in cssselect.parse(prelude):
            if selector.pseudo_element or ":hover" in prelude:
                continue  # dynamic or pseudo-element: nothing to match statically
            xpath = translator.selector_to_xpath(selector)
            for element in page.xpath(xpath):
                assert element in inside, f"{prelude!r} matched outside the scope"
    # And the scope still gets styled: the rewrite must not just break every rule.
    matched = {
        el
        for prelude in preludes
        for selector in cssselect.parse(prelude)
        if not selector.pseudo_element and ":hover" not in prelude
        for el in page.xpath(translator.selector_to_xpath(selector))
    }
    assert matched & inside


# --- found by the adversarial review of #10 ----------------------------------------


def _outside_rules(scoped_svg: str, scope: str):
    """Rules of *scoped_svg*'s stylesheets, decoded as a browser reads them, that are
    not confined to ``#<scope>``."""
    import html as html_lib
    import re

    pytest.importorskip("tinycss2")
    css = "".join(
        html_lib.unescape(m) for m in re.findall(r"<style[^>]*>(.*?)</style>", scoped_svg, re.S)
    )
    return [
        p
        for p in _qualified_preludes(css)
        if not all(s.strip().startswith(f"#{scope}") for s in p.split(","))
    ]


def test_entity_escaped_css_is_scoped_as_the_browser_decodes_it():
    """IPython re-serialises an SVG, turning '"' into '&quot;' in <style> text."""
    obj = bytes_to_image(
        b'<svg><style>p{content:"{"} q{color:red} svg>g{x:1}</style></svg>',
        svg_display="scoped",
    )
    out = obj._repr_html_()
    assert not _outside_rules(out, obj.scope_id), out
    assert f"#{obj.scope_id}&gt;g{{x:1}}" in out  # `svg>g` is the root's child


def test_a_self_closing_style_is_not_an_opener():
    out = scope_svg('<svg><style/><g class="a">t</g><style>p{x:1}</style></svg>', "k")
    assert '<style/><g class="a">t</g><style>#k p{x:1}</style>' in out


@pytest.mark.parametrize("value", ['url(a"b)', "url(http://x/*)"])
def test_an_unquoted_url_is_one_token(value):
    assert scope_css(f"p{{background:{value}}} q{{y:2}}", "k") == (
        f"#k p{{background:{value}}} #k q{{y:2}}"
    )


def test_page_global_at_rules_are_scoped_or_dropped():
    out = scope_css("@page{margin:0} @starting-style{p{opacity:0}}", "k")
    assert "@page" not in out
    assert "@starting-style{#k p{opacity:0}}" in out


def test_a_gt_inside_a_root_attribute_does_not_end_the_tag():
    out = scope_svg('<svg aria-label="a > b" id="m"><style>#m .n{x:1}</style></svg>', "k")
    assert out == '<svg aria-label="a > b" id="k"><style>#k .n{x:1}</style></svg>'


# --- edge cases from #11 -------------------------------------------------------------


def test_xml_id_on_the_root_is_the_roots_old_id():
    out = scope_svg('<svg xml:id="m"><style>#m .n{x:1}</style></svg>', "k")
    assert "#k .n{x:1}" in out and 'xml:id="k"' in out


def test_a_comment_at_the_head_of_a_part_does_not_hide_the_root():
    assert scope_css("a, /* c */ :root p{x:1}", "k") == "#k a, /* c */ #k p{x:1}"


def test_the_old_root_id_is_recognised_in_any_compound():
    assert scope_css(".dark #m .node{x:1}", "k", root_ids=["m"]) == ".dark #k .node{x:1}"
    assert scope_css("#m :root{--a:1}", "k", root_ids=["m"]) == "#k{--a:1}"
    # a lookalike id, and one inside an attribute selector, are not the root
    assert scope_css("#mx p{x:1}", "k", root_ids=["m"]) == "#k #mx p{x:1}"
    assert scope_css('[data-i="#m"]{x:1}', "k", root_ids=["m"]) == '#k [data-i="#m"]{x:1}'


def test_contradictory_isolate_svg_and_svg_display_are_refused():
    with pytest.raises(ValueError, match="contradicts"):
        bytes_to_image(LEAKY_SVG, isolate_svg=True, svg_display="scoped")
    with pytest.raises(ValueError, match="contradicts"):
        bytes_to_image(LEAKY_SVG, isolate_svg=False, svg_display="isolate")
    assert type(bytes_to_image(LEAKY_SVG, isolate_svg=True, svg_display="isolate")) is kroki.IsolatedSVG


# --------------------------------------------------------- global names (#12)

FONT_SVG = (
    '<svg id="a"><style><![CDATA[@font-face{font-family:"Inter";src:url(f.woff)} '
    "text{font-family:Inter, sans-serif} .x{animation:spin 1s} "
    "@keyframes spin{from{opacity:0}}]]></style>"
    '<text font-family="Inter" style="font: 12px Inter">Inter font: Inter</text></svg>'
)


def test_font_face_and_keyframes_names_are_renamed_per_scope():
    out = scope_svg(FONT_SVG, "k")
    assert '@font-face{font-family:"Inter-k"' in out
    assert "font-family:Inter-k, sans-serif" in out
    assert "animation:spin-k 1s" in out and "@keyframes spin-k" in out
    assert 'font-family="Inter-k"' in out and 'style="font: 12px Inter-k"' in out
    # text content is never rewritten
    assert ">Inter font: Inter</text>" in out


def test_two_scopes_do_not_share_font_names():
    a, b = scope_svg(FONT_SVG, "k1"), scope_svg(FONT_SVG, "k2")
    assert "Inter-k1" in a and "Inter-k2" not in a
    assert "Inter-k2" in b and "Inter-k1" not in b


def test_svg_without_global_names_is_unchanged_by_renaming():
    svg = '<svg id="a"><style>text{font-family:Inter}</style></svg>'
    assert scope_svg(svg, "k") == '<svg id="k"><style>#k text{font-family:Inter}</style></svg>'


def test_renamed_names_stay_safe_in_escaped_style_attributes():
    svg = '<svg><style>@font-face{font-family:F}</style><g style="font-family:F; x:&quot;y&quot;"/></svg>'
    out = scope_svg(svg, "k")
    assert 'style="font-family:F-k; x:&quot;y&quot;"' in out


def test_single_quoted_style_attribute_cannot_break_out():
    svg = (
        "<svg><style>@font-face{font-family:F}</style>"
        "<g style='font-family:F;a:&apos;\" onload=alert(1) x=&apos;'/></svg>"
    )
    out = scope_svg(svg, "k")
    assert "onload=alert(1) x=" not in out.replace("&apos;", "").replace("&quot;", "") or (
        "<g style='font-family:F-k;a:&apos;&quot; onload=alert(1) x=&apos;'/>" in out
    )
    import xml.etree.ElementTree as ET

    g = ET.fromstring(out)[1]
    assert list(g.attrib) == ["style"]


@pytest.mark.parametrize(
    "name", [r"a\1", r"a\g<x>", r"a\n", 'a"b', "a<b", "a]]>b", "a&b", "none", "ease"]
)
def test_unsafe_or_reserved_names_are_left_alone(name):
    svg = f'<svg><style><![CDATA[@font-face{{font-family:"{name}"}} t{{font-family:"{name}"}}]]></style></svg>'
    out = scope_svg(svg, "k")  # must not raise
    assert f"{name}-k" not in out


def test_keyframes_name_inside_the_keyword_is_renamed_in_place():
    out = scope_svg("<svg><style>@keyframes frames{to{x:1}}</style></svg>", "k")
    assert "@keyframes frames-k{" in out


def test_global_name_scan_is_linear():
    import time

    svg = "<svg><style>" + "@font-face{font-family:a;" * 6000 + "</style></svg>"
    t = time.perf_counter()
    scope_svg(svg, "k")
    assert time.perf_counter() - t < 2


def test_many_names_do_not_blow_up():
    import time

    css = "".join(f"@keyframes n{i}{{to{{x:1}}}} " for i in range(3000))
    t = time.perf_counter()
    scope_svg(f"<svg><style>{css}a{{animation:n1 1s}}</style></svg>", "k")
    assert time.perf_counter() - t < 3


def test_font_family_attribute_entities_are_decoded_before_matching():
    svg = '<svg><style>@font-face{font-family:"A B"}</style><text font-family="A B"/></svg>'
    assert 'font-family="A B-k"' in scope_svg(svg, "k")
