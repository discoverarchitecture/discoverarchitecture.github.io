"""A local stand-in for the Studio API, for testing site/studio/ offline. Test only: never deployed, never called
by the live page. It answers in the shapes of studio/server/README.md ("API (for the front end)") and fakes
Dodo's checkout page, so the whole journey can be clicked through with no backend, no payment and no AI.

    python3 tools/studio_mock/mock_api.py            # site on http://localhost:8791/studio/ , API on :8792

The site server hands out a config.js that points the page at the mock API (the real config.js is untouched).
Results come from the k5 sample run in the studio folder (STUDIO_DIR, default ~/FindGreatArchitecture/studio):
its story plan, panel crops, layout.json files, pictures and PDFs.

Switches (environment): MOCK_SPEED (default 1; 0.2 = five times faster), MOCK_MAX_MB (default 25),
MOCK_NO_EDIT=1 (status plan without the "edit" block, as an older server sends), MOCK_PREVIEWS (default 2 a day),
MOCK_STALE=1 (a finished preview is marked stale until refreshed once; the refresh is not counted).
An e-mail with "+fail" makes the paid build fail; a project title containing "nopics" makes the preview fail.
"""
import email.parser
import email.policy
import json
import os
import re
import secrets
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, quote

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
STUDIO = os.path.expanduser(os.environ.get("STUDIO_DIR", "~/FindGreatArchitecture/studio"))
K5 = os.path.join(STUDIO, "experiments", "exp01-great-board", "outputs", "k5-real-student")
WORK = os.path.join(STUDIO, "pipeline", "_eval", "pass2c", "k5-real-student", "work")
SITE_PORT, API_PORT = int(os.environ.get("MOCK_SITE_PORT", 8791)), int(os.environ.get("MOCK_API_PORT", 8792))
API = "http://localhost:%d" % API_PORT
ORIGIN = "http://localhost:%d" % SITE_PORT
SPEED = float(os.environ.get("MOCK_SPEED", 1))
MAX_MB = float(os.environ.get("MOCK_MAX_MB", 25))
PREVIEWS = int(os.environ.get("MOCK_PREVIEWS", 2))
PREVIEW_STAGES = ["Reading your files", "Finding every drawing", "Reading your concept", "Planning the story", "Laying out your board and deck"]
PREVIEW_KEYS = ["ingest", "read_sheets", "concept", "story", "composition"]
BUILD_KEYS = ["ingest", "read_sheets", "concept", "story", "pictures", "labels", "layout", "fill_slots", "build", "checks"]
BUILD_STAGES = ["Reading your files", "Finding every drawing", "Reading your concept", "Planning the story", "Making the pictures",
                "Labelling the drawings", "Laying out the board and deck", "Filling every slot", "Building the files", "Final checks"]
JOBS, LOCK, COUNT = {}, threading.Lock(), {"previews": 0}
LOG = []


def log(*a):
    line = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    LOG.append(line)
    print(line, flush=True)


# ------------------------------------------------------------------ the plan (preview.summarise + plan.edit_view)
STORY = json.load(open(os.path.join(WORK, "story.json")))
PANELS = {p["id"]: p for p in json.load(open(os.path.join(WORK, "panels.json")))}
REQUIRED = {"plan", "section", "context"}


def thumb(jid, pid):
    return "%s/jobs/%s/download/panels/%s.png?exp=9999999999&sig=mock" % (API, jid, pid)


