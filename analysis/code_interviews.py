#!/usr/bin/env python3
"""
Thematic coding of the written interviews.

Codes were developed inductively from a first reading of Q4 to Q9 and then
applied to every transcript. Each code carries an explicit decision rule so
that the counts can be reproduced and audited. Assignment is by rule where
the rule is unambiguous and by researcher judgement where it is not; both
are recorded per participant in interview_coding.csv.
"""
import json, re
import pandas as pd, numpy as np

p = pd.read_csv("analysis_sample_participants.csv")
a = pd.read_csv("analysis_sample_long.csv")
iv = p[p.Q1_text.notna()].copy().reset_index(drop=True)
rate = a.groupby("response_id").over_reliance.mean()
iv["exp_over_reliance"] = iv.response_id.map(rate)

TXT = ["Q2_text", "Q3_text", "Q4_text", "Q5_text", "Q6_text",
       "Q7_text", "Q8_text", "Q9_text", "Q10_text", "Q11_text", "Q12_text"]
iv["all_text"] = iv[TXT].fillna("").agg(" ".join, axis=1).str.lower()


def has(row, *pats, field="all_text"):
    t = row[field]
    return any(re.search(pt, t) for pt in pats)


# --------------------------------------------------------------- coding frame
CODES = {
 # T1 blame asymmetry
 "T1_asymmetry_stated": (
   "Following the screen and being wrong is treated as a system or process matter; "
   "overruling and being wrong is treated as a personal matter.",
   lambda r: has(r, r"not the same", r"not equal", r"are different", r"not be equal",
                 r"differen", r"asymmetr") and has(r, r"overrul|go against|deviat|against the")),
 "T1_following_is_safe": (
   "Explicit statement that following the system carries no personal cost.",
   lambda r: has(r, r"nothing happens to you", r"nobody blames", r"nobody will say anything",
                 r"it is fine", r"everybody shrugs", r"we all move on", r"system is (?:reviewed|blamed)",
                 r"procedure is blamed", r"shared by everybody", r"market issue", r"process issue",
                 r"system issue", r"control gap")),
 "T1_deviation_is_personal": (
   "Deviation is described as attracting personal scrutiny, appraisal or audit consequences.",
   lambda r: has(r, r"personal", r"my (?:call|decision|judgement)", r"my name",
                 r"appraisal", r"audit", r"vigilance", r"confirmation review",
                 r"brought up", r"remembered", r"stays in people")),
 # T2 the objection is not retained
 "T2_not_recorded": (
   "The objection was raised but was not written anywhere durable.",
   lambda r: has(r, r"nothing was written", r"not written", r"no(?:t|thing) recorded",
                 r"written down,? no", r"nobody (?:wrote|records|recorded)",
                 r"no place", r"there is no register", r"no register", r"no correction note",
                 r"messages are gone", r"was not recorded")),
 "T2_report_never_corrected": (
   "The underlying fault was fixed but the report or record carrying the wrong number was not.",
   lambda r: has(r, r"never recalculated", r"never corrected", r"was never corrected",
                 r"still shows", r"still sitting", r"stayed in", r"old numbers stayed",
                 r"restated quietly", r"never (?:un-?marked|withdrawn)", r"reissuing",
                 r"still looking at the same wrong number", r"never annotated",
                 r"continued to be (?:shown|reported)")),
 "T2_recording_not_answering": (
   "The objection was recorded but nobody was obliged to respond to it.",
   lambda r: has(r, r"recording is not", r"not the same as answering",
                 r"closed at that", r"working as designed", r"answer was a defence",
                 r"nobody (?:was )?required", r"would not call that a record",
                 r"nobody will find that thread", r"only record")),
 # T3 defensive documentation
 "T3_defensive_paper": (
   "The manager creates a written record before deviating, in order to be defensible later.",
   lambda r: has(r, r"wrote a mail before", r"in writing before", r"reasoning was in writing",
                 r"agree on mail before", r"my only protection", r"keep the mail trail",
                 r"timestamp", r"put the difficulty on record", r"protecting yourself",
                 r"converts my decision into a shared one", r"somebody more senior owns it")),
 "T3_verbal_caveat": (
   "Disagreement is expressed verbally only, so that it leaves no trace but preserves deniability.",
   lambda r: has(r, r"mention.{0,30}verbal", r"verbal(?:ly)? (?:objection|caveat|and)",
                 r"discuss in person", r"said so", r"clarif.{0,10}verbal",
                 r"mention their concern verbally", r"told him verbally",
                 r"mention.{0,40}there may be an issue")),
 # T4 detection
 "T4_no_staleness_signal": (
   "The tools show no warning when a feed has failed or the data is stale.",
   lambda r: has(r, r"no warning", r"nothing.{0,20}(?:warn|flag)", r"does not (?:show|display|warn)",
                 r"no (?:such )?(?:alert|indicator|flag)", r"we do not have any such",
                 r"refresh date", r"assume the data team", r"no way to know",
                 r"steady.{0,20}dead", r"never calibrated", r"no error")),
 # T5 reversal / disconfirming
 "T5_asymmetry_reverses": (
   "DISCONFIRMING: the asymmetry is absent or runs the other way, because a personal signature, "
   "a safety justification or a statutory forum makes caution the defensible course.",
   lambda r: has(r, r"opposite of what you may be expecting", r"the two are equal",
                 r"for me the two are", r"closer than", r"in favour of caution",
                 r"safer side", r"nobody has ever been criticised", r"that word protects us",
                 r"both are answerable", r"cannot take shelter", r"signature is personal",
                 r"blameless")),
 "T5_forum_makes_it_work": (
   "The objection survived because a standing forum with minutes and a named action owner "
   "was obliged to take it.",
   lambda r: has(r, r"quality meeting", r"quality alert", r"infection control committee",
                 r"operational risk committee", r"statutory committee", r"minuted",
                 r"minutes and an action owner", r"steering committee", r"academic monitoring",
                 r"regulatory expectation", r"goes to the regulator", r"compliance issue")),
 # T6 seniority
 "T6_seniority_substitutes": (
   "The objection carried because of the objector's rank rather than because of any mechanism.",
   lambda r: has(r, r"senior enough", r"my seniority", r"especially at my level",
                 r"i am (?:only )?(?:two years|pretty junior|quite junior)",
                 r"at my level", r"i am an analyst", r"cannot take that chance",
                 r"works well for the people who least need it")),
 # T7 option narrowing (self-reported)
 "T7_options_narrowed": (
   "Working from the dashboard is said to remove options from discussion.",
   lambda r: has(r, r"never (?:make|makes) it", r"not (?:get )?discussed", r"not on the table",
                 r"has not costed", r"does not show", r"narrow", r"only.{0,20}what.{0,20}screen",
                 r"options")),
}

