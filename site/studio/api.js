/* Studio FGA: the few calls the page makes to the Studio API (server/README.md, "API (for the front end)").
   The address comes from config.js (window.STUDIO_API). Every /jobs/{id} call carries the job's key as the
   X-Job-Token header. Answers are {ok, status, data}; data.error is the server's plain message. */
(function () {
  'use strict';
  const BASE = String(window.STUDIO_API || '').replace(/\/+$/, '');
  const ready = /^https?:\/\//.test(BASE) && !/REPLACE/i.test(BASE);

  async function call(method, path, job, body) {
    const h = {};
    if (job) h['X-Job-Token'] = job.t;
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
    const r = await fetch(BASE + '/jobs/' + encodeURIComponent(job.id) + '/download/' + path, { headers: { 'X-Job-Token': job.t } });
    if (!r.ok) throw new Error('Could not read ' + path + ' (' + r.status + ')');
    return as === 'json' ? r.json() : r.blob();
  }
  const J = (job) => '/jobs/' + encodeURIComponent(job.id);
  window.StudioAPI = {
    ready, base: BASE,
    create: () => call('POST', '/jobs'),
    upload,
    remove: (job, name) => call('DELETE', J(job) + '/files/' + encodeURIComponent(name), job),
    intake: (job, body) => call('PUT', J(job) + '/intake', job, body),
    preview: (job, email) => call('POST', J(job) + '/preview', job, email ? { email } : {}),
    status: (job) => call('GET', J(job), job),
    plan: (job, body) => call('PUT', J(job) + '/plan', job, body),
    checkout: (job, tier, email) => call('POST', J(job) + '/checkout', job, { tier, email }),
    redo: (job) => call('POST', J(job) + '/redo', job),
    feedback: (job, body) => call('POST', J(job) + '/feedback', job, body),
    file
  };
})();
