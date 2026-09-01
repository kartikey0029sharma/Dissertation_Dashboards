/**
 * Cloudflare Worker for "Decision-Making with Business Intelligence Dashboards".
 * Newcastle University Business School, MSc Business Analytics (ISO8007).
 *
 * ROUTES
 *   POST /submit      one participant's completed survey, 8 vignette rows
 *   POST /interview   one completed written interview
 *   POST /import      bulk import from a CSV upload, admin key required
 *   GET  /export      the whole of one table as CSV, admin key required
 *   GET  /status      counts and design balance, admin key required
 *   GET  /            liveness only, no key, no data
 *
 * THE ADMIN KEY TRAVELS IN THE `X-Admin-Key` HEADER, NEVER IN THE URL.
 * A query string ends up in browser history and in intermediary logs. The
 * Worker answers CORS preflight properly, which is what makes a header
 * possible here and is not possible on Apps Script.
 *
 * THE STUDY HOLDS NO PERSONAL DATA. No name, no email address, no IP address.
 * `CF-Connecting-IP` is available on every request and is deliberately
 * untouched. A participant who wants the written interview later is given their
 * own reference and an address to write to, rather than handing one over.
 */

import SCHEMA from '../../schema.js';

const { SURVEY_COLS, INTERVIEW_COLS } = SCHEMA;

const MAX_SURVEY_ROWS_PER_SUBMIT = 20;    /* the instrument sends 8 */
const MAX_IMPORT_ROWS_PER_CALL   = 2000;  /* the page chunks below this */
const D1_BATCH_SIZE              = 50;    /* statements per D1 batch */
const REQUIRED_SURVEY_COLS = ['response_id', 'position', 'scenario', 'data_signal', 'accountability'];

/* ------------------------------------------------------------------ CORS */

function corsHeaders(env, request) {
  const allowed = (env.ALLOWED_ORIGIN || '*').trim();
  const origin = request.headers.get('Origin') || '';
  return {
    'Access-Control-Allow-Origin': allowed === '*' ? '*' : (origin === allowed ? origin : allowed),
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Admin-Key',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin'
  };
}

function json(env, request, obj, status) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: Object.assign({ 'Content-Type': 'application/json; charset=utf-8' }, corsHeaders(env, request))
  });
}

function csvResponse(env, request, csv, filename) {
  return new Response(csv, {
    status: 200,
    headers: Object.assign({
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="' + filename + '"'
    }, corsHeaders(env, request))
  });
}

/* --------------------------------------------------------------- helpers */

function isAdmin(request, env) {
  const given = request.headers.get('X-Admin-Key') || '';
  const want = env.ADMIN_KEY || '';
  if (!want || given.length !== want.length) return false;
  /* constant-time-ish compare, so a wrong key does not leak its length by timing */
  let diff = 0;
  for (let i = 0; i < want.length; i++) diff |= given.charCodeAt(i) ^ want.charCodeAt(i);
  return diff === 0;
}

