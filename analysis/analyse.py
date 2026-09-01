#!/usr/bin/env python3
"""
Analysis pipeline for the dashboard-reliance study.
Reads the combined export, applies the pre-specified screening rules,
and writes every number the dissertation quotes into results.json.

Primary model: GEE logistic regression, exchangeable working correlation,
clustered on participant, with robust (sandwich) standard errors.
"""
import json, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.families import Binomial, Poisson, NegativeBinomial
from statsmodels.genmod.cov_struct import Exchangeable, Independence
from scipy import stats

warnings.filterwarnings("ignore")
np.random.seed(250559280)
R = {}

# ---------------------------------------------------------------- load
d = pd.read_csv("data_raw.csv")
R["raw_participants"] = int(d.response_id.nunique())
R["raw_observations"] = int(len(d))

# ---------------------------------------------------------------- screening
p = d.drop_duplicates("response_id").set_index("response_id")
med_page = d.groupby("response_id").seconds_on_page.median()
p["med_page"] = med_page

fail_attn   = p.attn_pass < 2                    # failed one or both instructed-response checks
speeder     = p.med_page < 15                    # implausibly fast on the vignette pages
short_total = p.total_seconds < 300              # under five minutes for eight vignettes

excl = fail_attn | speeder | short_total
R["excl_attention"]   = int(fail_attn.sum())
R["excl_speeding"]    = int((speeder & ~fail_attn).sum())
R["excl_short_total"] = int((short_total & ~fail_attn & ~speeder).sum())
R["excluded_total"]   = int(excl.sum())
R["excl_rate_pct"]    = round(100 * excl.mean(), 1)

keep = p.index[~excl]
a = d[d.response_id.isin(keep)].copy()
R["N"] = int(a.response_id.nunique())
R["obs"] = int(len(a))
R["median_page_seconds"] = float(a.seconds_on_page.median())
R["median_total_minutes"] = round(float(p.loc[keep, "total_seconds"].median()) / 60, 1)
R["iqr_page_seconds"] = [float(a.seconds_on_page.quantile(.25)), float(a.seconds_on_page.quantile(.75))]

# ---------------------------------------------------------------- coding
a["hidden"]    = (a.data_signal == "hidden").astype(int)
a["auditable"] = (a.accountability == "auditable").astype(int)
a["stakes_c"]  = a.perceived_stakes - a.perceived_stakes.mean()
a["conf_c"]    = a.confidence - a.confidence.mean()

exp_order = ["Less than 2 years", "2 to 4 years", "5 to 9 years",
             "10 to 14 years", "15 years or more"]
exp_num = {k: i for i, k in enumerate(exp_order)}
a["exp_n"] = a.experience.map(exp_num)
a["exp_c"] = a.exp_n - a.exp_n.mean()
a["senior"] = a.seniority.isin(["Senior manager or head of function", "Director or above"]).astype(int)
a["daily"] = (a.use_frequency == "Daily").astype(int)
a["pid"] = a.response_id.astype("category").cat.codes

# ---------------------------------------------------------------- descriptives
def rate(df, col="over_reliance"):
    return round(float(df[col].mean()), 3)

R["over_reliance_overall"] = rate(a)
R["accuracy_overall"] = rate(a, "accuracy")
R["or_hidden"]   = rate(a[a.hidden == 1]);    R["or_visible"] = rate(a[a.hidden == 0])
R["or_auditable"] = rate(a[a.auditable == 1]); R["or_own"]    = rate(a[a.auditable == 0])
R["acc_hidden"]  = rate(a[a.hidden == 1], "accuracy")
R["acc_visible"] = rate(a[a.hidden == 0], "accuracy")
R["acc_auditable"] = rate(a[a.auditable == 1], "accuracy")
R["acc_own"] = rate(a[a.auditable == 0], "accuracy")

# 2x2 cell means
cells = {}
for h in (0, 1):
    for au in (0, 1):
        s = a[(a.hidden == h) & (a.auditable == au)]
        key = f"{'hidden' if h else 'visible'}_{'auditable' if au else 'own'}"
        cells[key] = {"over_reliance": rate(s), "accuracy": rate(s, "accuracy"),
                      "n": int(len(s)), "confidence": round(float(s.confidence.mean()), 2)}
R["cells"] = cells

# choice distribution
R["choice_dist"] = {k: round(float(v), 3) for k, v in a.choice_key.value_counts(normalize=True).items()}
R["choice_by_signal"] = {
    sig: {k: round(float(v), 3) for k, v in g.choice_key.value_counts(normalize=True).items()}
    for sig, g in a.groupby("data_signal")}

# verification intent and confidence
R["verify_hidden"] = rate(a[a.hidden == 1], "verification_intent")
R["verify_visible"] = rate(a[a.hidden == 0], "verification_intent")
R["conf_hidden"] = round(float(a[a.hidden == 1].confidence.mean()), 2)
R["conf_visible"] = round(float(a[a.hidden == 0].confidence.mean()), 2)
R["conf_overreliant"] = round(float(a[a.over_reliance == 1].confidence.mean()), 2)
R["conf_not"] = round(float(a[a.over_reliance == 0].confidence.mean()), 2)
R["stakes_mean"] = round(float(a.perceived_stakes.mean()), 2)
R["stakes_sd"] = round(float(a.perceived_stakes.std()), 2)