def plan_for(j):
    st = STORY
    ideas = j.get("ideas_edit") or [{"id": "i%d" % (k + 1), "on": True} for k in range(len(st["ideas"]))]
    by = {"i%d" % (k + 1): it for k, it in enumerate(st["ideas"])}
    slide_off = j.get("slide_off", [])
    plan = {"project_name": j["intake"]["card"]["project_title"], "subtitle": st["subtitle"], "thesis": st["thesis"], "concept": st["concept"],
            "concept_statement": j["intake"].get("concept_text"), "story": st["story"], "accent_hex": st["accent_hex"], "hero": st["hero"],
            "ideas": [by[i["id"]] for i in ideas if i["on"]],
            "panels": [{"panel": p["panel"], "use": p["use"], "caption": p["caption"], "why": p.get("why"), "kind": PANELS.get(p["panel"], {}).get("kind"),
                        "title": PANELS.get(p["panel"], {}).get("title"), "file": PANELS.get(p["panel"], {}).get("file"), "thumb": thumb(j["id"], p["panel"])}
                       for p in st["panels"]],
            "diagrams": [{k: d.get(k) for k in ("id", "idea", "what", "caption")} for d in st.get("diagrams", [])],
            "programme": st.get("programme", []),
            "slides": [{k: s.get(k) for k in ("role", "label", "title", "lead")} for n, s in enumerate(st["slides"], 1) if n not in slide_off],
            "tier_suggested": tier_from(j["intake"]), "level": 2, "preset": "Pastel Collage", "text_style": "A", "size": "A1"}
    if os.environ.get("MOCK_NO_EDIT") != "1":
        plan["edit"] = {
            "ideas": [{"id": i["id"], "title": by[i["id"]]["tagline"], "text": by[i["id"]]["line"], "proof": by[i["id"]]["proof"], "on": i["on"]} for i in ideas],
            "altIdeas": [], "hero": st["hero"],
            "pictures": [{"id": p["panel"], "label": PANELS.get(p["panel"], {}).get("title"), "kind": PANELS.get(p["panel"], {}).get("kind"),
                          "file": PANELS.get(p["panel"], {}).get("file"), "use": p["use"], "on": True, "protected": p["use"] in ("process", "concept"),
                          "caption": p["caption"], "thumb": thumb(j["id"], p["panel"])} for p in st["panels"]],
            "slides": [dict({k: s.get(k) for k in ("role", "label", "title", "lead")}, n=n, required=s["role"] in REQUIRED) for n, s in enumerate(st["slides"], 1)],
            "slideOrder": j.get("slide_order") or list(range(1, len(st["slides"]) + 1)), "slideOff": slide_off,
            "subtitle": st["subtitle"], "concept": st["concept"], "story": st["story"]}
        plan["edited"] = bool(j.get("ideas_edit") or slide_off)
    return plan


def tier_from(intake):
    a = (intake.get("q8_ai_rework") or "")
    a = a.get("other", "") if isinstance(a, dict) else a
    return "nice" if re.match(r"(keep|polish)", a, re.I) else "great"


