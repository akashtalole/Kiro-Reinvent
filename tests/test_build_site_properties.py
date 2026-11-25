"""Property-based tests for scripts/build_site.py (Hypothesis).

Each property traces to a requirement in .kiro/specs/site-catalog/requirements.md.
Run: python -m pytest tests -q
"""
from __future__ import annotations

import json
import os
import posixpath
import string
import sys
from pathlib import Path

from hypothesis import given, settings, strategies as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_site as bs  # noqa: E402

KEY = st.text(alphabet=string.ascii_lowercase + "_", min_size=1, max_size=12)
# Printable values a lab author might type, excluding newlines (front matter is one line per key).
WORD = st.text(alphabet=string.ascii_letters + string.digits + " -_.()/&·—:',#[]", min_size=1, max_size=30)
SERVICE = st.one_of(
    st.sampled_from(["Kiro IDE", "Kiro CLI", "Kiro Crew", "Kiro Web", "Kiro autonomous agent", "AWS MCP Server",
                     "CloudWatch MCP", "Strands Agents", "AgentCore Runtime", "AgentCore Memory", "Amazon Bedrock",
                     "Bedrock Guardrails", "Lambda", "GitHub", "Kiro", "ACP", "MCP"]),
    WORD,
)


# --- Requirement 2: product derivation -------------------------------------------------

@given(st.lists(SERVICE, max_size=12))
def test_products_are_known_unique_and_canonically_ordered(services):
    products = bs.products_for(services)
    assert len(products) == len(set(products))
    assert all(p in bs.PRODUCT_NAMES for p in products)
    assert products == [p for p in bs.PRODUCT_NAMES if p in products]


@given(st.lists(SERVICE, max_size=8), st.lists(SERVICE, max_size=8))
def test_products_are_monotonic(base, extra):
    """Adding services to a lab can add products but never remove one."""
    assert set(bs.products_for(base)) <= set(bs.products_for(base + extra))


@given(st.lists(st.sampled_from(["AgentCore Runtime", "AgentCore Gateway", "AgentCore Memory", "AgentCore Policy"]), min_size=1))
def test_agentcore_alone_is_not_bedrock(services):
    products = bs.products_for(services)
    assert "AgentCore" in products and "Amazon Bedrock" not in products


@given(st.lists(st.sampled_from(bs.PRODUCT_NAMES), unique=True))
def test_explicit_products_override_and_keep_canonical_order(explicit):
    got = bs.products_for(["Lambda"], explicit or None)
    assert got == ([p for p in bs.PRODUCT_NAMES if p in explicit] if explicit else [])


# --- Requirement 1: front matter round-trips ---------------------------------------------

def _yaml_scalar(v):
    if isinstance(v, int):
        return str(v)
    return json.dumps(v, ensure_ascii=False)  # always quote strings


def _yaml_value(v):
    if isinstance(v, list):
        return "[" + ", ".join(_yaml_scalar(x) for x in v) + "]"
    return _yaml_scalar(v)


VALUE = st.one_of(
    st.integers(min_value=0, max_value=10_000),
    WORD,
    st.lists(WORD, max_size=6),
)


@settings(max_examples=300)
@given(st.dictionaries(KEY, VALUE, min_size=1, max_size=8), WORD)
def test_front_matter_round_trips(meta, heading):
    text = "---\n" + "".join(f"{k}: {_yaml_value(v)}\n" for k, v in meta.items()) + f"---\n\n# {heading}\n"
    parsed, body = bs.parse_front_matter(text)
    assert parsed == meta
    assert bs.first_heading(body) == heading.strip()


# --- Requirement 3: pretty-URL stubs point at the real page ------------------------------

SEGMENT = st.text(alphabet=string.ascii_lowercase + string.digits + "-", min_size=1, max_size=10)


@given(st.lists(SEGMENT, min_size=1, max_size=4), st.sampled_from(["labs.html", "doc.html?doc=x", "index.html#paths"]))
def test_stub_targets_resolve_to_site_root(segments, target):
    rel_dir = "/".join(segments)
    out = Path(os.environ.get("TMPDIR", "/tmp")) / "stub-prop"
    old = bs.OUT
    bs.OUT = out
    try:
        bs.write_stub(rel_dir, target, "T")
        html = (out / rel_dir / "index.html").read_text(encoding="utf-8")
    finally:
        bs.OUT = old
    href = html.split('http-equiv="refresh" content="0; url=')[1].split('"')[0]
    page, _, _ = target.partition("?")
    page = page.partition("#")[0]
    assert posixpath.normpath(posixpath.join(rel_dir, href.partition("?")[0].partition("#")[0])) == page


# --- Requirement 4: catalog integrity (example-based over the real data) -----------------

def _lab_ids():
    return {str(bs.parse_front_matter(p.read_text(encoding="utf-8"))[0]["id"]).zfill(2)
            for p in (ROOT / "labs").glob("*/README.md")}


def test_paths_and_use_cases_reference_real_labs():
    ids = _lab_ids()
    cat = json.loads((ROOT / "site/data/catalog.json").read_text(encoding="utf-8"))
    missing = [lab for p in cat["paths"] for lab in p["labs"] if lab not in ids]
    missing += [u["lab"] for kind in cat["useCases"].values() for u in kind if u.get("lab") and u["lab"] not in ids]
    assert not missing, missing


def test_every_lab_has_at_least_one_product():
    for readme in (ROOT / "labs").glob("*/README.md"):
        meta, _ = bs.parse_front_matter(readme.read_text(encoding="utf-8"))
        assert bs.products_for(meta.get("services", []), meta.get("products")), readme.parent.name
