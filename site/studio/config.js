/* Studio FGA: where the Studio API lives. The only setting the page has.

   After the owner deploys the backend (studio/server/README.md, "Deploy"), Modal prints the web address, like
   https://<workspace>--studio-fga-web.modal.run . Put that address here (no slash at the end), commit, and the
   page starts using it. Until then the page still works: "Start free" opens the demo with the sample project
   (?demo=1), which never calls the API. */
window.STUDIO_API = "https://akshatpagariya909--studio-fga-web.us-east.modal.run";

/* Prices in the visitor's own currency (owner, 5 Nov 2026): the page shows "about ₹950" beside $11. US dollars per
   unit, rough mid-market rates as of 5 Nov 2026; the page rounds the result, and Dodo charges the exact amount in the
   visitor's currency at checkout. Refresh these a few times a year. A currency missing here shows nothing extra. */
window.STUDIO_FX = { asOf: "2026-11-05", perUSD: {
  INR: 88, EUR: 0.86, GBP: 0.76, CHF: 0.80, SEK: 9.5, NOK: 10.1, DKK: 6.4, PLN: 3.65, CZK: 21, HUF: 335, RON: 4.35, TRY: 42,
  AUD: 1.53, NZD: 1.74, CAD: 1.40, MXN: 18.4, BRL: 5.4, COP: 3900, CLP: 950, ARS: 1450, PEN: 3.4,
  SGD: 1.30, MYR: 4.2, IDR: 16600, THB: 33, PHP: 58, VND: 26300, CNY: 7.1, HKD: 7.78, TWD: 30.5, JPY: 152, KRW: 1420,
  AED: 3.67, SAR: 3.75, QAR: 3.64, KWD: 0.307, BHD: 0.376, OMR: 0.385, JOD: 0.709, EGP: 48, MAD: 9.2,
  PKR: 282, BDT: 122, NPR: 141, LKR: 300, NGN: 1500, KES: 129, ZAR: 17.5
} };
