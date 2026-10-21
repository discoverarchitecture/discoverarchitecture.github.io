// FGA Studio waitlist: receives sign-ups from findgreatarchitecture.com/studio/ and keeps them in this Google Sheet.
// Paste into Extensions → Apps Script of the sheet, then Deploy → New deployment → Web app (see WAITLIST_SETUP.md).
// One row per email: a second message from the same email (the two optional questions) fills in that row.
const SHEET = 'Waitlist';
const HEAD = ['Signed up (UTC)', 'Email', 'I am a', 'Presenting next', 'Next jury', 'From (ref)', 'Building (b)', 'Page', 'Last update (UTC)'];

function doPost(e) {
  const p = (e && e.parameter) || {};
  const email = String(p.email || '').trim().toLowerCase();
  if (email.length > 200 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return reply('not an email');
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const book = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = book.getSheetByName(SHEET) || book.insertSheet(SHEET);
    if (sheet.getLastRow() === 0) { sheet.appendRow(HEAD); sheet.setFrozenRows(1); }
    // plain text only: a value starting with = + - or @ could be read as a formula, so it gets a leading '
    const clean = v => String(v || '').slice(0, 300).replace(/^[=+\-@]/, "'$&");
    const now = new Date();
    const n = sheet.getLastRow() - 1;
    const emails = n > 0 ? sheet.getRange(2, 2, n, 1).getValues().map(r => String(r[0])) : [];
    const at = emails.lastIndexOf(email);
    if (at >= 0) {
      const row = at + 2;
      [[3, p.role], [4, p.next], [5, p.when]].forEach(([col, v]) => { if (v) sheet.getRange(row, col).setValue(clean(v)); });
      sheet.getRange(row, 9).setValue(now);
    } else {
      sheet.appendRow([now, email, clean(p.role), clean(p.next), clean(p.when), clean(p.ref), clean(p.b), clean(p.page), now]);
    }
  } finally {
    lock.releaseLock();
  }
  return reply('ok');
}

function doGet() { return reply('FGA Studio waitlist: send sign-ups with POST.'); }
function reply(text) { return ContentService.createTextOutput(text); }
