#!/usr/bin/env node
/**
 * LOCAL HOST FOR THE STUDY
 *
 * Serves the instrument, the researcher page and the whole API from one port,
 * with no account, no install and no internet connection. Run it with:
 *
 *     node local-server.js
 *
 * then open http://localhost:8787 for the survey and
 * http://localhost:8787/admin.html for the researcher tools.
 *
 * WHY THIS EXISTS. The Cloudflare Worker is the intended store, but it needs an
 * account and a deploy. This file speaks exactly the same routes and returns
 * exactly the same JSON, so everything can be tested end to end first, and the
 * only thing that changes on the way to Cloudflare is the endpoint in config.js.
 *
 * STORAGE. Three newline-delimited JSON files under ./local-data/. No database
 * and no dependencies, so this runs on any Node 18 or later. Open the files in
 * a text editor if you want to see exactly what was recorded. Rows are keyed
 * the same way the D1 tables are, so re-sending a response replaces it rather
 * than duplicating it.
 *
 * THIS IS NOT FOR REAL PARTICIPANTS. It listens on localhost only, so nobody
 * else can reach it. Use it to rehearse the study and to check the data comes
 * out in the right shape.
 */

const http = require('http');
const fs   = require('fs');
const path = require('path');

const SCHEMA = require('./schema.js');
const { SURVEY_COLS, INTERVIEW_COLS } = SCHEMA;

const PORT      = Number(process.env.PORT || 8787);
const DATA_DIR  = path.join(__dirname, 'local-data');
const ADMIN_KEY = process.env.ADMIN_KEY || 'local-dev-key';
const MAX_SURVEY_ROWS_PER_SUBMIT = 20;
const MAX_IMPORT_ROWS_PER_CALL   = 2000;
const REQUIRED_SURVEY_COLS = ['response_id', 'position', 'scenario', 'data_signal', 'accountability'];

/* ------------------------------------------------------------- the store */

const TABLES = {
  survey:    { cols: SURVEY_COLS,    key: r => r.response_id + '|' + r.position },
  interview: { cols: INTERVIEW_COLS, key: r => r.response_id }
};
const store = {};

function fileFor(name) { return path.join(DATA_DIR, name + '.ndjson'); }

function load() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  for (const name of Object.keys(TABLES)) {
    store[name] = new Map();
    const f = fileFor(name);
    if (!fs.existsSync(f)) continue;
    let bad = 0;
    for (const line of fs.readFileSync(f, 'utf8').split('\n')) {
      if (!line.trim()) continue;
      try { const r = JSON.parse(line); store[name].set(TABLES[name].key(r), r); }
      catch (e) { bad++; }
    }
    if (bad) console.log('  note: skipped ' + bad + ' unreadable line(s) in ' + name + '.ndjson');
  }
}

function persist(name) {
  const lines = [...store[name].values()].map(r => JSON.stringify(r)).join('\n');
  fs.writeFileSync(fileFor(name), lines ? lines + '\n' : '');
}

function put(name, rows) {
  const t = TABLES[name];
  for (const r of rows) {
    const clean = {};
    for (const c of t.cols) clean[c] = r[c] === undefined || r[c] === null ? '' : String(r[c]);
    store[name].set(t.key(clean), clean);
  }
  persist(name);
  return rows.length;
}

/* --------------------------------------------------------------- helpers */

