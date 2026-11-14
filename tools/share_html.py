"""The Share button and the footer's social row, as HTML, for every generator (owner, 13 Nov 2026).

  SHARE_BTN                 the button for the top right of a page's header (site/share.js wires it, site/share.css styles it)
  SOCIAL                    the footer's row: Instagram and YouTube, a plain glyph and a label each
  assets(up, v)             the <link> and <script> a page's <head> needs (up: path to the site root, v: ?v= stamp)
  newtab(html)              Studio FGA's landing page opens in a new tab from the wall (owner, 13 Nov 2026)

Used by tools/build_pages.py (and, through it, architect, hub, film and guide pages), tools/build_guides.py and
tools/build_studio.py. The glyphs are drawn here, plain and generic (a rounded square with a circle, a rounded box with a
triangle); they are not anyone's logo. The same two addresses are in site/share.js (the popover's "Follow us").
"""
import re

IG = 'https://www.instagram.com/findgreatarchitecture/'
YT = 'https://www.youtube.com/@findgreatarchitecture'
_ICON_SHARE = '<circle cx="18" cy="5.5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="18.5" r="2.5"/><path d="m8.2 10.8 7.6-4M8.2 13.2l7.6 4"/>'
_ICON_IG = '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.2 6.8v.1"/>'
_ICON_YT = '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="m10 9.2 5 2.8-5 2.8z"/>'

SHARE_BTN = ('<button type="button" class="fga-share" aria-haspopup="dialog" aria-expanded="false" aria-label="Share this page">'
             f'<svg viewBox="0 0 24 24" aria-hidden="true">{_ICON_SHARE}</svg><span class="fga-share-t">Share</span></button>')
SOCIAL = ('<p class="fga-social" data-nosnippet>'
          f'<a href="{IG}" target="_blank" rel="noopener" data-social="instagram"><svg viewBox="0 0 24 24" aria-hidden="true">{_ICON_IG}</svg>Instagram</a>'
          f'<a href="{YT}" target="_blank" rel="noopener" data-social="youtube"><svg viewBox="0 0 24 24" aria-hidden="true">{_ICON_YT}</svg>YouTube</a></p>')


def assets(up, v='0'):
    return (f'<link rel="stylesheet" href="{up}share.css?v={v}">\n<script src="{up}share.js?v={v}" defer></script>')


def newtab(html):
    """Add target=_blank and rel=noopener to every link that opens Studio FGA itself (/studio/ with or without ?query),
    not to its guides or legal pages. Links already marked are left alone."""
    def tag(m):
        a = m.group(0)
        if 'target=' in a or not re.search(r'href="(?:\.\./|\./|/)*(?:[a-z.]*/)*?studio/(?:\?[^"]*)?"', a) or re.search(r'href="[^"]*studio/(?:guides|terms|privacy|refund)', a):
            return a
        return a[:-1] + ' target="_blank" rel="noopener">'
    return re.sub(r'<a\b[^>]*>', tag, html)