function esc(v) {
  return '"' + String(v === null || v === undefined ? '' : v).replace(/"/g, '""') + '"';
}

function toCsv(cols, rows) {
  const out = [cols.map(esc).join(',')];
  for (const r of rows) out.push(cols.map(c => esc(r[c])).join(','));
  return out.join('\n');
}

function stamp() {
  return new Date().toISOString().replace(/[:.]/g, '-').slice(0, 16);
}

/* Build one INSERT OR REPLACE statement for a table, given a column list. */
function insertSql(table, cols) {
  return 'INSERT OR REPLACE INTO ' + table + ' (' + cols.join(', ') + ') VALUES (' +
         cols.map(() => '?').join(', ') + ')';
}

/* Run many statements in D1 batches, so one huge import does not exceed a
   single batch limit. Returns the number of rows written. */
async function writeRows(env, table, cols, rows) {
  if (!rows.length) return 0;
  const sql = insertSql(table, cols);
  let written = 0;
  for (let i = 0; i < rows.length; i += D1_BATCH_SIZE) {
    const slice = rows.slice(i, i + D1_BATCH_SIZE);
    const stmts = slice.map(r => env.DB.prepare(sql).bind(...cols.map(c => {
      const v = r[c];
      return v === undefined || v === null ? null : (typeof v === 'object' ? JSON.stringify(v) : v);
    })));
    await env.DB.batch(stmts);
    written += slice.length;
  }
  return written;
}

/* Accept either objects keyed by column name, or a header plus arrays. */
function normaliseRows(body) {
  if (Array.isArray(body.rows) && body.rows.length && Array.isArray(body.rows[0])) {
    const header = body.header || [];
    return body.rows.map(arr => {
      const o = {};
      header.forEach((h, i) => { o[h] = arr[i]; });
      return o;
    });
  }
  return Array.isArray(body.rows) ? body.rows : [];
}

/* Keep only the columns the table knows about. Anything else is dropped
   rather than rejected, so a spreadsheet with a stray column still imports. */
function pick(row, cols) {
  const o = {};
  for (const c of cols) if (row[c] !== undefined) o[c] = row[c];
  return o;
}

function validateSurveyRows(rows) {
  if (!rows.length) return 'no rows';
  for (const c of REQUIRED_SURVEY_COLS) {
    if (!(c in rows[0])) return 'missing column ' + c;
  }
  for (const r of rows) {
    if (!r.response_id) return 'a row has no response_id';
    if (r.position === undefined || r.position === '') return 'a row has no position';
  }
  return null;
}

/* R5 minus R4, the blame asymmetry score, computed rather than trusted. */
function asymmetry(row) {
  const a = parseInt(row.R5, 10), b = parseInt(row.R4, 10);
  return (isNaN(a) || isNaN(b)) ? null : String(a - b);   /* string, so a TEXT column does not render it as 4.0 */
}

/* ---------------------------------------------------------------- routes */

async function handleSubmit(request, env, body) {
  const rows = normaliseRows(body);
  if (rows.length > MAX_SURVEY_ROWS_PER_SUBMIT) return json(env, request, { ok: false, error: 'too many rows' }, 400);
  const bad = validateSurveyRows(rows);
  if (bad) return json(env, request, { ok: false, error: bad }, 400);
  const n = await writeRows(env, 'survey', SURVEY_COLS, rows.map(r => pick(r, SURVEY_COLS)));
  return json(env, request, { ok: true, id: rows[0].response_id, saved: n });
}

async function handleInterview(request, env, body) {
  const row = body.row || body;
  if (!row || !row.response_id) return json(env, request, { ok: false, error: 'no response_id' }, 400);
  const clean = pick(row, INTERVIEW_COLS);
  clean.blame_asymmetry_R5_minus_R4 = asymmetry(clean);
  if (!clean.submitted_at) clean.submitted_at = new Date().toISOString();
  await writeRows(env, 'interview', INTERVIEW_COLS, [clean]);
  return json(env, request, { ok: true, id: clean.response_id });
}

/* Bulk import. One call may carry a chunk of a much larger file; the
   researcher page splits it and calls repeatedly. Interview values are
   expected to repeat on every row of a participant, so the first non-empty
   value per response_id wins. */
async function handleImport(request, env, body) {
  if (!isAdmin(request, env)) return json(env, request, { ok: false, error: 'admin key required' }, 401);

  const rows = normaliseRows(body);
  if (!rows.length) return json(env, request, { ok: false, error: 'no rows' }, 400);
  if (rows.length > MAX_IMPORT_ROWS_PER_CALL) return json(env, request, { ok: false, error: 'chunk too large' }, 400);

  const bad = validateSurveyRows(rows);
  if (bad) return json(env, request, { ok: false, error: bad }, 400);

  const surveyRows = rows.map(r => {
    const o = pick(r, SURVEY_COLS);
    if (!o.data_status) o.data_status = 'IMPORTED';
    return o;
  });
  const surveyWritten = await writeRows(env, 'survey', SURVEY_COLS, surveyRows);

  /* collapse the repeated interview columns down to one row per participant */
  let interviewWritten = 0;
  const hasInterview = INTERVIEW_COLS.some(c => c !== 'response_id' && c in rows[0]);
  if (hasInterview) {
    const byId = new Map();
    for (const r of rows) {
      const id = r.response_id;
      if (!byId.has(id)) byId.set(id, { response_id: id });
      const target = byId.get(id);
      for (const c of INTERVIEW_COLS) {
        if (c === 'response_id') continue;
        const v = r[c];
        if (v !== undefined && v !== null && String(v).trim() !== '' &&
            (target[c] === undefined || String(target[c]).trim() === '')) {
          target[c] = v;
        }
      }
    }
    /* only keep participants who actually have interview content */
    const meaningful = [...byId.values()].filter(o =>
      Object.keys(o).some(k => k !== 'response_id' && String(o[k]).trim() !== ''));
    for (const o of meaningful) {
      o.blame_asymmetry_R5_minus_R4 = asymmetry(o);
      if (!o.interview_mode) o.interview_mode = 'imported';
      if (!o.submitted_at) o.submitted_at = new Date().toISOString();
    }
    interviewWritten = await writeRows(env, 'interview', INTERVIEW_COLS, meaningful);
  }

  const participants = new Set(rows.map(r => r.response_id)).size;
  return json(env, request, {
    ok: true, participants: participants,
    survey_rows: surveyWritten, interview_rows: interviewWritten
  });
}

async function handleExport(request, env, url) {
  if (!isAdmin(request, env)) return json(env, request, { ok: false, error: 'admin key required' }, 401);
  const type = (url.searchParams.get('type') || 'survey').toLowerCase();

  if (type === 'survey' || type === 'interview') {
    const cols = type === 'survey' ? SURVEY_COLS : INTERVIEW_COLS;
    const order = type === 'survey' ? 'response_id, position' : 'response_id';
    const res = await env.DB.prepare('SELECT * FROM ' + type + ' ORDER BY ' + order).all();
    return csvResponse(env, request, toCsv(cols, res.results || []),
      'dashboard_study_' + type + '_' + stamp() + '.csv');
  }

  if (type === 'combined') {
    /* survey rows with the participant's interview values repeated on each,
       which is the same shape as the combined upload template */
    const s = await env.DB.prepare('SELECT * FROM survey ORDER BY response_id, position').all();
    const i = await env.DB.prepare('SELECT * FROM interview').all();
    const ivById = new Map((i.results || []).map(r => [r.response_id, r]));
    const ivCols = INTERVIEW_COLS.filter(c => c !== 'response_id');
    const merged = (s.results || []).map(r => {
      const iv = ivById.get(r.response_id) || {};
      const o = Object.assign({}, r);
      for (const c of ivCols) o[c] = iv[c] === undefined ? '' : iv[c];
      return o;
    });
    return csvResponse(env, request, toCsv(SURVEY_COLS.concat(ivCols), merged),
      'dashboard_study_combined_' + stamp() + '.csv');
  }

  return json(env, request, { ok: false, error: 'unknown type' }, 400);
}

async function handleStatus(request, env) {
  if (!isAdmin(request, env)) return json(env, request, { ok: false, error: 'admin key required' }, 401);

  const cells = await env.DB.prepare(
    'SELECT data_signal, accountability, COUNT(*) AS n FROM survey GROUP BY data_signal, accountability').all();
  const counts = await env.DB.prepare(
    'SELECT (SELECT COUNT(DISTINCT response_id) FROM survey)   AS participants,' +
    '       (SELECT COUNT(*) FROM survey)                      AS rows,' +
    '       (SELECT COUNT(*) FROM interview)                   AS interviews,' +
    '       (SELECT MAX(submitted) FROM survey)                AS last_received').first();

  const cellMap = {};
  for (const r of (cells.results || [])) cellMap[r.data_signal + '/' + r.accountability] = r.n;

  const modes = await env.DB.prepare(
    'SELECT interview_mode, COUNT(*) AS n FROM interview GROUP BY interview_mode').all();
  const modeMap = {};
  for (const r of (modes.results || [])) modeMap[r.interview_mode || 'unknown'] = r.n;

  return json(env, request, {
    ok: true,
    participants: counts ? counts.participants : 0,
    rows: counts ? counts.rows : 0,
    interviews: counts ? counts.interviews : 0,
    last_received: counts ? counts.last_received : null,
    cells: cellMap,
    interview_modes: modeMap
  });
}

/* ----------------------------------------------------------------- entry */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(env, request) });
    }

    try {
      if (request.method === 'GET') {
        if (path === '/export') return await handleExport(request, env, url);
        if (path === '/status') return await handleStatus(request, env);
        return json(env, request, { ok: true, status: 'endpoint live' });
      }

      if (request.method === 'POST') {
        let body;
        try { body = await request.json(); }
        catch (e) { return json(env, request, { ok: false, error: 'body is not JSON' }, 400); }

        if (path === '/submit')    return await handleSubmit(request, env, body);
        if (path === '/interview') return await handleInterview(request, env, body);
        if (path === '/import')    return await handleImport(request, env, body);
        return json(env, request, { ok: false, error: 'unknown route' }, 404);
      }

      return json(env, request, { ok: false, error: 'method not allowed' }, 405);
    } catch (err) {
      return json(env, request, { ok: false, error: String(err && err.message || err) }, 500);
    }
  }
};
