"""Live behavior checks on the standalone notebook outside the repository."""
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(os.environ.get('RUN_BROWSER_TESTS') != '1', reason='Set RUN_BROWSER_TESTS=1 for live checks')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


@pytest.fixture(scope='module')
def standalone_page(tmp_path_factory):
    from playwright.sync_api import sync_playwright
    isolated = tmp_path_factory.mktemp('standalone-only')
    notebook = isolated/'standalone_app.py'
    notebook.write_bytes((ROOT/'standalone_app.py').read_bytes())
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    url = f'http://127.0.0.1:{port}'
    runtime = os.environ.get('SUBMISSION_RUNTIME', sys.executable)
    log = (isolated/'server.log').open('w')
    proc = subprocess.Popen([runtime, '-m', 'marimo', 'run', str(notebook), '--headless', '--port', str(port)], cwd=isolated, stdout=log, stderr=log)
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=.5):
                    break
            except OSError:
                time.sleep(.1)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('CHROME_PATH', CHROME), headless=True)
            options = {'viewport': {'width':1440, 'height':1000}, 'accept_downloads':True}
            capture = os.environ.get('SUBMISSION_CAPTURE') == '1'
            if capture:
                options['record_video_dir'] = str(isolated/'video')
            context = browser.new_context(**options)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.goto(url, wait_until='networkidle', timeout=20000)
            page.locator('.bat-container').first.wait_for()
            page.get_by_text('Portable sample', exact=False).wait_for()
            yield page
            assert errors == [], errors
            if capture:
                video = page.video
            context.close()
            if capture:
                out = ROOT/'docs/videos/submission_interactions_rehearsal.webm'
                out.parent.mkdir(parents=True, exist_ok=True)
                video.save_as(str(out))
            browser.close()
    finally:
        proc.terminate()
        proc.wait(timeout=5)
        log.close()


def test_linked_controls_and_exact_csv(standalone_page):
    from playwright.sync_api import expect
    from models.txconformal_selector import conformal_fdr_select
    page = standalone_page
    # Long metric captions must not force any card outside the viewport.
    for width in (1440, 1024, 768, 390):
        page.set_viewport_size({'width': width, 'height': 1000})
        bounds = page.locator('.cyp-stat').evaluate_all(
            '(els) => els.map(e => ({right: e.getBoundingClientRect().right, '
            'width: e.getBoundingClientRect().width, scroll: e.scrollWidth}))'
        )
        assert len(bounds) == 10
        assert all(b['right'] <= width and b['scroll'] <= b['width'] + 2 for b in bounds)
    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.get_by_role('switch').click()
    expect(page.get_by_text('An alert is a hypothesis.', exact=False)).to_be_visible()
    page.screenshot(path=str(ROOT/'docs/screenshots/submission_overview.png'))

    # Change architecture and verify the resulting metrics, not just the dropdown state.
    model = page.locator('select').filter(has=page.locator('option[value="Logistic Regression (ECFP4)"]'))
    model.select_option(label='Logistic Regression (ECFP4)')
    expect(page.get_by_text('0.3738', exact=True)).to_be_visible()
    page.get_by_role('heading', name='Act 2: How much does the split matter?', exact=False).scroll_into_view_if_needed()
    page.screenshot(path=str(ROOT/'docs/screenshots/submission_benchmark.png'))
    model.select_option(label='LightGBM (ECFP4 2048-bit)')
    expect(page.get_by_text('0.3853', exact=True)).to_be_visible()

    custom = page.get_by_placeholder('Paste custom candidate SMILES', exact=False)
    custom.fill('invalid<<<');custom.press('Enter')
    expect(page.get_by_text('Structure unavailable', exact=False)).to_be_visible()
    custom.fill('N[C@H](C)C(=O)O');custom.press('Enter')
    expect(page.get_by_text('Structure drawn', exact=False)).to_be_visible()
    custom.fill('');custom.press('Enter')
    page.get_by_text('Browse all literature examples', exact=True).click()
    page.get_by_text('Inspect the saved docking results', exact=True).click()
    literature = page.locator('marimo-table').filter(has_text='Table 1.1')
    literature.get_by_role('row').filter(has_text='Paroxetine').get_by_role('checkbox').click()
    expect(page.get_by_role('heading', name='CYP3A4 Crystallographic Active-Site Docking: Paroxetine', exact=True)).to_be_visible()

    # A real chart-point click must change the candidate card.
    chart = page.locator('.vega-embed').last
    # Export uses the same Vega view. Read its plotted positions, then click the real canvas.
    import xml.etree.ElementTree as ET
    import re
    chart.locator('summary').click()
    with page.expect_download() as svg_info:
        chart.get_by_role('link', name='Save as SVG').click()
    svg = ET.parse(svg_info.value.path()).getroot()
    parents = {child: parent for parent in svg.iter() for child in parent}
    points = [node for node in svg.iter() if 'molecule_name:' in node.attrib.get('aria-label', '')]
    node = points[8]
    name = node.attrib['aria-label'].split('molecule_name: ')[1].split(';')[0]
    x = y = 0.0
    current = node
    while current is not None:
        transform = current.attrib.get('transform', '')
        for dx, dy in re.findall(r'translate\(([-\d.]+)[ ,]+([-\d.]+)\)', transform):
            x += float(dx); y += float(dy)
        current = parents.get(current)
    chart.locator('summary').click()
    chart.locator('canvas').click(position={'x':x, 'y':y})
    expect(page.locator('[id="2d-candidate-structure"]').locator('..').get_by_text(name, exact=True)).to_be_visible()
    table = page.locator('marimo-table').filter(has_text='Table 5.1')
    row_name = 'OCNT-0022129'
    table.get_by_role('row').filter(has_text=row_name).get_by_role('checkbox').click()
    expect(page.locator('[id="2d-candidate-structure"]').locator('..').get_by_text(row_name, exact=True)).to_be_visible()

    slider = page.get_by_role('slider')
    slider.press('Home')
    expect(page.get_by_text('N=100 display candidates; nominal α=0.05', exact=False)).to_be_visible()
    with page.expect_download() as info:
        page.get_by_text('Download Selected Candidates (CSV)', exact=True).click()
    rows = list(csv.DictReader(io.StringIO(Path(info.value.path()).read_text())))
    payload = json.loads((ROOT/'data/packaged/txconformal_selection_results.json').read_text())['test_candidates_sample']
    bh = conformal_fdr_select([row['weighted_pvalue'] for row in payload], .05)
    expected = {payload[i]['molecule_name']: payload[i] for i in bh['selected_indices']}
    assert {row['molecule_name'] for row in rows} == set(expected)
    for row in rows:
        assert float(row['nominal_alpha_threshold']) == .05
        assert float(row['conformal_cutoff_pstar']) == bh['critical_cutoff']
        assert float(row['weighted_conformal_pvalue']) == expected[row['molecule_name']]['weighted_pvalue']
    page.get_by_role('heading', name='Act 5: Which molecules would we test next?', exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(ROOT/'docs/screenshots/submission_selection.png'))
    slider.press('End')
    expect(page.get_by_text('N=100 display candidates; nominal α=0.20', exact=False)).to_be_visible()
    page.set_viewport_size({'width':390,'height':844})
    page.get_by_role('heading', name='CYP3A4 Crystallographic Active-Site Docking: Paroxetine', exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(ROOT/'docs/screenshots/submission_mobile.png'))
    assert page.locator('div[style*="grid-template-columns"]').first.evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length') == 1


