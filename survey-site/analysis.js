/* ============================================================================
   ANALYSIS FOR THE DASHBOARD DECISION STUDY

   Takes the survey and interview rows exactly as they come out of the store and
   produces the computations the dissertation actually needs, plus the charts.
   No libraries: the statistics and the SVG are both written out here so that
   every number on the screen can be traced to a line of code.

   WHAT THIS IS, AND WHAT IT IS NOT
   This is a descriptive and preliminary dashboard. The confirmatory model in the
   methodology is a GEE logistic regression with participant as the cluster, and
   that belongs in R or SPSS on the exported CSV. What is computed here is the
   within-person paired contrast, which is the honest companion to that model for
   a fully within-subjects design: each participant is their own control, so the
   participant random effect cancels out of the difference. It is conservative
   rather than clever, and it will not disagree with a correctly specified GEE on
   the main effects.

   EXCLUSIONS are applied before anything is computed and are always reported, so
   the analytic N on screen is never a mystery.
   ========================================================================= */
(function (root) {

  /* ------------------------------------------------------------ formatting */
  const pct  = v => (v === null || isNaN(v)) ? '—' : (100 * v).toFixed(1) + '%';
  const num  = (v, d) => (v === null || v === undefined || isNaN(v)) ? '—' : (+v).toFixed(d === undefined ? 2 : d);
  const pval = p => p === null || isNaN(p) ? '—' : (p < 0.001 ? 'p < .001' : 'p = ' + p.toFixed(3).replace(/^0/, ''));
  const esc  = s => String(s === null || s === undefined ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  /* ------------------------------------------------------------ statistics */
  function mean(a) { return a.length ? a.reduce((x, y) => x + y, 0) / a.length : null; }
  function sd(a) {
    if (a.length < 2) return null;
    const m = mean(a);
    return Math.sqrt(a.reduce((s, x) => s + (x - m) * (x - m), 0) / (a.length - 1));
  }
  function median(a) {
    if (!a.length) return null;
    const s = [...a].sort((x, y) => x - y), i = Math.floor(s.length / 2);
    return s.length % 2 ? s[i] : (s[i - 1] + s[i]) / 2;
  }

  /* Regularised incomplete beta, by the continued fraction in Numerical
     Recipes. Needed for an exact two-sided p from Student's t; a normal
     approximation would be wrong at the sample sizes this study will have. */
  function logGamma(x) {
    const c = [76.18009172947146, -86.50532032941677, 24.01409824083091,
               -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5];
    let y = x, t = x + 5.5, s = 1.000000000190015;
    t -= (x + 0.5) * Math.log(t);
    for (let j = 0; j < 6; j++) s += c[j] / ++y;
    return -t + Math.log(2.5066282746310005 * s / x);
  }
  function betacf(a, b, x) {
    const FPMIN = 1e-30, EPS = 3e-12;
    let qab = a + b, qap = a + 1, qam = a - 1, c = 1, d = 1 - qab * x / qap;
    if (Math.abs(d) < FPMIN) d = FPMIN;
    d = 1 / d;
    let h = d;
    for (let m = 1; m <= 200; m++) {
      const m2 = 2 * m;
      let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
      d = 1 + aa * d; if (Math.abs(d) < FPMIN) d = FPMIN;
      c = 1 + aa / c; if (Math.abs(c) < FPMIN) c = FPMIN;
      d = 1 / d; h *= d * c;
      aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
      d = 1 + aa * d; if (Math.abs(d) < FPMIN) d = FPMIN;
      c = 1 + aa / c; if (Math.abs(c) < FPMIN) c = FPMIN;
      d = 1 / d;
      const del = d * c; h *= del;
      if (Math.abs(del - 1) < EPS) break;
    }
    return h;
  }
  function betai(a, b, x) {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    const bt = Math.exp(logGamma(a + b) - logGamma(a) - logGamma(b) + a * Math.log(x) + b * Math.log(1 - x));
    return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
  }
  function tTwoSided(t, df) {
    if (!isFinite(t) || df <= 0) return null;
    return betai(df / 2, 0.5, df / (df + t * t));
  }
  /* 97.5th percentile of t, found by bisection, for the 95% interval */
  function tCrit(df) {
    let lo = 0, hi = 100;
    for (let i = 0; i < 80; i++) {
      const mid = (lo + hi) / 2;
      if (tTwoSided(mid, df) > 0.05) lo = mid; else hi = mid;
    }
    return (lo + hi) / 2;
  }

  /* One-sample t on a set of within-person differences. */
  function pairedT(diffs) {
    const n = diffs.length;
    if (n < 2) return { n, mean: mean(diffs), sd: null, se: null, lo: null, hi: null, t: null, df: null, p: null, dz: null };
    const m = mean(diffs), s = sd(diffs), se = s / Math.sqrt(n), df = n - 1;
    const t = se === 0 ? null : m / se, c = tCrit(df);
    return {
      n, mean: m, sd: s, se, df,
      lo: m - c * se, hi: m + c * se,
      t, p: t === null ? null : tTwoSided(t, df),
      dz: s === 0 ? null : m / s
    };
  }

  function pearson(xs, ys) {
    const n = xs.length;
    if (n < 3) return { n, r: null, p: null };
    const mx = mean(xs), my = mean(ys);
    let sxy = 0, sxx = 0, syy = 0;
    for (let i = 0; i < n; i++) {
      const a = xs[i] - mx, b = ys[i] - my;
      sxy += a * b; sxx += a * a; syy += b * b;
    }
    if (sxx === 0 || syy === 0) return { n, r: null, p: null };
    const r = sxy / Math.sqrt(sxx * syy), df = n - 2;
    const t = r * Math.sqrt(df / (1 - r * r));
    return { n, r, p: tTwoSided(t, df) };
  }

  /* ------------------------------------------------------------- computing */
  const N = v => { const x = parseFloat(v); return isNaN(x) ? null : x; };

  function computeAnalysis(surveyRows, interviewRows, opts) {
    const o = Object.assign({ minMedianSeconds: 10, requireAttention: true }, opts || {});

    /* ---- assemble participants -------------------------------------- */
    const byId = new Map();
    for (const r of surveyRows) {
      const id = r.response_id;
      if (!id) continue;
      if (!byId.has(id)) byId.set(id, { id, rows: [] });
      byId.get(id).rows.push(r);
    }

    const people = [...byId.values()].map(p => {
      const secs = p.rows.map(r => N(r.seconds_on_page)).filter(v => v !== null);
      const pass = Math.max(...p.rows.map(r => N(r.attn_pass) || 0));
      const total = Math.max(...p.rows.map(r => N(r.attn_total) || 0));
      p.nRows = p.rows.length;
      p.medianSeconds = median(secs);
      p.attnPass = pass; p.attnTotal = total;
      p.failedAttention = total > 0 && pass < total;
      p.tooFast = p.medianSeconds !== null && p.medianSeconds < o.minMedianSeconds;
      p.excluded = (o.requireAttention && p.failedAttention) || p.tooFast;
      p.reason = p.failedAttention ? 'attention check' : (p.tooFast ? 'implausibly fast' : '');
      p.version = p.rows[0].version;
      p.demo = p.rows[0];
      return p;
    });

    const kept = people.filter(p => !p.excluded);
    const obs = kept.reduce((s, p) => s + p.nRows, 0);

    /* ---- cell and marginal rates ------------------------------------ */
    function rate(rows, field) {
      const v = rows.map(r => N(r[field])).filter(x => x !== null);
      return v.length ? { rate: mean(v), n: v.length } : { rate: null, n: 0 };
    }
    const allRows = kept.flatMap(p => p.rows);
    const sel = (sig, acc) => allRows.filter(r =>
      (sig === null || r.data_signal === sig) && (acc === null || r.accountability === acc));

    const marg = {
      overall:    rate(allRows, 'over_reliance'),
      hidden:     rate(sel('hidden', null), 'over_reliance'),
      visible:    rate(sel('visible', null), 'over_reliance'),
      auditable:  rate(sel(null, 'auditable'), 'over_reliance'),
      own:        rate(sel(null, 'own'), 'over_reliance')
    };
    const cells = {};
    for (const sig of ['hidden', 'visible']) for (const acc of ['auditable', 'own']) {
      cells[sig + '/' + acc] = rate(sel(sig, acc), 'over_reliance');
    }
    const accuracy = {
      overall:  rate(allRows, 'accuracy'),
      hidden:   rate(sel('hidden', null), 'accuracy'),
      visible:  rate(sel('visible', null), 'accuracy')
    };
    const verify = {
      overall:  rate(allRows, 'verification_intent'),
      hidden:   rate(sel('hidden', null), 'verification_intent'),
      visible:  rate(sel('visible', null), 'verification_intent'),
      auditable: rate(sel(null, 'auditable'), 'verification_intent'),
      own:      rate(sel(null, 'own'), 'verification_intent')
    };
    const confidence = {
      hidden:  mean(sel('hidden', null).map(r => N(r.confidence)).filter(v => v !== null)),
      visible: mean(sel('visible', null).map(r => N(r.confidence)).filter(v => v !== null))
    };

    /* ---- within-person contrasts ------------------------------------
       A participant enters a test only if they have at least one observation at
       each level of that factor, which is what a paired contrast requires. */
    function withinDiff(field, levelA, levelB, outcome) {
      const diffs = [];
      for (const p of kept) {
        const a = p.rows.filter(r => r[field] === levelA).map(r => N(r[outcome])).filter(v => v !== null);
        const b = p.rows.filter(r => r[field] === levelB).map(r => N(r[outcome])).filter(v => v !== null);
        if (a.length && b.length) diffs.push(mean(a) - mean(b));
      }
      return pairedT(diffs);
    }
    function withinInteraction(outcome) {
      const diffs = [];
      for (const p of kept) {
        const g = (s, a) => p.rows.filter(r => r.data_signal === s && r.accountability === a)
          .map(r => N(r[outcome])).filter(v => v !== null);
        const ha = g('hidden', 'auditable'), ho = g('hidden', 'own');
        const va = g('visible', 'auditable'), vo = g('visible', 'own');
        if (ha.length && ho.length && va.length && vo.length) {
          diffs.push((mean(ha) - mean(va)) - (mean(ho) - mean(vo)));
        }
      }
      return pairedT(diffs);
    }

    const tests = [
      { key: 'H1', label: 'Hidden fault raises over-reliance',
        detail: 'hidden minus visible, over-reliance',
        res: withinDiff('data_signal', 'hidden', 'visible', 'over_reliance') },
      { key: 'H2', label: 'Auditable framing raises over-reliance',
        detail: 'auditable minus own judgement, over-reliance',
        res: withinDiff('accountability', 'auditable', 'own', 'over_reliance') },
      { key: 'H1a', label: 'Hidden fault lowers accuracy',
        detail: 'hidden minus visible, accuracy',
        res: withinDiff('data_signal', 'hidden', 'visible', 'accuracy') },
      { key: 'H1b', label: 'Hidden fault lowers verification intent',
        detail: 'hidden minus visible, asked for more before acting',
        res: withinDiff('data_signal', 'hidden', 'visible', 'verification_intent') },
      { key: 'H3', label: 'Signal by accountability interaction',
        detail: 'difference in differences, over-reliance. Exploratory: underpowered by design',
        res: withinInteraction('over_reliance') }
    ];

    /* ---- option generation, asked on a random three of eight --------- */
    const optRows = allRows.filter(r => N(r.options_asked) === 1);
    const optionCount = {
      n: optRows.length,
      hidden: mean(optRows.filter(r => r.data_signal === 'hidden').map(r => N(r.options_generated)).filter(v => v !== null)),
      visible: mean(optRows.filter(r => r.data_signal === 'visible').map(r => N(r.options_generated)).filter(v => v !== null)),
      auditable: mean(optRows.filter(r => r.accountability === 'auditable').map(r => N(r.options_generated)).filter(v => v !== null)),
      own: mean(optRows.filter(r => r.accountability === 'own').map(r => N(r.options_generated)).filter(v => v !== null))
    };

    /* ---- experience as a moderator, descriptive only ----------------- */
    const expOrder = ['Less than 2 years', '2 to 4 years', '5 to 9 years', '10 to 14 years', '15 years or more'];
    const byExperience = expOrder.map(band => {
      const rows = allRows.filter(r => r.experience === band);
      return {
        band,
        n: new Set(rows.map(r => r.response_id)).size,
        hidden: rate(rows.filter(r => r.data_signal === 'hidden'), 'over_reliance').rate,
        visible: rate(rows.filter(r => r.data_signal === 'visible'), 'over_reliance').rate
      };
    }).filter(b => b.n > 0);

    /* ---- design integrity -------------------------------------------- */
    const cellCounts = {};
    for (const r of allRows) {
      const k = r.data_signal + '/' + r.accountability;
      cellCounts[k] = (cellCounts[k] || 0) + 1;
    }
    const versions = {};
    for (const p of kept) versions[p.version] = (versions[p.version] || 0) + 1;

    const scenarios = [...new Set(allRows.map(r => r.scenario))].sort();
    const cellKeys = ['hidden/auditable', 'hidden/own', 'visible/auditable', 'visible/own'];
    const scenarioGrid = scenarios.map(sc => ({
      scenario: sc,
      counts: cellKeys.map(k => allRows.filter(r =>
        r.scenario === sc && (r.data_signal + '/' + r.accountability) === k).length)
    }));

    const mcImmediate = rate(kept.map(p => p.rows[0]), 'mc_immediate_correct');
    const mcCount     = rate(kept.map(p => p.rows[0]), 'mc_count_correct');
    const suspicion   = rate(kept.map(p => p.rows[0]), 'suspicion_pattern');

    /* ---- sample description ------------------------------------------ */
    /* dissent_route and analytics_familiarity are stored as the index of the
       chosen option, so they are mapped back to words before being tallied. */
    const DISSENT = ['Formal route, and it is used', 'Route on paper, rarely used',
                     'No formal route exists', 'Do not know'];
    function label(field, v) {
      if (field === 'dissent_route') { const i = parseInt(v, 10); return DISSENT[i] || 'Not given'; }
      return (v === '' || v === undefined || v === null) ? 'Not given' : v;
    }
    function tally(field) {
      const t = {};
      for (const p of kept) { const v = label(field, p.demo[field]); t[v] = (t[v] || 0) + 1; }
      return Object.entries(t).sort((a, b) => b[1] - a[1]);
    }

    /* ---- the written interview strand -------------------------------- */
    const iv = (interviewRows || []).filter(r => r.response_id);
    const ivKept = iv.filter(r => kept.some(p => p.id === r.response_id));
    const ratingMeans = ['R1','R2','R3','R4','R5','R6','R7','R8'].map(k => ({
      key: k,
      mean: mean(ivKept.map(r => N(r[k])).filter(v => v !== null)),
      n: ivKept.map(r => N(r[k])).filter(v => v !== null).length
    }));
    const asym = ivKept.map(r => N(r.blame_asymmetry_R5_minus_R4)).filter(v => v !== null);
    const r3 = [], asymPaired = [];
    for (const r of ivKept) {
      const a = N(r.R3), b = N(r.blame_asymmetry_R5_minus_R4);
      if (a !== null && b !== null) { r3.push(a); asymPaired.push(b); }
    }
    const codingFields = ['fault_detected','objection_raised','objection_recorded','objection_answered','outcome'];
    const coded = codingFields.map(f => ({
      field: f, done: ivKept.filter(r => String(r[f] || '').trim() !== '').length
    }));
    const ivModes = {};
    for (const r of ivKept) { const m = r.interview_mode || 'unknown'; ivModes[m] = (ivModes[m] || 0) + 1; }

    return {
      generated: new Date().toISOString(),
      options: o,
      recruit: {
        recorded: people.length,
        excluded: people.filter(p => p.excluded).length,
        excludedAttention: people.filter(p => p.failedAttention).length,
        excludedFast: people.filter(p => p.tooFast && !p.failedAttention).length,
        analytic: kept.length,
        observations: obs,
        incomplete: kept.filter(p => p.nRows < 8).length,
        medianSeconds: median(kept.map(p => p.medianSeconds).filter(v => v !== null))
      },
      marg, cells, accuracy, verify, confidence, tests, optionCount, byExperience,
      integrity: { cellCounts, versions, scenarioGrid, cellKeys, mcImmediate, mcCount, suspicion },
      sample: { sector: tally('sector'), seniority: tally('seniority'), experience: tally('experience'),
                orgSize: tally('org_size'), dissent: tally('dissent_route') },
      interview: {
        n: ivKept.length, total: iv.length, dropped: iv.length - ivKept.length,
        modes: ivModes, ratingMeans,
        asymMean: mean(asym), asymSd: sd(asym), asymN: asym.length,
        asymDist: asym,
        r3Corr: pearson(r3, asymPaired),
        coded
      }
    };
  }

  /* ============================================================== charts
     Hand-rolled SVG so the page keeps its no-dependency promise. Marks are
     thin, gridlines are solid hairlines one shade off the surface, and every
     chart is followed by its own table so no value is reachable only by hover.
     Palette: categorical slots 1 and 2 of the validated reference palette,
     checked against this page's surface (#FAFAF9) with the skill's validator:
     all-pairs CVD dE 24.7, normal-vision dE 33.6, both above the floors. */
  const C = {
    s1: '#2a78d6',            /* categorical slot 1 */
    s2: '#eb6834',            /* categorical slot 2 */
    seq: ['#cde2fb','#9ec5f4','#6da7ec','#3987e5','#256abf','#184f95'],
    /* Diverging arms for "deviation from expected": blue above, red below,
       neutral gray at expected. Two hues that read as opposite with a gray
       midpoint, three equal steps per arm, per the diverging rule. */
    divPos: ['#cde2fb','#9ec5f4','#5598e7'],
    divNeg: ['#f7dcdc','#eaa6a6','#d06a6a'],
    divMid: '#F0EFEC',
    ink: '#16191D', mid: '#6C737B', muted: '#898781',
    grid: '#E4E3DD', axis: '#C3C2B7', surface: '#FAFAF9'
  };

  function svgOpen(w, h) {
    return '<svg viewBox="0 0 ' + w + ' ' + h + '" width="100%" height="' + h +
           '" role="img" style="display:block">';
  }
  function txt(x, y, s, opt) {
    const o = opt || {};
    return '<text x="' + x + '" y="' + y + '" fill="' + (o.fill || C.mid) + '" font-size="' +
      (o.size || 11) + '" text-anchor="' + (o.anchor || 'start') + '"' +
      (o.weight ? ' font-weight="' + o.weight + '"' : '') +
      (o.tab ? ' style="font-variant-numeric:tabular-nums"' : '') + '>' + esc(s) + '</text>';
  }

  /* Horizontal bars, one series, one hue. Used for magnitude comparisons where
     the categories carry no order of their own. */
  function barsH(items, opts) {
    const o = Object.assign({ height: 22, gap: 10, labelW: 150, valueFmt: pct, max: null, colour: C.s1 }, opts || {});
    const w = 640, plotW = w - o.labelW - 60;
    const max = o.max !== null ? o.max : Math.max(0.0001, ...items.map(i => i.value || 0));
    let h = 8, out = '';
    for (const it of items) {
      if (it.spacer) { h += 12; continue; }
      const len = Math.max(0, (it.value || 0) / max) * plotW;
      out += '<g><title>' + esc(it.label + ': ' + o.valueFmt(it.value)) + '</title>' +
        txt(o.labelW - 10, h + o.height / 2 + 4, it.label, { anchor: 'end', fill: C.ink }) +
        '<rect x="' + o.labelW + '" y="' + h + '" width="' + Math.max(len, 1) + '" height="' + o.height +
        '" rx="4" fill="' + (it.colour || o.colour) + '"></rect>' +
        txt(o.labelW + len + 8, h + o.height / 2 + 4, o.valueFmt(it.value), { fill: C.ink, weight: 600, tab: 1 }) +
        (it.n !== undefined ? txt(o.labelW + len + 8 + 52, h + o.height / 2 + 4, 'n = ' + it.n, { size: 10 }) : '') +
        '</g>';
      h += o.height + o.gap;
    }
    return svgOpen(w, h + 4) + out + '</svg>';
  }

  /* Grouped columns, two series. Legend is always present; four marks is few
     enough that direct labels on all of them are informative rather than noise. */
  function grouped(groups, series, opts) {
    const o = Object.assign({ h: 210, valueFmt: pct }, opts || {});
    const w = 640, padL = 46, padR = 12, padT = 14, padB = 46;
    const plotW = w - padL - padR, plotH = o.h - padT - padB;
    const max = Math.max(0.0001, ...groups.flatMap(g => g.values));
    const nice = Math.ceil(max * 10) / 10;
    let out = '';
    for (let i = 0; i <= 4; i++) {
      const y = padT + plotH - (i / 4) * plotH;
      out += '<line x1="' + padL + '" y1="' + y + '" x2="' + (w - padR) + '" y2="' + y +
        '" stroke="' + (i === 0 ? C.axis : C.grid) + '" stroke-width="1"></line>' +
        txt(padL - 8, y + 4, o.valueFmt(nice * i / 4), { anchor: 'end', size: 10, tab: 1 });
    }
    const gw = plotW / groups.length, bw = Math.min(44, (gw - 40) / series.length);
    groups.forEach((g, gi) => {
      const gx = padL + gi * gw;
      g.values.forEach((v, si) => {
        const bh = (v / nice) * plotH;
        const x = gx + gw / 2 - (series.length * bw + 2) / 2 + si * (bw + 2);
        out += '<g><title>' + esc(g.label + ' · ' + series[si].label + ': ' + o.valueFmt(v)) + '</title>' +
          '<rect x="' + x + '" y="' + (padT + plotH - bh) + '" width="' + bw + '" height="' + Math.max(bh, 1) +
          '" rx="4" fill="' + series[si].colour + '"></rect>' +
          txt(x + bw / 2, padT + plotH - bh - 6, o.valueFmt(v), { anchor: 'middle', size: 10.5, fill: C.ink, weight: 600, tab: 1 }) +
          '</g>';
      });
      out += txt(gx + gw / 2, o.h - 24, g.label, { anchor: 'middle', fill: C.ink, size: 11.5, weight: 600 });
      if (g.sub) out += txt(gx + gw / 2, o.h - 10, g.sub, { anchor: 'middle', size: 10 });
    });
    return svgOpen(w, o.h) + out + '</svg>';
  }

  /* Estimate with a 95% interval against a zero line. One series, so no legend;
     significance is carried by whether the interval crosses zero and by the
     printed p, never by colour. */
  function forest(rows) {
    const w = 640, labelW = 210, padR = 96, h = 34 * rows.length + 44;
    const plotW = w - labelW - padR;
    const lim = Math.max(0.12, ...rows.flatMap(r => [Math.abs(r.lo || 0), Math.abs(r.hi || 0), Math.abs(r.mean || 0)])) * 1.15;
    const x = v => labelW + plotW / 2 + (v / lim) * (plotW / 2);
    let out = '';
    for (let i = -2; i <= 2; i++) {
      const v = lim * i / 2, xx = x(v);
      out += '<line x1="' + xx + '" y1="24" x2="' + xx + '" y2="' + (h - 20) +
        '" stroke="' + (i === 0 ? C.axis : C.grid) + '" stroke-width="1"></line>' +
        txt(xx, h - 6, (v > 0 ? '+' : '') + (100 * v).toFixed(0) + ' pp', { anchor: 'middle', size: 10, tab: 1 });
    }
    rows.forEach((r, i) => {
      const y = 40 + i * 34;
      out += txt(labelW - 12, y + 4, r.label, { anchor: 'end', fill: C.ink, size: 11.5 });
      if (r.mean === null || r.lo === null) { out += txt(labelW + 8, y + 4, 'not estimable', { size: 11 }); return; }
      out += '<g><title>' + esc(r.label + ': ' + (100 * r.mean).toFixed(1) + ' pp, 95% CI ' +
             (100 * r.lo).toFixed(1) + ' to ' + (100 * r.hi).toFixed(1)) + '</title>' +
        '<line x1="' + x(r.lo) + '" y1="' + y + '" x2="' + x(r.hi) + '" y2="' + y +
        '" stroke="' + C.s1 + '" stroke-width="2"></line>' +
        '<line x1="' + x(r.lo) + '" y1="' + (y - 5) + '" x2="' + x(r.lo) + '" y2="' + (y + 5) + '" stroke="' + C.s1 + '" stroke-width="2"></line>' +
        '<line x1="' + x(r.hi) + '" y1="' + (y - 5) + '" x2="' + x(r.hi) + '" y2="' + (y + 5) + '" stroke="' + C.s1 + '" stroke-width="2"></line>' +
        '<circle cx="' + x(r.mean) + '" cy="' + y + '" r="5" fill="' + C.s1 + '" stroke="' + C.surface + '" stroke-width="2"></circle>' +
        '</g>' +
        txt(w - 6, y + 4, (r.mean > 0 ? '+' : '') + (100 * r.mean).toFixed(1) + ' pp', { anchor: 'end', fill: C.ink, weight: 600, size: 11, tab: 1 });
    });
    out += txt(labelW + plotW / 2, 16, 'no difference', { anchor: 'middle', size: 10 });
    return svgOpen(w, h) + out + '</svg>';
  }

  /* Means on a fixed 1 to 7 scale with the neutral point marked. One series. */
  function dots(items) {
    const w = 640, labelW = 300, padR = 60, h = 26 * items.length + 40;
    const plotW = w - labelW - padR;
    const x = v => labelW + ((v - 1) / 6) * plotW;
    let out = '';
    for (let v = 1; v <= 7; v++) {
      out += '<line x1="' + x(v) + '" y1="20" x2="' + x(v) + '" y2="' + (h - 18) +
        '" stroke="' + (v === 4 ? C.axis : C.grid) + '" stroke-width="1"></line>' +
        txt(x(v), h - 4, String(v), { anchor: 'middle', size: 10, tab: 1 });
    }
    items.forEach((it, i) => {
      const y = 32 + i * 26;
      out += txt(labelW - 12, y + 4, it.label, { anchor: 'end', fill: C.ink, size: 11 });
      if (it.value === null) { out += txt(labelW + 8, y + 4, 'no answers yet', { size: 10.5 }); return; }
      out += '<g><title>' + esc(it.label + ': ' + num(it.value) + ' (n = ' + it.n + ')') + '</title>' +
        '<circle cx="' + x(it.value) + '" cy="' + y + '" r="5" fill="' + C.s1 +
        '" stroke="' + C.surface + '" stroke-width="2"></circle></g>' +
        txt(w - 6, y + 4, num(it.value), { anchor: 'end', fill: C.ink, weight: 600, size: 11, tab: 1 });
    });
    out += txt(x(4), 12, 'neither agree nor disagree', { anchor: 'middle', size: 10 });
    return svgOpen(w, h) + out + '</svg>';
  }

  /* Scenario against condition, coloured by DEVIATION FROM THE EXPECTED COUNT
     rather than by the count itself. Allocation is balanced by construction, so
     a raw-count ramp paints every cell the same shade and hides the one thing
     worth seeing. Deviation is a signed quantity around a baseline, so it takes
     the diverging pair with a neutral midpoint: a healthy grid reads as flat
     gray, and anything over or under represented stands out. */
  function deviationMap(grid, cellKeys) {
    const w = 640, labelW = 110, cellW = (w - labelW - 8) / cellKeys.length, cellH = 26;
    const h = grid.length * cellH + 62;
    const total = grid.reduce((t, g) => t + g.counts.reduce((x, y) => x + y, 0), 0);
    const expected = total / (grid.length * cellKeys.length);
    const band = d => {                       /* d is the deviation ratio */
      if (expected === 0) return { fill: C.divMid, dark: false };
      const a = Math.abs(d);
      const i = a < 0.05 ? -1 : (a < 0.15 ? 0 : (a < 0.30 ? 1 : 2));
      if (i < 0) return { fill: C.divMid, dark: false };
      return { fill: (d > 0 ? C.divPos : C.divNeg)[i], dark: i === 2 };
    };
    let out = '';
    cellKeys.forEach((k, i) => {
      out += txt(labelW + i * cellW + cellW / 2, 14, k.replace('/', ' / '), { anchor: 'middle', size: 10 });
    });
    grid.forEach((g, r) => {
      const y = 24 + r * cellH;
      out += txt(labelW - 10, y + cellH / 2 + 4, g.scenario, { anchor: 'end', fill: C.ink, size: 11 });
      g.counts.forEach((c, i) => {
        const d = expected ? (c - expected) / expected : 0;
        const bnd = band(d);
        out += '<g><title>' + esc(g.scenario + ' · ' + cellKeys[i] + ': ' + c + ' observations, expected ' +
               expected.toFixed(1) + ', ' + (d >= 0 ? '+' : '') + (100 * d).toFixed(0) + '%') + '</title>' +
          '<rect x="' + (labelW + i * cellW + 1) + '" y="' + (y + 1) + '" width="' + (cellW - 2) +
          '" height="' + (cellH - 2) + '" rx="2" fill="' + bnd.fill + '"></rect>' +
          txt(labelW + i * cellW + cellW / 2, y + cellH / 2 + 4, String(c),
              { anchor: 'middle', size: 10.5, fill: bnd.dark ? '#fff' : C.ink, weight: 600, tab: 1 }) +
          '</g>';
      });
    });
    const ly = grid.length * cellH + 46;
    out += txt(labelW - 10, ly, 'under', { anchor: 'end', size: 10 });
    [...C.divNeg].reverse().concat([C.divMid]).concat(C.divPos).forEach((f, i) => {
      out += '<rect x="' + (labelW + i * 22) + '" y="' + (ly - 9) + '" width="20" height="10" rx="2" fill="' + f +
        '" stroke="' + (f === C.divMid ? C.grid : 'none') + '"></rect>';
    });
    out += txt(labelW + 7 * 22 + 6, ly, 'over represented, against ' + expected.toFixed(1) + ' expected', { size: 10 });
    return svgOpen(w, h) + out + '</svg>';
  }

  /* --------------------------------------------------------------- tables */
  function table(headers, rows, opts) {
    const o = opts || {};
    return '<table class="an-t"><thead><tr>' +
      headers.map((h, i) => '<th' + (i && !o.leftAll ? ' class="r"' : '') + '>' + esc(h) + '</th>').join('') +
      '</tr></thead><tbody>' +
      rows.map(r => '<tr>' + r.map((c, i) =>
        '<td' + (i && !o.leftAll ? ' class="r"' : '') + '>' + (c === null ? '—' : esc(c)) + '</td>').join('') + '</tr>').join('') +
      '</tbody></table>';
  }

  /* --------------------------------------------------------------- render */
  function renderAnalysis(A) {
    const R = A.recruit, T = A.tests, I = A.integrity, V = A.interview;
    const tile = (n, l, sub) => '<div><div class="n">' + n + '</div><div class="l">' + esc(l) + '</div>' +
      (sub ? '<div class="s">' + esc(sub) + '</div>' : '') + '</div>';

    let h = '';

    /* ---- headline ---- */
    h += '<section class="an-card"><h3>The sample after exclusions</h3>' +
      '<div class="kv">' +
        tile(R.analytic, 'analytic N', R.recorded + ' recorded') +
        tile(R.observations, 'observations', 'vignette rows') +
        tile(pct(A.marg.overall.rate), 'over-reliance', 'followed the screen') +
        tile(pct(A.accuracy.overall.rate), 'accuracy', 'chose to verify') +
        tile(num(R.medianSeconds, 0) + 's', 'median per vignette', '') +
      '</div>' +
      '<p class="an-note"><b>' + R.excluded + ' excluded</b> of ' + R.recorded + ' recorded: ' +
        R.excludedAttention + ' failed an attention check, ' + R.excludedFast +
        ' had a median time under ' + A.options.minMedianSeconds + ' seconds a vignette. ' +
        (R.incomplete ? R.incomplete + ' of the analytic set stopped before all eight situations and are kept, because a within-person contrast only needs both levels of the factor being tested.' : 'Every analytic participant completed all eight situations.') +
      '</p></section>';

    /* ---- main effects ---- */
    h += '<section class="an-card"><h3>Over-reliance by condition</h3>' +
      '<p class="an-note">The proportion of decisions that followed the dashboard rather than the local knowledge in the brief. Higher is more reliance on the screen.</p>' +
      barsH([
        { label: 'Fault hidden',      value: A.marg.hidden.rate,    n: A.marg.hidden.n },
        { label: 'Fault shown',       value: A.marg.visible.rate,   n: A.marg.visible.n },
        { spacer: true },
        { label: 'Recorded against the system', value: A.marg.auditable.rate, n: A.marg.auditable.n },
        { label: 'Own judgement',     value: A.marg.own.rate,       n: A.marg.own.n }
      ]) +
      table(['Condition', 'Over-reliance', 'Accuracy', 'Asked to verify', 'Observations'], [
        ['Fault hidden', pct(A.marg.hidden.rate), pct(A.accuracy.hidden.rate), pct(A.verify.hidden.rate), A.marg.hidden.n],
        ['Fault shown',  pct(A.marg.visible.rate), pct(A.accuracy.visible.rate), pct(A.verify.visible.rate), A.marg.visible.n],
        ['Recorded against the system', pct(A.marg.auditable.rate), '—', pct(A.verify.auditable.rate), A.marg.auditable.n],
        ['Own judgement', pct(A.marg.own.rate), '—', pct(A.verify.own.rate), A.marg.own.n],
        ['Overall', pct(A.marg.overall.rate), pct(A.accuracy.overall.rate), pct(A.verify.overall.rate), A.marg.overall.n]
      ]) + '</section>';

    /* ---- the 2x2 ---- */
    const cv = k => A.cells[k].rate;
    h += '<section class="an-card"><h3>The four design cells</h3>' +
      '<div class="an-legend"><span><i style="background:' + C.s1 + '"></i>Recorded against the system</span>' +
      '<span><i style="background:' + C.s2 + '"></i>Own judgement</span></div>' +
      grouped([
        { label: 'Fault hidden', values: [cv('hidden/auditable'), cv('hidden/own')] },
        { label: 'Fault shown',  values: [cv('visible/auditable'), cv('visible/own')] }
      ], [{ label: 'Recorded against the system', colour: C.s1 }, { label: 'Own judgement', colour: C.s2 }]) +
      table(['Cell', 'Over-reliance', 'Observations'],
        I.cellKeys.map(k => [k.replace('/', ' / '), pct(A.cells[k].rate), A.cells[k].n])) +
      '</section>';

    /* ---- inferential ---- */
    h += '<section class="an-card"><h3>Within-person effects, with 95% intervals</h3>' +
      '<p class="an-note">Each participant is their own control, so the difference is computed inside each person and then averaged. The interval is a paired t interval on those differences. An interval that does not cross zero is the same thing as p below .05.</p>' +
      forest(T.map(t => ({ label: t.label, mean: t.res.mean, lo: t.res.lo, hi: t.res.hi }))) +
      table(['Contrast', 'Difference', '95% CI', 't', 'df', 'p', "Cohen's dz", 'Participants'],
        T.map(t => [
          t.key + '. ' + t.detail,
          t.res.mean === null ? null : (t.res.mean > 0 ? '+' : '') + (100 * t.res.mean).toFixed(1) + ' pp',
          t.res.lo === null ? null : (100 * t.res.lo).toFixed(1) + ' to ' + (100 * t.res.hi).toFixed(1),
          num(t.res.t), t.res.df, pval(t.res.p), num(t.res.dz), t.res.n
        ])) +
      '<p class="an-note"><b>This is preliminary, not the confirmatory analysis.</b> The methodology specifies a GEE logistic regression clustered on participant, which belongs in R or SPSS on the exported CSV. The paired contrast above is the honest companion to it for a fully within-subjects design, and it does not adjust for multiple comparisons. Treat the interaction row as exploratory: the power simulation put it near .40 even at the full sample.</p>' +
      '</section>';

    /* ---- confidence and options ---- */
    h += '<section class="an-card"><h3>Confidence, and the options considered</h3>' +
      table(['Measure', 'Fault hidden', 'Fault shown', 'Note'], [
        ['Mean confidence, 1 to 7', num(A.confidence.hidden), num(A.confidence.visible), 'Higher confidence on a hidden fault is the uncomfortable finding to look for'],
        ['Mean options generated', num(A.optionCount.hidden), num(A.optionCount.visible), 'Asked on a random three of eight vignettes, ' + A.optionCount.n + ' rows'],
        ['Mean options, by framing', num(A.optionCount.auditable) + ' recorded', num(A.optionCount.own) + ' own call', 'H5, option generation under accountability']
      ], { leftAll: true }) + '</section>';

    /* ---- experience ---- */
    if (A.byExperience.length) {
      h += '<section class="an-card"><h3>By experience, descriptive only</h3>' +
        '<p class="an-note">Experience is a between-person variable, so this is the one moderation the design cannot power. Read it as a description of the sample, not as a test.</p>' +
        table(['Years in the role', 'Participants', 'Over-reliance, hidden', 'Over-reliance, shown', 'Gap'],
          A.byExperience.map(b => [b.band, b.n, pct(b.hidden), pct(b.visible),
            (b.hidden === null || b.visible === null) ? null : ((100 * (b.hidden - b.visible)).toFixed(1) + ' pp')])) +
        '</section>';
    }

    /* ---- integrity ---- */
    const cc = I.cellKeys.map(k => I.cellCounts[k] || 0);
    const ccMean = mean(cc) || 0, ccGap = Math.max(...cc) - Math.min(...cc);
    h += '<section class="an-card"><h3>Design integrity</h3>' +
      '<p class="an-note">Allocation is balanced by construction, so a gap here means participants are dropping out part way through rather than that the Latin square has failed. The number to watch is the widest gap, not the four counts.</p>' +
      '<div class="kv">' + tile(ccGap, 'widest gap', 'observations between the fullest and emptiest cell') +
        tile(num(ccMean, 1), 'mean per cell', I.cellKeys.length + ' cells') + '</div>' +
      table(['Design cell', 'Observations', 'Against the mean'],
        I.cellKeys.map(k => {
          const v = I.cellCounts[k] || 0, d = v - ccMean;
          return [k.replace('/', ' / '), v, (d >= 0 ? '+' : '') + d.toFixed(1)];
        })) +
      '<h4>Scenario against condition</h4>' +
      '<p class="an-note">Every scenario should appear in all four cells. Cells are shaded by how far they sit from the expected count, so a healthy grid reads as flat grey and only a genuine imbalance takes colour. A blank column for a scenario means the rotation is not reaching that combination.</p>' +
      deviationMap(I.scenarioGrid, I.cellKeys) +
      '<h4>Checks</h4>' +
      table(['Check', 'Pass rate', 'Reading'], [
        ['Immediate manipulation check', pct(I.mcImmediate.rate), 'Did they notice whether the last dashboard carried a notice'],
        ['Retrospective count, correct at four', pct(I.mcCount.rate), 'Whether the manipulation registered across the whole run'],
        ['Noticed a pattern', pct(I.suspicion.rate), 'High rates mean the design is transparent; consider a robustness check excluding them'],
        ['Version spread', Object.entries(I.versions).sort().map(([k, v]) => k + ': ' + v).join(', '), 'The four Latin square versions should be roughly equal']
      ], { leftAll: true }) + '</section>';

    /* ---- sample ---- */
    const cols = [['Sector', A.sample.sector], ['Seniority', A.sample.seniority],
                  ['Experience', A.sample.experience], ['Formal dissent route', A.sample.dissent]];
    h += '<section class="an-card"><h3>Who took part</h3><div class="an-cols">' +
      cols.map(([name, t]) => '<div><h4>' + name + '</h4>' +
        table([name, 'n'], t.map(([k, v]) => [k, v])) + '</div>').join('') +
      '</div></section>';

    /* ---- interview ---- */
    h += '<section class="an-card"><h3>The written interview strand</h3>';
    if (!V.n) {
      h += '<p class="an-note">No written interviews from analytic participants yet' +
        (V.total ? ', although ' + V.total + ' arrived from participants who were excluded.' : '.') + '</p>';
    } else {
      h += '<div class="kv">' +
        tile(V.n, 'interviews', Object.entries(V.modes).map(([k, v]) => k + ' ' + v).join(', ')) +
        tile(num(V.asymMean, 2), 'blame asymmetry', 'R5 minus R4, n = ' + V.asymN) +
        tile(num(V.r3Corr.r, 2), 'r with R3', pval(V.r3Corr.p) + ', n = ' + V.r3Corr.n) +
        '</div>' +
        (V.dropped ? '<p class="an-note"><b>' + V.dropped + ' further interview' + (V.dropped === 1 ? '' : 's') +
          '</b> came from participants who were excluded from the survey analysis, so they are left out here. Their written answers are still in the interview export and can be read as qualitative material.</p>' : '') +
        '<p class="an-note">A positive asymmetry means overruling the screen costs a person more than following it, which is legitimacy asymmetry stated as personal risk. R3 asks the same construct directly, so the two should agree. If they do not, say so in the write-up rather than dropping one.</p>' +
        '<h4>Rating statements</h4>' +
        dots(V.ratingMeans.map(r => ({ label: r.key + '. ' + shortRating(r.key), value: r.mean, n: r.n }))) +
        table(['Statement', 'Mean', 'n'], V.ratingMeans.map(r => [r.key + '. ' + shortRating(r.key), num(r.mean), r.n])) +
        '<h4>Coding progress</h4>' +
        table(['Field', 'Coded', 'Remaining'], V.coded.map(c => [c.field, c.done, V.n - c.done]));
    }
    h += '</section>';

    h += '<p class="an-note" style="margin-top:18px">Generated ' + esc(A.generated.replace('T', ' ').slice(0, 16)) +
      ' from ' + R.observations + ' observations. Everything here is computed in this browser from the exported rows; nothing is sent anywhere.</p>';
    return h;
  }

  function shortRating(k) {
    const s = (root.STUDY_SCHEMA && root.STUDY_SCHEMA.RATINGS || []).find(r => r[0] === k);
    if (!s) return '';
    return s[1].length > 62 ? s[1].slice(0, 60) + '…' : s[1];
  }

  root.STUDY_ANALYSIS = { computeAnalysis, renderAnalysis, pct, num, pval };

})(typeof window !== 'undefined' ? window : globalThis);
