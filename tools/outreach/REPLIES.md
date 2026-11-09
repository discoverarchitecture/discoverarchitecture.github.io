# Answering librarians

SEO strategy chat, 6 Nov 2026. Replies go in the same thread, as HTML with links behind words (never raw addresses),
signed "Akshat" and the short "findgreatarchitecture.com". Short, warm, and only promise what a chat can do. The
reply to anyone who has said yes or made a suggestion is **drafted for the owner to send**, not sent automatically.
Log every reply in `sent.md` (the Reply column) without addresses.

## They said yes

> Hi [name],
>
> Thank you, that's lovely to hear. If you ever spot something wrong or missing for your students, I'd be glad to
> fix it.
>
> Thanks again,
> Akshat

## They said yes and suggested something

Fix it first if it can be fixed the same day, then say so with a link to the result. If it needs new buildings, name
the ones you'll add (check the wall first) and say "over the coming weeks, wherever free photos exist". First case:
Liv Valmestad, Manitoba, 6 Nov 2026 (search for "Canada", more Winnipeg buildings; `winnipeg.md`).

## They asked a question

Answer it in two or three sentences. Common ones:
- **Who runs it?** "Just me: I trained as an architect at CEPT and built it on my own. It has no ads and no sign-up."
- **Can students reuse the photos?** "Yes, every photo is public domain or Creative Commons, and each shows its
  credit, licence and a link to its source on Wikimedia Commons, so they can cite it as the source asks."
- **Where do the facts come from?** "Wikidata, Wikipedia and the linked sources on each page; I only show height,
  materials and similar details when a source gives them."
- **Is it commercial?** "The site is free and stays free. Separately I'm building a paid tool for presentation boards,
  but the precedent site has no paywall." (Say this only if they ask.)

## They said no, or that the guide only lists library-licensed resources

> Hi [name], thank you for letting me know, and for taking the time to look. Best wishes, Akshat

Mark the school "no" in `sent.md` and never write again.

## Out of office

No reply. If it names a return date, the follow-up waits until after it. If it gives another address, write there only
if the original was a personal address that will be away for weeks.

## Asked not to be contacted, or a complaint

Stop all sending at once and tell the owner. Reply only "Sorry for the trouble, I won't write again."

## Checking a listing (owner's question, 9 Nov 2026)

When a librarian says they will add the site, we check it ourselves; we never ask twice in a way that sounds like
chasing.

1. **The guide page itself.** `tools/check_outreach.py` already reads each guide and records `links_to_us` (does the
   page link to findgreatarchitecture.com). About two weeks after a "yes", put just those schools in a candidates file on
   an `claude/outreach-*` branch and push: `outreach-check.yml` runs on GitHub (no Claude time) and the result shows
   true or false. Mark the school in `sent.md` ("listed, seen <date>").
2. **Visits.** A live link sends students. GoatCounter's referrers (`latest.json` on `analytics-data`, and the Visitors
   dashboard) show visits from `libguides.*`, `guides.*`, `*.edu`, `*.ac.uk` addresses: proof the link is up and used.
3. **Google.** Search Console → Links → "Top linking sites" lists the university domains once Google has seen the link
   (takes a few weeks).
4. **If it isn't there after about three weeks:** one short, friendly note in the same thread ("just checking you have
   what you need; happy to send a line of description for the guide"), never a second.
