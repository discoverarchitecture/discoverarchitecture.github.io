# Paused scheduled runs

**The owner paused every scheduled run on 28 Oct 2026** to save compute while focusing on FGA Studio. Nothing in
Discover Architecture or FGA Studio runs on a timer now. The owner will restart work by chatting.

**Any chat asked about scheduled runs** ("what was scheduled?", "what did we pause?"): list the items below in plain
words (name, what it did, how often) and ask the owner which ones to resume. Resume only what the owner names.

## Claude routines (paused with `update_trigger` enabled=false; resume with enabled=true)

| Routine | id | What it did | When |
|---|---|---|---|
| Waitlist concierge (FGA Studio) | `trig_01M7EVvpPhMk1KCSTfd7apdh` | Drafted personal emails to new waitlist sign-ups, replies and one follow-up, in Gmail drafts (never sent) | Daily 08:42 IST |
| Strategy daily check (FGA Studio) | `trig_013ZamEU85rMNacM3baYrfap` | Read the FGA Studio chats, updated the "Strategy foundation" doc, briefed the concierge, reported the day's key decision | Daily 07:52 IST |
| Refresh Visitors dashboard | `trig_01BYgoCdX7sjupG413KDdt9Y` | Uploaded fresh GoatCounter numbers to the Visitors dashboard | Every 6 hours |
| Daily dashboard refresh | `trig_01Uhc9eZ5w3GuYBzRZi3Pwjc` | Refreshed the project progress dashboard from `main` | Daily 17:51 UTC |
| Affiliate links reminder | `trig_014tvSjnFb1zNc8LdMW4TgUf` | Checked weekly whether visits passed 10,000 in 30 days, to remind about book affiliate links | Mondays 06:23 UTC |
| Indexing decision (SEO, one-off) | `trig_01Hub6ZMKD7zaEsfDqFr6JkQ` | Report on Google indexing and whether to hide weak building pages | Was due 30 Oct 2026; give a new date when resuming |
| Click-rate check after new titles (SEO, one-off) | `trig_01U7a4EJdkbzD73mo2cXgnKe` | Compare Google click rates before and after the 20 Oct title change | Was due 4 Nov 2026; give a new date when resuming |

Already off before 28 Oct (finished work, listed for completeness): photo rescue (`trig_01A3kuX8uEKqgUgGcKAnMfvH`),
the two books curators (`trig_01JVzyrFJj73aVUxNAPRSwSP`, `trig_01QFDy6bSHi4u4U3YHgnoGgJ`) and "Keep adding buildings"
(`trig_0183WD5np919qQHVtz5ya53A`).

Not part of this project and left running: "PlaceCom Morning Digest" (the owner's XLRI placement email digest).

## GitHub Actions timers (paused by commenting out `schedule:`; resume by uncommenting it)

| Workflow | What it did | When |
|---|---|---|
| `.github/workflows/analytics.yml` (Fetch analytics) | Saved GoatCounter visitor numbers on the `analytics-data` branch | Every 6 hours |
| `.github/workflows/search-console.yml` (Fetch Search Console) | Saved Google searches, clicks and indexing verdicts on `analytics-data` | Daily 04:37 UTC |

No data is lost while these are off: GoatCounter keeps every visit and Search Console keeps 16 months, so the first
run after resuming catches up (Search Console's indexing checks restart where they stopped). Both can still be run by
hand from the Actions tab ("Run workflow").

Still automatic, because they only run when someone changes something (no timer): the site deploy on a push to
`main`, and the link and guide checkers on their own branches.