# ------------------------------------------------------------------ the composition preview (rule 26, D85)
def composition(j):
    """What goes where on the board and on each of 12 slides, as 0..1 fractions of the page: the student's drawings
    (source "student", with the panel crop as image_url), what Studio will create ("create") and text ("text")."""
    def st(pid, label, role, x, y, w, h):
        return {"id": pid + "-" + role, "label": label, "role": role, "source": "student", "image_url": thumb(j["id"], pid), "x": x, "y": y, "w": w, "h": h}

    tiers = {"elevation": "polish", "axonometric": "transform"}

    def new(label, role, x, y, w, h):
        return {"id": "new-" + role, "label": label, "role": role, "source": "create", "image_url": None, "x": x, "y": y, "w": w, "h": h,
                "tier": tiers.get(role, "transform")}

    def tx(label, role, x, y, w, h):
        return {"id": "t-" + role + "-%d" % int(x * 100 + y * 1000), "label": label, "role": role, "source": "text", "image_url": None, "x": x, "y": y, "w": w, "h": h}
    board = [tx("Title", "title", .034, .02, .69, .05), tx("Project details", "info", .743, .025, .223, .045),
             st("p04-1", "Render · entrance", "hero", .034, .076, .617, .209), tx("Concept", "concept", .664, .076, .302, .06),
             tx("The story", "story", .664, .14, .302, .07), tx("Three ideas", "ideas", .664, .214, .302, .09),
             st("p03-3", "Process sketch", "process", .034, .306, .302, .109), st("p03-1", "Process sketch", "process", .349, .306, .302, .109),
             st("p03-4", "Concept sketch", "concept", .664, .306, .302, .109),
             st("p05-2", "Model", "model", .034, .44, .302, .1), st("p03-6", "Model", "model", .349, .44, .302, .1), new("Axonometric · new", "axonometric", .664, .44, .302, .1),
             st("p01-1", "Site plan", "site", .034, .565, .302, .188), st("p06-1", "Plan · ground floor", "plan", .349, .565, .617, .188),
             st("p05-1", "Section · AA", "section", .034, .78, .617, .17), new("Elevation · new", "elevation", .664, .78, .302, .17)]
    full = lambda pid, lab, role: [st(pid, lab, role, .047, .25, .906, .66), tx("Headline", "headline", .047, .07, .7, .12)]
    left = lambda items, txt: items + [tx(txt, "text", .047, .07, .33, .5)]
    deck = [
        {"n": 1, "title": "Cover", "kind": "cover", "slots": [st("p04-1", "Render · entrance", "hero", .047, .063, .6, .816), tx("Project title", "title", .66, .06, .29, .37), tx("Details", "info", .66, .74, .29, .14)]},
        {"n": 2, "title": "Contents", "kind": "contents", "slots": [tx("Contents", "headline", .047, .07, .9, .12), tx("Sections", "contents", .047, .26, .42, .6), tx("Sections", "contents", .51, .26, .42, .6)]},
        {"n": 3, "title": "The brief", "kind": "brief", "slots": left([st("p05-3", "Model", "model", .43, .063, .52, .61)], "Brief and programme") + [tx("Three ideas", "ideas", .047, .76, .9, .17)]},
        {"n": 4, "title": "The setting", "kind": "context", "slots": left([st("p01-1", "Site plan", "site", .4, .063, .55, .82)], "Site and context")},
        {"n": 5, "title": "The idea", "kind": "concept", "slots": left([st("p03-4", "Concept sketch", "concept", .4, .063, .55, .82)], "Concept")},
        {"n": 6, "title": "The process", "kind": "process", "slots": [tx("Headline", "headline", .047, .07, .9, .12), st("p03-3", "Process sketch", "process", .047, .3, .29, .5), st("p03-1", "Process sketch", "process", .355, .3, .29, .5), st("p03-2", "Process sketch", "process", .663, .3, .29, .5)]},
        {"n": 7, "title": "The models", "kind": "models", "slots": [tx("Headline", "headline", .047, .07, .9, .12), st("p05-2", "Model", "model", .047, .3, .29, .5), st("p03-6", "Model", "model", .355, .3, .29, .5), st("p03-7", "Model", "model", .663, .3, .29, .5)]},
        {"n": 8, "title": "The plan", "kind": "plan", "slots": left([st("p06-1", "Plan · ground floor", "plan", .4, .063, .55, .82)], "Plan notes")},
        {"n": 9, "title": "The section", "kind": "section", "slots": full("p05-1", "Section · AA", "section")},
        {"n": 10, "title": "The elevation", "kind": "elevation", "slots": [tx("Headline", "headline", .047, .07, .9, .12), new("Elevation · new", "elevation", .047, .25, .906, .66)]},
        {"n": 11, "title": "The assembly", "kind": "axonometric", "slots": left([new("Axonometric · new", "axonometric", .4, .063, .55, .82)], "How it fits together")},
        {"n": 12, "title": "Closing", "kind": "closing", "slots": [st("p03-5", "Render · street", "render", .047, .063, .6, .816), tx("Closing words", "title", .66, .06, .29, .5)]}]
    contents = {1: ["Entrance render", "Project title and title block"], 2: ["The sections, numbered"], 3: ["Brief note", "1 model photo", "The three ideas"],
                4: ["1 site plan", "Site note"], 5: ["Concept note", "1 concept sketch"], 6: ["3 sketches"], 7: ["3 model photos"], 8: ["1 plan", "Plan note"],
                9: ["1 section"], 10: ["Elevation (new, AI Studio)"], 11: ["Axonometric (new, AI Studio)", "Structure note"], 12: ["Street render", "Closing words"]}
    titles = {1: "Cover", 2: "Contents", 3: "Brief & program", 4: "Site & context", 5: "Concept", 6: "Process", 7: "Models", 8: "Plans", 9: "Sections",
              10: "Elevations", 11: "Axonometric", 12: "Closing"}
    concept = (j.get("intake") or {}).get("concept_text") or STORY["concept"]
    for d in deck:
        d.update(title=titles[d["n"]], contents=contents[d["n"]], note=concept if d["kind"] == "concept" else None)
    basics = [{"key": "section", "label": "Section", "source": "student"}, {"key": "elevation", "label": "Elevation · new", "source": "create"},
              {"key": "axonometric", "label": "Axonometric · new", "source": "create"}]
    return {"board": {"w_mm": 594, "h_mm": 841, "slots": board}, "deck": {"w_mm": 338.7, "h_mm": 190.5, "slides": deck}, "basics": basics}