# scenario-level over-reliance (checks the Latin square did its job)
R["by_scenario"] = {s: {"over_reliance": rate(g), "n": int(len(g)),
                        "sector": g.scenario_sector.iloc[0]}
                    for s, g in a.groupby("scenario")}

# ---------------------------------------------------------------- GEE helper
def gee(formula, data, family=Binomial(), groups="pid", cov=Exchangeable()):
    m = smf.gee(formula, groups, data=data, family=family, cov_struct=cov).fit()
    out = {}
    for t in m.params.index:
        b, se = m.params[t], m.bse[t]
        out[t] = {"b": round(float(b), 4), "se": round(float(se), 4),
                  "or": round(float(np.exp(b)), 3),
                  "lo": round(float(np.exp(b - 1.96 * se)), 3),
                  "hi": round(float(np.exp(b + 1.96 * se)), 3),
                  "z": round(float(m.tvalues[t]), 3),
                  "p": float(m.pvalues[t])}
    return m, out

# ---- H1/H2 primary model: main effects + interaction
m1, o1 = gee("over_reliance ~ hidden * auditable", a)
R["model_primary"] = o1
try:
    R["icc_alpha"] = round(float(m1.cov_struct.dep_params), 3)
except Exception:
    R["icc_alpha"] = None

# ---- adjusted model with covariates
m2, o2 = gee("over_reliance ~ hidden * auditable + stakes_c + exp_c + senior + daily "
             "+ C(scenario)", a)
R["model_adjusted"] = {k: v for k, v in o2.items() if not k.startswith("C(scenario)")}
R["model_adjusted_scenario_ps"] = {k: round(v["p"], 4) for k, v in o2.items()
                                   if k.startswith("C(scenario)")}

# ---- accuracy model
m3, o3 = gee("accuracy ~ hidden * auditable", a)
R["model_accuracy"] = o3

# ---- verification intent
m4, o4 = gee("verification_intent ~ hidden * auditable", a)
R["model_verify"] = o4

# ---- H4: perceived stakes (measured, not manipulated)
m5, o5 = gee("over_reliance ~ hidden + auditable + stakes_c", a)
R["model_stakes"] = o5
hi_st = a[a.perceived_stakes >= 6]; lo_st = a[a.perceived_stakes <= 4]
R["or_high_stakes"] = rate(hi_st); R["or_low_stakes"] = rate(lo_st)
R["n_high_stakes"] = int(len(hi_st)); R["n_low_stakes"] = int(len(lo_st))

# ---- H5: option generation, asked on a random 3 of 8
opt = a[a.options_asked == 1].copy()
R["opt_obs"] = int(len(opt)); R["opt_participants"] = int(opt.response_id.nunique())
R["opt_mean"] = round(float(opt.options_generated.mean()), 2)
R["opt_var"] = round(float(opt.options_generated.var()), 2)
R["opt_mean_overreliant"] = round(float(opt[opt.over_reliance == 1].options_generated.mean()), 2)
R["opt_mean_not"] = round(float(opt[opt.over_reliance == 0].options_generated.mean()), 2)
R["opt_mean_hidden"] = round(float(opt[opt.hidden == 1].options_generated.mean()), 2)
R["opt_mean_visible"] = round(float(opt[opt.hidden == 0].options_generated.mean()), 2)

mp = smf.gee("options_generated ~ over_reliance + hidden + auditable", "pid",
             data=opt, family=Poisson(), cov_struct=Exchangeable()).fit()
R["model_options"] = {t: {"irr": round(float(np.exp(mp.params[t])), 3),
                          "lo": round(float(np.exp(mp.params[t] - 1.96 * mp.bse[t])), 3),
                          "hi": round(float(np.exp(mp.params[t] + 1.96 * mp.bse[t])), 3),
                          "p": float(mp.pvalues[t])} for t in mp.params.index}
# overdispersion check
pear = float(((opt.options_generated - mp.fittedvalues) ** 2 / mp.fittedvalues).sum())
R["opt_dispersion"] = round(pear / (len(opt) - len(mp.params)), 3)

# ---- H6: expertise moderation (declared exploratory)
m6, o6 = gee("over_reliance ~ hidden * exp_c + auditable", a)
R["model_expertise"] = o6

# ---- robustness: independence working correlation, and GLMM
m1i, o1i = gee("over_reliance ~ hidden * auditable", a, cov=Independence())
R["robust_independence"] = o1i
try:
    glmm = smf.mixedlm("over_reliance ~ hidden + auditable", a, groups=a.pid).fit()
    R["robust_lpm"] = {t: {"b": round(float(glmm.params[t]), 4),
                           "p": float(glmm.pvalues[t])} for t in glmm.params.index
                       if t in ("hidden", "auditable", "Intercept")}
