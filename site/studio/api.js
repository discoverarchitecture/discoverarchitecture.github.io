/* Studio FGA: the few calls the page makes to the Studio API (server/README.md, "API (for the front end)").
   The address comes from config.js (window.STUDIO_API). Every /jobs/{id} call carries the job's key as the
   X-Job-Token header (the owner's read-only view sends its signature instead). Answers are {ok, status, data}; data.error is the server's plain message. */
(function () {
  'use strict';
  const BASE = String(window.STUDIO_API || '').replace(/\/+$/, '');
  const ready = /^https?:\/\//.test(BASE) && !/REPLACE/i.test(BASE);

  /* the owner's read-only view (app.js, #view=…): the server's signature instead of the job token, and reads only */
  function auth(h, job) {
    if (job && job.view) { h['X-View-Exp'] = job.view.exp; h['X-View-Sig'] = job.view.sig; } else if (job) h['X-Job-Token'] = job.t;
    return h;
  }
  const refused = () => ({ ok: false, status: 403, data: { error: 'View only' } });
  async function call(method, path, job, body) {
    if (window.StudioAPI.readOnly && method !== 'GET') return refused();
    const h = auth({}, job);
    if (body !== undefined) h['Content-Type'] = 'application/json';
    try {
      const r = await fetch(BASE + path, { method, headers: h, body: body === undefined ? undefined : JSON.stringify(body), cache: 'no-store' });
      let data = null;
      try { data = await r.json(); } catch (e) { data = null; }
      return { ok: r.ok, status: r.status, data: data || {} };
    } catch (e) {
      return { ok: false, status: 0, data: { error: 'offline' } };
    }
  }
  /* one file per request, so each gets its own progress bar and its own error */
  function upload(job, kind, file, onProgress) {
    if (window.StudioAPI.readOnly) return Promise.resolve(refused());
    return new Promise((resolve) => {
      const x = new XMLHttpRequest(), fd = new FormData();
      fd.append('kind', kind);
      fd.append('file', file, file.name);
      x.open('POST', BASE + '/jobs/' + encodeURIComponent(job.id) + '/files');
      x.setRequestHeader('X-Job-Token', job.t);
      x.upload.onprogress = (e) => { if (e.lengthComputable && onProgress) onProgress(e.loaded / e.total); };
      x.onload = () => { let d = {}; try { d = JSON.parse(x.responseText); } catch (e) { d = {}; } resolve({ ok: x.status >= 200 && x.status < 300, status: x.status, data: d }); };
      x.onerror = () => resolve({ ok: false, status: 0, data: { error: 'offline' } });
      x.send(fd);
    });
  }
  /* a result file (layout.json or one of its pictures), read with the job's key */
  async function file(job, path, as) {
    const r = await fetch(BASE + '/jobs/' + encodeURIComponent(job.id) + '/download/' + path, { headers: auth({}, job) });
    if (!r.ok) throw new Error('Could not read ' + path + ' (' + r.status + ')');
    return as === 'json' ? r.json() : r.blob();
  }
  const J = (job) => '/jobs/' + encodeURIComponent(job.id);
  window.StudioAPI = {
    ready, base: BASE, readOnly: false,
    create: () => call('POST', '/jobs'),
    upload,
    remove: (job, name) => call('DELETE', J(job) + '/files/' + encodeURIComponent(name), job),
    intake: (job, body) => call('PUT', J(job) + '/intake', job, body),
    readCard: (job) => call('POST', J(job) + '/read-card', job),   // D116: the title, location and program read from the sheets
    preview: (job, email) => call('POST', J(job) + '/preview', job, email ? { email } : {}),
    status: (job) => call('GET', J(job), job),
    plan: (job, body) => call('PUT', J(job) + '/plan', job, body),
    building: (job, body) => call('PUT', J(job) + '/building', job, body),
    checkout: (job, tier, email) => call('POST', J(job) + '/checkout', job, { tier, email }),
    redo: (job) => call('POST', J(job) + '/redo', job),
    feedback: (job, body) => call('POST', J(job) + '/feedback', job, body),
    file
  };
})();