# ------------------------------------------------------------------ the job's state
def stage_of(j, now):
    out = {"stage": "upload", "step": None, "progress": 0}
    if j["files"]:
        out["stage"] = "questions"
    if j.get("intake"):
        out["stage"] = "preview"
    pv = j.get("preview")
    if pv:
        if pv["status"] in ("queued", "running"):
            k = int((now - pv["at"]) / (1.5 * SPEED))
            if k >= len(PREVIEW_STAGES):
                pv["status"] = "failed" if "nopics" in j["intake"]["card"]["project_title"].lower() else "done"
                if pv["status"] == "failed":
                    pv["error"] = "We could not find any drawings in your uploads. Add PNG, JPG or PDF drawings and try again."
            else:
                pv["status"] = "running" if k >= 1 else "queued"
                out.update(stage="previewing", step=PREVIEW_STAGES[k] if k >= 1 else "Waiting to start", progress=[5, 12, 60, 64, 88][k],
                           step_key=PREVIEW_KEYS[k] if k >= 1 else "queued",
                           elapsed_s=round(now - pv["at"], 1), step_elapsed_s=round((now - pv["at"]) % (1.5 * SPEED), 1))
        if pv["status"] == "done":
            out.update(stage="pay", progress=100)
        elif pv["status"] == "failed":
            out["stage"] = "preview_failed"
    if j.get("paid"):
        b = j["build"]
        if b["status"] in ("queued", "running"):
            k = int((now - b["at"]) / (1.0 * SPEED))
            if k >= len(BUILD_STAGES):
                b["status"] = "failed" if "+fail" in (j.get("email") or "") else "done"
                b["attempt"] = 2 if b["status"] == "failed" else 1
            else:
                b["status"] = "running" if k >= 1 else "queued"
                out.update(stage="building", step=BUILD_STAGES[k] if k >= 1 else "Waiting to start", progress=[3, 6, 18, 20, 30, 62, 70, 74, 80, 96][k] if k >= 1 else 0,
                           step_key=BUILD_KEYS[k] if k >= 1 else "queued",
                           elapsed_s=round(now - b["at"], 1), step_elapsed_s=round((now - b["at"]) % (1.0 * SPEED), 1))
        if b["status"] == "done":
            out.update(stage="ready", progress=100, step=None)
        elif b["status"] == "failed":
            out.update(stage="failed", step=None, progress=None)
    return out


OUTS = [("board/board.pdf", "Board PDF (print)", os.path.join(K5, "BOARD", "board.pdf")), ("board/board.png", "Board picture", os.path.join(K5, "BOARD", "board.png")),
        ("deck/deck.pptx", "Deck PowerPoint", os.path.join(K5, "DECK", "deck.pptx")), ("deck/deck.pdf", "Deck PDF", os.path.join(K5, "DECK", "deck.pdf")),
        ("board/layout.json", "Board layout (editor)", os.path.join(K5, "BOARD", "layout.json")), ("deck/layout.json", "Deck layout (editor)", os.path.join(K5, "DECK", "layout.json"))]