except Exception as e:
    R["robust_lpm"] = str(e)

# ---- robustness: excluding participants who guessed the design
nosusp = a[a.suspicion_pattern == 0]
R["n_suspicion"] = int(a.drop_duplicates("response_id").suspicion_pattern.sum())
R["n_nosusp"] = int(nosusp.response_id.nunique())
ms, os_ = gee("over_reliance ~ hidden * auditable", nosusp)
R["robust_nosuspicion"] = os_

# ---- McNemar paired contrast, one per participant (pre-committed fallback)
w = a.groupby(["response_id", "hidden"]).over_reliance.mean().unstack()
b_ = int(((w[1] > w[0])).sum()); c_ = int(((w[1] < w[0])).sum())
R["mcnemar_more_hidden"] = b_; R["mcnemar_more_visible"] = c_
R["mcnemar_tied"] = int((w[1] == w[0]).sum())
R["mcnemar_p"] = float(stats.binomtest(b_, b_ + c_, 0.5).pvalue)

# ---------------------------------------------------------------- manipulation checks
pk = p.loc[keep]
R["mc_immediate_pct"] = round(100 * float(pk.mc_immediate_correct.mean()), 1)
R["mc_count_pct"] = round(100 * float(pk.mc_count_correct.mean()), 1)
R["mc_count_median"] = float(pd.to_numeric(pk.mc_count_response, errors="coerce").median())
R["suspicion_pct"] = round(100 * float(pk.suspicion_pattern.mean()), 1)
R["attn_pass_pct"] = round(100 * float((p.attn_pass == 2).mean()), 1)

# ---------------------------------------------------------------- sample profile
def prof(col):
    v = pk[col].value_counts()
    return {str(k): {"n": int(n), "pct": round(100 * n / len(pk), 1)} for k, n in v.items()}
for c in ["role", "sector", "experience", "seniority", "org_size", "use_frequency",
          "dissent_route", "analytics_familiarity"]:
    R["profile_" + c] = prof(c)
R["n_followup_consent"] = int(pk.follow_up.sum())
R["n_interviews"] = int(pk.interview_mode.notna().sum())

# ---------------------------------------------------------------- design integrity checks
chk = a.groupby(["response_id"]).apply(
    lambda g: len(g.groupby(["hidden", "auditable"]).size()) == 4, include_groups=False)
R["check_all_four_cells"] = bool(chk.all())
R["check_versions"] = sorted(int(v) for v in a.version.unique())
xt = pd.crosstab(a.scenario, [a.data_signal, a.accountability])
R["check_scenario_balance"] = bool((xt.values > 0).all())
R["check_balance_table"] = {s: {f"{c[0]}_{c[1]}": int(xt.loc[s, c]) for c in xt.columns}
                            for s in xt.index}

with open("results.json", "w") as f:
    json.dump(R, f, indent=1, default=str)

a.to_csv("analysis_sample_long.csv", index=False)
pk.reset_index().to_csv("analysis_sample_participants.csv", index=False)

# ---------------------------------------------------------------- report
print(f"N = {R['N']} participants, {R['obs']} observations "
      f"(excluded {R['excluded_total']}, {R['excl_rate_pct']}%)")
print(f"  attention {R['excl_attention']}, speeding {R['excl_speeding']}, short {R['excl_short_total']}")
print(f"over-reliance overall {R['over_reliance_overall']}  "
      f"hidden {R['or_hidden']} vs visible {R['or_visible']}  "
      f"auditable {R['or_auditable']} vs own {R['or_own']}")
print(f"accuracy overall {R['accuracy_overall']}  hidden {R['acc_hidden']} visible {R['acc_visible']}")
print("\n-- primary GEE (over_reliance ~ hidden * auditable) --")
for k, v in o1.items():
    print(f"  {k:26s} OR {v['or']:6.3f} [{v['lo']:.3f}, {v['hi']:.3f}]  p={v['p']:.4g}")
print("\n-- accuracy --")
for k, v in o3.items():
    print(f"  {k:26s} OR {v['or']:6.3f} [{v['lo']:.3f}, {v['hi']:.3f}]  p={v['p']:.4g}")
print("\n-- options (Poisson) --")
for k, v in R["model_options"].items():
    print(f"  {k:26s} IRR {v['irr']:6.3f} [{v['lo']:.3f}, {v['hi']:.3f}]  p={v['p']:.4g}")
print("\n-- expertise --")
for k, v in o6.items():
    print(f"  {k:26s} OR {v['or']:6.3f} [{v['lo']:.3f}, {v['hi']:.3f}]  p={v['p']:.4g}")
print(f"\nchecks: all four cells {R['check_all_four_cells']}, "
      f"versions {R['check_versions']}, scenario balance {R['check_scenario_balance']}")
print(f"alpha (exchangeable) {R['icc_alpha']}  dispersion {R['opt_dispersion']}")
print(f"McNemar: {b_} more hidden, {c_} more visible, p={R['mcnemar_p']:.4g}")
