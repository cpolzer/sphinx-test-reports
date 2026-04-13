from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "html", "srcdir": "doc_test/doc_test_file"}],
    indirect=True,
)
def test_doc_build_html(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text()
    assert html


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "html", "srcdir": "doc_test/doc_test_file"}],
    indirect=True,
)
def test_test_file_needs_extra_options_no_warning(test_app):
    import subprocess

    app = test_app

    srcdir = Path(app.srcdir)
    out_dir = srcdir / "_build"

    out = subprocess.run(
        ["sphinx-build", "-M", "html", srcdir, out_dir],
        capture_output=True,
        check=False,
    )

    assert out.returncode == 0

    # Check no warnings — Sphinx writes warnings to stderr, not stdout
    assert "WARNING" not in out.stdout.decode("utf-8")
    assert "WARNING" not in out.stderr.decode("utf-8")
    assert "ERROR" not in out.stderr.decode("utf-8")


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "html", "srcdir": "doc_test/doc_test_file"}],
    indirect=True,
)
def test_test_file_renders_need_with_counts(test_app):
    """test-file directive must render a need node with correct count fields.

    Catches regressions where int values (suites, cases, passed, etc.) passed
    to add_need() are rejected by newer sphinx-needs versions.
    """
    app = test_app
    app.build()
    assert app.statuscode == 0

    html = Path(app.outdir, "index.html").read_text()
    assert "TESTFILE_1" in html
    
    # Test 1: Verify HTML contains the need with expected structure
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    need = soup.find(class_='need', attrs={'data-need-id': 'TESTFILE_1'})
    assert need is not None
    
    # Test 2: Verify data attributes for integer fields exist
    required_fields = ['suites', 'cases', 'passed', 'skipped', 'failed', 'errors']
    for field in required_fields:
        assert f'data-{field}' in need.attrs, f"Missing data-{field} attribute"
        value = need[f'data-{field}']
        assert value.isdigit(), f"data-{field} should be numeric, got: {value}"
    
    # Test 3: Optional - Verify actual values are reasonable
    assert int(need['data-suites']) >= 0  # Should be non-negative
    assert int(need['data-cases']) >= 0   # Should be non-negative