def test_widget_invalid_to_valid_preserves_tooltip(standalone_page):
    from playwright.sync_api import sync_playwright, expect
    from widgets.layout_engine import generate_molecule_layout
    module = 'data:text/javascript;base64,' + base64.b64encode((ROOT/'widgets/bioactivation_tracer.js').read_bytes()).decode()
    layout = generate_molecule_layout('c1ccoc1')
    page = standalone_page.context.new_page()
    try:
        page.set_content('<div id="widget"></div>')
        page.add_style_tag(content=(ROOT/'widgets/bioactivation_tracer.css').read_text())
        page.evaluate('''async ({module, layout}) => {
            const {render} = await import(module);
            const listeners = {};
            const model = {data:{layout, overlay_mode:'warheads'}, get(k){return this.data[k]}, set(k,v){this.data[k]=v}, save_changes(){}, on(k,cb){listeners[k]=cb}, off(k){delete listeners[k]}};
            window.updateLayout = value => {model.data.layout=value;listeners['change:layout']()};
            window.cleanupWidget = render({model,el:document.querySelector('#widget')});
        }''', {'module':module, 'layout':layout})
        assert page.locator('.bat-tooltip').count() == 1
        page.evaluate('v => updateLayout(v)', {'is_valid':False, 'error':'<img src=x onerror=alert(1)>'})
        assert page.locator('#widget img').count() == 0
        page.evaluate('v => updateLayout(v)', layout)
        assert page.locator('.bat-tooltip').count() == 1
        page.locator('.bat-atom-group').first.hover()
        expect(page.locator('.bat-tooltip')).to_be_visible()
        expect(page.locator('.bat-tooltip')).to_contain_text('Structural-alert heuristic')
        page.emulate_media(color_scheme='dark')
        assert page.locator('.bat-container').evaluate('(e)=>getComputedStyle(e).getPropertyValue("--bat-bg").trim()')
        page.evaluate('cleanupWidget()')
        assert page.locator('.bat-container').count() == 0
    finally:
        page.close()