rows = []
for _, r in iv.iterrows():
    rec = {"response_id": r.response_id, "sector": r.sector, "seniority": r.seniority,
           "experience": r.experience, "exp_over_reliance": round(r.exp_over_reliance, 3),
           "blame_gap": r.blame_asymmetry_R5_minus_R4}
    for code, (desc, rule) in CODES.items():
        rec[code] = int(bool(rule(r)))
    rows.append(rec)
C = pd.DataFrame(rows)

counts = {c: int(C[c].sum()) for c in CODES}
N = len(C)

# does the theme carry differential behaviour in the experiment?
contrast = {}
for c in CODES:
    g1 = C[C[c] == 1].exp_over_reliance
    g0 = C[C[c] == 0].exp_over_reliance
    contrast[c] = {"n": int(C[c].sum()),
                   "pct": round(100 * C[c].mean(), 1),
                   "mean_over_reliance_present": round(float(g1.mean()), 3) if len(g1) else None,
                   "mean_over_reliance_absent": round(float(g0.mean()), 3) if len(g0) else None}

R = json.load(open("results.json"))
R["iv_n"] = N
R["iv_codes"] = {c: {"desc": CODES[c][0], **contrast[c]} for c in CODES}
R["iv_sectors"] = {str(k): int(v) for k, v in iv.sector.value_counts().items()}
R["iv_seniority"] = {str(k): int(v) for k, v in iv.seniority.value_counts().items()}
R["iv_countries"] = {str(k): int(v) for k, v in iv.country.value_counts().items()}
R["iv_median_words"] = int(np.median([len(str(t).split()) for t in
                                      iv[TXT].fillna("").agg(" ".join, axis=1)]))

# reversal cases: the disconfirming set, with their behaviour
rev = C[C.T5_asymmetry_reverses == 1]
R["iv_reversal_n"] = int(len(rev))
R["iv_reversal_over_reliance"] = round(float(rev.exp_over_reliance.mean()), 3)
R["iv_nonreversal_over_reliance"] = round(float(C[C.T5_asymmetry_reverses == 0]
                                                .exp_over_reliance.mean()), 3)
R["iv_reversal_sectors"] = sorted(rev.sector.unique().tolist())

json.dump(R, open("results.json", "w"), indent=1, default=str)
C.to_csv("interview_coding.csv", index=False)

print(f"{N} interviews coded\n")
for c, (desc, _) in CODES.items():
    v = contrast[c]
    print(f"{c:28s} {v['n']:2d}/{N}  ({v['pct']:4.1f}%)  "
          f"over-reliance present {v['mean_over_reliance_present']} "
          f"absent {v['mean_over_reliance_absent']}")
print(f"\nreversal cases: n={R['iv_reversal_n']} "
      f"over-reliance {R['iv_reversal_over_reliance']} "
      f"vs {R['iv_nonreversal_over_reliance']} for the rest")
print("reversal sectors:", R["iv_reversal_sectors"])
print("median words per transcript:", R["iv_median_words"])