def status(j):
    now = time.time()
    s = stage_of(j, now)
    paid = bool(j.get("paid"))
    b = j.get("build") or {"status": "none"}
    outs = [{"name": n, "label": l, "bytes": os.path.getsize(p) if os.path.exists(p) else 0, "url": "%s/jobs/%s/download/%s?exp=9999999999&sig=mock" % (API, j["id"], n)}
            for n, l, p in OUTS] if paid and b["status"] in ("done", "failed") else []
    if outs:
        outs.append({"name": "indesign/board_InDesign.zip", "label": "Board InDesign", "bytes": 1234, "url": "%s/jobs/%s/download/indesign/board_InDesign.zip?exp=9999999999&sig=mock" % (API, j["id"])})
    pv = j.get("preview") or {"status": "none"}
    redo_until = j["paid_at"] + 7 * 86400 if paid else None
    pk = s.get("step_key") if s["stage"] == "previewing" else None
    bk = s.get("step_key") if s["stage"] == "building" else None
    stale = os.environ.get("MOCK_STALE") == "1" and pv["status"] == "done" and not j.get("refreshed")
    return dict(job_id=j["id"], **s, preview={"status": pv["status"], "error": pv.get("error"), "stage": pk, "label": s.get("step") if pk else None, "stale": stale,
                                          "composition": composition(j) if pv["status"] == "done" else None},
                build={"status": b["status"], "attempt": b.get("attempt"), "reason": b.get("reason"), "stage": bk, "label": s.get("step") if bk else None,
                       "error": "Something went wrong on our side. We have been told and will rerun it at no cost." if b["status"] == "failed" else None},
                plan=plan_for(j) if pv["status"] == "done" else None, tier=j.get("tier") or (tier_from(j["intake"]) if j.get("intake") else None),
                tier_suggested=tier_from(j["intake"]) if j.get("intake") else None, paid=paid, email=j.get("email"), files=j["files"],
                intake=j.get("intake"), outputs=outs,
                redo_available=bool(paid and not j.get("redo_used") and b["status"] == "done"), redo_used=bool(j.get("redo_used")),
                redo_until=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(redo_until)) if redo_until else None,
                feedback=j.get("feedback"), created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(j["created"])))


# ------------------------------------------------------------------ HTTP
class Fail(Exception):
    def __init__(self, status, msg):
        self.status, self.msg = status, msg


class ApiHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def cors(self):
        o = self.headers.get("Origin")
        if o in (ORIGIN, "http://127.0.0.1:%d" % SITE_PORT):
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")

    def reply(self, status, data=None, ctype="application/json", raw=None, extra=None):
        body = raw if raw is not None else json.dumps(data).encode()
        self.send_response(status)
        self.cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type, x-job-token, authorization")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def json_body(self):
        b = self.body()
        try:
            d = json.loads(b or b"{}")
        except ValueError:
            raise Fail(400, "send JSON")
        if not isinstance(d, dict):
            raise Fail(400, "send a JSON object")
        return d

    def job(self, jid, q):
        j = JOBS.get(jid)
        tok = self.headers.get("X-Job-Token") or (q.get("t") or [None])[0]
        if not j or (tok != j["token"] and (q.get("sig") or [None])[0] != "mock"):
            raise Fail(404, "no such job")
        return j

    def route(self, method):
        u = urlparse(self.path)
        q, p = parse_qs(u.query), u.path.rstrip("/")
        if p.startswith("/mock-dodo"):
            return self.dodo(method, p, q)
        if method == "POST" and p == "/jobs":
            jid = time.strftime("%y%m%d-") + secrets.token_hex(4)
            tok = secrets.token_urlsafe(24)
            JOBS[jid] = {"id": jid, "token": tok, "files": [], "created": time.time()}
            log("create", jid)
            return self.reply(201, {"job_id": jid, "token": tok, "receipt_link": "%s/studio/#job=%s&t=%s" % (ORIGIN, jid, tok)})
        m = re.match(r"^/jobs/([^/]+)(?:/(.*))?$", p)
        if not m:
            raise Fail(404, "not found")
        jid, rest = m.group(1), m.group(2) or ""
        j = self.job(jid, q)
        busy = (j.get("preview") or {}).get("status") in ("queued", "running") or (j.get("build") or {}).get("status") in ("queued", "running")
        if method == "GET" and rest == "":
            return self.reply(200, status(j))
        if method == "POST" and rest == "files":
            return self.upload(j, busy)
        if method == "DELETE" and rest.startswith("files/"):
            name = rest[6:]
            if busy:
                raise Fail(409, "your project is being worked on; try again when it finishes")
            if name not in {f["name"] for f in j["files"]}:
                raise Fail(404, "no such file")
            j["files"] = [f for f in j["files"] if f["name"] != name]
            log("delete", jid, name)
            return self.reply(200, {"files": j["files"]})
        if method == "PUT" and rest == "intake":
            if busy:
                raise Fail(409, "your project is being worked on; try again when it finishes")
            d = self.json_body()
            if d.get("path") not in ("student", "professional"):
                raise Fail(422, "path must be 'student' or 'professional'")
            card = d.get("card") or {}
            for k in ("name", "project_title", "project_location", "program"):
                if not str(card.get(k) or "").strip():
                    raise Fail(422, "card.%s: required" % k)
            allowed = {"student": {"s2_year", "q2_jury_word", "q3_impress", "q4_last_crit"}, "professional": {"p3_stage", "p4_room", "p11_firm"}}[d["path"]] | \
                {"q1_shown_at", "q5_hero", "q6_proudest", "q7_personality", "q8_ai_rework", "q9_text", "q10_process"}
            bad = sorted(set(d.get("answers") or {}) - allowed)
            if bad:
                raise Fail(422, "answers not on the %s path: %s" % (d["path"], ", ".join(bad)))
            intake = dict(d.get("answers") or {}, path=d["path"], card=card, concept_text=d.get("concept_text"))
            j["intake"] = intake
            log("intake", jid, json.dumps(d)[:400])
            return self.reply(200, {"ok": True, "tier_suggested": tier_from(intake)})
        if method == "POST" and rest == "preview":
            self.json_body()
            if not any(f["kind"] == "drawing" for f in j["files"]):
                raise Fail(409, "upload at least one drawing first")
            if not j.get("intake"):
                raise Fail(409, "answer the questions first")
            if busy:
                raise Fail(409, "a preview or build is already running")
            stale = os.environ.get("MOCK_STALE") == "1" and (j.get("preview") or {}).get("status") == "done" and not j.get("refreshed")
            if stale:
                j["refreshed"] = True   # refreshing a stale preview is free (not counted)
            elif not j.get("paid"):
                if COUNT["previews"] >= PREVIEWS:
                    raise Fail(429, "You have used today's %d free previews. Come back tomorrow." % PREVIEWS)
                COUNT["previews"] += 1
            j["preview"] = {"status": "queued", "at": time.time()}
            j.pop("ideas_edit", None), j.pop("slide_off", None), j.pop("slide_order", None)
            log("preview", jid, "count", COUNT["previews"])
            return self.reply(202, {"ok": True, "preview_seq": COUNT["previews"]})
        if method == "PUT" and rest == "plan":
            if (j.get("preview") or {}).get("status") != "done":
                raise Fail(409, "make the free preview first")
            if j.get("paid") and j.get("redo_used"):
                raise Fail(409, "the plan can only change before paying, or before your free redo")
            d = self.json_body()
            notes = []
            ideas = d.get("ideas")
            if ideas is not None:
                if sum(1 for i in ideas if i.get("on") is not False) not in range(2, 5):
                    raise Fail(422, "ideas: keep 2 to 4 ideas turned on")
                j["ideas_edit"] = [{"id": i["id"], "on": i.get("on") is not False} for i in ideas]
            off = []
            for n in d.get("slideOff") or []:
                s = STORY["slides"][n - 1]
                if s["role"] in REQUIRED:
                    notes.append("The %s slide is needed for your drawings, so it stays in the deck." % s["label"])
                else:
                    off.append(n)
            j["slide_off"] = off
            order = d.get("slideOrder")
            if order and order != sorted(order):
                notes.append("The deck keeps the jury-deck order (cover, brief, context, concept, drawings, views); you can move slides in the editor after the build.")
            j["slide_order"] = order
            log("plan", jid, json.dumps(d))
            return self.reply(200, {"ok": True, "notes": notes, "plan": plan_for(j)})
        if method == "POST" and rest == "checkout":
            d = self.json_body()
            if d.get("tier") not in ("nice", "great"):
                raise Fail(422, "tier must be nice or great")
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", d.get("email") or ""):
                raise Fail(422, "enter the e-mail address for your receipt")
            if j.get("paid"):
                raise Fail(409, "this project is already paid for")
            if (j.get("preview") or {}).get("status") != "done":
                raise Fail(409, "make the free preview first")
            j["email"], j["checkout"] = d["email"], d["tier"]
            ret = "%s/studio/#job=%s&t=%s" % (ORIGIN, jid, j["token"])
            log("checkout", jid, d["tier"], d["email"])
            return self.reply(200, {"checkout_url": "%s/mock-dodo?job=%s&tier=%s&return=%s" % (API, jid, d["tier"], quote(ret, safe="")), "session_id": "cks_mock", "plan_kept": True})
        if method == "POST" and rest == "redo":
            if not j.get("paid"):
                raise Fail(402, "pay for the project first")
            if j.get("redo_used"):
                raise Fail(409, "the free redo has been used")
            if busy or j["build"]["status"] != "done":
                raise Fail(409, "wait for the current build to finish")
            j["redo_used"] = True
            j["build"] = {"status": "queued", "at": time.time(), "reason": "redo"}
            log("redo", jid)
            return self.reply(202, {"ok": True})
        if method == "POST" and rest == "feedback":
            d = self.json_body()
            try:
                r = int(d.get("rating"))
            except (TypeError, ValueError):
                raise Fail(422, "rating must be 1 to 5")
            if not 1 <= r <= 5:
                raise Fail(422, "rating must be 1 to 5")
            j["feedback"] = {"rating": r, "note": str(d.get("note") or "")[:2000], "feature_ok": bool(d.get("feature_ok"))}
            log("feedback", jid, json.dumps(j["feedback"]))
            return self.reply(200, {"ok": True})
        if method == "GET" and rest.startswith("download/"):
            return self.download(j, rest[9:])
        raise Fail(404, "not found")

    def upload(self, j, busy):
        if busy:
            raise Fail(409, "your project is being worked on; try again when it finishes")
        ctype = self.headers.get("Content-Type", "")
        raw = self.body()
        msg = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + raw)
        kind, files = "drawing", []
        for part in msg.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if name == "kind":
                kind = part.get_content().strip()
            elif name == "file":
                files.append((part.get_filename() or "file", part.get_payload(decode=True) or b""))
        added = []
        for fn, data in files:
            ext = os.path.splitext(fn)[1].lower().lstrip(".")
            magic = data[:8]
            okmagic = magic.startswith(b"\x89PNG") or magic.startswith(b"\xff\xd8") or magic.startswith(b"%PDF") or data[8:12] == b"WEBP"
            if ext not in ("png", "jpg", "jpeg", "webp", "pdf") or not okmagic:
                raise Fail(415, "%s: only PNG, JPG, WebP or PDF" % fn)
            if len(data) > MAX_MB * 1048576:
                raise Fail(413, "%s is larger than %d MB" % (fn, MAX_MB))
            if len(j["files"]) + len(added) >= 30:
                raise Fail(413, "at most 30 files per project")
            safe = re.sub(r"[^A-Za-z0-9._-]+", "_", fn)[:80] or "file"
            base, n = safe, 1
            while safe in {f["name"] for f in j["files"] + added}:
                n += 1
                safe = "%s-%d%s" % (os.path.splitext(base)[0], n, os.path.splitext(base)[1])
            added.append({"name": safe, "kind": kind if kind in ("drawing", "brief") else "drawing", "bytes": len(data), "type": ext, "original": fn[:200]})
        time.sleep(0.4 * SPEED)   # so the progress bar is seen
        j["files"] += added
        log("upload", j["id"], [a["name"] for a in added])
        return self.reply(200, {"files": j["files"], "added": added})

    def download(self, j, path):
        m = re.match(r"^panels/(p\d{2,3}-\d{1,2})\.png$", path)
        if m:
            f = os.path.join(WORK, "panels", m.group(1) + ".png")
        else:
            if not j.get("paid"):
                raise Fail(402, "pay for the project to download it")
            if path.startswith("indesign/"):
                return self.reply(200, raw=b"PK mock zip", ctype="application/zip")
            top, _, sub = path.partition("/")
            f = {"board": os.path.join(K5, "BOARD", sub), "deck": os.path.join(K5, "DECK", sub)}.get(top)
        if not f or not os.path.isfile(f) or ".." in path:
            raise Fail(404, "no such file")
        ext = os.path.splitext(f)[1].lower()
        ct = {".png": "image/png", ".jpg": "image/jpeg", ".json": "application/json", ".pdf": "application/pdf",
              ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"}.get(ext, "application/octet-stream")
        return self.reply(200, raw=open(f, "rb").read(), ctype=ct, extra={"Cache-Control": "private, max-age=300"})

    def dodo(self, method, p, q):
        """A fake Dodo checkout page: Pay marks the job paid (as the webhook would) and returns to the receipt link."""
        if method == "GET":
            jid, tier, ret = q["job"][0], q["tier"][0], q["return"][0]
            page = ("<!doctype html><meta name=viewport content='width=device-width'><title>Mock Dodo checkout</title><body style='font:16px system-ui;max-width:420px;margin:40px auto;padding:0 16px'>"
                    "<h1>Mock checkout (test)</h1><p>Job %s · %s · $%s</p><form method=post action='/mock-dodo/pay'><input type=hidden name=job value='%s'>"
                    "<input type=hidden name=ret value='%s'><button id=pay style='font-size:18px;padding:12px 20px'>Pay (test)</button></form>"
                    "<p><a id=cancel href='%s'>Cancel and go back</a></p></body>") % (jid, tier, 16 if tier == "great" else 11, jid, ret.replace("'", "%27"), ret.replace("'", "%27") + "?payment_id=pay_x&status=cancelled")
            return self.reply(200, raw=page.encode(), ctype="text/html; charset=utf-8")
        form = parse_qs(self.body().decode())
        jid, ret = form["job"][0], form["ret"][0]
        j = JOBS[jid]
        j.update(paid=True, tier=j.get("checkout"), paid_at=time.time(), build={"status": "queued", "at": time.time(), "reason": "paid"})
        log("PAID", jid, j["tier"])
        self.send_response(303)
        self.send_header("Location", ret + "?payment_id=pay_mock&status=succeeded")   # Dodo adds its own query after the link
        self.end_headers()

    def handle_any(self, method):
        try:
            with LOCK:
                self.route(method)
        except Fail as e:
            log("  ->", e.status, method, self.path[:80], e.msg)
            self.reply(e.status, {"error": e.msg})

    def do_GET(self):
        self.handle_any("GET")

    def do_POST(self):
        self.handle_any("POST")

    def do_PUT(self):
        self.handle_any("PUT")

    def do_DELETE(self):
        self.handle_any("DELETE")


class SiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=SITE, **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")   # test server: always the files on disk
        super().end_headers()

    def do_GET(self):
        if urlparse(self.path).path == "/studio/config.js":
            body = ("/* served by tools/studio_mock/mock_api.py (test only) */\nwindow.STUDIO_API = %s;\n" % json.dumps(API)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()


if __name__ == "__main__":
    for d in (K5, WORK):
        if not os.path.isdir(d):
            sys.exit("missing fixture folder: %s (set STUDIO_DIR)" % d)
    api = ThreadingHTTPServer(("127.0.0.1", API_PORT), ApiHandler)
    site = ThreadingHTTPServer(("127.0.0.1", SITE_PORT), SiteHandler)
    threading.Thread(target=api.serve_forever, daemon=True).start()
    print("site  %s/studio/\napi   %s" % (ORIGIN, API), flush=True)
    site.serve_forever()
