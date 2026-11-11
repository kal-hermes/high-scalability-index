#!/usr/bin/env python3
"""Inject a functional test driver into a copy of the site page and read results."""
import pathlib
import shutil

SITE = pathlib.Path("/workspace/projects/highscalability-catalogue/site")
FX = pathlib.Path("/workspace/projects/highscalability-catalogue/.impeccable/build/fixture")
if FX.exists():
    shutil.rmtree(FX)
shutil.copytree(SITE, FX)

driver = """
<script>
window.addEventListener('load', function () {
  setTimeout(function () {
    const R = {};
    const results = document.getElementById('results');
    R.initialRows = results.children.length;
    R.initialTitle = document.getElementById('section-title').textContent;
    R.initialMeta = document.getElementById('results-meta').textContent;
    R.initialNo = document.querySelector('.row-no') && document.querySelector('.row-no').textContent;
    // expand first row
    const toggle = document.querySelector('.row-toggle');
    toggle.click();
    R.excerptVisible = toggle.getAttribute('aria-expanded') === 'true' &&
      document.querySelector('li.expanded .row-excerpt').getBoundingClientRect().height > 10;
    // switch topic via hash
    location.hash = '#/topic/war-stories';
    setTimeout(function () {
      R.warTitle = document.getElementById('section-title').textContent;
      R.warFirst = results.children[0] && results.children[0].querySelector('.row-title').textContent;
      R.warRailOn = document.querySelector('#rail-list li.on a span').textContent;
      // search
      location.hash = '#/search/kafka';
      setTimeout(function () {
        R.searchMeta = document.getElementById('results-meta').textContent;
        R.searchTitle = document.getElementById('section-title').textContent;
        // empty search
        location.hash = '#/search/zzzqqqxxx';
        setTimeout(function () {
          R.emptyShown = !document.getElementById('empty').hidden;
          // back to topic, paginate
          location.hash = '#/topic/scalability-architecture-patterns';
          setTimeout(function () {
            const next = document.getElementById('next');
            R.pages = document.getElementById('page-info').textContent;
            next.click();
            R.pageAfterNext = document.getElementById('page-info').textContent;
            R.firstRowPage2 = results.children[0] && results.children[0].querySelector('.row-no').textContent;
            // year filter
            const year = document.getElementById('year');
            year.value = '2024';
            year.dispatchEvent(new Event('change', {bubbles: true}));
            R.metaAfterYear = document.getElementById('results-meta').textContent;
            R.prefersReduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
            document.getElementById('test-results').textContent = JSON.stringify(R);
            document.title = 'TESTS-DONE';
          }, 120);
        }, 120);
      }, 120);
    }, 120);
  }, 400);
});
</script>
"""

html = (FX / "index.html").read_text()
html = html.replace("</body>", "<pre id=\"test-results\" style=\"display:none\"></pre>" + driver + "</body>")
(FX / "index.html").write_text(html)
print("fixture ready:", FX)
