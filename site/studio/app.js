/* Studio FGA: the student's journey, screen by screen (findgreatarchitecture.com/studio).
   upload -> questions (student or professional path) -> title block -> concept (optional, own words) -> free preview
   -> price -> Dodo checkout -> making -> result -> editor -> files -> rate.
   Every step talks to the Studio API (api.js; its address is in config.js). ?demo=1 runs the same screens offline
   on the sample project, as the approved prototype did, so the page works before the backend is live. */
(function () {
  'use strict';
  const F = window.FGA, X = window.FGAExport, SAMPLE = window.SAMPLE, API = window.StudioAPI, LAY = window.FGALayout;
  const app = document.getElementById('app');
  const DEMO = new URLSearchParams(location.search).get('demo') === '1';
  const KS = DEMO ? 'studio-fga-demo-flow-v1' : 'studio-fga-flow-v1', KP = 'studio-fga-demo-project-v1';
  const VERSION = 3, SV = 5;
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* storage off */ } }
  };
  const esc = F.esc;

  /* ---------------------------------------------------------- state */
  function freshP() {
    const P = F.clone(SAMPLE);
    Object.assign(P, { v: VERSION, ts: 'A', base: 'sample/', slug: 'law-garden', slideOrder: P.slides.map((s) => s.n), slideOff: [] });
    return F.prepare(P);
  }
  function freshS() { return { v: SV, screen: 'home', q: 1, ans: {}, oth: {}, card: {}, tier: null, email: '', fromHeard: false, extra: [], job: null, files: [] }; }
  /* HP: the sample project, always (the landing page's before and after). P: the project in the editor (the demo: the
     sample; live: the paid build, read from its layout.json). PV: the free preview's sketch (live only). ST: the last
     job status from the API. */
  const HP = freshP();
  let P = null, restored = false, PV = null, ST = null, ORIG = null;
  if (DEMO) { P = store.get(KP); restored = true; if (!P || P.v !== VERSION || P.built !== SAMPLE.built) { P = freshP(); restored = false; } ORIG = freshP(); }
  let S = store.get(KS); if (!S || S.v !== SV) S = freshS();
  const editKey = () => DEMO ? KP : 'studio-fga-edit-' + (S.job ? S.job.id : 'none');
  const Q = () => DEMO ? P : PV;   // the model the preview and price screens show
  const libOf = (M) => { const seen = {}, out = []; if (!M) return out; const add = (pg) => Object.values(pg.contents).forEach((c) => { if (!seen[c.src]) { seen[c.src] = 1; out.push(c); } });
    add(M.board); M.slides.forEach(add); return out; };
  let LIB = libOf(ORIG);
  /* a picture's address outside the sheets: sample paths in the demo, full or blob: addresses live */
  const pic = (M, s) => /^(blob:|data:|https?:)/.test(s || '') ? s : F.srcOf(M || HP, s);
  const paid = () => !DEMO && !!(ST && ST.paid);

  let hist = [JSON.stringify(P)], hi = 0, lastSoft = false, saveT = null;
  function resetHist() { hist = [JSON.stringify(P)]; hi = 0; lastSoft = false; }
  function setP(np, label, soft) {
    P = np;
    const snap = JSON.stringify(P);
    if (snap === hist[hi]) return;
    if (lastSoft) hist[hi] = snap;
    else { hist = hist.slice(0, hi + 1); hist.push(snap); if (hist.length > 150) hist.shift(); hi = hist.length - 1; }
    lastSoft = !!soft;
    scheduleSave();
    bar();
  }
  function scheduleSave() {
    clearTimeout(saveT);
    const el = document.getElementById('saved');
    if (el) el.textContent = 'Saving…';
    saveT = setTimeout(() => {
      const ok = store.set(editKey(), P);
      const e2 = document.getElementById('saved');
      if (e2) e2.textContent = ok ? 'Saved on this device' : 'Not saved: browser storage is off';
    }, 400);
  }
  const saveS = () => store.set(KS, S);

  /* ---------------------------------------------------------- the 10 questions (prompts/INTAKE_QUESTIONS.md) */
  const ICO = {
    'Jury pin-up': '<rect x="4" y="6" width="16" height="13" rx="1"/><path d="M12 2v5M10 3h4M7 10h6M7 13h10M7 16h8"/>',
    'Design review': '<path d="M15 4l5 5L9 20H4v-5z"/><path d="M13 6l5 5"/>',
    'Portfolio': '<path d="M3 7h6l2 2h10v10H3z"/>',
    'Competition entry': '<path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8 20h8"/>',
    'Instagram / showcase': '<rect x="4" y="4" width="16" height="16" rx="5"/><circle cx="12" cy="12" r="3.5"/><circle cx="16.8" cy="7.2" r=".6"/>',
    '“Beautiful”': '<path d="M12 3l2.2 5.3L20 9l-4.4 3.8L17 19l-5-3-5 3 1.4-6.2L4 9l5.8-.7z"/>',
    '“Clever”': '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z"/>',
    '“Brave”': '<path d="M12 3c1 4 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3.5 2-4.5 0 2 1 3 2 3 0-3-1-5.5 1-8.5z"/>',
    '“Thoughtful”': '<path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19l7-7"/>',
    'My studio tutor': '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c1-4 4-6 7-6s6 2 7 6"/>',
    'External jury': '<circle cx="12" cy="8" r="3"/><circle cx="5.5" cy="10" r="2.3"/><circle cx="18.5" cy="10" r="2.3"/><path d="M7 19c.7-3 2.7-4.5 5-4.5s4.3 1.5 5 4.5M2 18c.4-2 1.6-3 3.5-3M22 18c-.4-2-1.6-3-3.5-3"/>',
    'A firm / recruiter': '<rect x="3" y="8" width="18" height="12" rx="1.5"/><path d="M9 8V5h6v3M3 13h18"/>',
    'Classmates & Instagram': '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    '“Concept isn’t clear”': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 .9-1 1.7M12 17h.01"/>',
    '“Too much, no story”': '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5M3 17.5l9 5 9-5"/>',
    '“Presentation is weak”': '<path d="M3 6l6 6 4-4 8 8"/><path d="M15 16h6v-6"/>',
    '“Good, just polish it”': '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.8 2.8L16.5 9"/>',
    'The big idea': '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r=".8"/>',
    'Form & structure': '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>',
    'Site & context': '<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.3"/>',
    'People & life': '<circle cx="8" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M2.5 20c.8-4 3-6 5.5-6s4.7 2 5.5 6M14 19.5c.5-2.7 1.8-4 3.5-4s3 1.3 3.5 4"/>',
    'Poetic': '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    'Rational': '<rect x="4" y="4" width="16" height="16"/><path d="M4 9.3h16M4 14.6h16M9.3 4v16M14.6 4v16"/>',
    'Bold': '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    'Rooted': '<path d="M12 21v-8M12 13c-4 0-6-2.5-6-5.5S8.5 2 12 2s6 2.5 6 5.5-2 5.5-6 5.5zM12 17l-3 3M12 17l3 3"/>',
    'Keep mine, clean up': '<path d="M16 3l5 5-9 9-5-5z"/><path d="M7 12l-4 4 5 5h7"/>',
    'Polish them': '<path d="M12 4v4M12 16v4M4 12h4M16 12h4M6.5 6.5L9 9M15 15l2.5 2.5M17.5 6.5L15 9M9 15l-2.5 2.5"/>',
    'Transform them': '<path d="M4 20L15 9M15 9l2-2M17 3v2M21 7h-2M19.5 4.5L18 6M9 4h.01M20 13h.01"/>',
    'Surprise me': '<rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="9" cy="9" r=".9"/><circle cx="15" cy="15" r=".9"/><circle cx="15" cy="9" r=".9"/><circle cx="9" cy="15" r=".9"/><circle cx="12" cy="12" r=".9"/>',
    'Maximum drawings, limited text': '<rect x="3" y="5" width="18" height="14" rx="1.5"/><circle cx="8.5" cy="10" r="1.6"/><path d="M21 16l-5-5-8 8"/>',
    'Captions + 3 ideas': '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    'Elaborate writing': '<path d="M4 5c3-1 5.5-1 8 1 2.5-2 5-2 8-1v14c-3-1-5.5-1-8 1-2.5-2-5-2-8-1z"/><path d="M12 6v14"/>',
    'AI decides': '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M18 15l.9 2.1L21 18l-2.1.9L18 21l-.9-2.1L15 18l2.1-.9z"/>',
    'A lot, it’s the story': '<path d="M3 17c3-4 5 2 8-2s4-6 7-3M15 4l5 5M20 4l-4 4"/>',
    'A slice': '<path d="M12 3v9h9A9 9 0 1 1 12 3z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15z"/>',
    'Final only': '<rect x="3" y="3" width="18" height="18"/><rect x="7" y="7" width="10" height="10"/>',
    'Student': '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c2 2 10 2 12 0v-5M22 9v6"/>',
    'Professional / firm': '<path d="M4 21V5l8-3v19M12 9h8v12M2 21h20M7 8h2M7 12h2M7 16h2M15 13h2M15 17h2"/>',
    '1st–2nd': '<path d="M3 20h18M3 20v-5h6v5"/>',
    '3rd': '<path d="M3 20h18M3 20v-5h6v-5h6v10"/>',
    '4th–5th / thesis': '<path d="M3 20h18M3 20v-5h6v-5h6v-5h6v15"/>',
    'Masters': '<rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M7 8h10M7 11h6"/><circle cx="16" cy="16" r="2.5"/><path d="M15 18.5l-1 3M17 18.5l1 3"/>',
    'Client presentation': '<rect x="3" y="4" width="18" height="12" rx="1"/><path d="M12 16v4M8 21h8M7 12l3-3 3 2 4-4"/>',
    'Approval / planning submission': '<path d="M9 3h6v6l3 3v3H6v-3l3-3z"/><path d="M4 20h16"/>',
    'Website & portfolio': '<rect x="3" y="4" width="18" height="16" rx="1.5"/><path d="M3 9h18M6 6.5h.01M8.5 6.5h.01"/>',
    'Awards entry': '<circle cx="12" cy="15" r="5"/><path d="M8 3l2.5 7M16 3l-2.5 7M12 13v4"/>',
    'Concept': '<path d="M3 18c3-6 6-9 9-9s3 4 6 4 3-3 3-3"/><circle cx="6" cy="6" r="2"/>',
    'Schematic': '<rect x="3" y="10" width="8" height="10"/><rect x="11" y="5" width="10" height="15"/>',
    'Design development': '<path d="M4 20V4l16 16z"/><path d="M8 16v-4l4 4z"/>',
    'Built / completed': '<path d="M4 21V9l8-5 8 5v12M2 21h20M10 21v-6h4v6"/>',
    'Client (not an architect)': '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c1-4 4-6 7-6s6 2 7 6"/>',
    'Authority / planners': '<path d="M3 9l9-5 9 5M5 9v9M9 9v9M15 9v9M19 9v9M3 20h18"/>',
    'Peers & press': '<rect x="3" y="5" width="15" height="14" rx="1"/><path d="M18 9h3v8a2 2 0 0 1-2 2M6 9h9M6 12h9M6 15h6"/>',
    'Firm name in the title block': '<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M3 15h18M12 15v5M6 17.5h3"/>',
    'Unbranded': '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/>',
  };
  ICO['Competition jury'] = ICO['External jury'];
  ICO['Keep ours, clean up'] = ICO['Keep mine, clean up'];
  const ico = t => '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (ICO[t] || '<circle cx="12" cy="12" r="7"/>') + '</svg>';
  /* Question bank (prompts/INTAKE_QUESTIONS.md v2, D80). The ten v1 questions keep their wording and order;
     the professional path reuses six of them with "ours" wording. */
  const QB = {
    who: { k: 'You', q: 'Who’s presenting?', sub: 'Students and practices get slightly different questions.', o: [['Student', 'Student questions: year, crit, jury'], ['Professional / firm', 'Practice questions: client, stage, room']] },
    year: { k: 'Year', q: 'Which year are you in?', sub: 'Sets the vocabulary. A thesis gets a fuller story.', o: [['1st–2nd', 'Simple words, a clear story'], ['3rd', 'Studio vocabulary, a confident story'], ['4th–5th / thesis', 'A fuller story, research up front'], ['Masters', 'Precise language, the argument first']] },
    where: { k: 'Where', q: 'Where will this be shown?', sub: 'Sets how polished it gets.', o: [['Jury pin-up', 'Jury-ready finish, board and deck'], ['Design review', 'Lighter finish; your working story stays visible'], ['Portfolio', 'Tight edit, sized for a portfolio page'], ['Competition entry', 'One bold board with one strong hero'], ['Instagram / showcase', 'A punchy hero that crops to a square']] },
    word: { k: 'The one word', q: 'What one word do you want the jury to say?', sub: 'AI Studio leans the whole board that way.', o: [['“Beautiful”', 'Atmosphere first: big hero, mood renders'], ['“Clever”', 'Idea first: diagrams up front'], ['“Brave”', 'Gesture first: scale, contrast, few words'], ['“Thoughtful”', 'Site, people and process up front']] },
    aud: { k: 'Audience', q: 'Who do you need to impress?', sub: 'Sets the voice of every caption.', o: [['My studio tutor', 'Captions pick up from your last crit'], ['External jury', 'The story is explained from zero'], ['A firm / recruiter', 'Crisp captions that show your skills'], ['Classmates & Instagram', 'Short, punchy lines']] },
    crit: { k: 'Last crit', q: 'What did your tutor say last?', sub: 'AI Studio fixes this first.', o: [['“Concept isn’t clear”', 'Fix first: idea diagrams'], ['“Too much, no story”', 'Fix first: cut and sequence'], ['“Presentation is weak”', 'Fix first: graphics and renders'], ['“Good, just polish it”', 'Fix first: finish only']] },
    hero: { k: 'Hero', q: 'What’s the hero of your project?', sub: 'Decides which diagrams AI Studio proposes.', o: [['The big idea', 'Leads with a concept diagram'], ['Form & structure', 'Leads with an axonometric and a section'], ['Site & context', 'Leads with the site plan and context'], ['People & life', 'Leads with views full of people']] },
    proud: { k: 'Proudest', q: 'Which drawing are you proudest of?', sub: 'AI Studio found these in your files. Your pick gets the biggest slot.', thumbs: true, o: null },
    pers: { k: 'Personality', q: 'Your project’s personality?', sub: 'Pre-picks a style. You can change it later.', o: [['Poetic', 'Pastel Collage style, soft light'], ['Rational', 'Minimal style, crisp grid'], ['Bold', 'Crisp style, strong contrast'], ['Rooted', 'Warm Editorial style, earthy tones']] },
    ai: { k: 'How much AI', q: 'How far should AI go with your drawings?', sub: 'This also picks Polish or Transform.', o: [['Keep mine, clean up', 'Polish: your drawings, cleaned up'], ['Polish them', 'Polish: cleaned and polished'], ['Transform them', 'Transform: the hero view is re-rendered'], ['Surprise me', 'Transform: AI Studio picks what to re-render']] },
    words: { k: 'How many words', q: 'How much should your board talk?', sub: 'Sets the word budget.', o: [['Maximum drawings, limited text', 'Titles and labels only'], ['Captions + 3 ideas', 'Captions plus your 3 key ideas'], ['Elaborate writing', 'The full story, on board and deck'], ['AI decides', 'AI Studio picks the right amount for your project']] },
    proc: { k: 'Process', q: 'How much process to show?', sub: 'Adds a process strip, or not.', o: [['A lot, it’s the story', 'Process strip on the board, plus process slides'], ['A slice', 'One small process strip'], ['Final only', 'Final drawings only']] },
    pwhere: { k: 'Where', q: 'Where will this be shown?', sub: 'Sets the template and the polish.', o: [['Client presentation', 'The deck leads, the board backs it up'], ['Competition entry', 'One bold board, unbranded'], ['Approval / planning submission', 'Clear, factual sheets, drawings first'], ['Website & portfolio', 'Tight edit, sized for screens'], ['Awards entry', 'The strongest images, a short story']] },
    stage: { k: 'Stage', q: 'What stage is the project?', sub: 'Sets how real the renders look.', o: [['Concept', 'Diagram-led, soft renders'], ['Schematic', 'Plans and massing, light renders'], ['Design development', 'Detailed drawings, realistic renders'], ['Built / completed', 'Photo-led, drawings support']] },
    room: { k: 'Audience', q: 'Who’s in the room?', sub: 'Sets the voice of every caption.', o: [['Client (not an architect)', 'Plain language, no jargon'], ['Competition jury', 'The idea first, few words'], ['Authority / planners', 'Plain and factual'], ['Peers & press', 'Confident, design-led lines']] },
    firm: { k: 'Title block', q: 'Your firm on the sheet?', sub: 'Most competitions are anonymous, so entries stay unbranded.', o: [['Firm name in the title block', 'Your name or firm in the title block'], ['Unbranded', 'No name on the sheets']] }
  };
  /* "Which drawing are you proudest of?" is built from the uploads: the sample's drawings in the demo, the
     student's own drawings live (their pictures shown from this device; the answer sent is the file's name) */
  const PLACE = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 4 3%22%3E%3Crect width=%224%22 height=%223%22 fill=%22%23EDE4D3%22/%3E%3C/svg%3E';
  const THUMBS = {};
  const nice = (n) => { const l = String(n || '').replace(/\.[a-z0-9]+$/i, '').replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim(); return l.charAt(0).toUpperCase() + l.slice(1); };
  const drawings = () => (S.files || []).filter((f) => f.kind !== 'brief');
  function proudOpts() {
    if (DEMO) return HP.found.map((f) => { const l = f.label.replace(/^\d\s\s/, '').replace(/^Process \d: /, ''); const L = l.charAt(0).toUpperCase() + l.slice(1); return [L, L + ' gets the biggest slot', f.src]; });
    return drawings().map((f) => { const L = nice(f.original || f.name); return [L, L + ' gets the biggest slot', THUMBS[f.name] || PLACE, f.original || f.name]; });
  }
  QB.proud.o = proudOpts();
  const PRO = { hero: { q: 'What’s the hero of the project?' }, pers: { q: 'The project’s personality?' }, ai: { q: 'How far should AI go with the drawings?', o0: 'Keep ours, clean up' }, words: { q: 'How much should the board talk?' } };
  const PATHS = { student: ['who', 'year', 'where', 'word', 'aud', 'crit', 'hero', 'proud', 'pers', 'ai', 'words', 'proc', 'cname', 'ctitle', 'cloc', 'cprog', 'concept'],
    pro: ['who', 'pwhere', 'stage', 'room', 'hero', 'proud', 'pers', 'ai', 'words', 'proc', 'firm', 'cname', 'ctitle', 'cloc', 'cprog', 'concept'] };
  /* the title block, one fact per screen (owner, 28 Oct): field, question, example */
  const CARD = { cname: ['name', () => isPro() ? 'Your name or firm' : 'Your name', () => isPro() ? 'e.g. Morgan & Lee Architects' : 'e.g. Alex Morgan'],
    ctitle: ['title', () => 'Project title?', () => 'e.g. A Community Centre for Market Vendors'],
    cloc: ['loc', () => 'Location?', () => 'e.g. Law Garden, Ahmedabad'],
    cprog: ['prog', () => 'Building program?', () => 'e.g. Community centre with workshops and a stage'] };
  /* Typed text is corrected, never reworded (owner, 28 Oct: "architecture is a clear language").
     The live app runs a spelling and grammar pass; this stand-in fixes spacing and capitals. Names stay as typed. */
  const SMALL = /^(a|an|the|and|or|of|for|in|on|at|to|by|with)$/i;
  const cap1 = (w) => w.charAt(0).toUpperCase() + w.slice(1);
  function tidy(f, v) {
    v = String(v || '').replace(/\s+/g, ' ').trim().replace(/\s+([,.;:!?])/g, '$1').replace(/([,;:])(?=\S)/g, '$1 ');
    if (!v || f === 'name') return v;
    if (f === 'title') return v.replace(/\.+$/, '').split(' ').map((w, i) => i && SMALL.test(w) ? w.toLowerCase() : w === w.toLowerCase() ? cap1(w) : w).join(' ');
    if (f === 'loc') return v.split(' ').map((w) => w === w.toLowerCase() && !SMALL.test(w) ? cap1(w) : w).join(' ');
    return cap1(v);
  }
  const FIXNOTE = 'We correct spelling and grammar, never the meaning.';
  const isPro = () => S.ans.who === 1;
  const path = () => PATHS[isPro() ? 'pro' : 'student'];
  const curKey = () => path()[S.q - 1];
  function qd(k) {
    const b = QB[k], o = isPro() && PRO[k];
    return o ? Object.assign({}, b, { q: o.q }, o.o0 ? { o: [[o.o0, b.o[0][1]]].concat(b.o.slice(1)) } : {}) : b;
  }
  const ans = (k) => S.ans[k] === undefined ? null : S.ans[k];
  const forcedUnbranded = () => isPro() && ans('pwhere') === 1;
  const unbranded = () => isPro() && (forcedUnbranded() || ans('firm') === 1);
  const cardOk = () => ['name', 'title', 'loc', 'prog'].every((f) => (S.card[f] || '').trim());
  /* D82: the concept is the student's own words, used exactly as typed (or none: Studio plans from the drawings) */
  const concept = () => tidy('concept', S.concept);
  const briefs = () => DEMO ? (S.briefs || []) : (S.files || []).filter((f) => f.kind === 'brief').map((f) => f.original || f.name);
  const conceptLabel = () => S.fromHeard ? (paid() ? 'Save my answers' : 'Back to preview') : concept() ? 'See my preview' : 'Skip and see my preview';
  const norm = (s) => String(s).toLowerCase().replace(/[“”"’']/g, '').trim();
  /* D84 renamed the tiers: older answers (the sample's, a saved intake) still say "Re-render to Great" */
  const normA = (s) => { const n = norm(s); return n === 're-render to great' ? 'transform them' : n; };
  const V1 = ['where', 'word', 'aud', 'crit', 'hero', 'proud', 'pers', 'ai', 'words', 'proc'];
  function studentAnswers() {
    S.ans = { who: 0 }; S.oth = {};
    Object.values(P.intake).forEach((v, i) => { const k = V1[i], j = QB[k].o.findIndex((o) => norm(o[0]) === normA(v) || norm(o[0]).startsWith(normA(v))); if (j >= 0) S.ans[k] = j; });
    S.concept = 'Fabric as identity';
    S.card = { name: S.card.name || '', title: SAMPLE.name, loc: 'Law Garden, Ahmedabad', prog: 'Community centre for the cloth market’s vendors' };
  }
  const said = (k) => { const a = ans(k); return a === null ? 'skipped' : a === 'other' ? '“' + S.oth[k] + '”' : qd(k).o[a][0]; };
  const heard = (k, fb) => { const a = ans(k); return a === null ? fb : a === 'other' ? 'Your words: “' + S.oth[k] + '”' : qd(k).o[a][1]; };
  const planImg = (k) => {
    if (!DEMO) {   // live: the student's own drawings, by how the plan uses them
      const pics = ((S.edit || {}).pictures || []).filter((p) => p.thumb), hero = pics.find((p) => p.id === (S.edit || {}).hero) || pics[0];
      const want = { crit: ['site', 'render'], room: ['site', 'render'], word: ['model', 'render'], stage: ['model', 'render'], words: ['concept', 'process'], proc: ['process', 'concept'] }[k] || [];
      const p = k === 'proud' ? hero : pics.find((x) => want.includes(x.use)) || hero;
      return p ? p.thumb : PLACE;
    }
    return k === 'proud' ? (ans('proud') !== null && ans('proud') !== 'other' && QB.proud.o[ans('proud')] ? QB.proud.o[ans('proud')][2] : 'board/hero.jpg')
      : ({ crit: 'board/street.jpg', room: 'board/street.jpg', word: 'board/model-roof.jpg', stage: 'board/model-roof.jpg', words: 'board/fabric.jpg', proc: 'board/sk1.jpg' })[k] || 'board/hero.jpg';
  };
  const tierFromAnswers = () => ans('ai') === 0 || ans('ai') === 1 ? 'nice' : 'great';

  /* The answers as the API takes them (server/core/intake.py; prompts/INTAKE_QUESTIONS.md v2): the option's own words,
     {"other": text} for an Other box, nothing for a skipped question. */
  const AKEY = { student: { year: 's2_year', where: 'q1_shown_at', word: 'q2_jury_word', aud: 'q3_impress', crit: 'q4_last_crit', hero: 'q5_hero', proud: 'q6_proudest', pers: 'q7_personality', ai: 'q8_ai_rework', words: 'q9_text', proc: 'q10_process' },
    pro: { pwhere: 'q1_shown_at', stage: 'p3_stage', room: 'p4_room', hero: 'q5_hero', proud: 'q6_proudest', pers: 'q7_personality', ai: 'q8_ai_rework', words: 'q9_text', proc: 'q10_process', firm: 'p11_firm' } };
  const plain = (s) => String(s).replace(/[“”"]/g, '').trim();
  function intakeBody() {
    const pro = isPro(), answers = {};
    QB.proud.o = proudOpts();
    Object.entries(AKEY[pro ? 'pro' : 'student']).forEach(([k, key]) => {
      const a = k === 'firm' && forcedUnbranded() ? 1 : ans(k);
      if (a === null) return;
      if (a === 'other') { const t = (S.oth[k] || '').trim(); if (t) answers[key] = { other: t.slice(0, 300) }; return; }
      const o = qd(k).o[a];
      if (o) answers[key] = k === 'proud' ? (o[3] || o[0]) : plain(o[0]);
    });
    const c = S.card, body = { path: pro ? 'professional' : 'student', answers,
      card: { name: String(c.name || '').trim(), project_title: tidy('title', c.title), project_location: tidy('loc', c.loc), program: tidy('prog', c.prog) } };
    if (concept()) body.concept_text = concept();
    return body;
  }
  /* the other way: a saved intake (status "intake") back into the screens, e.g. on a new device from the receipt link */
  function fromIntake(it) {
    if (!it) return;
    S.ans = { who: it.path === 'professional' ? 1 : 0 }; S.oth = {};
    QB.proud.o = proudOpts();
    Object.entries(AKEY[it.path === 'professional' ? 'pro' : 'student']).forEach(([k, key]) => {
      const v = it[key];
      if (v === undefined || v === null || v === '') return;
      if (typeof v === 'object') { S.ans[k] = 'other'; S.oth[k] = v.other || v.text || ''; return; }
      const j = qd(k).o.findIndex((o) => norm(o[3] || o[0]) === norm(v) || norm(o[0]) === normA(v));
      if (j >= 0) S.ans[k] = j; else { S.ans[k] = 'other'; S.oth[k] = v; }
    });
    const c = it.card || {};
    S.card = { name: c.name || '', title: c.project_title || '', loc: c.project_location || '', prog: c.program || '' };
    S.concept = it.concept_text || '';
  }

  /* Demo only: put the typed title block and the chosen concept onto the sample board and deck (live, the build
     does this). Only the four typed facts show in the title block; unbranded entries drop the name. */
  function applyIntake() {
    const np = F.clone(P), c = S.card, pages = [np.board].concat(np.slides), orig = freshP();
    const T = (pg, pred) => pg.texts.find(pred);
    if (cardOk()) {
      const title = tidy('title', c.title), old = np.tbTitle || SAMPLE.name;
      if (title !== old) pages.forEach((pg) => pg.texts.forEach((t) => (t.paras || []).forEach((p) => p.runs.forEach((r) => { r.t = r.t.split(old).join(title).split(old.toUpperCase()).join(title.toUpperCase()); }))));
      np.tbTitle = title;
      const rows = [[isPro() ? 'Architect' : 'Student', c.name.trim()], ['Project', title], ['Location', tidy('loc', c.loc)], ['Program', tidy('prog', c.prog)]].filter((r, i) => i || !unbranded());
      const info = T(np.board, (t) => t.kind === 'info');
      if (info) info.rows = rows.map(([k, v]) => ({ k, v, ph: false }));
      np.slides.forEach((sl) => {
        const fr = sl.texts.filter((t) => t.name === 'info' && t.paras);
        if (fr.length === 2) {
          const kp = fr[0].paras[0], vp = fr[1].paras.find((p) => p.runs[0].c !== '#D33A2C') || fr[1].paras[0];
          fr[0].paras = rows.map(([k]) => Object.assign({}, kp, { runs: [Object.assign({}, kp.runs[0], { t: k.toUpperCase() })] }));
          fr[1].paras = rows.map(([, v]) => Object.assign({}, vp, { runs: [Object.assign({}, vp.runs[0], { t: v, c: '#1D1D1B' })] }));
        }
        sl.texts.filter((t) => t.name === 'credits').forEach((t) => {
          const r0 = t.paras[0].runs[0], sep = t.paras[0].runs.find((r) => r.t.trim() === '·') || r0;
          const parts = (unbranded() ? [] : [c.name.trim()]).concat([tidy('prog', c.prog), tidy('loc', c.loc)]);
          t.paras = [Object.assign({}, t.paras[0], { runs: [].concat(...parts.map((v, i) => (i ? [Object.assign({}, sep)] : []).concat([Object.assign({}, r0, { t: v, c: '#1D1D1B' })]))) })];
        });
      });
    }
    /* the concept heads the board's concept text and the deck's concept slide */
    const cs = np.slides.find((sl) => sl.texts.some((t) => t.name === 'section' && /CONCEPT/.test(t.paras[0].runs.map((r) => r.t).join(''))));
    const spots = [[np.board, T(np.board, (t) => t.name === 'concept'), 1]].concat(cs ? [[cs, T(cs, (t) => t.name === 'lead'), 0]] : []);
    spots.forEach(([pg, t, pi]) => {
      if (!t) return;
      const o = (pg.kind === 'board' ? orig.board : orig.slides.find((x) => x.n === pg.n)).texts.find((x) => x.id === t.id);
      const txt = concept() || o.paras[pi].runs.map((r) => r.t).join('');
      t.paras[pi] = Object.assign({}, t.paras[pi], { runs: [Object.assign({}, t.paras[pi].runs[0], { t: txt })] });
    });
    setP(np, 'Title block and concept');
  }

  /* ---------------------------------------------------------- routing */
  const SCREENS = ['home', 'upload', 'q', 'heard', 'planning', 'plan', 'price', 'making', 'result', 'edit', 'files', 'share'];
  const LEGAL = ['terms', 'privacy', 'refund'];
  function go(screen, quiet) {
    if (ed && ed.editing) ed.stopEdit();
    const before = STEP[S.screen];
    S.screen = screen; saveS();
    try { history.replaceState(null, '', location.pathname + (DEMO ? '?demo=1' : '') + '#' + screen); } catch (e) { /* sandboxed */ }
    render();
    window.scrollTo(0, 0);
    if (STEP[screen] > before && !quiet) {
      const chip = document.querySelectorAll('.steps span.done')[before];
      if (chip) chip.classList.add('justdone');
      confetti();
    }
  }
  function confetti() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const cs = getComputedStyle(document.documentElement);
    const cols = ['--coral', '--lime', '--sun', '--lilac', '--ink'].map((v) => cs.getPropertyValue(v).trim() || '#FF5A36');
    const c = document.createElement('canvas'), dpr = window.devicePixelRatio || 1, W = innerWidth, H = innerHeight;
    c.width = W * dpr; c.height = H * dpr; c.className = 'confetti'; c.setAttribute('aria-hidden', 'true');
    document.body.appendChild(c);
    const g = c.getContext('2d'); g.scale(dpr, dpr);
    const bits = Array.from({ length: 110 }, () => ({ x: W / 2 + (Math.random() - 0.5) * W * 0.3, y: H * 0.32, vx: (Math.random() - 0.5) * 14, vy: -Math.random() * 13 - 4,
      r: Math.random() * 6.3, vr: (Math.random() - 0.5) * 0.35, s: 6 + Math.random() * 7, k: Math.floor(Math.random() * 3), col: cols[Math.floor(Math.random() * cols.length)] }));
    const t0 = performance.now();
    (function frame(t) {
      const age = t - t0; g.clearRect(0, 0, W, H); g.globalAlpha = Math.max(0, 1 - Math.max(0, age - 1100) / 600);
      for (const b of bits) {
        b.vy += 0.42; b.vx *= 0.985; b.x += b.vx; b.y += b.vy; b.r += b.vr;
        g.save(); g.translate(b.x, b.y); g.rotate(b.r); g.fillStyle = b.col; g.strokeStyle = cs.getPropertyValue('--line').trim() || '#1B1A17'; g.lineWidth = 1.2;
        g.beginPath();
        if (b.k === 0) g.rect(-b.s / 2, -b.s / 2, b.s, b.s);
        else if (b.k === 1) { g.moveTo(0, -b.s / 1.6); g.lineTo(b.s / 1.8, b.s / 2.2); g.lineTo(-b.s / 1.8, b.s / 2.2); g.closePath(); }
        else { g.moveTo(-b.s / 2, b.s / 2); g.lineTo(-b.s / 2, 0); g.arc(0, 0, b.s / 2, Math.PI, 0); g.lineTo(b.s / 2, b.s / 2); g.closePath(); }
        g.fill(); g.stroke(); g.restore();
      }
      if (age < 1700) requestAnimationFrame(frame); else c.remove();
    })(t0);
  }
  const STEP = { home: -1, upload: 0, q: 1, heard: 1, planning: 2, plan: 2, price: 3, making: 3, result: 4, edit: 4, files: 5, share: 6 };
  function top() {
    const n = STEP[S.screen], back = (i) => i < n && n <= 3 && !paid() && (i < 2 || DEMO || PV);
    const steps = ['Upload', 'Questions', 'Preview', 'Pay', 'Edit', 'Download', 'Share'].map((t, i) => '<span class="' + (i < n ? 'done' : i === n ? 'now' : '') + (back(i) ? ' back' : '') + '"' + (back(i) ? ' data-act="go" data-s="' + ['upload', 'q', 'plan'][i] + '" role="button" tabindex="0" title="Go back to ' + t + '"' : '') + '>' + (i < n ? '✓ ' : '') + t + '</span>').join('');
    return '<header class="top"><a class="logo" href="#home" data-act="home"><i aria-hidden="true">✦</i>Studio FGA</a><nav class="steps hide-phone" aria-label="Steps">' + steps +
      '</nav><span class="spacer"></span>' + (DEMO ? '<span class="chip sun">DEMO · SAMPLE PROJECT</span>' : '') + '</header>';
  }

  /* ---------------------------------------------------------- shared parts (landing and app use the same pieces) */
  const SPARK = '<svg class="spark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l2.2 6.3L20.5 10.5l-6.3 2.2L12 19l-2.2-6.3L3.5 10.5l6.3-2.2z"/><path d="M19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z"/></svg>';
  const shiny = (act, title, small, extra) => '<button class="btn shiny' + (extra ? ' ' + extra : '') + '" data-act="' + act + '">' + SPARK + '<span class="cta"><b>' + title + '</b>' + (small ? '<small>' + small + '</small>' : '') + '</span><span class="arrow" aria-hidden="true">→</span></button>';
  const TICK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
  /* part: 'key' = only the magic part, 'rest' = only the six tiles, none = all */
  function getsData(tier, nSl) {
    const ai = tier === 'great' ? ['Up to 15 new images', 'Hero view, plans, sections and diagrams, redrawn by AI']
      : tier === 'nice' ? ['1–4 new images', 'Your key views re-rendered by AI, the rest cleaned up']
      : ['Up to 15 new images', 'Hero view, plans, sections and diagrams, redrawn by AI (1–4 with Polish)'];
    const gets = [[ai[0], ai[1], 'key'], ['A1 board, print-ready', '594 × 841 mm on a clean grid'], ['Jury deck, ' + (nSl || 13) + ' slides', 'Contents first, one idea per slide'],
      ['Story and captions written', 'From your answers, checked against your drawings'], ['Labels, scale bars and north', 'Titles and drawing labels done for you'],
      ['Files you can keep editing', 'PDF, PowerPoint and InDesign'], [tier === 'nice' ? 'Ready in under 10 minutes' : tier === 'great' ? 'Ready in about 5 minutes' : 'Ready in minutes', 'Plus one free redo within 7 days']];
    return gets.map((g, i) => [g[0], g[1], g[2] || '', ['spark', 'board', 'deck', 'text', 'north', 'files', 'clock'][i]]);
  }
  function getsList(tier, nSl, part) {
    const gets = getsData(tier, nSl);
    const pick = part === 'key' ? gets.slice(0, 1) : part === 'rest' ? gets.slice(1) : gets;
    return '<ul class="gets">' + pick.map((g) => '<li' + (g[2] ? ' class="key"' : '') + '>' + TICK + '<div>' + (g[2] ? '<em class="keytag">✦ The magic part</em>' : '') + '<b>' + g[0] + '</b><span>' + g[1] + '</span></div></li>').join('') + '</ul>';
  }
  /* line icons for the buying panel */
  const DI = { spark: '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M18 15l.9 2.1L21 18l-2.1.9L18 21l-.9-2.1L15 18l2.1-.9z"/>',
    board: '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M8 7h8M8 10.5h4M13.5 10.5H16v5h-2.5zM8 14h4M8 17.5h8"/>', deck: '<rect x="3" y="5" width="18" height="12" rx="1.5"/><path d="M7 9h6M7 12h4M12 17v4M8 21h8"/>',
    text: '<path d="M5 6h14M5 10h14M5 14h9M5 18h6"/>', north: '<path d="M3 18h12M3 16v4M7.5 16.5v3M11 16v4M15 16v4"/><path d="M18.5 3l2.5 7-2.5-1.6L16 10z"/>',
    files: '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4M9 12h6M9 15.5h6M9 19h3"/>', clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    noacct: '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c1-4 4-6 7-6s6 2 7 6"/><path d="M3 3l18 18"/>', redo: '<path d="M4 12a8 8 0 1 0 2.4-5.7M4 4v4h4"/>', lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>' };
  const dic = (k) => '<svg class="dic" viewBox="0 0 24 24" aria-hidden="true">' + DI[k] + '</svg>';
  const TRUST = () => '<ul class="trust"><li>' + dic('noacct') + 'No account needed</li><li>' + dic('redo') + 'One free redo in 7 days</li><li>' + dic('lock') + 'Secure checkout · Dodo Payments</li></ul>';
  /* board and deck side by side at equal weight (owner: "Deck & board both are important") */
  /* m: which model the thumbnails draw ('h' the sample, 'v' the preview, '' the project) */
  function sheets(nShow, extra, m) {
    const M = modelOf(m), mm = m ? ' data-m="' + m + '"' : '';
    const sl = F.visibleSlides(M), show = nShow ? sl.slice(0, nShow) : sl;
    return '<div class="sheets"><figure class="sbox"><figcaption class="kicker">A1 board</figcaption><div class="sth" data-mini="board"' + mm + ' data-w="340" data-fit="1"></div>' + (extra || '') + '</figure>' +
      '<figure class="sbox"><figcaption class="kicker">Jury deck · ' + sl.length + ' slides</figcaption><div class="sgrid' + (nShow ? ' wide' : '') + '">' +
      show.map((x) => '<div><div class="sth" data-mini="slide:' + x.n + '"' + mm + ' data-w="170" data-fit="1" data-min="60"></div></div>').join('') + '</div></figure></div>';
  }
  const modelOf = (m) => m === 'h' ? HP : m === 'v' ? Q() : P;
  const didCards = () => '<div class="didgrid">' + DID.map(([b, a, t, d]) => '<figure class="pair"><div class="pimgs"><div><img src="' + HP.base + b + '" alt="Before: ' + esc(t) + '" loading="lazy"><em>Before</em></div><span class="parrow" aria-hidden="true">→</span><div><img src="' + HP.base + a + '" alt="After: ' + esc(t) + '" loading="lazy"><em class="after">After</em></div></div><figcaption><b>' + t + '</b><span>' + d + '</span></figcaption></figure>').join('') + '</div>';
  const TIERS = { nice: ['Polish', 11, ['Your drawings cleaned up and lined up', '1–4 new images', 'Captions, labels, scale bars and north', 'Board + deck: PDF, PowerPoint, InDesign']],
    great: ['Transform', 16, ['Everything in the Polish option ($11)', 'Up to 15 new images', 'Hero view, plans and sections redrawn', 'New diagrams in the same family']] };

  /* ---------- composition preview (rule 26, D85; owner picked option 2 on 28 Oct, prototype b6c744c..d9a1f66).
     The final layout: slots from the student's drawings are shown faded with a bold label and an AI mark, slots
     AI Studio will create are grey "· new" boxes, text slots are placeholder lines. Live data: the status's
     preview.composition (server/README.md, "The composition"); x, y, w, h are fractions of the page. The demo uses
     the prototype's mock on the sample sheets (`crop` is a demo-only extra so one sheet can show the right part). */
  let COMP = null, COMPSRC = null;
  const CONCEPT_NOTE = () => concept() || (DEMO ? (P.board.texts.find((x) => x.id === 'b-concept') || { paras: [{ runs: [] }, { runs: [] }] }).paras[1].runs.map((r) => r.t).join('') : '');
  const noteOf = (sd) => typeof sd.note === 'string' ? sd.note : sd.note ? CONCEPT_NOTE() : '';
  function composition() {
    if (DEMO) return COMP || (COMP = demoComposition());
    const c = ST && ST.preview && ST.preview.composition;
    if (c && c.board && c.deck) {
      if (COMPSRC !== c) {
        COMPSRC = c;
        const dw = c.deck.w_mm || 338.667, dh = c.deck.h_mm || 190.5;
        COMP = { board: { slots: c.board.slots || [], ratio: (c.board.w_mm || 594) / (c.board.h_mm || 841) },
          deck: { ratio: dw / dh, slides: (c.deck.slides || []).map((x, i) => ({ n: x.n || i + 1, title: x.title || '', kind: x.kind || '', contents: x.contents || [], note: x.note || null, slots: x.slots || [] })) },
          basics: c.basics || [] };
      }
      return COMP;
    }
    return compFromSketch();
  }
  /* an older server without `composition`: the same picture made from the plan's sketch */
  function compFromSketch() {
    const M = PV;
    if (!M) return { board: { slots: [], ratio: 594 / 841 }, deck: { ratio: 16 / 9, slides: [] } };
    const of = (pg) => pg.slots.map((sl) => { const c = pg.contents[sl.content]; return { label: c.alt || 'Drawing', role: '', source: 'student', image_url: c.src, x: sl.x / pg.w, y: sl.y / pg.h, w: sl.w / pg.w, h: sl.h / pg.h }; })
      .concat(pg.texts.map((t) => ({ label: NAMES[t.name] || 'Text', role: t.name === 'title' ? 'title' : 'text', source: 'text', image_url: null, x: t.x / pg.w, y: t.y / pg.h, w: t.w / pg.w, h: (t.maxH || 10) / pg.h })));
    return { board: { slots: of(M.board), ratio: 594 / 841 }, deck: { ratio: 16 / 9, slides: M.slides.map((pg) => { const m = (M.slideMeta || {})[pg.n]; return { n: pg.n, title: m ? m.label : 'Cover', kind: m ? m.role : 'cover', contents: [], note: null, slots: of(pg) }; }) } };
  }
  function demoComposition() {
    const BW = P.board.w, BH = P.board.h, raw = (f) => P.base + 'raw/' + f;
    const at = (o) => ({ x: o.x / BW, y: o.y / BH, w: o.w / BW, h: (o.h || o.maxH) / BH });
    const img = (id, label, role, source, file, crop) => Object.assign(at(P.board.slots.find((x) => x.id === id)), { label, role, source, image_url: file ? raw(file) : null, crop });
    const txt = (id, label, role) => Object.assign(at(P.board.texts.find((x) => x.id === id)), { label, role, source: 'text', image_url: null });
    const board = { ratio: BW / BH, slots: [txt('b-title', 'Title', 'title'), txt('b-info', 'Title block', 'info'), img('b-hero', 'Hero render', 'render', 'create'),
      txt('b-concept', 'Concept', 'concept'), txt('b-story', 'Story', 'text'), txt('b-ideas', 'Three ideas', 'text'),
      img('b-sk1', 'Sketch', 'process', 'student', 'sheet-3.jpg', [.228, .036, .474, .338]), img('b-sk2', 'Sketch', 'process', 'student', 'sheet-3.jpg', [.228, .36, .474, .66]),
      img('b-sk3', 'Sketch', 'process', 'student', 'sheet-3.jpg', [.228, .68, .474, .98]), img('b-fabric', 'Concept diagram', 'concept', 'student', 'sheet-3.jpg', [.609, .07, .987, .25]),
      img('b-elev', 'Elevation', 'elevation', 'create'), img('b-model-court', 'Model photo', 'model', 'student', 'sheet-3.jpg', [.609, .507, .987, .74]),
      img('b-model-fabric', 'Model photo', 'model', 'student', 'sheet-3.jpg', [.609, .75, .987, .99]), img('b-model-roof', 'Model photo', 'model', 'student', 'sheet-5.jpg', [.176, .548, .647, .99]),
      img('b-site', 'Site plan', 'site', 'student', 'sheet-1.jpg', [.15, .225, .578, .97]), img('b-plan', 'Plan', 'plan', 'student', 'sheet-6.jpg'),
      img('b-section', 'Section', 'section', 'student', 'sheet-5.jpg', [.005, .028, .995, .524]), img('b-street', 'Section perspective', 'view', 'create')] };
    const S_ = (label, role, source, x, y, w, h, file, crop) => ({ label, role, source, x, y, w, h, image_url: file ? raw(file) : null, crop });
    const T_ = (label, x, y, w, h, role) => S_(label, role || 'text', 'text', x, y, w, h);
    const head = T_('Title', .04, .07, .5, .14, 'heading');
    const slides = [
      ['Cover', 'cover', ['Hero render · new', 'Project title and title block'], [S_('Hero render', 'render', 'create', .04, .08, .56, .84), T_('Title', .64, .1, .32, .26, 'title'), T_('Title block', .64, .7, .32, .18, 'info')]],
      ['Contents', 'contents', ['The sections, numbered'], [T_('Contents', .06, .1, .88, .78)]],
      ['Brief & program', 'brief', ['Brief note', '1 brief sheet'], [head, T_('Brief', .04, .3, .38, .55), S_('Brief sheet', 'brief', 'student', .48, .3, .48, .55, 'sheet-2.jpg')]],
      ['Site & context', 'site', ['1 site plan', 'Site note'], [head, S_('Site plan', 'site', 'student', .36, .24, .6, .7, 'sheet-1.jpg', [.15, .225, .578, .97]), T_('About the site', .04, .62, .28, .28)]],
      ['Concept', 'concept', ['Concept note', '1 concept diagram'], [head, S_('Concept diagram', 'concept', 'student', .36, .26, .6, .5, 'sheet-3.jpg', [.609, .07, .987, .25]), T_('Concept', .04, .3, .28, .4, 'concept')]],
      ['Process', 'process', ['2 sketches', '1 model photo'], [head, S_('Sketch', 'process', 'student', .04, .32, .29, .5, 'sheet-3.jpg', [.228, .036, .474, .338]), S_('Sketch', 'process', 'student', .355, .32, .29, .5, 'sheet-3.jpg', [.228, .36, .474, .66]), S_('Model photo', 'model', 'student', .67, .32, .29, .5, 'sheet-3.jpg', [.609, .507, .987, .74])]],
      ['Plans', 'plan', ['1 plan', 'Plan note'], [head, S_('Plan', 'plan', 'student', .36, .1, .6, .84, 'sheet-6.jpg'), T_('About the plan', .04, .62, .28, .28)]],
      ['Sections', 'section', ['1 section', 'Section note'], [head, S_('Section', 'section', 'student', .04, .27, .92, .5, 'sheet-5.jpg', [.005, .028, .995, .524]), T_('About the section', .04, .82, .5, .1)]],
      ['Elevations', 'elevation', ['1 elevation · new'], [head, S_('Elevation', 'elevation', 'create', .04, .3, .92, .48), T_('About the elevation', .04, .82, .5, .1)]],
      ['Views', 'views', ['1 entrance view', '1 model photo', '1 interior view · new'], [S_('Entrance view', 'render', 'student', .04, .08, .6, .84, 'sheet-4.jpg'), S_('Model photo', 'model', 'student', .68, .08, .28, .4, 'sheet-5.jpg', [.176, .548, .647, .99]), S_('Interior view', 'render', 'create', .68, .52, .28, .4)]],
      ['Axonometric', 'axonometric', ['1 axonometric · new', 'Structure note'], [head, S_('Axonometric', 'axonometric', 'create', .36, .1, .6, .84), T_('How it stands', .04, .62, .28, .28)]],
      ['Closing', 'closing', ['Hero render', 'The three ideas'], [S_('Hero render', 'render', 'create', 0, 0, 1, 1), T_('Three ideas', .05, .58, .5, .32)]]
    ].map(([title, kind, contents, slots], i) => ({ n: i + 1, title, kind, contents, note: kind === 'concept', slots }));
    return { board, deck: { ratio: 16 / 9, slides } };
  }
  /* the deck's order and left-out slides. Demo: kept here. Live: a slide that matches one of the plan's slides is left
     out through the plan (PUT /jobs/{id}/plan), so the build follows it; the others (cover, contents, new basics) stay. */
  function editOf(sd) {
    if (DEMO || !PV || !PV.slideMeta) return null;
    const metas = Object.values(PV.slideMeta), norm2 = (x) => String(x || '').toLowerCase();
    const m = metas.find((x) => norm2(x.role) === norm2(sd.kind)) || metas.find((x) => norm2(x.label) === norm2(sd.title) || norm2(x.title) === norm2(sd.title));
    return m || null;
  }
  const isOff = (sd) => { if (DEMO) return (S.pvOff || []).includes(sd.n); const m = editOf(sd); return !!(m && PV.slideOff.includes(m.n)); };
  const pvSlides = () => { const all = composition().deck.slides, ord = (S.pvOrder && S.pvOrder.length === all.length && all.every((x) => S.pvOrder.includes(x.n))) ? S.pvOrder : all.map((x) => x.n);
    return ord.map((n) => all.find((x) => x.n === n)); };
  const pvOn = () => pvSlides().filter((x) => !isOff(x));
  function compCounts(c) {
    const yours = {}, made = {}, byTier = { polish: {}, transform: {} };
    [c.board.slots].concat(c.deck.slides.map((x) => x.slots)).forEach((list) => list.forEach((sl) => {
      if (sl.source === 'student') yours[sl.image_url ? String(sl.image_url).split('?')[0] + (sl.crop || '') : sl.label] = 1;
      else if (sl.source === 'create') { made[sl.label] = 1; if (sl.tier === 'polish' || sl.tier === 'transform') byTier[sl.tier][sl.label] = 1; } }));
    const np = Object.keys(byTier.polish).length, nt = Object.keys(byTier.transform).length;
    return [Object.keys(yours).length, Object.keys(made).length, np + nt ? [np, np + nt] : null];
  }
  const cropCSS = (cr) => !cr ? 'background-size:cover;background-position:center' : (() => { const w = cr[2] - cr[0], h = cr[3] - cr[1], bp = (a, sp) => sp >= 1 ? '0' : (a / (1 - sp) * 100).toFixed(1) + '%';
    return 'background-size:' + (100 / w).toFixed(1) + '% ' + (100 / h).toFixed(1) + '%;background-position:' + bp(cr[0], w) + ' ' + bp(cr[1], h); })();
  const MINISPARK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/></svg>';
  const projTitle = () => tidy('title', S.card.title) || (ST && ST.intake && ST.intake.card ? ST.intake.card.project_title : '') || (DEMO ? SAMPLE.name : 'Your project');
  function compSlot(sl, p, i) {
    const pos = 'left:' + (sl.x * 100).toFixed(2) + '%;top:' + (sl.y * 100).toFixed(2) + '%;width:' + (sl.w * 100).toFixed(2) + '%;height:' + (sl.h * 100).toFixed(2) + '%';
    const sel = S.pvSel && S.pvSel[0] === p && S.pvSel[1] === i ? ' sel' : '';
    if (sl.source === 'text') {
      if (sl.role === 'title') return '<div class="cs ctitle" style="' + pos + '"><b>' + esc(projTitle()) + '</b><i></i><i></i></div>';
      return '<button class="cs text' + sel + '" data-act="slotInfo" data-p="' + p + '" data-i="' + i + '" style="' + pos + '" aria-label="' + esc(sl.label) + ', text"><span>' + esc(sl.label) + '</span><i></i><i></i><i></i></button>';
    }
    const src = sl.source === 'create' ? 'create' : 'student';
    const im = src === 'student' && sl.image_url ? '<b class="ci" style="background-image:url(&quot;' + esc(sl.image_url) + '&quot;);' + cropCSS(sl.crop) + '"></b>' : '';
    const lab = String(sl.label || '').replace(/\s*·\s*new$/i, '');
    return '<button class="cs ' + src + sel + '" data-act="slotInfo" data-p="' + p + '" data-i="' + i + '" style="' + pos + '" aria-label="' + esc(lab) + (src === 'create' ? ', new by AI Studio' : ', from your drawings, retouched by AI Studio') + '">' + im +
      '<span class="cl">' + (src === 'create' ? MINISPARK : '') + esc(lab) + (src === 'create' ? ' · new' : '<em class="aim" aria-hidden="true">' + MINISPARK + 'AI</em>') + '</span></button>';
  }
  const compPage = (slots, ratio, p) => '<div class="comp show-' + (S.pvShow || 'all') + '" style="aspect-ratio:' + ratio.toFixed(4) + '">' + slots.map((sl, i) => compSlot(sl, p, i)).join('') + '</div>';
  const compBoard = () => compPage(composition().board.slots, composition().board.ratio, 0);
  const compSlide = (sd) => compPage(sd.slots, composition().deck.ratio, sd.n);
  function slotWhat(sl) {
    if (!sl) return ['Tap any box', 'See what each part of your board and deck will become.'];
    const lab = String(sl.label || '').replace(/\s*·\s*new$/i, '');
    if (sl.source === 'create') return [lab + ' · new by AI Studio', 'Drawn by AI Studio from your plans, sections and views, in the same style as the rest. Nothing is made up: it shows only what your drawings show.' + (sl.tier === 'transform' ? ' Made with Transform.' : sl.tier === 'polish' ? ' Made with Polish and Transform.' : '')];
    if (sl.source === 'text') return [lab + ' · written by AI Studio', 'Written from your answers and drawings. You can change every word in the editor.'];
    const tech = /plan|section|site|elevation/.test(sl.role || '') ? ', scale bar and north arrow' : '';
    return [lab + ' · from your drawings, retouched by AI', 'Your own drawing, cleaned up and reworked by AI to match the board, with its caption' + tech + '.'];
  }
  const selSlot = () => { if (!S.pvSel) return null; const c = composition(); const list = S.pvSel[0] === 0 ? c.board.slots : (c.deck.slides.find((x) => x.n === S.pvSel[0]) || { slots: [] }).slots; return list[S.pvSel[1]] || null; };
  const slotInfoHTML = () => { const sl = selSlot(), w = slotWhat(sl);
    return '<div class="sinfo' + (sl ? ' on ' + (sl.source === 'create' ? 'create' : sl.source) : '') + '" id="slotinfo" aria-live="polite"><b>' + esc(w[0]) + '</b><span>' + esc(w[1]) + '</span></div>'; };
  /* No tier is chosen here (owner, 28 Oct): the "how far should AI go" answer is about moving away from the design,
     not about quality, so the card shows the starting price and both tiers; the student picks on the next page. */
  function orderCard(nSl, tiers) {
    const key = getsData(null, nSl)[0];
    return '<aside class="order"><div class="ohead"><p class="kicker">Your order</p></div>' +
      '<h2 class="mid">Your board and deck</h2><p class="osub">A1 board · ' + nSl + '-slide jury deck · ready in minutes</p>' +
      '<p class="oprice"><small>from</small><b>$11</b><span>Polish $11 · Transform $16 · one payment, no subscription</span></p>' +
      (tiers ? '<p class="osub" style="margin:0">Polish adds ' + tiers[0] + ' new · Transform adds ' + tiers[1] + ' new</p>' : '') +
      '<div class="magic">' + dic('spark') + '<div><em class="keytag">✦ The magic part</em><b>' + key[0] + '</b><span>' + key[1] + '</span></div></div>' +
      '<div id="maincta">' + shiny('toPrice', 'Make my board and deck', 'Pick Polish or Transform next') + '</div>' + TRUST() + '</aside>';
  }
  const includedCards = (nSl) => '<div class="ifull"><p class="kicker">What’s included</p><ul class="icards">' + getsData(null, nSl).slice(1).map((r) => '<li>' + dic(r[3]) + '<b>' + r[0] + '</b><span>' + r[1] + '</span></li>').join('') + '</ul></div>';
  const capOf = (sd) => '<figcaption><b>' + esc(sd.title) + '</b><span>' + esc((sd.contents || []).join(' · ')) + '</span></figcaption>';
  function previewPanel() {
    const c = composition(), nSl = pvOn().length, [ny, nn, tiers] = compCounts(c), sh = S.pvShow || 'all';
    const legend = '<div class="legend"><span class="lg yours"><i></i>' + ny + ' from your drawings, retouched by AI</span><span class="lg new"><i></i>' + nn + ' new by AI Studio</span><span class="lg txt"><i></i>Text written for you</span></div>';
    const showSeg = '<div class="seg pvseg" role="group" aria-label="Show">' + [['all', 'Everything'], ['yours', 'Your drawings <small class="airew">(AI reworks)</small>'], ['new', 'What AI Studio adds']].map(([v, l]) => '<button data-act="pvShow" data-v="' + v + '" class="' + (sh === v ? 'on' : '') + '" aria-pressed="' + (sh === v) + '">' + l + '</button>').join('') + '</div>';
    const ctabar = '<div class="ctabar" id="ctabar"><div><b>Your board + ' + nSl + '-slide deck</b><span>' + ny + ' of your drawings · ' + nn + ' new · from $11</span></div><button class="btn primary" data-act="toPrice">Make it</button></div>';
    const head = '<div class="pvhead"><div><p class="kicker">Step 3 · free preview</p><h1 class="mid">This is your board and deck</h1></div></div>';
    const tab = S.pvTab === 'deck' ? 'deck' : 'board';
    const tabs = '<div class="seg pvtabs" role="tablist" aria-label="Sheet">' + [['board', 'A1 board'], ['deck', 'Jury deck · ' + nSl]].map(([v, l]) => '<button role="tab" data-act="pvTab" data-v="' + v + '" class="' + (tab === v ? 'on' : '') + '" aria-selected="' + (tab === v) + '">' + l + '</button>').join('') + '</div>';
    const stage = tab === 'board' ? '<div class="pvstage board">' + compBoard() + '</div>'
      : '<div class="pvstage deck"><div class="dgrid">' + pvOn().map((sd) => '<figure class="dslide">' + compSlide(sd) + capOf(sd) + '</figure>').join('') + '</div></div>';
    return '<section class="deal dealx pv2">' + head + '<div class="pvtop"><div class="pvmain"><div class="pvtools">' + tabs + showSeg + '</div>' + legend + stage + '</div>' +
      '<div class="pvrail">' + slotInfoHTML() + orderCard(nSl, tiers) + '</div></div>' + includedCards(nSl) + ctabar + '</section>';
  }
  function pvList() {
    const all = pvSlides();
    return '<ol class="dlist">' + all.map((sd, k) => {
      const o = isOff(sd), pos = all.slice(0, k + 1).filter((x) => !isOff(x)).length, m = editOf(sd), note = noteOf(sd);
      const locked = !DEMO && (!m || (m.required && !o)), why = !DEMO && !m ? ' title="AI Studio keeps this slide"' : !DEMO && m && m.required ? ' title="Needed for your drawings"' : '';
      return '<li class="drow' + (o ? ' off' : '') + '"><span class="dnum" aria-hidden="true">' + (o ? '–' : String(pos).padStart(2, '0')) + '</span><div class="dcard"><div class="dthumb">' + compSlide(sd) + '</div>' +
        '<div class="dtxt"><b>' + esc(sd.title) + '</b><ul class="dcont">' + (sd.contents || []).map((x) => '<li>' + esc(x) + '</li>').join('') + '</ul>' + (note ? '<p class="dnote">“' + esc(note) + '”</p>' : '') + (o ? '<p class="hint">Left out of the deck</p>' : '') + '</div>' +
        '<div class="dctl"><button data-act="pvMove" data-k="' + k + '" data-d="-1" aria-label="Move ' + esc(sd.title) + ' up"' + (k <= 1 ? ' disabled' : '') + '>↑</button><button data-act="pvMove" data-k="' + k + '" data-d="1" aria-label="Move ' + esc(sd.title) + ' down"' + (k === 0 || k === all.length - 1 ? ' disabled' : '') + '>↓</button>' +
        '<button data-act="pvLeave" data-n="' + sd.n + '"' + (k === 0 || locked ? ' disabled' : '') + why + '>' + (o ? 'Put back' : 'Leave out') + '</button></div></div></li>'; }).join('') + '</ol>';
  }

  /* ---------------------------------------------------------- screens */
  const V = {};
  const nFiles = () => DEMO ? P.raw.length - (S.rmRaw || []).length + S.extra.length : (S.files || []).length;
  const RM = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  /* live upload: the student's files on the server, plus the ones still on their way or refused (UP). A file gets
     its slot the moment it is dropped or picked: its picture (or a PDF tag), a spinner and a progress bar; it
     becomes a normal thumbnail when the server has it, or shows why it failed (owner's test note 1). */
  let UP = [], upSeq = 0, upErr = '';
  const upBusy = () => UP.filter((u) => !u.err).length;
  const upCard = (u) => {
    const pc = Math.round(u.pct * 100), img = '<img src="' + (u.thumb || PLACE) + '" alt="">' + (u.thumb ? '' : '<span class="fkind">' + esc((u.name.split('.').pop() || 'file').toUpperCase()) + '</span>');
    if (u.err) return '<div class="file err">' + img + '<span>' + esc(u.name) + '</span><span class="ferr" role="alert">' + esc(u.err) + '</span>' +
      '<button class="rm" data-act="dropUp" data-k="' + u.k + '" aria-label="Dismiss ' + esc(u.name) + '">' + RM + '</button>' + (u.retry ? '<button class="link" data-act="retryUp" data-k="' + u.k + '" style="min-height:32px;align-self:flex-start">Try again</button>' : '') + '</div>';
    return '<div class="file up">' + img + '<i class="spin" aria-hidden="true"></i><span>' + esc(u.name) + ' · ' + (u.pct > 0 ? (pc >= 100 ? 'finishing…' : pc + '%') : 'starting…') + '</span>' +
      '<div class="bar upbar" role="progressbar" aria-label="Uploading ' + esc(u.name) + '" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + pc + '"><i id="up-' + u.k + '" style="width:' + pc + '%"></i></div></div>';
  };
  const kb = (b) => b >= 1048576 ? (b / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(b / 1024)) + ' KB';
  V.upload = () => DEMO ? V.uploadDemo() : '<main class="wrap"><p class="kicker">' + (paid() ? 'Before your free redo' : 'Step 1 · free') + '</p><h1 class="big">Add your drawings. 5–10 works best.</h1>' +
    '<section class="drop" id="drop" aria-label="Your files"><div class="row"><span class="chip lime">' + drawings().length + ' FILES</span>' + (upBusy() ? '<span class="chip">UPLOADING ' + upBusy() + '</span>' : '') + '</div>' +
    '<div class="files">' + drawings().map((f) => '<div class="file"><img src="' + (THUMBS[f.name] || PLACE) + '" alt="' + esc(f.original || f.name) + '">' + (THUMBS[f.name] ? '' : '<span class="fkind">' + esc(String(f.type || 'file').toUpperCase()) + '</span>') + '<span>' + esc(f.original || f.name) + ' · ' + kb(f.bytes || 0) + '</span><button class="rm" data-act="rmFile" data-name="' + esc(f.name) + '" aria-label="Remove ' + esc(f.original || f.name) + '">' + RM + '</button></div>').join('') +
    UP.filter((u) => u.kind !== 'brief').map(upCard).join('') + '</div>' +
    (drawings().length || UP.length ? '' : '<p class="status">Plans, sections, sketches, model photos, renders, or screenshots of your sheets.</p>') +
    '<div class="row"><button class="btn small" data-act="add">Add files</button><input id="add" type="file" multiple accept="image/png,image/jpeg,image/webp,application/pdf,.pdf,.png,.jpg,.jpeg,.webp" hidden><span class="status">or drag them here · PNG, JPG, WebP or PDF, up to 25 MB each</span></div>' +
    '<p class="err" id="upErr" role="alert">' + esc(upErr) + '</p>' +
    '<div class="row"><button class="link" data-act="addBrief">Brief or concept note? Add it here (optional)</button>' + (S.files || []).filter((f) => f.kind === 'brief').map((f) => '<span class="chip sun">BRIEF · ' + esc(f.original || f.name) + ' <button class="link" data-act="rmFile" data-name="' + esc(f.name) + '" aria-label="Remove ' + esc(f.original || f.name) + '">✕</button></span>').join('') +
    UP.filter((u) => u.kind === 'brief').map((u) => u.err ? '<span class="chip">BRIEF · ' + esc(u.name) + ' · not added <button class="link" data-act="dropUp" data-k="' + u.k + '" aria-label="Dismiss">✕</button></span>' : '<span class="chip">BRIEF · ' + esc(u.name) + ' · uploading</span>').join('') +
    UP.filter((u) => u.kind === 'brief' && u.err).map((u) => '<p class="err" role="alert" style="flex-basis:100%">' + esc(u.err) + '</p>').join('') + '</div></section>' +
    '<div class="row">' + (paid() ? '<button class="btn primary" data-act="toResult">Back to my board</button><span class="status">Your free redo uses these drawings.</span>' : '<button class="btn primary" data-act="toQ">Next</button><span class="status">No account needed.</span>') + '</div>' +
    (S.job && (S.files || []).length ? '<button class="link" data-act="newJob" style="align-self:flex-start">' + (S.newArm ? 'Click again: this clears these files from this page' : 'Start a new project instead') + '</button>' : '') + '</main>';
  V.uploadDemo = () => '<main class="wrap"><p class="kicker">Step 1 · free</p><h1 class="big">Add your drawings. 5–10 works best.</h1>' +
    '<section class="drop" id="drop" aria-label="Your files"><div class="row"><span class="chip lime">' + nFiles() + ' FILES</span><span class="chip">Sample: Law Garden community centre</span></div>' +
    '<div class="files">' + P.raw.map((r, i) => (S.rmRaw || []).includes(i) ? '' : '<div class="file"><img src="' + P.base + r.src + '" alt="' + esc(r.name) + '"><span>' + esc(r.name) + ' · ' + r.kb + ' KB</span><button class="rm" data-act="rmFile" data-k="raw" data-i="' + i + '" aria-label="Remove ' + esc(r.name) + '"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>').join('') +
    S.extra.map((n, i) => '<div class="file"><button class="rm" data-act="rmFile" data-k="extra" data-i="' + i + '" aria-label="Remove ' + esc(n) + '"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button><img src="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 4 3%22%3E%3Crect width=%224%22 height=%223%22 fill=%22%23EDE4D3%22/%3E%3C/svg%3E" alt=""><span>' + esc(n) + '</span></div>').join('') + '</div>' +
    '<div class="row"><button class="btn small" data-act="add">Add files</button><input id="add" type="file" multiple accept="image/*,.pdf" hidden><span class="status">or drag them here</span></div>' +
    '<div class="row"><button class="link" data-act="addBrief">Brief or concept note? Add it here (optional)</button>' + briefs().map((n, i) => '<span class="chip sun">BRIEF · ' + esc(n) + ' <button class="link" data-act="rmFile" data-k="brief" data-i="' + i + '" aria-label="Remove ' + esc(n) + '">✕</button></span>').join('') + '</div></section>' +
    '<div class="row"><button class="btn primary" data-act="toQ">Next</button><span class="status">No account needed.</span></div></main>';

  /* One screen per step of the path: a tap question, the typed title-block card, or the optional concept box (D80, D82). */
  /* shows the corrected text under the box when it differs from what was typed */
  const onSheet = (f, v) => '<p class="hint fixed" id="fixed" style="margin:0">' + (tidy(f, v) && tidy(f, v) !== String(v || '').trim() ? 'On the sheet: <b>' + esc(tidy(f, v)) + '</b>' : '') + '</p>';
  V.q = () => {
    QB.proud.o = proudOpts();
    const pth = path(), n = pth.length, k = curKey(), last = S.q === n;
    const head = '<main class="wrap narrow"><div class="qtop"><button class="round" data-act="qback" aria-label="Back"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>' +
      '<div class="bar" role="progressbar" aria-valuemin="0" aria-valuemax="' + n + '" aria-valuenow="' + S.q + '"><i style="width:' + (S.q / n * 100).toFixed(1) + '%"></i></div><span class="kicker">' + S.q + ' / ' + n + '</span></div>';
    const helper = DEMO ? '<button class="link" data-act="student">Fill in the student’s real answers</button>' : '';
    const other = (ph) => '<div class="field"><label for="other">Other</label><input id="other" class="input' + (ans(k) === 'other' ? ' filled' : '') + '" type="text" maxlength="300" placeholder="' + ph + '" value="' + esc(S.oth[k] || '') + '"></div>';
    const fresh = !DEMO && S.fromHeard && !paid() ? '<p class="hint">Changing an answer makes a fresh preview. You get 2 free previews a day.</p>' : '';
    const next = (label, on) => fresh + '<p class="err" id="qErr" role="alert"></p><div class="row"><button class="btn ' + (on ? 'primary' : '') + '" data-act="qnext">' + (S.fromHeard ? (paid() ? 'Save my answers' : 'Back to preview') : label) + '</button>' + helper + '</div></main>';
    if (CARD[k]) {
      const [f, q, ph] = CARD[k], v = S.card[f] || '', idx = Object.keys(CARD).indexOf(k) + 1;
      const note = f === 'name' ? (unbranded() ? 'Kept off the sheets: this entry is unbranded.' : 'Goes on the sheet exactly as you type it.') : FIXNOTE;
      return head + '<p class="kicker">Title block · ' + idx + ' of 4</p><h1 class="mid">' + esc(q()) + '</h1><p class="lede">' + note + '</p>' +
        '<div class="field"><input id="cardin" data-card="' + f + '" class="input" type="text" required maxlength="' + (f === 'prog' ? 200 : 120) + '" aria-label="' + esc(q()) + '" value="' + esc(v) + '" placeholder="' + esc(ph()) + '">' + onSheet(f, v) + '</div><p class="err" id="cardErr"></p>' +
        next(last ? 'See my preview' : 'Continue', !!v.trim());
    }
    if (k === 'concept') {
      const b = briefs();
      return head + '<p class="kicker">Optional</p><h1 class="mid">Concept?</h1><p class="lede">In a few words. ' + FIXNOTE + '</p>' +
        '<div class="field"><input id="concept" class="input" type="text" maxlength="140" aria-label="Concept" placeholder="e.g. a market that becomes a garden at night" value="' + esc(S.concept || '') + '">' + onSheet('concept', S.concept) +
        '<p class="hint" style="margin:0">' + (b.length ? 'Brief attached: ' + esc(b.join(', ')) + '. AI Studio reads it for text.' : 'Or attach your brief or a concept note in your files. <button class="link" data-act="go" data-s="upload">Go to your files</button>') + '</p></div>' +
        next(conceptLabel(), !!concept());
    }
    const q = qd(k), a = ans(k), locked = k === 'firm' && forcedUnbranded(), sel = locked ? 1 : a;
    const opts = q.thumbs
      ? '<div class="thumbs">' + q.o.map((o, j) => '<button class="thumb' + (sel === j ? ' sel' : '') + '" data-act="pick" data-j="' + j + '" aria-pressed="' + (sel === j) + '"><img src="' + pic(HP, o[2]) + '" alt=""><span>' + esc(o[0]) + '</span></button>').join('') + '</div>'
      : '<div class="opts">' + q.o.map((o, j) => '<button class="opt' + (sel === j ? ' sel' : '') + '" data-act="pick" data-j="' + j + '" aria-pressed="' + (sel === j) + '"' + (locked ? ' disabled' : '') + '><b class="ico">' + ico(o[0]) + '</b>' + esc(o[0]) + '</button>').join('') + '</div>';
    return head + '<p class="kicker">' + esc(q.k) + '</p><h1 class="mid">' + esc(q.q) + '</h1><p class="lede">' + esc(q.sub) + '</p>' + opts +
      (locked ? '<p class="hint">Competition entries stay unbranded. To put your firm on the sheet, change where it will be shown.</p>' : other('Say it your way')) +
      next(last ? 'See my preview' : a !== null || locked ? 'Continue' : 'Skip this one', a !== null || locked);
  };


  const backbar = (items) => '<nav class="backbar" aria-label="Go back">' + items.map(([t, sc]) => '<button class="link" data-act="go" data-s="' + sc + '">' + t + '</button>').join('') + '</nav>';
  V.heard = () => { const ks = path().filter((k) => QB[k]);
    return '<main class="wrap">' + backbar([['← Back to the questions', 'q'], ['Add or remove drawings', 'upload']]) + '<span class="chip sun" style="align-self:flex-start">ALL ' + nFiles() + ' DRAWINGS CLEANED</span><h1 class="big">Here’s what we heard</h1>' +
    '<p class="lede">Each answer, turned into what AI Studio will do. Tap a line to change it.</p><div class="heard">' +
    ks.map((k) => '<button data-act="editq" data-k="' + k + '"><small>Q' + (path().indexOf(k) + 1) + ' · ' + esc(QB[k].k.toUpperCase()) + ' · you said ' + esc(said(k)) + '</small><strong>' + esc(heard(k, 'AI Studio decides')) + '</strong></button>').join('') +
    '</div><div class="row"><button class="btn primary" data-act="toPlan">See my preview</button></div></main>'; };

  /* A 3-4 word job for each slide, so the flow is clear in the plan. */
  function slideRole(s) {
    const sec = s.texts.find((x) => x.name === 'section'), meta = (Q().slideMeta || {})[s.n];
    const lab = meta ? (meta.role + ' ' + meta.label).toUpperCase() : sec ? sec.paras.map((p) => p.runs.map((r) => r.t).join('')).join(' ').toUpperCase() : '';
    const order = Q().slideOrder, last = order[order.length - 1];
    if (s.n === order[0]) return 'Your first impression';
    if (s.texts.some((x) => x.name === 'contents')) return 'Shows the running order';
    if (s.n === last && !sec) return 'Ends on your ideas';
    if (!sec) return 'Lets the view speak';
    const R = [['INTENT', 'States the brief, ideas'], ['BRIEF', 'States the brief, ideas'], ['SETTING', 'Places it on site'], ['SITE', 'Places it on site'], ['CONTEXT', 'Places it on site'],
      ['PROCESS', 'Shows how it began'], ['CONCEPT', 'Explains the core idea'], ['MODEL', 'Shows the form evolving'], ['FORM', 'Shows the form evolving'], ['PLAN', 'Walks through the plan'],
      ['SECTION', 'Cuts through the building'], ['ELEVATION', 'Shows the faces'], ['STRUCTURE', 'Explains how it stands'], ['AXONOMETRIC', 'Shows how it fits together'], ['DIAGRAM', 'Shows life inside'], ['PRECEDENT', 'Shows what inspired you'], ['RENDER', 'Lets the view speak'], ['VIEW', 'Lets the view speak'], ['DETAIL', 'Zooms into the details'], ['IDEA', 'Explains the core idea']];
    const hit = R.find(([k]) => lab.includes(k));
    return hit ? hit[1] : 'Adds to the story';
  }
  function slideTitle(s) {
    const t = s.texts.find((x) => x.name === 'headline') || s.texts.find((x) => x.name === 'title');
    if (t) return t.paras[0].runs.map((r) => r.t).join('');
    const c = s.slots[0] && s.contents[s.slots[0].content];
    return c && c.cap ? c.cap[0].runs[0].t + ' (full picture)' : 'Slide ' + s.n;
  }
  V.plan = () => {
    const M = Q();
    if (!M) return '<main class="wrap narrow"><p class="kicker">Step 3 · free</p><h1 class="mid">Opening your preview…</h1></main>';
    const on = M.ideas.filter((i) => i.on).length, minOn = DEMO ? 1 : 2;
    const ideas = M.ideas.map((idea, i) => {
      const pos = M.ideas.slice(0, i + 1).filter((x) => x.on).length;
      const alts = S.swapOpen === i ? '<div class="alts"><p class="kicker">Swap for another idea from your files</p>' + M.altIdeas.map((al, j) =>
        '<div class="item"><div class="txt"><strong>' + esc(al.title) + '</strong><span>' + esc(al.text) + '</span><span class="tag">' + esc(al.why) + '</span></div><div class="ctl"><button data-act="useAlt" data-i="' + i + '" data-j="' + j + '">Use this</button></div></div>').join('') + '</div>' : '';
      return '<div class="item' + (idea.on ? '' : ' off') + '"><span class="num">' + (idea.on ? pos : '–') + '</span><div class="txt"><strong>' + esc(idea.title) + '</strong><span>' + esc(idea.text) + '</span></div><div class="ctl">' +
        '<button data-act="ideaUp" data-i="' + i + '" aria-label="Move up"' + (i === 0 ? ' disabled' : '') + '>↑</button><button data-act="ideaDown" data-i="' + i + '" aria-label="Move down"' + (i === M.ideas.length - 1 ? ' disabled' : '') + '>↓</button>' +
        (M.altIdeas.length ? '<button data-act="ideaSwap" data-i="' + i + '">Swap</button>' : '') + '<button data-act="ideaOn" data-i="' + i + '"' + (idea.on && on <= minOn ? ' disabled title="Keep at least ' + minOn + ' ideas"' : '') + '>' + (idea.on ? 'Turn off' : 'Turn on') + '</button></div></div>' + alts;
    }).join('');
    const slides = pvList();
    const hero = ans('proud') !== null && ans('proud') !== 'other' ? QB.proud.o[ans('proud')][0].toLowerCase() : 'your strongest view';
    const tags = [['Hero: ' + hero, 'proud']].concat(isPro() ? [[heard('room', 'Voice: AI Studio decides'), 'room'], [heard('stage', 'Renders: AI Studio decides'), 'stage']] : [[heard('crit', 'Fix first: AI Studio checks the weakest part'), 'crit'], [heard('word', 'Balanced emphasis'), 'word']])
      .concat([[heard('words', 'Captions plus 3 key ideas'), 'words'], [heard('proc', 'Process: AI Studio decides'), 'proc']])
      .map(([t, k]) => '<div class="pcard"><img src="' + pic(HP, planImg(k)) + '" alt=""><div class="pbody"><b>' + esc(t) + '</b><span class="tag">' + (ans(k) === null ? 'AI Studio’s pick' : 'Because you said: ' + esc(said(k))) + '</span></div></div>').join('');
    const cline = concept() ? '<section class="cline card"><p class="kicker">Your concept</p><p class="ctext">' + esc(concept()) + '</p><div class="row"><span class="tag">Your words, spelling checked</span><button class="link" data-act="editq" data-k="concept">Change</button></div></section>'
      : '<p class="hint">No concept typed' + (briefs().length ? ': AI Studio takes it from your brief.' : ': AI Studio plans the story from your drawings.') + ' <button class="link" data-act="editq" data-k="concept">Add your concept</button></p>';
    /* first view: the composition preview with the order card; payment stays on the next page */
    const deal = previewPanel();
    const notes = DEMO ? '' : '<p class="status" id="planSaved" aria-live="polite">' + esc(planSaved) + '</p>' + (S.planNotes && S.planNotes.length ? '<div class="card"><p class="kicker">Notes from AI Studio</p>' + S.planNotes.map((x) => '<p class="hint" style="margin:4px 0 0">' + esc(x) + '</p>').join('') + '</div>' : '');
    const stale = !DEMO && ST && ST.preview && ST.preview.stale ? '<div class="card stale" role="status"><p class="lede" style="color:var(--on-accent)"><b>We’ve improved Studio since this preview.</b> Refresh it (free): it doesn’t count towards your 2 free previews.</p><div class="row"><button class="btn primary" data-act="preview">Refresh my preview</button></div></div>' : '';
    return '<main class="wrap pvwrap">' + backbar([['← Change your answers', 'q'], ['Add or remove drawings', 'upload']]) + (DEMO ? '' : '<div class="row" style="margin-top:-6px">' + newJobLink() + '</div>') + stale + deal + '<h2 class="mid" style="margin-top:28px">Change anything first</h2><p class="lede">Built from your answers and your drawings. Move, swap or remove anything until it tells your project the way you would at the pin-up.</p>' + cline +
      '<div class="pcards">' + tags + '</div>' + notes + '<div class="two"><div class="list"><h2 class="mid">The three ideas</h2><p class="lede">The spine of your board and deck. Reorder, swap or turn one off; the board preview updates as you go.</p>' + ideas +
      '<h2 class="mid" style="margin-top:18px">The jury deck</h2><p class="lede">' + pvOn().length + ' slides, in the order a jury reads them. Move one or leave it out; the cover stays first.</p>' + slides + '</div>' +
      '<aside class="list" style="position:sticky;top:90px"><p class="kicker">Your A1 board</p>' + compBoard() +
      '<button class="btn shiny small-shiny" data-act="toPrice">' + SPARK + '<span class="cta"><b>Make it now</b><small>Board + deck · from $11</small></span><span class="arrow" aria-hidden="true">→</span></button></aside></div></main>';
  };

  /* Pay page (owner comments, 28 Oct): Transform selected until the student changes it; the landing's taped
     before/after instead of a blurred board; a clear "Write your email" label; the Pay button floats at the bottom. */
  V.price = () => {
    const t = S.tier || 'great';
    const card = (id, name, price, items) => '<button class="tier' + (t === id ? ' sel' : '') + '" data-act="tier" data-t="' + id + '" aria-pressed="' + (t === id) + '"><span class="kicker">' + name + '</span><span class="price">$' + price + '</span><ul>' + items.map((x) => '<li>' + x + '</li>').join('') + '</ul></button>';
    const note = S.payNote === 'cancelled' ? '<div class="card"><p class="kicker">Payment cancelled</p><p class="lede">Nothing was charged. Pick your finish and try again when you are ready.</p></div>'
      : S.payNote === 'unconfirmed' ? '<div class="card"><p class="kicker">Payment not confirmed yet</p><p class="lede">If you paid, it can take a minute: we email your receipt as soon as it is confirmed. If you cancelled, nothing was charged.</p><div class="row"><button class="btn small" data-act="recheck">Check again</button></div></div>' : '';
    return '<main class="wrap narrow paywrap">' + backbar([['← Back to your preview', 'plan'], ['Change your answers', 'q'], ['Add or remove drawings', 'upload']]) + note + '<p class="kicker">Step 4</p><h1 class="big">Pick your finish</h1><p class="lede">Both give you the A1 board and the jury deck, as PDF and PowerPoint, with an editor to fix anything. Pay once. No subscription.</p>' +
      '<div class="tiers">' + card('nice', ...TIERS.nice) + card('great', ...TIERS.great) + '</div>' +
      '<section class="paywow"><p class="kicker">What AI Studio does</p>' + heroArt() + '</section>' +
      '<div class="field"><label for="email" class="biglabel">Write your email</label><p class="hint" style="margin:0 0 6px">For your receipt and a link back to your files.</p><input id="email" class="input" type="email" autocomplete="email" placeholder="you@school.edu" value="' + esc(S.email) + '"></div><p class="err" id="emailErr" role="alert"></p>' +
      '<div class="ctabar paybar"><div><b>' + TIERS[t][0] + ' · board + deck</b><span>$' + TIERS[t][1] + ' · one payment, no subscription</span></div>' +
      '<button class="btn primary" data-act="pay" id="payBtn">Pay $' + TIERS[t][1] + '</button></div>' +
      '<p class="hint"><b>No refunds. One free redo within 7 days.</b> ' + LEGALLINKS + '</p>' +
      (DEMO ? '<p class="status">Demo: no card and no charge. The live app opens the Dodo Payments checkout here.</p>' : '<p class="status">Secure checkout by Dodo Payments, shown in your currency.</p>') + '</main>';
  };

  const isGreat = () => (S.tier || 'great') === 'great';
  const MAKE = () => ['Drawings cleaned and placed on the grid', 'Plan, section and site set to scale, scale bars and north drawn']
    .concat(isGreat() ? ['Re-rendering the entrance view', 'Redrawing the plan and section: tones, shadows, trees', 'Drawing new diagrams in the same family'] : ['Polishing your drawings, with 1–4 AI re-renders'])
    .concat(['Writing the story and captions from your answers', 'Checking every sentence against your sheets', 'Laying out the A1 board', 'Building the ' + F.visibleSlides(P).length + '-slide jury deck']);
  /* live: the build's own stages (server/core/progress.py BUILD_STAGES), ticked off as the status reports them */
  /* The step list follows the server's own stage (owner's test note 2). The running step carries a moving bar and the
     time it has been running (the server's step_elapsed_s when it sends one, else counted here from when this page
     first saw the step), so it never looks stuck; a step not yet started shows "Waiting to start". */
  const mmss = (s) => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
  let clk = { key: null, base: 0, at: 0 };
  function clockFrom(st) {
    const key = (st.stage || '') + '|' + (st.step || '') + '|' + ((st.preview || {}).status || '') + '|' + ((st.build || {}).status || ''), now = Date.now();
    if (typeof st.step_elapsed_s === 'number') clk = { key, base: st.step_elapsed_s, at: now };
    else if (key !== clk.key) clk = { key, base: 0, at: now };
  }
  const clockNow = () => clk.base + (Date.now() - clk.at) / 1000;
  setInterval(() => { const el = document.getElementById('mkt'); if (el) el.textContent = mmss(clockNow()); const tt = document.getElementById('mktt'); if (tt && typeof (ST || {}).elapsed_s === 'number') tt.textContent = mmss(ST.elapsed_s + (Date.now() - clk.got) / 1000) + ' SO FAR'; }, 1000);
  function stepList(labels, at, running) {
    return labels.map((m, i) => {
      const s = !running ? (i === 0 ? 'now' : 'todo') : i < at ? 'done' : i === at ? 'now' : 'todo';
      return '<div class="mk ' + s + '"><i aria-hidden="true">' + (s === 'done' ? '✓' : '') + '</i>' + esc(!running && i === 0 ? 'Waiting to start' : m) +
        (s === 'now' ? '<span class="mkt" id="mkt" aria-label="Time on this step">' + mmss(clockNow()) + '</span>' : '') + '</div>';
    }).join('');
  }
  const totalChip = () => typeof (ST || {}).elapsed_s === 'number' ? '<span class="chip" id="mktt">' + mmss(ST.elapsed_s) + ' SO FAR</span>' : '';
  const BUILD = ['Reading your files', 'Finding every drawing', 'Reading your concept', 'Planning the story', 'Making the pictures', 'Labelling the drawings',
    'Laying out the board and deck', 'Filling every slot', 'Building the files', 'Final checks'];
  V.makingLive = () => {
    const st = ST || {}, b = st.build || {}, g = (st.tier || S.tier) === 'great', mail = esc(st.email || S.email || 'you');
    if (!st.paid) return '<main class="wrap narrow"><p class="kicker">Step 4</p><h1 class="big">Confirming your payment</h1><div class="making"><div class="mk now"><i aria-hidden="true"></i>Waiting for Dodo Payments to confirm</div></div>' +
      '<p class="lede">This usually takes a few seconds. Keep this page open; it moves on by itself.</p></main>';
    if (st.stage === 'failed') return '<main class="wrap narrow"><p class="kicker">Paid · receipt sent to ' + mail + '</p><h1 class="big">Something went wrong on our side</h1>' +
      '<div class="card"><p class="lede">We are rerunning it for free. You will get an email at <b>' + mail + '</b> as soon as your board and deck are ready, with a link back here.</p></div>' +
      '<p class="hint">Nothing to do on your side. Questions: hello@findgreatarchitecture.com</p></main>';
    const at = stepAt(BUILD_KEYS, BUILD, b.stage || st.step_key, b.label || st.step), held = b.status === 'held';
    return '<main class="wrap narrow"><p class="kicker">Paid · receipt sent to ' + mail + '</p><h1 class="big">Making your board and deck</h1>' +
      '<div class="row"><span class="chip ink">' + (g ? 'TRANSFORM · ABOUT 5 MINUTES' : 'POLISH · UNDER 10 MINUTES') + '</span><span class="chip">' + (held || b.status === 'queued' || b.status === 'none' ? 'IN THE QUEUE' : 'STEP ' + (at + 1) + ' OF ' + BUILD.length) + '</span>' + (typeof st.progress === 'number' ? '<span class="chip">' + st.progress + '%</span>' : '') + totalChip() + '</div>' +
      (held ? '<div class="card"><p class="lede">It is a busy day, so your build waits in a short queue. We will email you when it starts and when it is ready.</p></div>' : '') +
      '<div class="making" id="mk">' + stepList(BUILD, at, b.status === 'running') + '</div>' +
      '<p class="lede">You can close this tab. We will email <b>' + mail + '</b> when it is ready, with a link back to your board.</p></main>';
  };
  /* live: the free preview being planned (server/core/progress.py PREVIEW_STAGES), or why it stopped */
  const PLANS = ['Reading your files', 'Finding every drawing', 'Reading your concept', 'Planning the story', 'Laying out your board and deck'];
  /* the server's step keys (server/README.md, "Progress"); the label is the fallback for an older server */
  const PLAN_KEYS = ['ingest', 'read_sheets', 'concept', 'story', 'composition'];
  const BUILD_KEYS = ['ingest', 'read_sheets', 'concept', 'story', 'pictures', 'labels', 'layout', 'fill_slots', 'build', 'checks'];
  const stepAt = (keys, labels, key, label) => Math.max(0, keys.indexOf(key) >= 0 ? keys.indexOf(key) : labels.indexOf(label));
  V.planning = () => {
    const st = ST || {}, pv = st.preview || {}, back = backbar([['← Change your answers', 'q'], ['Add or remove drawings', 'upload']]);
    if (S.limit) return '<main class="wrap narrow">' + back + '<p class="kicker">Step 3 · free</p><h1 class="big">That’s today’s free previews</h1>' +
      '<div class="card"><p class="lede">You get 2 free previews a day, and today’s are used. Your drawings and answers are saved, so come back tomorrow and press the button below.</p></div>' +
      '<div class="row"><button class="btn primary" data-act="preview">Make my preview</button></div></main>';
    if (S.pvErr || pv.status === 'failed') return '<main class="wrap narrow">' + back + '<p class="kicker">Step 3 · free</p><h1 class="big">The preview didn’t work this time</h1>' +
      '<div class="card"><p class="lede">' + esc(S.pvErr || pv.error || 'The preview could not be made this time. Try again in a minute.') + '</p></div>' +
      '<div class="row"><button class="btn primary" data-act="preview">Try again</button><button class="btn" data-act="go" data-s="upload">Add or change drawings</button></div></main>';
    const at = stepAt(PLAN_KEYS, PLANS, pv.stage || st.step_key, pv.label || st.step), running = pv.status === 'running';
    return '<main class="wrap narrow"><p class="kicker">Step 3 · free</p><h1 class="big">Planning your board and deck</h1>' +
      '<div class="row"><span class="chip ink">FREE PREVIEW</span><span class="chip">' + (running ? 'STEP ' + (at + 1) + ' OF ' + PLANS.length : 'STARTING') + '</span>' + totalChip() + '</div>' +
      '<div class="making" id="mk">' + stepList(PLANS, at, running) + '</div>' +
      '<p class="lede">AI Studio is reading every sheet and planning the story from your answers. It opens here by itself, usually in a minute or two.</p></main>';
  };
  V.making = () => {
    if (!DEMO) return V.makingLive();
    const g = isGreat(), n = MAKE().length, k = Math.min(S.mk || 0, n - 1) + 1;
    return '<main class="wrap narrow"><p class="kicker">Paid · receipt sent to ' + esc(S.email || 'your email') + '</p><h1 class="big">Making your board and deck</h1>' +
      '<div class="row"><span class="chip ink">' + (g ? 'TRANSFORM · ABOUT 5 MINUTES' : 'POLISH · UNDER 10 MINUTES') + '</span><span class="chip">STEP ' + k + ' OF ' + n + '</span><span class="chip sun">DEMO: SPED UP</span></div>' +
      '<div class="making" id="mk">' + MAKE().map((m, i) => '<div class="mk ' + (i < S.mk ? 'done' : i === S.mk ? 'now' : 'todo') + '"><i aria-hidden="true">' + (i < S.mk ? '✓' : '') + '</i>' + esc(m) + '</div>').join('') + '</div>' +
      '<p class="lede">' + (g ? 'You can close this tab. We will email <b>' + esc(S.email || 'you') + '</b> when it is ready, with a link back to your board.' : 'You can stay on this page. It opens on its own when it is done.') + '</p>' +
      '<p class="status">In this demo nothing is being generated: the steps are shown sped up.</p><button class="link" data-act="toResult">Skip ahead</button></main>';
  };

  const DID = [['raw/sheet-4.jpg', 'board/hero.jpg', 'Sketch to hero render', 'Your entrance sketch, rendered in light and material.'],
    ['raw/sheet-6.jpg', 'board/plan.jpg', 'Plan, cleaned and coloured', 'Walls in poché, rooms labelled, greenery, north and scale.'],
    ['raw/sheet-5.jpg', 'board/section.jpg', 'Section, redrawn', 'Clear cut, terracotta street, trees for context.'],
    ['raw/sheet-1.jpg', 'board/site.jpg', 'Site map to site plan', 'The garden in colour, the site marked, labels aligned.'],
    ['raw/sheet-3.jpg', 'board/sk1.jpg', 'Sketches, sharpened', 'Paper whitened, charcoal kept, each one captioned.']];
  const date = (iso) => { try { return new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'long' }); } catch (e) { return ''; } };
  let redoArm = false;
  function redoCard() {
    const st = ST || {};
    if (st.redo_available) return '<section class="card"><p class="kicker">One free redo</p><h2 class="mid">Not quite right?</h2><p class="lede">Redo it free, once, until ' + esc(date(st.redo_until)) + '. Change your answers or drawings first if you like; the redo uses them.</p>' +
      '<div class="row"><button class="btn primary" data-act="redoJob">' + (redoArm ? 'Click again to start the redo' : 'Redo it free') + '</button><button class="btn" data-act="redoQ">Change answers</button><button class="btn" data-act="go" data-s="upload">Change drawings</button></div></section>';
    return st.redo_used ? '<p class="hint">Your free redo has been used. Something still wrong? Email hello@findgreatarchitecture.com.</p>' : '';
  }
  const outputsList = () => '<div class="list">' + ((ST || {}).outputs || []).filter((o) => !/layout\.json$/.test(o.name)).map((o) => '<div class="dl"><div class="txt"><strong>' + esc(o.label || o.name) + '</strong><span>' + kb(o.bytes || 0) + '</span></div><a class="btn" href="' + esc(o.url) + '" download>Download</a></div>').join('') + '</div>';
  V.result = () => !P ? V.resultFiles() : '<main class="wrap"><span class="chip lime" style="align-self:flex-start">READY</span><h1 class="big">Your board and deck are ready</h1><p class="lede">Check every word before the jury does. Open the editor to swap pictures, crop them, fix text or switch the text style.</p>' +
    '<div class="result"><div class="list"><p class="rlabel"><b class="chip lime">Board · A1</b> ' + Math.round(P.board.w) + ' × ' + Math.round(P.board.h) + ' mm, portrait</p><div class="ewrap"><div class="sth" data-mini="board" data-w="360"></div><button class="editbtn" data-act="editAt" data-v="board" aria-label="Edit the board">'+'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4l5 5L9 20H4v-5z"/><path d="M13 6l5 5"/></svg>'+'Edit</button></div></div><div class="list"><p class="rlabel"><b class="chip lime">Deck · ' + F.visibleSlides(P).length + ' slides</b> 16:9 widescreen</p><div class="strip">' +
    F.visibleSlides(P).map((s, i) => '<div class="ewrap"><div class="sth" data-mini="slide:' + s.n + '" data-w="150"></div><button class="editbtn" data-act="editAt" data-v="deck" data-n="' + s.n + '" aria-label="Edit slide ' + (i + 1) + '">'+'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4l5 5L9 20H4v-5z"/><path d="M13 6l5 5"/></svg>'+'Edit</button></div>').join('') + '</div>' +
    '<div class="row"><button class="btn shiny dlall2" data-act="dlAll"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg><span class="cta"><span><b>Download all</b></span><small>Board PDF + JPG · Deck PDF + PowerPoint</small></span><span class="arrow" aria-hidden="true">↓</span></button>' +
    '<button class="btn" data-act="toEdit"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4l5 5L9 20H4v-5z"/><path d="M13 6l5 5"/></svg>Open the editor</button></div></div></div>' +
    (DEMO ? '<section class="did"><p class="kicker">Scroll: what AI Studio did with your drawings</p><h2 class="mid">From your sheets to a jury board</h2>' + didCards() +
    '<div class="row"><button class="btn primary big" data-act="toShare">Love it? Rate and share</button></div></section>' : redoCard() + '<div class="row"><button class="btn primary big" data-act="toShare">Love it? Rate and share</button></div>' +
    '<button class="link" data-act="newJob" style="align-self:flex-start">' + (S.newArm ? 'Click again to start a new project (this one stays on your receipt link)' : 'Start a new project') + '</button>') + '</main>';
  /* live, when the editor could not open the build (the files are still there) */
  V.resultFiles = () => '<main class="wrap narrow"><span class="chip lime" style="align-self:flex-start">READY</span><h1 class="big">Your board and deck are ready</h1>' +
    '<p class="lede">' + esc(S.resErr || 'The editor could not open your board on this device, but every file is ready to download.') + '</p><div class="row"><button class="btn small" data-act="reopen">Try the editor again</button></div>' +
    outputsList() + redoCard() + '<div class="row"><button class="btn primary" data-act="toShare">Next: rate and share</button></div></main>';

  const DL = () => [
    ['boardPDF', 'Board · A1 PDF', 'For printing at the pin-up. ' + Math.round(P.board.w) + ' × ' + Math.round(P.board.h) + ' mm.'],
    ['boardJPG', 'Board · A1 picture (JPG)', 'For Instagram, WhatsApp or a quick look.'],
    ['deckPDF', 'Jury deck · PDF', F.visibleSlides(P).length + ' slides, 16:9.'],
    ['deckPPTX', 'Jury deck · PowerPoint', 'Every word stays editable. Fonts are named, not embedded.']
  ];
  V.files = () => !P ? V.resultFiles() : '<main class="wrap narrow"><p class="kicker">Step 6</p><h1 class="big">Download</h1><p class="lede">These include every edit you made, in text style ' + P.ts + ' · ' + F.TS[P.ts].name + '.</p><div class="list">' +
    DL().map((d) => '<div class="dl"><div class="txt"><strong>' + d[1] + '</strong><span>' + d[2] + '</span><span class="status" id="st-' + d[0] + '"></span></div><button class="btn" data-act="exp" data-k="' + d[0] + '">Download</button></div>').join('') +
    '</div><p class="status">The PDF and JPG with your edits are high-resolution pictures of each sheet.' + (DEMO ? ' The live app also gives the sharp vector originals.' : ' The originals below are sharp vector files.') + '</p>' +
    (DEMO ? '' : '<h2 class="mid">As AI Studio first made them</h2><p class="lede">Before your edits, straight from the layout engine.</p>' + outputsList()) +
    exportExtras() + '<div class="row"><button class="btn primary" data-act="toShare">Next: rate and share</button><button class="btn" data-act="toEdit">Back to the editor</button></div></main>';


  function exportExtras() {
    const fonts = P.ts === 'C' ? 'Archivo Narrow, IBM Plex Sans and IBM Plex Mono' : 'Inter and Inter Tight';
    const idml = ((ST || {}).outputs || []).find((o) => /^indesign\//.test(o.name));
    return '<h2 class="mid">More ways to open it</h2><div class="list">' +
      '<div class="dl"><span class="fmt">IDML</span><div class="txt"><strong>Board · InDesign</strong><span>An .idml file: opens in InDesign with every frame editable.</span>' + (idml ? '' : '<span class="status">' + (DEMO ? 'In the live app. This demo makes PDF, JPG and PowerPoint.' : 'Not part of this build.') + '</span>') + '</div>' +
      (idml ? '<a class="btn" href="' + esc(idml.url) + '" download>Download</a>' : '<button class="btn" disabled>Download</button>') + '</div>' +
      '<div class="dl"><span class="fmt">CANVA</span><div class="txt"><strong>Open in Canva</strong><span>Download the PowerPoint, then in Canva choose Upload, then Import. Text stays editable.</span></div><button class="btn" data-act="exp" data-k="deckPPTX">Get the PowerPoint</button></div>' +
      '<div class="dl"><span class="fmt">FONTS</span><div class="txt"><strong>Using PowerPoint or Keynote?</strong><span>Install the free fonts first, or they get swapped: ' + fonts + ' (Google Fonts). Google Slides and the PDF need nothing.</span></div><a class="btn" href="https://fonts.google.com" target="_blank" rel="noopener">Google Fonts</a></div></div>' +
      '<div class="card"><h3 class="h3">Printing the A1 at a shop</h3><ul class="tips"><li>Send the PDF, not the PowerPoint.</li><li>Ask for 100% scale, no “fit to page”.</li><li>Matt paper, 120–170 gsm, keeps drawings crisp.</li></ul></div>';
  }

  /* Step 7: rate and share. Ask at the happiest moment (just after the files are saved).
     4-5 stars: ask for a share and a testimonial (no referral reward, D79). 1-3 stars: ask privately what to fix, no share prompt. */
  V.share = () => {
    const r = S.rate || 0, code = 'FRIEND-' + (P.short || 'STUDIO').replace(/[^A-Za-z]/g, '').slice(0, 6).toUpperCase();
    const link = 'findgreatarchitecture.com/studio';
    const stars = [1, 2, 3, 4, 5].map((n) => '<button class="star' + (n <= r ? ' on' : '') + '" data-act="rate" data-r="' + n + '" aria-label="' + n + ' star' + (n > 1 ? 's' : '') + '" aria-pressed="' + (n === r) + '"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/></svg></button>').join('');
    let body = '';
    if (r && r <= 3) {
      body = S.fbSent
        ? '<div class="card"><h2 class="mid">Thank you</h2><p class="lede">We read every note. You will hear back by email, and your next redo is on us.</p></div>'
        : '<div class="card"><h2 class="mid">What should we fix?</h2><p class="lede">Only we see this. One line is enough.</p><div class="field"><label for="fb">Your note</label><textarea id="fb" class="input" rows="3" placeholder="The plan came out too small…"></textarea></div><div class="row"><button class="btn primary" data-act="sendFb">Send to the team</button></div></div>';
    } else if (r >= 4) {
      const first = drawings().find((f) => THUMBS[f.name]);
      const before = DEMO ? (P.raw && P.raw[0] ? '<img src="' + P.base + P.raw[0].src + '" alt="Before: the original sheet">' : '') : first ? '<img src="' + THUMBS[first.name] + '" alt="Before: your original sheet">' : '';
      body =
        '<div class="sharecard"><div class="ba"><figure>' + before + '<figcaption>Before</figcaption></figure><figure><div class="sth" data-mini="board" data-w="200"></div><figcaption>After · Studio FGA</figcaption></figure></div>' +
        '<div class="sharetxt"><h2 class="mid">Show your friends</h2><p class="lede">Post your before and after. Tag <b>@findgreatarchitecture</b> and we may feature your board.</p>' +
        '<div class="row"><a class="btn primary" href="https://wa.me/?text=' + encodeURIComponent('Made my jury board with Studio FGA: ' + link) + '" target="_blank" rel="noopener">Send on WhatsApp</a>' +
        '<button class="btn" data-act="copyTxt" data-t="' + link + '" data-f="lnk">Copy link</button></div><input id="lnk" class="input" readonly value="' + link + '"></div></div>' +
        '<div class="sharetwo"><div class="card"><h2 class="mid">Can we feature your board?</h2><p class="lede">On @findgreatarchitecture, with your name. Only if you say yes.</p><div class="row"><button class="btn' + (S.feature === true ? ' primary' : '') + '" data-act="feature" data-v="yes">Yes, feature it</button><button class="btn' + (S.feature === false ? ' primary' : '') + '" data-act="feature" data-v="no">Not now</button></div></div></div>';
    }
    return '<main class="wrap narrow"><span class="chip lime" style="align-self:flex-start">YOU MADE IT</span><h1 class="big">How did Studio do?</h1><p class="lede">One tap. It helps us make the next board better.</p><div class="stars" role="group" aria-label="Rating">' + stars + '</div>' + body + '</main>';
  };
  V.edit = () => '<div class="ed" id="ed"><div class="edbar"><button class="btn small" data-act="toResult" aria-label="Back to results">←</button>' +
    '<div class="seg" role="group" aria-label="Sheet"><button data-act="view" data-v="board" class="' + (S.edView !== 'deck' ? 'on' : '') + '">Board</button><button data-act="view" data-v="deck" class="' + (S.edView === 'deck' ? 'on' : '') + '">Deck</button></div>' +
    '<div class="seg" role="group" aria-label="History"><button data-act="undo" id="undo" title="Undo (Ctrl or Cmd + Z)" aria-label="Undo">↶<span class="hide-phone"> Undo</span></button><button data-act="redo" id="redo" title="Redo (Shift + Ctrl or Cmd + Z)" aria-label="Redo">↷<span class="hide-phone"> Redo</span></button></div>' +
    '<div class="seg" role="group" aria-label="Text style"><button data-act="ts" data-v="A" class="' + (P.ts === 'A' ? 'on' : '') + '">A<span class="hide-phone"> · Swiss Bold</span></button><button data-act="ts" data-v="C" class="' + (P.ts === 'C' ? 'on' : '') + '">C<span class="hide-phone"> · Drawing Sheet</span></button></div>' +
    '<div class="seg hide-phone" role="group" aria-label="View zoom"><button data-act="vz" data-v="-1" aria-label="Zoom out">−</button><button data-act="vz" data-v="0">Fit</button><button data-act="vz" data-v="1" aria-label="Zoom in">+</button></div>' +
    '<span class="spacer"></span><span class="saved hide-phone" id="saved">Saved on this device</span><button class="btn small dlall" data-act="dlAll" id="dlall"><span>Download all</span><small>Board PDF + JPG · Deck PDF + PowerPoint</small></button></div>' +
    '<div class="edbody ' + (S.edView === 'deck' ? 'deck' : 'board') + '"><nav class="rail" id="rail" aria-label="Slides"></nav><div class="viewport" id="vp"></div><aside class="panel" id="panel" aria-label="Edit panel"></aside></div></div>';

  /* ---------------------------------------------------------- landing page: findgreatarchitecture.com/studio */
  function lnav() {
    return '<header class="top lnav"><a class="logo" href="#home" data-act="home"><i aria-hidden="true">✦</i>Studio FGA</a><nav class="llinks hide-phone" aria-label="Page">' +
      [['how', 'How it works'], ['get', 'What you get'], ['pricing', 'Pricing'], ['faq', 'Questions']].map(([id, t]) => '<a href="#' + id + '" data-act="sec" data-id="' + id + '">' + t + '</a>').join('') + '</nav><span class="spacer"></span>' +
      '<button class="btn small on" data-act="start">Start free</button></header>';
  }
  const PH = (t) => '<span class="ph">[' + t + ']</span>';
  /* Hero before/after (prototype commit 3ed209a, option B, owner picked 28 Oct): six small crops of the student's real
     sheets (three rough: sketches and a model photo; three decent: plan, section, site map) -> green arrow -> the
     finished A1 board. Crops are CSS windows on the original files: [file, x0, y0, x1, y1 as fractions, label, rough]. */
  const RAWSZ = { 'raw/sheet-1.jpg': [900, 609], 'raw/sheet-3.jpg': [900, 503], 'raw/sheet-5.jpg': [900, 611], 'raw/sheet-6.jpg': [806, 576] };
  const CROPS = [['raw/sheet-6.jpg', 0, 0, 1, 1, 'Plan', 0], ['raw/sheet-3.jpg', .228, .036, .474, .338, 'Sketch', 1], ['raw/sheet-5.jpg', .10, .03, .75, .52, 'Section', 0],
    ['raw/sheet-3.jpg', .609, .507, .987, .740, 'Model photo', 1], ['raw/sheet-1.jpg', .15, .225, .578, .97, 'Site map', 0], ['raw/sheet-3.jpg', .609, .258, .987, .497, 'Elevation sketch', 1]];
  function cropEl([src, x0, y0, x1, y1, lab, rough], i) {
    const [W, H] = RAWSZ[src], w = x1 - x0, h = y1 - y0, bp = (a, span) => span >= 1 ? '0' : (a / (1 - span) * 100).toFixed(2) + '%';
    return '<div class="crop c' + i + (rough ? ' rough' : '') + '" role="img" aria-label="' + lab + ', as uploaded" style="aspect-ratio:' + (w * W / (h * H)).toFixed(3) +
      ';background-image:url(' + HP.base + src + ');background-size:' + (100 / w).toFixed(2) + '% ' + (100 / h).toFixed(2) + '%;background-position:' + bp(x0, w) + ' ' + bp(y0, h) + '"></div>';
  }
  const GARROW = '<svg class="garrow" viewBox="0 0 72 44" aria-hidden="true"><path d="M3 15h40V4l26 18-26 18V29H3z"/></svg>';
  function heroArt() {
    return '<div class="lart" aria-label="Before and after: six rough sketches, photos and drawings become one finished A1 board">' +
      '<div class="before"><div class="crops">' + CROPS.map(cropEl).join('') + '</div><span class="ptag">Before · 6 files</span></div>' +
      '<div class="arrowcol"><span class="atag">✦ AI Studio</span>' + GARROW + '</div>' +
      '<div class="after"><div class="sth" data-mini="board" data-m="h" data-w="480" data-fit="1"></div><span class="ptag lime">After · your A1 board</span></div></div>';
  }
  /* a saved job is offered on the landing, never opened by itself (owner's live test, 28 Oct) */
  const newJobLink = () => '<button class="link" data-act="newJob">' + (S.newArm ? 'Click again: this clears your saved project from this browser' : 'Start a new project') + '</button>';
  const savedJobRow = () => !DEMO && S.job ? '<div class="row savedjob"><button class="chip lime" data-act="resume">Continue your project →</button>' + newJobLink() + '</div>' : '';
  V.home = () => {
    const steps = [['Upload', 'Drop in what you have: plans, sections, sketches, model photos, even screenshots of your sheets. 5 to 10 is best.', 'up'],
      ['Answer a few questions', 'A few quick taps and your concept in a few words.', 'q'],
      ['Preview your board and deck, free', 'See which drawing goes where and what each slide says. Move, swap or remove anything.', 'plan'],
      ['Pay once, then download', 'Your A1 board and jury deck. Fix anything in the editor, then take PDF, PowerPoint or InDesign.', 'dl']];
    const sico = { up: '<path d="M12 16V4M7 9l5-5 5 5M5 20h14"/>', q: '<path d="M9 9a3 3 0 1 1 4 2.8c-.7.3-1 .8-1 1.6M12 17h.01"/><circle cx="12" cy="12" r="9"/>', plan: '<path d="M4 6h16M4 12h10M4 18h7"/><circle cx="19" cy="16" r="3"/>', dl: '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>' };
    const faq = [
      ['What if I don’t like the result?', 'You preview your whole board and deck before you pay. If the result is not right, you get one free redo within 7 days. There are no refunds, so check the preview first. <a class="link" href="refund/">Refund policy</a>'],
      ['Can I keep editing after I download?', 'Yes. Swap pictures, crop them and fix any line in Studio’s editor, then keep going in PowerPoint, Keynote, Google Slides, Canva or InDesign.'],
      ['How many free previews can I make?', 'Two a day. Each one is a full preview of your board and deck.'],
      ['What happens to my files?', 'Your uploads and your finished board and deck are kept for 30 days so you can reopen, edit and redo them, then deleted. We don’t sell your data or use your files to train AI models. <a class="link" href="privacy/">Privacy policy</a>'],
      ['Does it work on my phone?', 'Yes. A laptop is easier for editing a big board, and it is usually where your drawings are.']];
    return '<main class="land">' +
      '<section class="lhero wrap"><div class="lcopy"><p class="kicker">For architecture students and studios · preview free before you pay</p>' +
      '<h1 class="huge">Messy drawings. <span class="hl">Jury-ready board.</span></h1>' +
      '<p class="lede">Upload your plans, sections, sketches and model photos. Answer a few quick questions. AI Studio plans the story, writes the text and sets an A1 board and a matching jury deck that you can still edit.</p>' +
      shiny('start', 'Start free', 'No login · preview free') + savedJobRow() +
      '<div class="row fmts"><span class="chip">A1 board</span><span class="chip">16:9 jury deck</span><span class="chip">PDF · PowerPoint · InDesign</span></div></div>' +
      heroArt() + '</section>' +
      '<section class="wrap opens"><p class="kicker">Opens in</p><div class="row"><span class="chip">PowerPoint</span><span class="chip">Keynote</span><span class="chip">Google Slides</span><span class="chip">Canva</span><span class="chip">InDesign</span></div>' +
      '<p class="status">Sample: a real student’s community centre for the cloth vendors of Law Garden, Ahmedabad, shown with the owner’s permission.</p></section>' +
      '<section class="wrap" id="how"><p class="kicker">How it works</p><h2 class="big">Four steps. The first three are free.</h2><div class="lsteps">' +
      steps.map((t, i) => '<div class="lstep card"><span class="lnum">' + (i + 1) + '</span><svg viewBox="0 0 24 24" aria-hidden="true">' + sico[t[2]] + '</svg><h3 class="h3">' + t[0] + '</h3><p>' + t[1] + '</p></div>').join('') + '</div></section>' +
      '<section class="band"><div class="wrap bandin"><div><h2 class="big">See it before you pay.</h2><p class="lede">Upload, answer a few questions and preview your board and deck for free. Pay only when you want the final files.</p></div>' + shiny('start', 'Start free', 'No login · preview free') + '</div></section>' +
      '<section class="wrap" id="get"><p class="kicker">What you get</p><h2 class="big">Everything a jury expects, done for you</h2><div class="deal deal2">' + sheets(8, '', 'h') +
      '<div class="dealtxt">' + getsList(null, F.visibleSlides(HP).length) + '</div></div></section>' +
      '<section class="wrap" id="examples"><p class="kicker">Before and after</p><h2 class="big">From your sheets to a jury board</h2><p class="lede">Real pairs from the sample project.</p>' + didCards() + '</section>' +
      '<section class="wrap" id="pricing"><p class="kicker">Pricing</p><h2 class="big">Pay once per project. No subscription.</h2><div class="tiers">' +
      ['nice', 'great'].map((k) => '<div class="tier ltier' + (k === 'great' ? ' sel' : '') + '"><span class="kicker">' + TIERS[k][0] + (k === 'great' ? ' · the full treatment' : '') + '</span><span class="price">$' + TIERS[k][1] + '</span><p class="per">A1 board + jury deck</p><ul>' + TIERS[k][2].map((x) => '<li>' + x + '</li>').join('') + '</ul></div>').join('') +
      '</div><p class="lede">Both include the editor and one free redo within 7 days. No refunds. Shown in your currency at checkout. Opens in PowerPoint, Keynote, Google Slides, Canva and InDesign.</p>' + shiny('start', 'Start free', 'Preview free before you pay') + '</section>' +
      '<section class="wrap narrow2" id="faq"><p class="kicker">Questions</p><h2 class="big">Before you start</h2><div class="faq">' +
      faq.map(([q, a]) => '<details><summary>' + q + '</summary><p>' + a + '</p></details>').join('') + '</div></section>' +
      '<section class="band dark"><div class="wrap bandin"><h2 class="big">Your jury is closer than you think.</h2>' + shiny('start', 'Start free', 'No login · preview free') + '</div></section>' +
      lfoot() + '</main>';
  };

  /* the legal pages are real pages (terms/, privacy/, refund/), made from studio/legal/*.md */
  const LEGALLINKS = '<a class="link" href="terms/">Terms</a> · <a class="link" href="privacy/">Privacy</a> · <a class="link" href="refund/">Refund policy</a>';
  const FOOTLINE = 'Studio FGA is run by Akshat Pagaria · 302, Shantinath Residency, Beawar, Rajasthan, India · hello@findgreatarchitecture.com · Payments handled by Dodo Payments, our merchant of record';
  const lfoot = () => '<footer class="lfoot wrap"><a class="logo" href="#home" data-act="home"><i aria-hidden="true">✦</i>Studio FGA</a><p>' + FOOTLINE + '</p><p class="row">' + LEGALLINKS + '</p>' +
    '<p>Part of <a class="link" href="/">Find Great Architecture</a> · findgreatarchitecture.com/studio · @findgreatarchitecture</p>' + (DEMO ? '' : '<a class="link" href="?demo=1#home">Try the demo with a sample project</a>') + '</footer>';

  /* ---------------------------------------------------------- render */
  let ed = null;
  function render() {
    const sc = S.screen;
    document.body.classList.toggle('editing', sc === 'edit');
    document.body.dataset.screen = sc;
    if (sc !== 'edit') ed = null;
    if ((sc === 'edit' && !P) || (sc === 'plan' && !Q())) { S.screen = sc = (sc === 'edit' ? 'result' : 'upload'); }
    app.innerHTML = (sc === 'edit' ? '' : (STEP[sc] === -1) ? lnav() : top()) + V[sc]();
    fillMinis(app);
    if (sc === 'edit') startEditor();
    if (sc === 'making' && DEMO) runMaking();
    if (sc === 'upload') bindDrop();
    if (sc === 'q') { const ci = document.getElementById('cardin'); if (ci) ci.focus(); }
  }
  function fillMinis(root) {
    root.querySelectorAll('[data-mini]').forEach((el) => {
      const M = modelOf(el.dataset.m);
      if (!M) return;
      const [kind, n] = el.dataset.mini.split(':');
      const page = kind === 'board' ? M.board : M.slides.find((s) => s.n === +n);
      if (!page) return;
      el.innerHTML = '';
      const w = el.dataset.fit ? Math.max(+(el.dataset.min || 110), Math.min(+el.dataset.w, (el.parentElement.clientWidth || +el.dataset.w) - 6)) : +el.dataset.w;
      el.appendChild(F.miniSheet(M, page, w));
    });
  }

  /* ---------- making */
  let mkT = null;
  function runMaking() {
    clearTimeout(mkT);
    if (S.mk === undefined || S.mk >= MAKE().length) S.mk = 0;
    mkT = setTimeout(() => {
      if (S.screen !== 'making') return;
      S.mk += 1; saveS();
      if (S.mk >= MAKE().length) { S.mk = 0; go('result'); } else render();
    }, 1100);
  }

  /* ---------- upload */
  function bindDrop() {
    const d = document.getElementById('drop');
    ['dragenter', 'dragover'].forEach((t) => d.addEventListener(t, (e) => { e.preventDefault(); d.classList.add('hot'); }));
    ['dragleave', 'drop'].forEach((t) => d.addEventListener(t, (e) => { e.preventDefault(); d.classList.remove('hot'); }));
    d.addEventListener('drop', (e) => { asBrief = false; addFiles(e.dataTransfer.files); });
    document.getElementById('add').addEventListener('change', (e) => { addFiles(e.target.files); e.target.value = ''; });
  }
  let asBrief = false;
  /* live: check each file here first (type and size, as server/core/uploads.py does), then send them one by one */
  const OKTYPE = /\.(png|jpe?g|webp|pdf)$/i, MAXMB = 25, MAXFILES = 30;
  function upMsg(r, name) {
    const e = (r.data && r.data.error) || '';
    if (r.status === 0) return 'Studio can’t be reached right now. Check your connection and try again.';
    if (r.status === 415) return '“' + name + '” is not a file Studio can read. Use PNG, JPG, WebP or PDF.';
    if (r.status === 413) return /many|at most \d+ files/i.test(e) ? 'That is the most files one project can take (' + MAXFILES + '). Remove some first.' : '“' + name + '” is too large. Files can be up to ' + MAXMB + ' MB each: export it smaller or split it.';
    if (r.status === 409) return 'Your project is being worked on right now. Try again when it finishes.';
    return e ? e.charAt(0).toUpperCase() + e.slice(1) + '.' : 'Something went wrong with “' + name + '”. Try again.';
  }
  async function ensureJob() {
    if (S.job) return true;
    if (!API.ready) { upErr = 'Studio isn’t open yet. Try the demo with a sample project meanwhile.'; render(); return false; }
    const r = await API.create();
    if (!r.ok) { upErr = upMsg(r, ''); render(); return false; }
    S.job = { id: r.data.job_id, t: r.data.token }; saveS();
    return true;
  }
  async function addLive(list, kind) {
    upErr = '';
    /* every file gets its slot at once; the ones that can't go up say why */
    const items = [...list].map((f) => {
      const u = { k: ++upSeq, f, name: f.name, kind, pct: 0, thumb: /^image\/(png|jpeg|webp)$/.test(f.type) ? URL.createObjectURL(f) : null, err: null, retry: false };
      if (!OKTYPE.test(f.name) && !/^(image\/(png|jpeg|webp)|application\/pdf)$/.test(f.type)) u.err = 'Not a file Studio can read. Use PNG, JPG, WebP or PDF.';
      else if (f.size > MAXMB * 1048576) u.err = (f.size / 1048576).toFixed(0) + ' MB: files can be up to ' + MAXMB + ' MB. Export it smaller or split it.';
      else if ((S.files || []).length + upBusy() >= MAXFILES) u.err = 'The most one project can take is ' + MAXFILES + ' files. Remove some first.';
      if (!u.err) u.pct = 0;
      UP.push(u);
      return u;
    });
    render();
    const todo = items.filter((u) => !u.err);
    if (!todo.length) return;
    if (!(await ensureJob())) { todo.forEach((u) => { u.err = upErr || 'Studio can’t be reached right now.'; u.retry = true; }); upErr = ''; render(); return; }
    for (const u of todo) await sendUp(u);
    if (kind === 'brief' && todo.some((u) => !u.err)) toast('Brief added. AI Studio reads it for text, not for the board.');
  }
  async function sendUp(u) {
    u.err = null; u.retry = false; u.pct = 0;
    const r = await API.upload(S.job, u.kind, u.f, (p) => {
      u.pct = p;
      const bar = document.getElementById('up-' + u.k);
      if (bar) { bar.style.width = Math.round(p * 100) + '%'; bar.parentElement.setAttribute('aria-valuenow', Math.round(p * 100)); const t = bar.parentElement.previousElementSibling; if (t) t.textContent = u.name + ' · ' + (p >= 1 ? 'finishing…' : Math.round(p * 100) + '%'); }
    });
    if (r.ok) {
      UP = UP.filter((x) => x !== u);
      S.files = r.data.files || S.files;
      (r.data.added || []).forEach((a) => { if (u.thumb) THUMBS[a.name] = u.thumb; });
      saveS();
    } else {
      u.err = upMsg(r, u.name); u.retry = r.status === 0 || r.status === 409 || r.status >= 500;
      if (r.status === 404) { S.job = null; saveS(); u.retry = true; }
    }
    if (S.screen === 'upload') render();
  }
  function addFiles(list) {
    if (!DEMO) { const k = asBrief ? 'brief' : 'drawing'; asBrief = false; addLive(list, k); return; }
    const b = asBrief; asBrief = false;
    [...list].forEach((f) => { if (b) S.briefs = briefs().concat(f.name); else S.extra.push(f.name); }); saveS(); render();
    toast(b ? 'Brief added. AI Studio reads it for text, not for the board.' : list.length + ' file' + (list.length === 1 ? '' : 's') + ' added. This demo keeps using the sample project.');
  }

  /* ---------------------------------------------------------- editor */
  const NAMES = { title: 'Title', headline: 'Slide title', lead: 'Lead sentence', concept: 'Concept', story: 'The story', ideas: 'The three ideas', idea: 'The ideas', notes: 'Notes', section: 'Section label',
    footer: 'Footer', contents: 'Contents', programme: 'Programme', credits: 'Credits', info: 'Project details', text: 'Text', caption: 'Caption', madewith: 'Footer' };
  function startEditor() {
    const root = document.getElementById('ed');
    ed = new F.Editor(root, {
      getP: () => P,
      setP: (np, label, soft) => setP(np, label, soft),
      onSelect: () => { lastSoft = false; panel(); },
      onLive: (slot, c) => { const z = document.getElementById('zoom'); if (z) z.value = Math.round(c.view.z * 100); },
      onTyping: (over) => { const w = document.getElementById('overwarn'); if (w) w.hidden = !over; }
    });
    ed.view = S.edView === 'deck' ? 'deck' : 'board';
    ed.slideN = S.edSlide || 1;
    ed.render();
    rail(); panel(); bar();
  }
  function rail() {
    const r = document.getElementById('rail');
    if (!r || !ed) return;
    if (ed.view !== 'deck') { r.innerHTML = ''; return; }
    const phone = window.matchMedia('(max-width: 899px)').matches;
    r.innerHTML = F.visibleSlides(P).map((s, i) => '<button data-act="slide" data-n="' + s.n + '" class="' + (s.n === ed.slideN ? 'on' : '') + '" aria-label="Slide ' + (i + 1) + '"><div class="sth" data-mini="slide:' + s.n + '" data-w="' + (phone ? 92 : 142) + '"></div>' + (i + 1) + ' · ' + esc(slideTitle(s).slice(0, 22)) + '</button>').join('');
    fillMinis(r);
  }
  let railT = null;
  function railSoon() {
    clearTimeout(railT);
    railT = setTimeout(() => {
      if (!ed || ed.view !== 'deck') return;
      const el = document.querySelector('#rail [data-mini="slide:' + ed.slideN + '"]');
      if (el) { el.innerHTML = ''; el.appendChild(F.miniSheet(P, P.slides.find((s) => s.n === ed.slideN), +el.dataset.w)); }
    }, 350);
  }
  function bar() {
    const u = document.getElementById('undo'), r = document.getElementById('redo');
    if (u) u.disabled = hi <= 0;
    if (r) r.disabled = hi >= hist.length - 1;
    railSoon();
  }
  let resetArm = false;
  function panel() {
    const el = document.getElementById('panel');
    if (!el || !ed) return;
    const sel = ed.sel, page = ed.page();
    if (window.matchMedia('(max-width: 899px)').matches && !S.panelPinned) el.classList.toggle('min', !sel);
    const phoneMin = '<button class="btn small show-phone" data-act="panelMin" style="align-self:flex-end">' + (el.classList.contains('min') ? 'Show tools' : 'Hide tools') + '</button>';
    let h = '';
    if (!sel) {
      h = '<h3>' + (ed.view === 'board' ? 'Your A1 board' : 'Slide ' + (F.visibleSlides(P).findIndex((s) => s.n === ed.slideN) + 1)) + '</h3>' +
        '<div class="howto"><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 8v8M8 12h8"/></svg><span>Click a picture</span></div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v18M3 12h18M12 3l-3 3M12 3l3 3M12 21l-3-3M12 21l3-3M3 12l3-3M3 12l3 3M21 12l-3-3M21 12l-3 3"/></svg><span>Drag to move</span></div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21M8 10.5h5M10.5 8v5"/></svg><span>Scroll to zoom</span></div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 4L3 8l4 4M3 8h13M17 20l4-4-4-4M21 16H8"/></svg><span>Drop on another to swap</span></div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 6V4h14v2M12 4v16M9 20h6"/></svg><span>Click text twice to type</span></div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/></svg><span>⌘Z undo · autosaves</span></div></div>' +
        '<button class="btn small" data-act="reset">' + (resetArm ? 'Click again to confirm' : 'Undo all my edits') + '</button><p class="hint">Goes back to the board and deck exactly as AI Studio first made them. Your own changes are removed.</p>' +
        '<h4 class="pdl">Download, with your edits</h4><div class="pdlgrid">' +
        [['boardPDF', 'Board · PDF'], ['boardJPG', 'Board · JPG'], ['deckPDF', 'Deck · PDF'], ['deckPPTX', 'Deck · PowerPoint']]
          .map((d) => '<button class="btn small" data-act="exp" data-k="' + d[0] + '"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>' + d[1] + '</button>').join('') +
        '</div><p class="hint">' + [['boardPDF'], ['boardJPG'], ['deckPDF'], ['deckPPTX']].map((d) => '<span class="status" id="st-' + d[0] + '"></span>').join(' ') + '</p>';
    } else if (sel.type === 'slot') {
      const slot = page.slots.find((s) => s.id === sel.slot), c = page.contents[slot.content];
      const others = page.slots.filter((s) => s.id !== slot.id);
      h = '<h3>Picture</h3><p class="tip">' + esc(c.alt || 'Picture') + '</p>' +
        '<div class="field"><label for="zoom">Zoom inside the frame</label><input id="zoom" class="range" type="range" min="100" max="400" step="5" value="' + Math.round(c.view.z * 100) + '"></div>' +
        '<div class="row"><button class="btn small" data-act="fitpic">Fit again</button></div>' +
        '<p class="tip">Drag inside the picture to move the crop. ' + (c.labels.length || c.scales.length ? 'Its labels, scale bar and north move with it.' : '') + '</p>' +
        (others.length ? '<p class="kicker">Swap with a picture on this ' + (page.kind === 'board' ? 'board' : 'slide') + '</p><div class="pick">' + others.map((o) => '<button data-act="swap" data-s="' + o.id + '" aria-label="Swap with ' + esc(page.contents[o.content].alt || 'picture') + '"><img src="' + F.srcOf(P, page.contents[o.content].src) + '" alt=""></button>').join('') + '</div>' : '') +
        '<details><summary class="kicker" style="cursor:pointer;min-height:44px;display:flex;align-items:center">Replace with any drawing from your project</summary><div class="pick">' +
        LIB.map((c2, i) => '<button data-act="lib" data-i="' + i + '" aria-label="Use ' + esc(c2.alt || 'picture') + '"><img src="' + F.srcOf(P, c2.src) + '" alt="" loading="lazy"></button>').join('') + '</div></details>';
    } else if (sel.type === 'label') {
      const slot = page.slots.find((s) => s.id === sel.slot), L = page.contents[slot.content].labels[sel.label];
      h = '<h3>Label on the drawing</h3><div class="field"><label for="labtext">Label text</label><input id="labtext" class="input" type="text" value="' + esc(L.runs.map((r) => r.t).join('')) + '"></div>' +
        '<div class="row"><button class="btn small" data-act="labOff">Hide this label</button></div><p class="tip">Labels sit on straight leaders. Hidden labels come back with “Fit again” on the picture… or with Undo.</p>';
    } else {
      let name = 'Caption', locked = false, over = false;
      if (sel.type !== 'cap') {
        const t = F.derivedTexts(P, page).find((x) => x.id === sel.id);
        name = NAMES[t ? t.name : 'text'] || 'Text';
        locked = !!(t && t.locked);
      }
      const q = sel.type === 'cap' ? '.cap[data-cap="' + sel.slot + '"]' : '.tb[data-text="' + sel.id + '"]';
      const tb = ed.sheet && ed.sheet.querySelector(q);
      over = !!(tb && tb.classList.contains('over'));
      h = '<h3>' + esc(name) + '</h3>' + (locked
        ? '<p class="tip">These lines come from your preview. Reorder, swap or turn off ideas there and both the board and the deck follow.</p><button class="btn small" data-act="toPlan">Open the preview</button>'
        : '<p class="tip">' + (sel.type === 'info' ? 'Click a value to type. Red values are placeholders: replace them before the jury sees the board.' : 'Click the text again to type. Enter finishes, Esc too. Pasted text comes in plain.') + '</p>') +
        '<p class="warn" id="overwarn"' + (over ? '' : ' hidden') + '>Too long for its box. Cut a few words so nothing is hidden.</p>';
    }
    el.innerHTML = phoneMin + h;
    const z = document.getElementById('zoom');
    if (z) {
      z.addEventListener('input', () => { const slot = page.slots.find((s) => s.id === sel.slot); page.contents[slot.content].view.z = z.value / 100; ed.liveSlot(slot); });
      z.addEventListener('change', () => ed.commit('Zoom picture'));
    }
    const lt = document.getElementById('labtext');
    if (lt) {
      lt.addEventListener('input', () => {
        const slot = page.slots.find((s) => s.id === sel.slot), L = page.contents[slot.content].labels[sel.label];
        L.runs = [Object.assign({}, L.runs[0], { t: lt.value })];
        setP(P, 'Edit label', true);
        ed.liveSlot(slot);
        ed.markSel();
      });
      lt.addEventListener('change', () => { lastSoft = false; });
    }
  }

  /* ---------------------------------------------------------- actions */
  const A = {
    home: (el, e) => { e.preventDefault(); go('home'); },
    start: () => {
      if (!DEMO && !API.ready) { location.href = location.pathname + '?demo=1#upload'; return; }
      if (!DEMO && S.job) { S.screen = 'home'; refresh(); return; }   // the job's status picks the screen
      go('upload');
    },
    resume: () => { S.screen = 'home'; refresh(); },
    newJob: () => {
      if (!S.newArm) { S.newArm = true; render(); setTimeout(() => { S.newArm = false; if (['home', 'upload', 'plan', 'result'].includes(S.screen)) render(); }, 4000); return; }
      Object.keys(THUMBS).forEach((k) => delete THUMBS[k]);
      S = freshS(); PV = null; P = null; ST = null; UP = []; upErr = ''; saveS(); go('upload');
    },
    sec: (el, e) => { e.preventDefault(); const away = S.screen !== 'home'; if (away) go('home'); const t = document.getElementById(el.dataset.id); if (t) t.scrollIntoView({ behavior: away ? 'auto' : 'smooth' }); },
    add: () => { asBrief = false; document.getElementById('add').click(); },
    addBrief: () => { asBrief = true; document.getElementById('add').click(); },
    toQ: () => {
      if (!DEMO) {
        const why = upBusy() ? 'Wait a moment: your files are still uploading.' : !drawings().length ? 'Add at least one drawing first.' : '';
        if (why) { upErr = why; const e = document.getElementById('upErr'); if (e) e.textContent = why; return; }
        upErr = '';
      }
      S.q = 1; S.fromHeard = false; go('q');
    },
    pick: (el) => { const k = curKey(), j = +el.dataset.j; S.ans[k] = S.ans[k] === j ? null : j; S.oth[k] = ''; saveS(); render(); },
    qnext: () => {
      const ck = CARD[curKey()];
      if (ck && !(S.card[ck[0]] || '').trim()) { document.getElementById('cardErr').textContent = 'Needed for the title block, so it never shows a blank.'; document.getElementById('cardin').focus(); return; }
      if (S.fromHeard || S.q === path().length) { if (DEMO) { S.fromHeard = false; applyIntake(); go('plan'); } else finishQuestions(); } else { S.q += 1; saveS(); render(); }
    },
    qback: () => { if (S.fromHeard) { S.fromHeard = false; go(paid() ? 'result' : 'plan'); } else if (S.q > 1) { S.q -= 1; saveS(); render(); } else go('upload'); },
    student: () => { studentAnswers(); S.fromHeard = false; S.q = path().indexOf('cname') + 1; saveS(); go('q'); toast(S.card.name ? 'Filled in the student’s real answers.' : 'Filled in the student’s answers. Type any name to test.'); },
    editq: (el) => { S.q = path().indexOf(el.dataset.k) + 1; S.fromHeard = true; go('q'); },
    toPlan: () => go('plan'),
    ideaUp: (el) => { moveIdea(+el.dataset.i, -1); },
    ideaDown: (el) => { moveIdea(+el.dataset.i, 1); },
    ideaSwap: (el) => { const i = +el.dataset.i; S.swapOpen = S.swapOpen === i ? null : i; render(); },
    useAlt: (el) => { const M = Q(), i = +el.dataset.i, j = +el.dataset.j, old = M.ideas[i]; M.ideas[i] = Object.assign({}, M.altIdeas[j], { on: true }); M.altIdeas[j] = Object.assign({ why: 'Your original idea' }, old, { on: true }); S.swapOpen = null; planEdit('Swap idea'); },
    ideaOn: (el) => { const M = Q(), i = +el.dataset.i; M.ideas[i].on = !M.ideas[i].on; planEdit('Idea on/off'); },
    slUp: (el) => moveSlide(+el.dataset.k, -1),
    slDown: (el) => moveSlide(+el.dataset.k, 1),
    slOn: (el) => { const M = Q(), n = +el.dataset.n; M.slideOff = M.slideOff.includes(n) ? M.slideOff.filter((x) => x !== n) : M.slideOff.concat(n); planEdit('Slide on/off'); },
    toPrice: () => go('price'),
    pvShow: (el) => { S.pvShow = el.dataset.v; saveS(); document.querySelectorAll('.comp').forEach((c) => { c.className = 'comp show-' + S.pvShow; });
      document.querySelectorAll('[data-act="pvShow"]').forEach((b) => { b.classList.toggle('on', b.dataset.v === S.pvShow); b.setAttribute('aria-pressed', b.dataset.v === S.pvShow); }); },
    pvTab: (el) => { S.pvTab = el.dataset.v; saveS(); render(); },
    slotInfo: (el) => { S.pvSel = [+el.dataset.p, +el.dataset.i]; saveS(); document.querySelectorAll('.cs.sel').forEach((x) => x.classList.remove('sel')); el.classList.add('sel');
      const box = document.getElementById('slotinfo'); if (box) box.outerHTML = slotInfoHTML(); },
    pvMove: (el) => {
      const ord = pvSlides().map((x) => x.n), k = +el.dataset.k, j = k + +el.dataset.d;
      if (k < 1 || j < 1 || j >= ord.length) return;
      [ord[k], ord[j]] = [ord[j], ord[k]]; S.pvOrder = ord; saveS();
      if (DEMO || !PV) { render(); return; }
      /* the plan's own slides, in the new order (the server notes when the deck keeps the jury order) */
      const seq = pvSlides().map(editOf).filter(Boolean).map((m) => m.n), rest = PV.slideOrder.filter((n) => n !== 0 && !seq.includes(n));
      PV.slideOrder = [0].concat(seq, rest); planEdit('Move slide');
    },
    pvLeave: (el) => {
      const n = +el.dataset.n;
      if (DEMO) { const off = S.pvOff || []; S.pvOff = off.includes(n) ? off.filter((x) => x !== n) : off.concat(n); saveS(); render(); return; }
      const sd = composition().deck.slides.find((x) => x.n === n), m = sd && editOf(sd);
      if (!m) return;
      PV.slideOff = PV.slideOff.includes(m.n) ? PV.slideOff.filter((x) => x !== m.n) : PV.slideOff.concat(m.n); planEdit('Slide on/off');
    },
    tier: (el) => { S.tier = el.dataset.t; saveS(); render(); },
    pay: async (el) => {
      const v = document.getElementById('email').value.trim(), er = document.getElementById('emailErr');
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) {
        /* take the student to the email box so the problem is obvious (owner comment) */
        const m = document.getElementById('email');
        er.textContent = v ? 'That email doesn’t look right. Check it and press Pay again.' : 'Write your email here first, then press Pay.';
        m.classList.remove('needs'); void m.offsetWidth; m.classList.add('needs');
        m.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
        setTimeout(() => m.focus({ preventScroll: true }), 350); return;
      }
      S.email = v; S.tier = S.tier || 'great';
      if (DEMO) { S.mk = 0; go('making'); return; }
      el.disabled = true; el.textContent = 'Opening the secure checkout…';
      await flushPlan();
      const r = await API.checkout(S.job, S.tier, v);
      if (r.ok && r.data.checkout_url) { S.payStarted = Date.now(); S.payNote = null; saveS(); location.href = r.data.checkout_url; return; }
      el.disabled = false; el.textContent = 'Pay $' + TIERS[S.tier || 'great'][1];
      if (r.status === 409 && /already paid/i.test(r.data.error || '')) { await refresh(); return; }
      er.textContent = r.status === 0 ? 'Studio can’t be reached right now. Check your connection and try again.'
        : r.status === 409 ? 'Your preview needs to finish first. ' + (r.data.error || '') : r.status === 503 ? 'Payments are not open yet. Please try again later.' : (r.data.error || 'The checkout could not be opened. Try again in a minute.');
    },
    toResult: () => { clearTimeout(mkT); go('result'); },
    preview: () => startPreview(),
    recheck: () => refresh(),
    reopen: async () => { S.resErr = null; await openResult(true); render(); },
    redoQ: () => { S.q = path().indexOf('cname') + 1 || 1; S.fromHeard = true; go('q'); },
    redoJob: async () => {
      if (!redoArm) { redoArm = true; render(); setTimeout(() => { if (redoArm) { redoArm = false; if (S.screen === 'result') render(); } }, 4000); return; }
      redoArm = false;
      const r = await API.redo(S.job);
      if (!r.ok) { toast(r.status === 0 ? 'Studio can’t be reached right now.' : (r.data.error || 'The redo could not start.')); render(); return; }
      ST = Object.assign({}, ST, { stage: 'building', build: { status: 'queued' }, redo_available: false, redo_used: true });
      S.editsFor = null; go('making'); poll(1500);
    },
    toEdit: () => go('edit'),
    editAt: (el) => { S.edView = el.dataset.v; if (el.dataset.n) S.edSlide = +el.dataset.n; saveS(); go('edit'); },
    toFiles: () => go('files'),
    go: (el) => go(el.dataset.s),
    rmFile: async (el) => {
      if (!DEMO) {
        el.disabled = true;
        const r = await API.remove(S.job, el.dataset.name);
        if (r.ok) { S.files = r.data.files || []; upErr = ''; } else upErr = r.status === 404 ? 'That file was already removed.' : upMsg(r, el.dataset.name);
        if (r.status === 404) S.files = (S.files || []).filter((f) => f.name !== el.dataset.name);
        saveS(); render(); return;
      }
      const i = +el.dataset.i; if (el.dataset.k === 'raw') { S.rmRaw = (S.rmRaw || []).concat(i); } else if (el.dataset.k === 'brief') { S.briefs = briefs().filter((x, j) => j !== i); } else { S.extra.splice(i, 1); } saveS(); render();
    },
    dropUp: (el) => { const u = UP.find((x) => x.k === +el.dataset.k); if (u && u.thumb) URL.revokeObjectURL(u.thumb); UP = UP.filter((x) => x !== u); render(); },
    retryUp: async (el) => { const u = UP.find((x) => x.k === +el.dataset.k); if (!u) return; u.err = null; render(); if (!(await ensureJob())) { u.err = upErr || 'Studio can’t be reached right now.'; u.retry = true; upErr = ''; render(); return; } sendUp(u); },
    toShare: () => go('share'),
    rate: (el) => { S.rate = +el.dataset.r; saveS(); render(); if (S.rate >= 4) sendFeedback({ rating: S.rate }); },
    sendFb: () => { const t = document.getElementById('fb'); S.fb = t ? t.value : ''; S.fbSent = true; saveS(); render(); sendFeedback({ rating: S.rate, note: S.fb }); },
    feature: (el) => { S.feature = el.dataset.v === 'yes'; saveS(); render(); sendFeedback({ rating: S.rate, feature_ok: S.feature }); },
    copyTxt: async (el) => { const t = el.dataset.t; try { await navigator.clipboard.writeText(t); el.textContent = 'Copied'; } catch (e) { const i = document.getElementById(el.dataset.f); if (i) { i.focus(); i.select(); } el.textContent = 'Select and copy'; } },
    view: (el) => { S.edView = el.dataset.v; saveS(); ed.view = S.edView; ed.sel = null; ed.zoom = 1;
      document.querySelectorAll('[data-act="view"]').forEach((b) => b.classList.toggle('on', b.dataset.v === S.edView));
      document.querySelector('.edbody').className = 'edbody ' + S.edView; ed.render(); rail(); panel(); },
    slide: (el) => { ed.stopEdit(); ed.slideN = +el.dataset.n; S.edSlide = ed.slideN; saveS(); ed.sel = null; ed.render(); rail(); panel(); },
    undo: () => undo(), redo: () => redo(),
    ts: (el) => { if (P.ts === el.dataset.v) return; P.ts = el.dataset.v; setP(P, 'Text style'); document.querySelectorAll('[data-act="ts"]').forEach((b) => b.classList.toggle('on', b.dataset.v === P.ts)); ed.render(); rail(); panel(); },
    vz: (el) => { const v = +el.dataset.v; ed.zoom = v === 0 ? 1 : Math.max(0.5, Math.min(6, ed.zoom * (v > 0 ? 1.4 : 1 / 1.4))); ed.render(); },
    fitpic: () => { const page = ed.page(), slot = page.slots.find((s) => s.id === ed.sel.slot), c = page.contents[slot.content]; c.view = { z: 1, cx: 0.5, cy: 0.5 }; c.labels.forEach((L) => { L.on = true; }); ed.commit('Fit picture'); },
    swap: (el) => ed.swap(ed.sel.slot, el.dataset.s),
    lib: (el) => ed.replace(ed.sel.slot, LIB[+el.dataset.i]),
    labOff: () => { const page = ed.page(), slot = page.slots.find((s) => s.id === ed.sel.slot); page.contents[slot.content].labels[ed.sel.label].on = false; ed.sel = { type: 'slot', slot: slot.id }; ed.commit('Hide label'); },
    reset: () => { if (!resetArm) { resetArm = true; panel(); setTimeout(() => { resetArm = false; panel(); }, 4000); return; }
      resetArm = false; const keep = { ideas: P.ideas, altIdeas: P.altIdeas, slideOrder: P.slideOrder, slideOff: P.slideOff }; P = Object.assign(F.clone(ORIG), keep); setP(P, 'Start over'); ed.sel = null; ed.render(); rail(); panel(); toast('Back to AI Studio’s version. Undo brings your edits back.'); },
    panelMin: () => { const el = document.getElementById('panel'); S.panelPinned = true; el.classList.toggle('min'); panel(); },
    dlAll: async (el) => {
      if (el.disabled) return;
      el.disabled = true;
      const lab = el.querySelector('b') || el.querySelector('span'), sub = el.querySelector('small'), keys = [['boardPDF', 'Board PDF'], ['boardJPG', 'Board JPG'], ['deckPDF', 'Deck PDF'], ['deckPPTX', 'Deck PowerPoint']];
      let ok = 0;
      try {
        for (const [k, name] of keys) {
          lab.textContent = 'Saving ' + (ok + 1) + ' of 4'; sub.textContent = name + '…';
          const r = await X[k](P, () => {});
          if (r === 'declined') break;
          ok++;
        }
      } catch (e) { sub.textContent = e.message || String(e); }
      if (ok) askRating();
      if (ok === 4) { lab.textContent = 'All 4 files saved'; sub.textContent = 'Next: rate and share'; confetti(); el.dataset.act = 'toShare'; }
      else if (ok) { lab.textContent = ok + ' of 4 saved'; sub.textContent = 'Click to try the rest again'; }
      else { lab.textContent = 'Download all'; sub.textContent = 'Not saved: the download was declined.'; }
      el.disabled = false;
    },
    exp: async (el) => {
      const k = el.dataset.k, st = document.getElementById('st-' + k);
      el.disabled = true;
      try { const r = await X[k](P, (m) => { st.textContent = m + '…'; }); st.textContent = r === 'declined' ? 'Not saved: the download was declined.' : 'Done. Check your downloads.'; if (r !== 'declined') askRating(); }
      catch (e) { st.textContent = e.message || String(e); }
      el.disabled = false;
    },
    orig: async (el) => {
      const st = document.getElementById('st-' + el.dataset.k);
      el.disabled = true;
      try { const r = await X.original(P, el.dataset.k, el.dataset.name); st.textContent = r === 'declined' ? 'Not saved: the download was declined.' : 'Done. Check your downloads.'; if (r !== 'declined') askRating(); }
      catch (e) { st.textContent = e.message || String(e); }
      el.disabled = false;
    }
  };
  function moveIdea(i, d) { const M = Q(), j = i + d; if (j < 0 || j >= M.ideas.length) return; const t = M.ideas[i]; M.ideas[i] = M.ideas[j]; M.ideas[j] = t; planEdit('Move idea'); }
  function moveSlide(k, d) { const M = Q(), j = k + d; if (j < 1 || j >= M.slideOrder.length || k < 1) return; const o = M.slideOrder, t = o[k]; o[k] = o[j]; o[j] = t; planEdit('Move slide'); }
  function undo() { if (ed && ed.editing) ed.stopEdit(); if (hi <= 0) return; hi -= 1; P = JSON.parse(hist[hi]); afterHist('Undone'); }
  function redo() { if (ed && ed.editing) ed.stopEdit(); if (hi >= hist.length - 1) return; hi += 1; P = JSON.parse(hist[hi]); afterHist('Redone'); }
  function afterHist(msg) {
    lastSoft = false; scheduleSave(); bar();
    if (ed) { ed.sel = null; ed.render(); rail(); panel(); document.querySelectorAll('[data-act="ts"]').forEach((b) => b.classList.toggle('on', b.dataset.v === P.ts)); }
    else render();
    toast(msg);
  }

  app.addEventListener('click', (e) => {
    const el = e.target.closest('[data-act]');
    if (!el || !app.contains(el) || el.disabled) return;
    const f = A[el.dataset.act];
    if (f) f(el, e);
  });
  app.addEventListener('input', (e) => {
    if (e.target.id === 'other') {
      const k = curKey(), v = e.target.value;
      S.oth[k] = v; S.ans[k] = v.trim() ? 'other' : (S.ans[k] === 'other' ? null : ans(k));
      e.target.classList.toggle('filled', S.ans[k] === 'other');
      document.querySelectorAll('.opt.sel, .thumb.sel').forEach((b) => { if (S.ans[k] === 'other') b.classList.remove('sel'); });
      saveS();
    }
    if (e.target.id === 'concept' || (e.target.dataset && e.target.dataset.card)) { const fx = document.getElementById('fixed'); if (fx) fx.outerHTML = onSheet(e.target.id === 'concept' ? 'concept' : e.target.dataset.card, e.target.value); }
    if (e.target.id === 'concept') { S.concept = e.target.value; saveS(); const nb = document.querySelector('[data-act="qnext"]'); if (nb) { nb.textContent = conceptLabel(); nb.classList.toggle('primary', !!concept()); } }
    if (e.target.dataset && e.target.dataset.card) { S.card[e.target.dataset.card] = e.target.value; saveS(); const on = !!e.target.value.trim(), er = document.getElementById('cardErr'); if (er && on) er.textContent = ''; const nb = document.querySelector('[data-act="qnext"]'); if (nb) nb.classList.toggle('primary', on); }
    if (e.target.id === 'email') { S.email = e.target.value; saveS(); e.target.classList.remove('needs'); const er = document.getElementById('emailErr'); if (er) er.textContent = ''; }
  });
  app.addEventListener('change', (e) => { if (e.target.id === 'other') render(); });
  document.addEventListener('keydown', (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('span[role="button"][data-act]')) { e.preventDefault(); e.target.click(); return; }
    if (e.key === 'Enter' && e.target.matches && e.target.matches('#cardin, #concept')) { e.preventDefault(); A.qnext(); return; }
    if (S.screen !== 'edit') return;
    const mod = e.metaKey || e.ctrlKey;
    if (mod && (e.key === 'z' || e.key === 'Z')) { e.preventDefault(); if (e.shiftKey) redo(); else undo(); }
    else if (mod && (e.key === 'y' || e.key === 'Y')) { e.preventDefault(); redo(); }
    else if (e.key === 'Escape' && ed && !ed.editing) ed.select(null);
  });
  let rsT = null;
  window.addEventListener('resize', () => { clearTimeout(rsT); rsT = setTimeout(() => { if (ed) { ed.render(); rail(); } else if (S.screen === 'home' || S.screen === 'plan') fillMinis(app); }, 150); });

  /* Rating pop-up right after the first download (owner, 28 Oct). A native <dialog>: focus stays inside, Esc closes,
     the page behind is inert. The stars are real radio buttons, so arrow keys and screen readers work. */
  const RATE = ['Poor', 'Not great', 'Okay', 'Good', 'Excellent'];
  const STAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/></svg>';
  function askRating() {
    if (S.rateAsked || !window.HTMLDialogElement) return;
    S.rateAsked = true; saveS();
    const d = document.createElement('dialog');
    d.className = 'ratebox'; d.setAttribute('aria-labelledby', 'rt-h');
    d.innerHTML = '<form method="dialog" class="ratef"><h2 class="mid" id="rt-h">How did Studio do?</h2><p class="lede">One tap while your files save. It helps us make the next board better.</p>' +
      '<fieldset class="rstars"><legend class="sr">Your rating, 1 to 5 stars</legend>' + RATE.map((t, i) => '<input type="radio" name="rt" id="rt' + (i + 1) + '" value="' + (i + 1) + '"><label for="rt' + (i + 1) + '" title="' + t + '">' + STAR + '<span class="sr">' + (i + 1) + (i ? ' stars, ' : ' star, ') + t + '</span></label>').join('') + '</fieldset>' +
      '<p class="rword" id="rt-word" aria-live="polite">Tap a star</p>' +
      '<div class="field"><label for="rt-fb">Anything to fix or keep? (optional)</label><textarea id="rt-fb" class="input" rows="3" placeholder="The plan came out too small…"></textarea></div>' +
      '<p class="err" id="rt-err" role="alert"></p><div class="row"><button class="btn primary" value="send">Send</button><button class="btn" value="later">Not now</button></div></form>';
    document.body.appendChild(d);
    const val = () => +((d.querySelector('input[name="rt"]:checked') || {}).value || 0);
    d.addEventListener('change', () => { const n = val(); d.querySelectorAll('.rstars label').forEach((l, i) => l.classList.toggle('on', i < n)); d.querySelector('#rt-word').textContent = n ? n + ' of 5 · ' + RATE[n - 1] : 'Tap a star'; d.querySelector('#rt-err').textContent = ''; });
    d.addEventListener('submit', (e) => {
      const b = e.submitter && e.submitter.value;
      if (b === 'later') return;
      e.preventDefault();
      if (b === 'share') { d.close(); go('share'); return; }
      if (b === 'done') { d.close(); return; }
      const n = val();
      if (!n) { d.querySelector('#rt-err').textContent = 'Pick 1 to 5 stars first.'; d.querySelector('#rt1').focus(); return; }
      S.rate = n; S.fb = d.querySelector('#rt-fb').value.trim(); S.fbSent = !!S.fb; saveS();
      sendFeedback({ rating: n, note: S.fb });
      d.querySelector('form').innerHTML = '<h2 class="mid" id="rt-h" tabindex="-1">Thank you</h2><p class="lede">' + (n >= 4 ? 'Glad it worked. Want to show your before and after?' : 'We read every note. If something is wrong, your free redo is waiting.') + '</p>' +
        '<div class="row">' + (n >= 4 ? '<button class="btn primary" value="share">Share it</button>' : '') + '<button class="btn' + (n >= 4 ? '' : ' primary') + '" value="done">Close</button></div>';
      d.querySelector('#rt-h').focus();
    });
    d.addEventListener('close', () => d.remove());
    d.showModal();
  }

  let toastT = null;
  function toast(msg) {
    let t = document.getElementById('toast');
    if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; t.setAttribute('role', 'status'); document.body.appendChild(t); }
    t.textContent = msg; t.hidden = false;
    clearTimeout(toastT); toastT = setTimeout(() => { t.hidden = true; }, 3200);
  }

  /* ---------------------------------------------------------- live: the API steps */
  const offline = 'Studio can’t be reached right now. Check your connection and try again.';
  const fileSig = () => JSON.stringify((S.files || []).map((f) => f.name + ':' + f.bytes));
  function sendFeedback(body) {
    if (DEMO || !S.job || !body.rating) return;
    API.feedback(S.job, body).then((r) => { if (!r.ok && r.status !== 0) console.warn('feedback', r.status, r.data.error); });
  }
  /* the last question: save the answers, then ask for the free preview (or, after paying, keep them for the redo) */
  async function finishQuestions() {
    const er = document.getElementById('qErr'), btn = document.querySelector('[data-act="qnext"]');
    const body = intakeBody(), same = JSON.stringify(body) === S.lastIntake && fileSig() === S.pvSig;
    if (same && PV && !paid()) { S.fromHeard = false; saveS(); go('plan'); return; }
    if (btn) { btn.disabled = true; btn.textContent = 'Saving…'; }
    const r = await API.intake(S.job, body);
    if (!r.ok) {
      if (btn) { btn.disabled = false; btn.textContent = 'Try again'; }
      if (er) er.textContent = r.status === 0 ? offline : r.status === 422 ? 'Something in your answers needs a look: ' + (r.data.error || '') : (r.data.error || 'Your answers could not be saved. Try again.');
      return;
    }
    S.lastIntake = JSON.stringify(body); S.fromHeard = false; saveS();
    if (paid()) { toast('Answers saved. Your free redo will use them.'); go('result'); return; }
    startPreview();
  }
  async function startPreview() {
    S.limit = null; S.pvErr = null; PV = null; S.edit = null; S.planNotes = []; S.pvSig = fileSig();
    const r = await API.preview(S.job, null);
    if (r.status === 429) S.limit = r.data.error || 'You have used today’s free previews.';
    else if (r.status === 409 && /answer/i.test(r.data.error || '')) { S.q = path().length; go('q'); toast('Answer the questions first.'); return; }
    else if (r.status === 409 && /drawing/i.test(r.data.error || '')) { upErr = 'Add at least one drawing first.'; go('upload'); return; }
    else if (!r.ok && !(r.status === 409 && /running/i.test(r.data.error || ''))) S.pvErr = r.status === 0 ? offline : (r.data.error || 'The preview could not be started. Try again in a minute.');
    else ST = Object.assign({}, ST, { stage: 'previewing', preview: { status: 'queued' } });
    saveS(); go('planning', true);
    if (!S.limit && !S.pvErr) poll(2500);
  }
  /* the preview's plan as a model (thumbnails measured first, so pictures crop instead of stretching) */
  function dims(urls) {
    return Promise.all(urls.map((u) => new Promise((res) => { const im = new Image(); const t = setTimeout(() => res([u, null]), 8000);
      im.onload = () => { clearTimeout(t); res([u, [im.naturalWidth, im.naturalHeight]]); }; im.onerror = () => { clearTimeout(t); res([u, null]); }; im.src = u; })))
      .then((rs) => rs.reduce((m, [u, d]) => { if (d) m[u] = d; return m; }, {}));
  }
  async function buildPV() {
    const plan = ST && ST.plan;
    if (!plan) { PV = null; return; }
    const edit = plan.edit || LAY.editFromPlan(plan);
    const card = Object.assign({}, (ST.intake || {}).card || {}, { pro: isPro(), unbranded: unbranded() });
    if (!card.project_title && S.card.title) Object.assign(card, { name: S.card.name, project_title: tidy('title', S.card.title), project_location: tidy('loc', S.card.loc), program: tidy('prog', S.card.prog) });
    const d = await dims((edit.pictures || []).map((p) => p.thumb).filter(Boolean));
    S.edit = edit;
    PV = LAY.fromPlan(edit, plan, card, d);
  }
  /* preview edits go to the server (PUT /jobs/{id}/plan, server/core/plan.py) a moment after the last change */
  let planT = null, planSaved = '', planBusy = null;
  function planEdit(label) {
    if (DEMO) { setP(P, label); render(); return; }
    planSaved = 'Saving your changes…'; render();
    clearTimeout(planT); planT = setTimeout(savePlan, 700);
  }
  function planBody() {
    return { ideas: PV.ideas.map((i) => ({ id: i.id, on: !!i.on })), slideOrder: PV.slideOrder.filter((n) => n !== 0), slideOff: PV.slideOff.filter((n) => n !== 0) };
  }
  function savePlan() {
    planT = null;
    planBusy = (async () => {
      const r = await API.plan(S.job, planBody());
      if (r.ok) {
        S.planNotes = r.data.notes || [];
        const e = r.data.plan && r.data.plan.edit;
        if (e && e.slideOff) PV.slideOff = e.slideOff.slice();   // e.g. a slide the deck needs stays in
        planSaved = 'Saved. The paid build follows this plan.';
        const st = await API.status(S.job);
        if (st.ok) { ST = st.data; await buildPV(); }
      } else if (r.status === 404 || r.status === 405) planSaved = 'Saved on this device.';
      else planSaved = r.status === 0 ? 'Not saved: ' + offline : 'Not saved: ' + (r.data.error || 'try again');
      saveS();
      if (S.screen === 'plan') render(); else { const el = document.getElementById('planSaved'); if (el) el.textContent = planSaved; }
    })();
    return planBusy;
  }
  async function flushPlan() { if (planT) { clearTimeout(planT); await savePlan(); } else if (planBusy) await planBusy; }

  /* the paid build: its layout.json files and their pictures, read with the job's key, become the editor's model */
  async function openResult(force) {
    const outs = (ST && ST.outputs) || [], has = (n) => outs.some((o) => o.name === n);
    const lo = outs.find((o) => o.name === 'board/layout.json');
    const key = (S.job ? S.job.id : '') + ':' + (lo ? lo.bytes : 0) + ':' + ((ST.build || {}).attempt || 0) + ':' + (ST.redo_used ? 'r' : '');
    if (P && P.built === key && !force) return true;
    if (!has('board/layout.json')) { P = null; S.resErr = 'The editor could not open this build, but every file is ready to download.'; return false; }
    try {
      const board = await API.file(S.job, 'board/layout.json', 'json');
      const deck = has('deck/layout.json') ? await API.file(S.job, 'deck/layout.json', 'json') : null;
      const paths = [];
      [[board, 'board/'], [deck, 'deck/']].forEach(([L, dir]) => { if (L) L.pages.forEach((pg) => pg.items.forEach((it) => { if (it.k === 'img' && it.src && !paths.includes(dir + it.src)) paths.push(dir + it.src); })); });
      window.FGA_ASSETS = window.FGA_ASSETS || {};
      const todo = paths.filter((p) => !window.FGA_ASSETS[p]);
      for (let i = 0; i < todo.length; i += 6) {
        await Promise.all(todo.slice(i, i + 6).map((p) => API.file(S.job, p, 'blob').then((b) => { window.FGA_ASSETS[p] = URL.createObjectURL(b); }).catch(() => null)));
      }
      ORIG = LAY.fromLayout(board, deck, key);
      const saved = store.get(editKey());
      P = saved && saved.built === key ? saved : F.clone(ORIG);
      restored = !!(saved && saved.built === key);
      LIB = libOf(ORIG); resetHist(); S.resErr = null;
      return true;
    } catch (e) {
      console.warn(e);
      P = null; S.resErr = 'The editor could not open your board on this device, but every file is ready to download.';
      return false;
    }
  }

  /* the job's status, read every few seconds while something runs */
  let pollT = null;
  function poll(ms) { clearTimeout(pollT); pollT = setTimeout(tick, ms || 2500); }
  async function tick() {
    if (DEMO || !S.job) return;
    const r = await API.status(S.job);
    if (!r.ok) { if (r.status === 404) { lost(); return; } poll(7000); return; }
    ST = r.data; clockFrom(ST); clk.got = Date.now();
    await onStatus();
  }
  async function onStatus() {
    const st = ST, sc = S.screen;
    if (sc === 'planning') {
      if ((st.preview || {}).status === 'done' && st.plan) { await buildPV(); saveS(); go('plan', true); confetti(); return; }
      render();
      if (['queued', 'running'].includes((st.preview || {}).status)) poll();
      return;
    }
    if (sc === 'making') {
      if (!st.paid) {
        if (S.payDeadline && Date.now() > S.payDeadline) { S.payNote = 'unconfirmed'; S.payDeadline = null; saveS(); await buildPV(); go('price'); poll(15000); return; }
        render(); poll(2500); return;
      }
      S.payStarted = null; S.payDeadline = null; S.payNote = null; saveS();
      if (st.stage === 'ready') { await openResult(true); go('result'); return; }
      render(); poll(st.stage === 'failed' ? 60000 : 2500); return;
    }
    if (sc === 'price' && S.payNote === 'unconfirmed' && st.paid) { S.payNote = null; go('making'); poll(500); }
  }
  function lost() {
    S = freshS(); saveS(); PV = null; P = null; ST = null;
    go('home'); toast('That project link has expired or is not valid. Start a new project any time.');
  }
  /* where a job belongs, from its status (a reload, the receipt link on another device, or the return from Dodo) */
  async function refresh(fromReceipt) {
    if (DEMO || !S.job) { render(); return; }
    if (!app.innerHTML) app.innerHTML = '<main class="wrap narrow"><p class="kicker">Studio FGA</p><h1 class="mid">Opening your project…</h1></main>';
    const r = await API.status(S.job);
    if (!r.ok) {
      if (r.status === 404) { lost(); return; }
      render(); toast(offline); return;
    }
    ST = r.data; clockFrom(ST); clk.got = Date.now();
    S.files = ST.files || S.files || [];
    if (ST.intake && (!S.lastIntake || fromReceipt || !Object.keys(S.card || {}).length)) { fromIntake(ST.intake); S.lastIntake = JSON.stringify(intakeBody()); }
    if (ST.email && !S.email) S.email = ST.email;
    const stg = ST.stage, cur = S.screen;
    let to = cur;
    if (stg === 'upload' || stg === 'questions') to = ['upload', 'q'].includes(cur) ? cur : 'upload';
    else if (stg === 'preview') to = cur === 'q' ? 'q' : (S.limit ? 'planning' : 'q');
    else if (stg === 'previewing' || stg === 'preview_failed') to = 'planning';
    else if (stg === 'pay') {
      await buildPV();
      if (!S.pvSig) S.pvSig = fileSig();
      if (S.payStarted && fromReceipt) { S.payDeadline = S.payDeadline || Date.now() + 120000; to = 'making'; }
      else if (S.payStarted) { S.payStarted = null; S.payNote = 'cancelled'; to = 'price'; }
      else to = ['plan', 'price', 'q', 'upload'].includes(cur) ? cur : 'plan';
    } else if (stg === 'building' || stg === 'failed') to = 'making';
    else if (stg === 'ready') { await openResult(); to = ['result', 'edit', 'files', 'share', 'q', 'upload'].includes(cur) ? cur : 'result'; }
    if (to === 'q' && stg === 'preview') S.q = path().length;
    if (to === 'q' && !(S.q >= 1 && S.q <= path().length)) S.q = 1;
    saveS();
    go(to, true);
    if (to === 'planning' || to === 'making') poll(1500);
    if (restored && S.screen === 'edit') setTimeout(() => toast('Your edits from last time are back.'), 600);
  }
  /* back from Dodo (or the bfcache after the back button): read the job again */
  window.addEventListener('pageshow', (e) => { if (e.persisted && !DEMO && S.job) refresh(false); });

  /* ---------------------------------------------------------- start */
  const h = (location.hash || '').replace(/^#/, '');
  if (LEGAL.includes(h)) { location.replace(h + '/'); return; }
  /* the receipt link: #job=<id>&t=<token>. Dodo may add ?payment_id=…&status=… after it: ignored. */
  const mj = /(?:^|[#&?])job=([A-Za-z0-9_-]+)/.exec(location.hash), mt = /(?:^|[#&?])t=([A-Za-z0-9_-]+)/.exec(location.hash);
  const fromReceipt = !DEMO && !!(mj && mt);
  if (fromReceipt) {
    if (!S.job || S.job.id !== mj[1]) S = freshS();   // a new device: the status decides the screen
    else if (!['plan', 'price', 'making'].includes(S.screen)) S.screen = 'home';
    S.job = { id: mj[1], t: mt[1] }; saveS();
  } else if (SCREENS.includes(h)) S.screen = h;
  else if (!h && !DEMO) S.screen = 'home';   // a plain /studio/ opens on the landing; a saved job is offered with a pill
  if (S.screen === 'q' && !(S.q >= 1 && S.q <= path().length)) S.q = 1;
  if (DEMO) {
    if (restored && hist.length === 1 && S.screen === 'edit') setTimeout(() => toast('Your edits from last time are back.'), 600);
    render();
  } else if (S.job && API.ready) {
    if (S.screen === 'home' && !fromReceipt) render();   // the landing page needs nothing from the API
    else refresh(fromReceipt);
  } else {
    if (!['home'].includes(S.screen) && !API.ready) S.screen = 'home';
    if (!S.job && !['home', 'upload'].includes(S.screen)) S.screen = 'home';
    render();
  }
})();
