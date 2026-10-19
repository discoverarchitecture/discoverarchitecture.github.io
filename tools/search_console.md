# Getting the site into Google and Bing

Both services are free. Each needs you to sign in and prove you own the site once. Claude can't sign in to them, so
Google's numbers reach Claude only through the daily copy described in "Search Console data for Claude" below.

## Google Search Console (10 minutes, once)

1. Go to https://search.google.com/search-console and sign in with a Google account you'll keep.
2. Choose **URL prefix** (not Domain) and enter exactly:
   `https://findgreatarchitecture.com/`
3. Under verification methods pick **HTML tag**. Google shows a line like
   `<meta name="google-site-verification" content="abc123…">`.
   Paste that whole line into a chat with Claude: it goes into `site/index.html` just below `<meta name="viewport">`,
   and the change is deployed by merging to `main`. Then press **Verify** in Search Console.
4. In the left menu open **Sitemaps**, enter `sitemap.xml`, and press **Submit**. The sitemap already lists every
   building page (`site/sitemap.xml`, rebuilt by `tools/build_pages.py`).
5. Come back after two weeks. **Performance** shows which queries bring impressions and clicks, per page.
   **Pages** shows what is indexed and why anything was left out.

Optional, in the same place: **URL inspection → Request indexing** for the home page and ten of the most
looked-up buildings (the list is at the bottom of the home page) to get the first crawl started sooner.

## Bing Webmaster Tools (2 minutes, after Google)

1. Go to https://www.bing.com/webmasters and sign in (Microsoft or Google account).
2. Choose **Import from Google Search Console**. It copies the verified site and the sitemap; no code to add.
   Bing's index also feeds DuckDuckGo and Yahoo.

## Search Console data for Claude (15 minutes, once)

A GitHub Action (`.github/workflows/search-console.yml`, running `tools/fetch_search_console.py`) copies Search
Console's numbers every day at 04:37 UTC to the `analytics-data` branch, folder `search_console/`, next to the visitor
numbers. It needs a read-only "robot" Google account (a service account) that you add to Search Console.

1. Go to https://console.cloud.google.com and sign in with the same Google account as Search Console. At the top,
   choose **Select a project → New project**, name it `find-great-architecture`, and create it.
2. In the search bar type **Google Search Console API**, open it and press **Enable**.
3. In the search bar type **Service accounts** and open it. Press **Create service account**, name it
   `search-console-reader`, then **Done** (skip the optional roles). Copy its email address; it ends in
   `iam.gserviceaccount.com`.
4. Open the new service account, go to the **Keys** tab, **Add key → Create new key → JSON**. A small file downloads.
   It is a password: never email it or put it in a chat.
5. In Search Console, **Settings → Users and permissions → Add user**. Paste the email from step 3 and choose
   **Restricted** (it can only read).
6. In GitHub, the repository's **Settings → Secrets and variables → Actions → New repository secret**. Name:
   `GSC_SERVICE_ACCOUNT`. Value: open the downloaded file in a text editor and paste all of it. Save, then delete the file.
7. **Actions** tab → **Fetch Search Console** → **Run workflow**. A green tick within a few minutes means it works;
   tell Claude, and every chat can then read the numbers.

What it saves, in `search_console/` on the `analytics-data` branch:

- `daily.csv`: day, clicks, impressions (times a page was shown in results), ctr (clicks ÷ impressions) and
  position (average rank; 1 is the top) for Google web search.
- `latest.json`: the last 28 days, web and image search separately: top queries, pages, countries, devices, and
  which query brought people to which page.
- `indexing.json`: Google's verdict on each page in the sitemap (indexed or not, and why), 300 pages a day, so all of
  them are checked in under two weeks and then re-checked. Its `summary` counts pages per verdict.

If the run fails: "refused the service account key" means the secret isn't the whole JSON file; "sees no Search
Console property" means step 5 is missing; "has not been used in project … or it is disabled" means step 2. Google's
numbers run two or three days behind, so the newest days start small and fill in.

## What to watch

- Impressions for queries that contain a building's name plus *plan*, *section*, *case study* or the architect.
- Which of the "About" pages (the 100 most looked-up buildings and the South Asian ones) earn clicks.
- Buildings appearing for their own name without the architect's (for example Barbican, Salk Institute, Sangath), and which countries the clicks come from: the audience is worldwide, Western countries first.

## Checks to repeat now and then

- Repository **Settings → Pages**: "Enforce HTTPS" ticked, custom domain `findgreatarchitecture.com` shown as verified.
- Search Console **Sitemaps**: `sitemap.xml` listed with status Success; Bing Webmaster **Sitemaps** the same.
- Search Console **Pages**: look at "Not indexed" reasons ("Crawled – currently not indexed" means pages look too alike).
- The sitemap lists the home page, `/play/` (the game), the A–Z index and every building page. The `/yt/` redirect pages are left out on purpose.
