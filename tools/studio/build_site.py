#!/usr/bin/env python3
"""Writes the FGA Studio waitlist page for the real site, site/studio/index.html, from the prototype (gen.py).

Adds what the prototype leaves out: the site's own photo paths, search and share tags, GoatCounter, and the waitlist
sending. Sign-ups go to the owner's Google Sheet through its Apps Script web app (the /exec link in waitlist_url.txt,
set up as in WAITLIST_SETUP.md) and are counted as the GoatCounter event studio/signup (no email in it), which the
analytics job adds to the daily numbers. Without the link it refuses to write the page, so no sign-up can be lost;
--draft writes it anyway, for screenshots only.

    python3 tools/studio/salk2.py && python3 tools/studio/build_site.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, '..', '..', 'site')
sys.path.insert(0, HERE)
import gen  # noqa: E402  (builds the prototype too)

BASE = 'https://findgreatarchitecture.com/'
URL = BASE + 'studio/'
TITLE = 'AI architecture presentation board generator · FGA Studio'
# Words students search in the US, UK and Europe: "architecture presentation board" (SEO strategy chat, 21 Oct 2026).
DESC = ('Turn your plans, sections and renders into an A1 architecture presentation board and an editable PowerPoint '
        'for your jury or crit. Join the waitlist.')


def main():
    draft = '--draft' in sys.argv
    url = open(os.path.join(HERE, 'waitlist_url.txt')).read().strip() if os.path.exists(os.path.join(HERE, 'waitlist_url.txt')) else ''
    if not url.startswith('https://script.google.com/') and not draft:
        raise SystemExit('No Google Apps Script link in tools/studio/waitlist_url.txt yet (see WAITLIST_SETUP.md). '
                         'Not writing the page, so no sign-up is lost. Use --draft for screenshots.')
    assert len(TITLE) <= 60 and len(DESC) <= 155, (len(TITLE), len(DESC))
    html = gen.page('A')
    html = html.replace('src="images/salk/', 'src="../images/salk-institute/')
    ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': TITLE, 'description': DESC, 'url': URL,
          'isPartOf': {'@type': 'WebSite', 'name': 'Find Great Architecture', 'url': BASE},
          'about': {'@type': 'SoftwareApplication', 'name': 'FGA Studio', 'applicationCategory': 'DesignApplication', 'operatingSystem': 'Web',
                    'description': 'An AI tool that turns architecture students’ drawings into an editable architecture presentation board and slide deck.'}}
    head = (f'<title>{TITLE}</title>\n<meta name="description" content="{DESC}">\n<link rel="canonical" href="{URL}">\n'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="Find Great Architecture">'
            f'<meta property="og:title" content="{TITLE}"><meta property="og:description" content="{DESC}"><meta property="og:url" content="{URL}">'
            f'<meta property="og:image" content="{URL}og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#FFF6EA">\n'
            '<link rel="icon" href="../favicon.ico" sizes="any"><link rel="icon" href="../favicon-96.png" type="image/png" sizes="96x96">\n'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n<script src="../analytics.js"></script>')
    start = html.index('<title>'); end = html.index('<link rel="preconnect"')
    html = html[:start] + head + '\n' + html[end:]
    html = html.replace('<span class="by">by Find Great Architecture</span></a>', '</a><a class="by" href="../">by Find Great Architecture</a>', 1)
    send = '''<script>
// Waitlist: each form is sent to the owner's Google Sheet (Apps Script web app) and counted as studio/signup.
(function () {
  var URL_ = %s;
  function send(form, stage) {
    var d = new URLSearchParams(new FormData(form)); d.set('stage', stage); d.set('page', location.pathname);
    try { fetch(URL_, { method: 'POST', mode: 'no-cors', body: d, keepalive: true }); } catch (e) { /* offline */ }
    if (stage === 'signup' && window.fgaEvent) fgaEvent('studio/signup', 'FGA Studio waitlist sign-up');
  }
  var qf = document.getElementById('qf'), wl = document.getElementById('join');
  qf.addEventListener('submit', function () { send(qf, 'signup'); });
  qf.querySelector('.qf-more .cta').addEventListener('click', function () { send(qf, 'details'); if (window.fgaEvent) fgaEvent('studio/details', 'FGA Studio waitlist: optional answers'); });
  wl.addEventListener('submit', function () { send(wl, 'signup'); });
})();
</script>
''' % json.dumps(url)
    html = html.replace('</body></html>', send + '</body></html>')
    os.makedirs(os.path.join(SITE, 'studio'), exist_ok=True)
    open(os.path.join(SITE, 'studio', 'index.html'), 'w').write(html)
    print('wrote site/studio/index.html' + (' (DRAFT: no waitlist link)' if not url else ''))


if __name__ == '__main__':
    main()
