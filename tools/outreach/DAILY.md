# Library outreach, every weekday (owner, 15 Nov 2026)

The owner asked for library outreach to run on its own: new emails every weekday, a thank-you or a gentle reminder a
week after a librarian says yes, and one follow-up two weeks after each email that gets no answer. The SEO strategy chat
runs this from a routine; no permission is needed for ordinary emails and replies. **Important mails go to the owner
first**: a complaint, anyone asking not to be contacted (stop everything at once), a question about money, partnership
or the paid tool, or anything you are unsure of.

Everything here works from three files on the branch `claude/outreach-daily`: `sent.md` (the log, one row per school,
never an email address), `queue.json` (guides not yet emailed) and this runbook. Email addresses only ever live in
Gmail and in the run's own scratch folder; the repository is public.

## Each run, in this order

### 1. Read the inbox (every run)

Search Gmail for anything since the last run that answers an outreach email (replies, auto-replies, bounces). Handle
each one as `REPLIES.md` says and write the outcome in the Reply column of `sent.md`, with the date:
- **Yes** ("I'll add it", "added"): reply with the short thank-you from `REPLIES.md`; note `yes <date>`.
- **Question or suggestion:** answer it as `REPLIES.md` says, or tell the owner if it needs their decision.
- **No / only licensed resources:** short thanks; note `no <date>`; never write again.
- **Out of office with a return date:** note `away until <date>`; the follow-up waits until after it.
- **Bounce or "has left":** note it; if another named librarian is given, the follow-up may go there instead.
- **Complaint or "don't contact me":** reply only "Sorry for the trouble, I won't write again.", stop all sending,
  and tell the owner in the chat.

### 2. A week after a yes: thank-you or gentle reminder (once per school)

For every `yes` that is at least 7 days old and has no `checked` note yet:
1. Check the guide: put those schools (with their guide `url`) in `tools/outreach/candidates_daily.json` on this branch
   and push. `outreach-check.yml` opens each guide on GitHub and writes `daily.json` with `links_to_us` (true or false)
   within a few minutes. Also look at GoatCounter referrers (`latest.json` on `analytics-data`) for the school's domain.
2. **Listed:** a short thank-you in the same thread ("I saw Find Great Architecture on your guide this week, thank you!
   If your students ever spot something wrong or missing, I'd be glad to fix it."). Note `listed <date>, thanked`.
3. **Not listed yet:** one gentle reminder in the same thread ("Just checking in, in case it got buried: happy to send
   a one-line description for the guide if that helps."). Note `reminded <date>`. Never a second reminder; after it,
   the school is done unless they write again.
A guide can be updated without us seeing the link at once (caching, a page not yet republished): when in doubt, thank
rather than remind.

### 3. Two weeks after an unanswered email: one follow-up (once per school)

For every row sent at least 14 days ago with an empty Reply (or `none`), no follow-up yet, and no `away until` date
still in the future: one short note in the same thread, then note `followed up <date>`. Never a third email.

> Hi [name], just a short follow-up in case my note below got buried. If Find Great Architecture fits your guide I'd be
> grateful for a mention; if not, no worries at all. Best wishes, Akshat

At most 15 follow-ups in one run; the rest wait for the next.

### 4. New emails: five every weekday

Take the next five schools from `queue.json` that are not in `sent.md`. Their contact details come from
`outreach-contacts.yml`, which reads each guide on GitHub and encrypts the answers to **this run's own key**:

```
cd <scratch folder for this run>
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out key.pem
openssl pkey -in key.pem -pubout -out pub.pem
```

Copy `pub.pem` (only the public half) to `tools/outreach/pub.pem` on this branch, write
`--list queue.json <i> <i> ...` (positions in `queue.json`) into `tools/outreach/contacts_request.txt`, commit and push.
When the workflow has committed `tools/outreach/sealed/k.b64` and `c.b64` (a few minutes), pull and open them:

```
base64 -d tools/outreach/sealed/k.b64 | openssl pkeyutl -decrypt -inkey key.pem -out k.txt
base64 -d tools/outreach/sealed/c.b64 | openssl enc -d -aes-256-cbc -pbkdf2 -pass file:k.txt -out contacts.json
```

Keep `key.pem`, `k.txt` and `contacts.json` in the scratch folder only, and delete them at the end of the run. Never put
an address in the repository, a commit message, a pull request or the chat.

For each school with a named librarian or a guide-specific address, send the email below from Gmail (HTML, links behind
words, never a raw address). A school with only a general library address gets it too, but address it to "Hello" and
name the guide. A school with no address at all: note `no contact` in `sent.md` and move on. Add one row per email to
`sent.md`: next number, school, guide section named, today's date in Drafted and Sent, empty Reply.

**Subject:** A free resource for your [guide name] guide

> Hello [name, or nothing],
>
> I'm Akshat. I trained as an architect at CEPT University in Ahmedabad and am now doing an MBA. As a student I found
> that discovering great architecture was harder than it should be, so I built [Find Great Architecture]: a free site
> where architecture students browse buildings instead of searching for them.
>
> I came across [the guide name, and the section if it has one], and thought this might be a useful free addition for
> students working on precedents:
>
> - Photos of each building that students can reuse in coursework, all public domain or Creative Commons, each credited
>   with a link to its source
> - Architect, year, place and key features, with links to plans and drawings where they exist
> - Pages by style, type, city and architect ([Brutalism], for example)
>
> No ads, no sign-up, no paywall. If it fits the guide, I'd be grateful for a mention, and if you see anything that would
> make it more useful to your students, I'd really like to hear it.
>
> Thanks for your time,
> Akshat
> findgreatarchitecture.com

Links: "Find Great Architecture" → `https://findgreatarchitecture.com/?ref=libguide`; "Brutalism" →
`https://findgreatarchitecture.com/styles/brutalism/?ref=libguide`; the sign-off links the home page the same way.
Before sending, make sure every promise is still true (no ads, no sign-up, no paywall on the wall).

### 5. When the queue runs low (fewer than 15 left)

Find more architecture library guides the same way round 2 did (`BRIEF.md`): a web search for architecture or
architectural history LibGuides and research guides with a section of free websites or image resources, **Western
countries first** (US, UK, Canada, Australia, Ireland, New Zealand, then Europe), never schools already in `sent.md`.
Put them in `candidates_daily.json` and push; `outreach-check.yml` writes `daily.json`. Append the ones with
`about_architecture: true` and `links_to_us: false` to `queue.json`. About 40 at a time.

### 6. Log and report

Commit `sent.md` and `queue.json` to `claude/outreach-daily` and push. In the chat, write a short note only when
something happened that the owner would want to know: a new yes, a listing seen, a question that needs them, or a
problem. Otherwise one line: "Outreach: N sent, N follow-ups, no new replies."

## Limits

- Weekdays only. At most 5 new emails and 15 follow-ups or reminders per run, so the account isn't flagged.
- One follow-up per school, one reminder per yes. Never a third email to anyone.
- Stop everything and tell the owner at the first complaint or request not to be contacted.
