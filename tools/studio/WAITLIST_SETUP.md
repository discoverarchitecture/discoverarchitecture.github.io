# FGA Studio waitlist: where the emails go

Sign-ups on findgreatarchitecture.com/studio/ go into a private Google Sheet in the owner's Google account, through a
small Apps Script web app (`waitlist_apps_script.gs`). Each sign-up is also counted in GoatCounter as the event
`studio/signup` (a number only, no email), which the analytics job adds to `signups.csv` and the Visitors dashboard.

## Set it up once (about 3 minutes, owner)

1. Open https://sheets.new (signed in to your Google account) and name the sheet **FGA Studio waitlist**.
2. Menu **Extensions → Apps Script**. Delete what is there, paste everything from `tools/studio/waitlist_apps_script.gs`,
   and click **Save** (the disk icon).
3. Click **Deploy → New deployment**. Next to "Select type", click the gear and choose **Web app**.
   - Description: `waitlist`
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Click **Deploy**, then **Authorize access** and choose your account. Google warns that the app isn't verified (it is
   your own script): click **Advanced → Go to … (unsafe)** → **Allow**.
5. Copy the **Web app URL** (it starts with `https://script.google.com/macros/s/` and ends with `/exec`) and send it to
   Claude. It goes into `tools/studio/waitlist_url.txt`, and `build_site.py` writes it into the page.

Sign-ups then appear as rows in the sheet's **Waitlist** tab: date, email, role, what they're presenting next, when the
jury is, where they came from (`ref`), the building they came from (`b`) and the page.

## If you change the script later

Use **Deploy → Manage deployments → Edit (pencil) → Version: New version → Deploy**. That keeps the same URL. A *new*
deployment makes a new URL, which would then have to go into `waitlist_url.txt` again.