function esc(v) { return '"' + String(v === null || v === undefined ? '' : v).replace(/"/g, '""') + '"'; }
function toCsv(cols, rows) {
  return [cols.map(esc).join(',')].concat(rows.map(r => cols.map(c => esc(r[c])).join(','))).join('\n');
}
function pick(row, cols) {
  const o = {};
  for (const c of cols) if (row[c] !== undefined) o[c] = row[c];
  return o;
}
function normaliseRows(body) {
  if (Array.isArray(body.rows) && body.rows.length && Array.isArray(body.rows[0])) {
    const header = body.header || [];
    return body.rows.map(arr => { const o = {}; header.forEach((h, i) => { o[h] = arr[i]; }); return o; });
  }
  return Array.isArray(body.rows) ? body.rows : [];
}
function validateSurveyRows(rows) {
  if (!rows.length) return 'no rows';
  for (const c of REQUIRED_SURVEY_COLS) if (!(c in rows[0])) return 'missing column ' + c;
  for (const r of rows) {
    if (!r.response_id) return 'a row has no response_id';
    if (r.position === undefined || r.position === '') return 'a row has no position';
  }
  return null;
}
function asymmetry(row) {
  const a = parseInt(row.R5, 10), b = parseInt(row.R4, 10);
  return (isNaN(a) || isNaN(b)) ? '' : String(a - b);
}
function sortRows(name) {
  const rows = [...store[name].values()];
  if (name === 'survey') {
    rows.sort((x, y) => x.response_id.localeCompare(y.response_id) || (+x.position) - (+y.position));
  } else {
    rows.sort((x, y) => x.response_id.localeCompare(y.response_id));
  }
  return rows;
}

function send(res, status, body, headers) {
  res.writeHead(status, Object.assign({ 'Cache-Control': 'no-store' }, headers || {}));
  res.end(body);
}
function sendJson(res, obj, status) {
  send(res, status || 200, JSON.stringify(obj), { 'Content-Type': 'application/json; charset=utf-8' });
}
function isAdmin(req) { return (req.headers['x-admin-key'] || '') === ADMIN_KEY; }

/* ---------------------------------------------------------------- routes */

function handleSubmit(res, body) {
  const rows = normaliseRows(body);
  if (rows.length > MAX_SURVEY_ROWS_PER_SUBMIT) return sendJson(res, { ok: false, error: 'too many rows' }, 400);
  const bad = validateSurveyRows(rows);
  if (bad) return sendJson(res, { ok: false, error: bad }, 400);
  const n = put('survey', rows.map(r => pick(r, SURVEY_COLS)));
  console.log('  survey    ' + rows[0].response_id + '  ' + n + ' rows');
  sendJson(res, { ok: true, id: rows[0].response_id, saved: n });
}

function handleInterview(res, body) {
  const row = body.row || body;
  if (!row || !row.response_id) return sendJson(res, { ok: false, error: 'no response_id' }, 400);
  const clean = pick(row, INTERVIEW_COLS);
  clean.blame_asymmetry_R5_minus_R4 = asymmetry(clean);
  if (!clean.submitted_at) clean.submitted_at = new Date().toISOString();
  put('interview', [clean]);
  console.log('  interview ' + clean.response_id + '  mode ' + (clean.interview_mode || '?'));
  sendJson(res, { ok: true, id: clean.response_id });
}

function handleImport(req, res, body) {
  if (!isAdmin(req)) return sendJson(res, { ok: false, error: 'admin key required' }, 401);
  const rows = normaliseRows(body);
  if (!rows.length) return sendJson(res, { ok: false, error: 'no rows' }, 400);
  if (rows.length > MAX_IMPORT_ROWS_PER_CALL) return sendJson(res, { ok: false, error: 'chunk too large' }, 400);
  const bad = validateSurveyRows(rows);
  if (bad) return sendJson(res, { ok: false, error: bad }, 400);

  const surveyRows = rows.map(r => {
    const o = pick(r, SURVEY_COLS);
    if (!o.data_status) o.data_status = 'IMPORTED';
    return o;
  });
  const surveyWritten = put('survey', surveyRows);

  let interviewWritten = 0;
  const hasInterview = INTERVIEW_COLS.some(c => c !== 'response_id' && c in rows[0]);
  if (hasInterview) {
    const byId = new Map();
    for (const r of rows) {
      if (!byId.has(r.response_id)) byId.set(r.response_id, { response_id: r.response_id });
      const t = byId.get(r.response_id);
      for (const c of INTERVIEW_COLS) {
        if (c === 'response_id') continue;
        const v = r[c];
        if (v !== undefined && v !== null && String(v).trim() !== '' &&
            (t[c] === undefined || String(t[c]).trim() === '')) t[c] = v;
      }
    }
    const meaningful = [...byId.values()].filter(o =>
      Object.keys(o).some(k => k !== 'response_id' && String(o[k]).trim() !== ''));
    for (const o of meaningful) {
      o.blame_asymmetry_R5_minus_R4 = asymmetry(o);
      if (!o.interview_mode) o.interview_mode = 'imported';
      if (!o.submitted_at) o.submitted_at = new Date().toISOString();
    }
    interviewWritten = meaningful.length ? put('interview', meaningful) : 0;
  }

  const participants = new Set(rows.map(r => r.response_id)).size;
  console.log('  import    ' + participants + ' participants, ' + surveyWritten + ' survey rows, ' +
              interviewWritten + ' interviews');
  sendJson(res, { ok: true, participants, survey_rows: surveyWritten, interview_rows: interviewWritten });
}

function handleExport(req, res, url) {
  if (!isAdmin(req)) return sendJson(res, { ok: false, error: 'admin key required' }, 401);
  const type = (url.searchParams.get('type') || 'survey').toLowerCase();
  const when = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 16);

  if (type === 'survey' || type === 'interview') {
    const cols = type === 'survey' ? SURVEY_COLS : INTERVIEW_COLS;
    return send(res, 200, toCsv(cols, sortRows(type)), {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="dashboard_study_' + type + '_' + when + '.csv"'
    });
  }
  if (type === 'combined') {
    const ivCols = INTERVIEW_COLS.filter(c => c !== 'response_id');
    const merged = sortRows('survey').map(r => {
      const iv = store.interview.get(r.response_id) || {};
      const o = Object.assign({}, r);
      for (const c of ivCols) o[c] = iv[c] === undefined ? '' : iv[c];
      return o;
    });
    return send(res, 200, toCsv(SURVEY_COLS.concat(ivCols), merged), {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="dashboard_study_combined_' + when + '.csv"'
    });
  }
  sendJson(res, { ok: false, error: 'unknown type' }, 400);
}

function handleStatus(req, res) {
  if (!isAdmin(req)) return sendJson(res, { ok: false, error: 'admin key required' }, 401);
  const survey = [...store.survey.values()];
  const cells = {}, modes = {};
  for (const r of survey) {
    const k = r.data_signal + '/' + r.accountability;
    cells[k] = (cells[k] || 0) + 1;
  }
  for (const r of store.interview.values()) {
    const k = r.interview_mode || 'unknown';
    modes[k] = (modes[k] || 0) + 1;
  }
  const last = survey.map(r => r.submitted).filter(Boolean).sort().pop() || null;
  sendJson(res, {
    ok: true,
    participants: new Set(survey.map(r => r.response_id)).size,
    rows: survey.length,
    interviews: store.interview.size,
    last_received: last,
    cells: cells,
    interview_modes: modes
  });
}

/* --------------------------------------------------------- static files */

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
               '.css': 'text/css; charset=utf-8', '.csv': 'text/csv; charset=utf-8',
               '.png': 'image/png', '.svg': 'image/svg+xml', '.json': 'application/json',
               '.md': 'text/markdown; charset=utf-8' };

function serveStatic(res, pathname) {
  let rel = pathname === '/' ? '/index.html' : pathname;
  rel = rel.replace(/\.\./g, '');                       /* no climbing out */
  const file = path.resolve(__dirname, '.' + rel);

  /* The collected data sits inside the served folder, so it has to be refused
     explicitly. Without this, /local-data/interview.ndjson would hand out every
     written answer to anything on this machine that asked for it. */
  const inDataDir = file === DATA_DIR || file.startsWith(DATA_DIR + path.sep);
  if (inDataDir || file.endsWith('.ndjson')) {
    return send(res, 404, 'Not found', { 'Content-Type': 'text/plain' });
  }

  if (!file.startsWith(__dirname) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    return send(res, 404, 'Not found', { 'Content-Type': 'text/plain' });
  }
  send(res, 200, fs.readFileSync(file), { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream' });
}

/* ----------------------------------------------------------------- serve */

load();

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost:' + PORT);
  const p = url.pathname.replace(/\/+$/, '') || '/';

  /* Same origin serves both the pages and the API, so no CORS is involved.
     The headers are here anyway in case the pages are opened from a file. */
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Key');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  if (req.method === 'OPTIONS') return send(res, 204, '');

  if (req.method === 'GET') {
    if (p === '/status') return handleStatus(req, res);
    if (p === '/export') return handleExport(req, res, url);
    return serveStatic(res, p === '/' ? '/' : p);
  }

  if (req.method === 'POST') {
    let raw = '';
    req.on('data', c => { raw += c; if (raw.length > 20e6) req.destroy(); });
    req.on('end', () => {
      let body;
      try { body = JSON.parse(raw); }
      catch (e) { return sendJson(res, { ok: false, error: 'body is not JSON' }, 400); }
      try {
        if (p === '/submit')    return handleSubmit(res, body);
        if (p === '/interview') return handleInterview(res, body);
        if (p === '/import')    return handleImport(req, res, body);
        sendJson(res, { ok: false, error: 'unknown route' }, 404);
      } catch (err) {
        sendJson(res, { ok: false, error: String(err && err.message || err) }, 500);
      }
    });
    return;
  }

  sendJson(res, { ok: false, error: 'method not allowed' }, 405);
});

/* A friendly message beats a stack trace when the port is already taken, which
   is what happens if the launcher is double-clicked twice. */
server.on('error', err => {
  if (err && err.code === 'EADDRINUSE') {
    console.log('');
    console.log('  Port ' + PORT + ' is already in use.');
    console.log('  The study is probably already running: try http://localhost:' + PORT + '/');
    console.log('  To use a different port instead:  PORT=8788 node local-server.js');
    console.log('');
    process.exit(1);
  }
  throw err;
});

server.listen(PORT, '127.0.0.1', () => {
  const counts = Object.keys(TABLES).map(n => n + ' ' + store[n].size).join(', ');
  console.log('');
  console.log('  Dashboard study, running locally');
  console.log('  ---------------------------------------------------------');
  console.log('  Survey            http://localhost:' + PORT + '/');
  console.log('  Researcher tools  http://localhost:' + PORT + '/admin.html');
  console.log('');
  console.log('  Endpoint to paste on the researcher page:  http://localhost:' + PORT);
  console.log('  Admin key:                                 ' + ADMIN_KEY);
  console.log('');
  console.log('  Data files        ' + DATA_DIR);
  console.log('  Already holding   ' + counts);
  console.log('  Listening on localhost only. Press Ctrl and C to stop.');
  console.log('');
});
