#!/usr/bin/env python3
"""Emits Chapter 4 sections 4.3 to 4.5 with every number taken from results.json."""
import json
R = json.load(open("results.json"))

def p(x):
    """Format a p-value for reporting."""
    return "$p < .001$" if x < .001 else f"$p = {x:.3f}$".replace("0.", ".")

def orci(v):
    return f"OR {v['or']:.2f}, 95\\% CI [{v['lo']:.2f}, {v['hi']:.2f}], {p(v['p'])}"

M  = R["model_primary"]; A = R["model_accuracy"]; V = R["model_verify"]
C  = R["cells"];         D = R["decomp"];        RT = R["route_table"]
IV = R["iv_behaviour_tests"]; RB = R["rating_behaviour_corr"]; RG = R["ratings"]

T = r"""
\section{Strand 1: experimental findings \textcolor{redc}{[pre-collection dataset]}}

\simbox{\textbf{\textcolor{redc}{THE DATASET ANALYSED IN THIS SECTION IS NOT A HUMAN SAMPLE.}}
Of the %(raw_participants)d participant records in the combined export, one arrived through the
live hosted instrument. The remainder were generated to the design at section 3.5.1 and loaded
through the bulk import route that exists to exercise the store and the extraction pipeline. The
\emph{analysis} is the real one: screening rule, models, robustness checks and coding frame are
those that will be applied in November. The numbers are not findings and every one will be
replaced. Each affected heading, table and figure is marked, and the released dataset records the
provenance of every row.}

\subsection{Sample and screening \textcolor{redc}{[pre-collection dataset]}}

The export holds %(raw_participants)d participant records and %(raw_observations)d observations,
eight per participant, with no missing vignettes. The screening rule fixed at section 3.5.1 removes
%(excluded_total)d participants (%(excl_rate_pct).1f per cent), all for failing at least one
instructed-response check; none was removed by the speed filters. The analytic sample is %(N)d
participants and %(obs)d observations. Median time on a scenario page is
%(median_page_seconds).0f seconds (IQR %(iqr_lo).0f to %(iqr_hi).0f) and median time on the whole
instrument is %(median_total_minutes).1f minutes, against the ten to twelve the information sheet
states. That gap is a finding about the instrument, and section 6.6 returns to it. Table
%(nbsp)s\ref{tab:profile} gives the analytic sample, which is not claimed to be representative of
any population.

%(profile_table)s

One background item bears directly on the argument. Asked whether their organisation has a formal
way of recording disagreement with a report, only %(route_used_n)d of %(N)d
(%(route_used_pct).1f per cent) say a route exists and is used. %(route_paper_n)d say it exists on
paper but is rarely used, %(route_none_n)d that none exists, %(route_dk_n)d that they do not know.

\subsection{Checks on the design \textcolor{redc}{[pre-collection dataset]}}

Four checks preceded any hypothesis test. \textbf{\emph{Balance:}} every participant contributed
two observations in each of the four cells, and across the four versions every scenario appeared in
every cell, so condition is orthogonal to scenario. That is what the Latin square was introduced to
achieve and what the earlier block design could not deliver. \textbf{\emph{Order:}} deference does
not drift across the eight positions (%(pos_or).2f per position, 95\%% CI [%(pos_lo).2f,
%(pos_hi).2f], %(pos_p)s), although median page time falls from %(pos1_sec).0f seconds to
%(pos8_sec).0f. Eight vignettes therefore sit within this population's tolerance, which was the
open question when the count was raised from four. \textbf{\emph{Manipulation checks:}}
%(mc_immediate_pct).1f per cent correctly identified whether the last vignette carried a notice,
but only %(mc_count_pct).1f per cent gave the correct retrospective count of
%(mc_count_median).0f. Participants see the notice when asked at once and cannot reconstruct how
often they saw it, which is consistent with shallow rather than absent processing.
\textbf{\emph{Suspicion:}} %(suspicion_pct).1f per cent described a pattern resembling the design;
excluding them strengthens the effects (section 4.3.8).

\subsection{Descriptive results \textcolor{redc}{[pre-collection dataset]}}

Across %(obs)d observations participants followed the dashboard against the local evidence in
%(over_reliance_overall).3f of decisions and chose the defensible action in
%(accuracy_overall).3f. The differences between conditions matter more, and
Figure%(nbsp)s\ref{fig:cells} shows them.

\begin{figure}[H]
\centering
\includegraphics[width=0.98\textwidth]{fig/f_cells.pdf}
\caption{\SIM Deference and defensible choice across the four conditions}
\label{fig:cells}
\end{figure}

Deference nearly doubles when the fault is hidden rather than disclosed (%(or_hidden).3f against
%(or_visible).3f) and rises by about half when the decision is framed as auditable rather than as
the manager's own (%(or_auditable).3f against %(or_own).3f). Defensible choice moves the opposite
way on both, from %(acc_visible).3f to %(acc_hidden).3f and from %(acc_own).3f to
%(acc_auditable).3f.

The second contrast is the one to hold on to. Dashboard, brief and local evidence were identical
across the two accountability conditions. Only the sentence describing how the decision would later
be reviewed differed. A manipulation that changes nothing about the available information changes
what a quarter of participants do with it.

The mean conceals a divided sample rather than a uniform one: %(never_overrelied)d of %(N)d
participants never deferred across eight vignettes, %(always_hi)d deferred six times or more, and
the mean participant deferred %(mean_overrel_per_person).2f times out of eight.

\subsection{Hypothesis tests \textcolor{redc}{[pre-collection dataset]}}

The primary model is the generalised estimating equation pre-committed at section 3.5.1, with a
logit link, an exchangeable working correlation clustered on participant and robust standard
errors. The estimated within-participant correlation is %(icc_alpha).3f, close to the .18 assumed
in the power simulation.

\textbf{H1 is supported:} hiding the fault raises the odds of deference (%(h1)s).
\textbf{H2 is supported:} auditable framing raises them with the data held constant (%(h2)s).
\textbf{The two effects are additive, not interactive:} the interaction is not distinguishable
from zero (%(hxa)s). Making a decision auditable adds about the same deference whether the fault is
visible or hidden, and the converse holds. Section 2.7 treated these as two inputs to one
attentional pathway; they do not behave that way, and section 5.2 takes up what follows.

The result survives the pre-committed fallback: comparing each participant with themselves,
%(mcnemar_more_hidden)d deferred more often under the hidden condition against
%(mcnemar_more_visible)d the other way, with %(mcnemar_tied)d tied (exact binomial, %(mcn_p)s).
Figure%(nbsp)s\ref{fig:forest} collects the estimates and Appendix%(nbsp)sP gives the full models.

\begin{figure}[H]
\centering
\includegraphics[width=0.98\textwidth]{fig/f_forest.pdf}
\caption{\SIM Odds ratios with 95 per cent confidence intervals for the three outcomes}
\label{fig:forest}
\end{figure}

\subsection{Separating detection failure from authority failure \textcolor{redc}{[pre-collection dataset]}}

Section 5.2 argued from the documentary evidence that two distinct things go wrong and that theory
had been treating them as one. The experiment measures them separately.

\begin{figure}[H]
\centering
\includegraphics[width=0.98\textwidth]{fig/f_decomp.pdf}
\caption{\SIM Decomposition of deference from the disclosed, own-judgement baseline}
\label{fig:decomp}
\end{figure}

Where the warning is shown and the decision is the manager's own, %(base).3f of decisions follow
the screen. Hiding the fault adds %(det).3f; framing the same decision as auditable adds
%(auth).3f. Together they give %(joint).3f against %(sum_parts).3f under independence, so the
residual is %(resid).3f and the additive account holds. Detection failure accounts for about
%(det_share).0f per cent of the rise above baseline and authority failure for about
%(auth_share).0f per cent.

Two readings of that split are available. The first is that detection is the larger problem and so
the one to spend on. The second is that authority failure is smaller but is produced by a single
sentence about review, at no informational cost, which makes it both the easier to create by
accident and, on the argument at section 6.2, the cheaper to remove. Section 5.4 sets out why this
study prefers the second.

Neither mechanism depends on the other. Auditable framing raises deference when the warning is
shown (%(sa_vis)s) and when the fault is hidden (%(sa_hid)s); hiding the fault raises it under own
judgement (%(sh_own)s) and under audit (%(sh_aud)s).

\subsection{The two manipulations work through different channels \textcolor{redc}{[pre-collection dataset]}}

Additivity shows that two effects exist, not that they differ in kind. The instrument measures
intention to verify and stated confidence alongside the choice so that this can be tested.

\begin{figure}[H]
\centering
\includegraphics[width=0.98\textwidth]{fig/f_mech.pdf}
\caption{\SIM What each manipulation moves. Hiding the fault shifts all three measures; auditable
framing shifts only the choice.}
\label{fig:mech}
\end{figure}

Hiding the fault behaves as an attentional account predicts. Deference rises, intention to verify
falls from %(verify_visible).3f to %(verify_hidden).3f (%(vh)s), and stated confidence rises from
%(conf_visible).2f to %(conf_hidden).2f on a seven-point scale. The absence of a warning is read as
the presence of an assurance, which is Wang and Strong's (1996) point about believability restated
as behaviour.

The accountability frame behaves differently. Deference rises by %(auth).3f while intention to
verify does not move (%(va)s) and confidence does not move either. Participants under audit were no
less inclined to check and no more sure of themselves. They chose differently.

This is the discriminating result. An attentional explanation of the accountability effect predicts
that people under audit would look less carefully, and they did not. What changed was which of two
known options a manager was willing to put their name to. That is what legitimacy asymmetry
predicts and automation bias does not, and it is why section 5.2 treats authority failure as a
separate mechanism rather than a second route to inattention.

\subsection{Accuracy, confidence and calibration \textcolor{redc}{[pre-collection dataset]}}

Both manipulations reduce the chance of the defensible choice, hiding the fault (%(a1)s) and
auditable framing (%(a2)s). Confidence carries some signal, at %(conf_when_right).2f when the
defensible action was chosen against %(conf_when_wrong).2f when it was not, and the difference
holds controlling for condition (%(cf_acc_b)+.2f, %(cf_acc_p)s). The problem is the level.

\begin{figure}[H]
\centering
\includegraphics[width=0.90\textwidth]{fig/f_calib.pdf}
\caption{\SIM Stated confidence by condition and by whether the defensible action was chosen}
\label{fig:calib}
\end{figure}

Under a hidden fault, participants who chose wrongly reported confidence of %(calib_h_wrong).2f,
as high as participants who chose correctly when the warning was shown (%(calib_v_right).2f).
Hiding the fault raises confidence by %(cf_hid_b)+.2f points (%(cf_hid_p)s) whether or not the
decision was right. A manager working from a silent dashboard is not only more likely to be wrong,
but wrong with the assurance they would have had if they were right.

\subsection{Option generation: H5 is not supported \textcolor{redc}{[pre-collection dataset]}}

H5 predicted that managers who defer name fewer alternative actions. They do not. The open item was
asked on three vignettes of eight, giving %(opt_obs)d responses from all %(opt_participants)d
participants, mean %(opt_mean).2f distinct actions. A Poisson model clustered on participant
returns an incidence rate ratio for deference of %(opt_irr).2f, 95\%% CI [%(opt_lo).2f,
%(opt_hi).2f], %(opt_p)s. Dispersion is %(opt_disp).2f, so the Poisson assumption holds and no
negative binomial fallback was needed. Neither manipulation moves the count.

\begin{figure}[H]
\centering
\includegraphics[width=0.98\textwidth]{fig/f_options.pdf}
\caption{\SIM Distinct alternative actions named, with the model estimate at right}
\label{fig:options}
\end{figure}

Three readings survive the data. The measure may be insensitive, a free-text box in a short task
being a weak proxy for the option set a manager works through over a week. The effect may be real
but small, since the interval does not exclude a reduction of a fifth. Or narrowing may operate at
the level of the team and the planning meeting rather than the individual, which is what section
4.4 suggests and what a scenario task cannot reach. Section 6.6 treats this as a case for a
different design rather than a larger sample. Reporting H5 as unsupported constrains the argument:
the claim that dashboards narrow the options considered is retained only where the interview
evidence carries it, and it is not carried by the experiment.

\subsection{Expertise, stakes and robustness \textcolor{redc}{[pre-collection dataset]}}

\textbf{\emph{H6, declared exploratory.}} Experience neither moderates the hidden-fault effect
(%(h6)s) nor has a main effect (%(h6m)s). The power simulation predicted about .40 power for a
between-participants moderator of a within-participant effect, so a null here is close to
uninformative and is reported as such rather than as evidence of no moderation.

\textbf{\emph{Perceived stakes.}} Higher perceived stakes is associated with slightly less
deference (%(st)s), pointing towards H4b rather than H4a. The range is narrow, with a mean of
%(stakes_mean).2f and standard deviation of %(stakes_sd).2f and only %(n_low_stakes)d observations
at four or below, so a manipulation would be needed to settle it.

\textbf{\emph{The formal-route item predicts nothing.}} Participants who say a formal route exists
and is used defer at %(route_used_rate).3f against %(route_other_rate).3f for everyone else
(%(route_mw_p)s), and the item adds nothing to the model (%(route_or)s). The ordering across the
four answers is not monotonic. This is a useful negative result about measurement: a tick-box
asking whether a route exists captures whether a policy document exists, not whether an objection
is answered. Section 4.4.5 asks the second question and does track behaviour.

\textbf{\emph{Robustness.}} Estimates are unchanged under an independence working correlation.
Excluding the %(n_suspicion)d participants who described the design leaves %(n_nosusp)d and
strengthens both effects (hidden %(rs_h).2f, auditable %(rs_a).2f), so neither is an artefact of
participants guessing what was tested. Adjusting for perceived stakes, experience, seniority, use
frequency and scenario fixed effects leaves them essentially unchanged (hidden %(adj_h).2f,
auditable %(adj_a).2f). Time on page does not predict deference, so the effect is not a matter of
rushing.

\section{Strand 3: interview findings \textcolor{redc}{[pre-collection dataset]}}

\simbox{\textbf{\textcolor{redc}{THE INTERVIEW MATERIAL SHARES THE PROVENANCE DESCRIBED AT SECTION
4.3.}} The coding frame, the counts and the procedure linking codes to experimental behaviour are
those that will be applied to the collected transcripts. The quoted text is not the speech of
research participants and is not offered as such.}

\subsection{Participants and material \textcolor{redc}{[pre-collection dataset]}}

%(n_followup_consent)d of the %(N)d participants consented to follow-up and %(iv_n)d completed the
written interview, above the floor of eight at section 3.5.3 and inside the range at which
saturation usually appears in a fairly homogeneous sample (Guest, Bunce and Johnson, 2006). The
median transcript runs to %(iv_median_words)d words across twelve open questions. Ten sectors are
represented, none contributing more than five, and seniority runs from analyst to director.

Participants were selected on observed behaviour rather than availability. Question 10 is generated
from each participant's own record, preferring a vignette in which the fault was hidden and they
followed the screen, and quotes their actual choice back to them. That is what makes the sampling
behavioural and what permits section 4.4.5.

\subsection{The blame gap, measured directly \textcolor{redc}{[pre-collection dataset]}}

%(ratings_table)s

Three statements carry the argument. %(r3_agree).0f per cent agree that a report-backed decision is
easier to defend than a judgement-backed one, which is the legitimacy asymmetry of section 2.5
endorsed almost unanimously. R4 and R5 put a number on it: %(r5_agree).0f per cent expect personal
responsibility for overruling the dashboard and being wrong, against %(r4_agree).0f per cent for
following it and being wrong. The mean gap is %(bg_mean).2f points on a seven-point scale (paired
$t$(%(bg_df)d) = %(bg_t).2f, %(bg_p)s, $d$ = %(bg_d).2f) and is positive for %(bg_pos).0f per cent
of participants. R7 is the lowest-rated statement in the set: only %(r7_agree).0f per cent agree
that somebody must formally answer a raised concern before a decision proceeds. That is the
statement the proposal at section 6.2 is built to change.

\subsection{Themes \textcolor{redc}{[pre-collection dataset]}}

Codes were developed from a first reading of the questions on doubt, escalation and consequence,
then applied against explicit decision rules recorded in the coding script so that counts are
reproducible. Four themes carry the material.

\textbf{\emph{The asymmetry is described, not merely implied}} (%(t1a)d of %(iv_n)d). Participants
distinguish the two ways of being wrong unprompted, and consistently as a system problem against a
personal one. One public sector participant put the audit consequence plainly: a decision taken as
per the monitoring data is accepted at every level, whereas a deviation invites the question of
what basis the officer had for deviating, which is described as difficult to answer even when the
deviation was right.

\textbf{\emph{The objection is raised and leaves no trace}} (%(t2)d of %(iv_n)d). This is the most
common pattern and it is more specific than a general complaint about record keeping. The technical
fault is usually fixed, often quickly, while the report carrying the wrong number is not:
%(t2b)d participants describe exactly that split. One retail participant noted that nothing in
their systems records that a store's conversion metric was invalid for a month, so an analysis run
next year will read the wrong figure as real. Another observed that the corrected number simply
appeared, the archive kept the old one, and nobody told management that the figure they had praised
was not real.

\textbf{\emph{Recording is not answering}} (%(t2c)d of %(iv_n)d). A smaller group draws a
distinction the governance literature tends to collapse. One described a properly minuted objection
with a file number, traceable years later, answered by the statement that the system was working as
designed, after which the matter was closed. Their summary, that recording is not the same as
answering, is the sentence this study carries into section 6.2.

\textbf{\emph{Defensive documentation}} (%(t3)d of %(iv_n)d). Managers describe writing a
timestamped note before deviating, or securing a superior's agreement by email first, to convert a
personal decision into a shared one; one said this is not dishonest, it is how you survive. A
cheaper move appears in %(t3b)d transcripts: the concern is voiced aloud and never written, which
preserves the ability to say afterwards that it was raised while leaving nothing on the record. One
participant called that verbal caveat useless precisely because it is not recorded.

\subsection{Disconfirming accounts \textcolor{redc}{[pre-collection dataset]}}

%(t5)d of %(iv_n)d transcripts describe the asymmetry as absent or reversed, and they are the most
informative material in the set because they identify the conditions under which the mechanism
switches off. They come from %(rev_sectors)d sectors and share a structure: deviating in the
cautious direction is the defensible act rather than the exposed one, and the reason is
institutional rather than cultural.

A healthcare participant signs the rota personally, so following the staffing model and having a
patient harmed is their responsibility while keeping an extra nurse invites at most a question about
agency cost. A quality manager said the release note carries their signature, so they cannot take
shelter behind a report. An energy participant said invoking safety ends the argument and that the
word protects them. A banking participant described a committee where following the model without
applying challenge is itself an audit finding, and added that this holds because it is a regulatory
expectation rather than because the institution is virtuous.

The rating scale corroborates the coding independently: participants coded as describing a reversal
record a blame gap of %(rev_bg_mean).2f points against %(oth_bg_mean).2f for the rest ($t$ =
%(rev_bg_t).2f, %(rev_bg_p)s).

One account cuts against the governance proposal and is reported for that reason. A technology
director described an objection that was minuted and answered, and attributed the outcome to their
own seniority rather than the mechanism, observing that the formal route works well for the people
who least need it. %(t6)d transcripts carry that code, and section 6.2 has to answer it.

\subsection{Linking what managers say to how they behaved \textcolor{redc}{[pre-collection dataset]}}

Because interview participants also completed the experiment, each theme can be set against that
participant's own deference rate. This is the join the sequential explanatory design exists to
make, reported in full including where it is weak.

\begin{figure}[H]
\centering
\includegraphics[width=0.98\textwidth]{fig/f_integration.pdf}
\caption{\SIM Interview themes against the same participant's deference rate. Mann-Whitney $U$ on
participant-level rates, $n$ = %(iv_n)d.}
\label{fig:integration}
\end{figure}

Participants describing the asymmetry as absent or reversed deferred at %(rev_rate).3f against
%(oth_rate).3f (%(mw_rev)s); those describing a standing forum obliged to answer an objection at
%(forum_rate).3f against %(forum_oth).3f (%(mw_forum)s). In the other direction, participants whose
objection left no durable record deferred at %(nr_rate).3f against %(nr_oth).3f (%(mw_nr)s), and
the six describing disagreement voiced only verbally at %(vc_rate).3f, the highest of any group
(%(mw_vc)s). The ratings point the same way: a participant's blame gap correlates with their own
deference rate at $\rho$ = %(rho_bg).2f (%(rho_bg_p)s), R7 at $\rho$ = %(rho_r7).2f
(%(rho_r7_p)s), and R6 at $\rho$ = %(rho_r6).2f (%(rho_r6_p)s). Managers who work where objections
are answered defer less in a task that has nothing to do with their employer.

Two cautions belong with this. First, $n$ = %(iv_n)d and these are correlations: a person disposed
to question a screen may also be disposed to describe their organisation as one that listens.
Second, the contrast with section 4.3.8, where the tick-box item predicted nothing. The measures
that track behaviour here ask whether an objection gets \emph{answered}; the measure that tracked
nothing asked whether a route \emph{exists}. If that distinction survives collection it is a
finding about how to measure the construct as much as about the construct itself.

\section{Integration across the three strands}

Table%(nbsp)s\ref{tab:joint2} is the joint display. It records disagreement as well as agreement,
following the convention that an integration reporting only convergence has not been done properly
(Creswell and Plano Clark, 2018).

%(joint_table)s

Three points follow. The strands agree that deference is conditional rather than general, and they
agree on both conditions. They disagree about option narrowing, where the experiment finds nothing
and the interviews describe it clearly, which is recorded as unresolved rather than settled in
favour of the more convenient strand. And the documentary strand supplies what neither of the
others can, which is evidence that these mechanisms produce serious harm at scale rather than small
effects in a short online task.
"""

# ---------------------------------------------------------------- tables
prof = R["profile_sector"]
sect_rows = "\n".join(
    f"{k} & {v['n']} & {v['pct']:.1f} \\\\" for k, v in
    sorted(prof.items(), key=lambda x: -x[1]["n"]))
sen = R["profile_seniority"]
sen_rows = "\n".join(
    f"{k} & {v['n']} & {v['pct']:.1f} \\\\" for k, v in
    sorted(sen.items(), key=lambda x: -x[1]["n"]))
exp = R["profile_experience"]
exp_order = ["Less than 2 years", "2 to 4 years", "5 to 9 years",
             "10 to 14 years", "15 years or more"]
exp_rows = "\n".join(
    f"{k} & {exp[k]['n']} & {exp[k]['pct']:.1f} \\\\" for k in exp_order if k in exp)

profile_table = r"""
\begin{table}[H]
\centering\small
\caption{\SIM Profile of the analytic sample ($N$ = %d)}
\label{tab:profile}
\rowcolors{2}{palegrey}{white}
\begin{tabularx}{\textwidth}{@{}X r r@{\hspace{1.4em}} X r r@{}}
\toprule
\rowcolor{palenavy}
\textbf{Sector} & \textbf{n} & \textbf{\%%} & \textbf{Seniority and experience} & \textbf{n} & \textbf{\%%} \\
\midrule
%s
\bottomrule
\end{tabularx}
\end{table}
""" % (R["N"], "")

# build the two-column body by zipping the lists
left = [(k, v["n"], v["pct"]) for k, v in sorted(prof.items(), key=lambda x: -x[1]["n"])]
right = ([("\\emph{Seniority}", "", "")] +
         [(k, v["n"], v["pct"]) for k, v in sorted(sen.items(), key=lambda x: -x[1]["n"])] +
         [("\\emph{Experience}", "", "")] +
         [(k, exp[k]["n"], exp[k]["pct"]) for k in exp_order if k in exp])
rows = []
for i in range(max(len(left), len(right))):
    l = left[i] if i < len(left) else ("", "", "")
    r = right[i] if i < len(right) else ("", "", "")
    fl = f"{l[0]} & {l[1]} & {l[2]}" if l[1] != "" else f"{l[0]} & &"
    fr = f"{r[0]} & {r[1]} & {r[2]}" if r[1] != "" else f"{r[0]} & &"
    rows.append(f"{fl} & {fr} \\\\")
profile_table = profile_table.replace("\n%s\n" % "", "\n" + "\n".join(rows) + "\n")

rat_rows = "\n".join(
    f"{k} & {v['stmt'][0].upper()+v['stmt'][1:]} & {v['mean']:.2f} & {v['sd']:.2f} & {v['pct_agree']:.0f} \\\\"
    for k, v in RG.items())
ratings_table = r"""
\begin{table}[H]
\centering\small
\caption{\SIM Rating statements, means and percentage agreeing (6 or 7 on a seven-point scale), $n$ = %d}
\label{tab:ratings}
\rowcolors{2}{palegrey}{white}
\begin{tabularx}{\textwidth}{@{}p{0.8cm} X r r r@{}}
\toprule
\rowcolor{palenavy}
\textbf{ID} & \textbf{Statement} & \textbf{Mean} & \textbf{SD} & \textbf{\%% agree} \\
\midrule
%s
\bottomrule
\end{tabularx}
\end{table}
""" % (R["iv_n"], rat_rows)

joint_table = r"""
\begin{table}[H]
\centering\footnotesize
\caption{Joint display: what each strand contributes to each proposition, and where they disagree}
\label{tab:joint2}
\rowcolors{2}{palegrey}{white}
\begin{tabularx}{\textwidth}{@{}p{3.0cm} X X p{2.4cm}@{}}
\toprule
\rowcolor{palenavy}
\textbf{Proposition} & \textbf{Experiment \textcolor{redc}{[pre-collection]}} &
\textbf{Interviews \textcolor{redc}{[pre-collection]}} & \textbf{Documents \textcolor{greenc}{[collected]}} \\
\midrule
A hidden fault raises deference &
Deference %(or_visible).3f to %(or_hidden).3f; verification intent falls; confidence rises &
Half describe tools that display no staleness signal at all &
7 of 12 cases had no visible sign; those faults survived years \\
Auditable framing raises deference with the data held constant &
%(or_own).3f to %(or_auditable).3f, with no change in verification intent &
%(r3_agree).0f per cent agree a report-backed decision is easier to defend; blame gap %(bg_mean).2f points &
Objection raised and overruled in 9 of 12 cases \\
The two failures are distinct &
Additive, residual %(resid).3f; different channels &
Recording and answering distinguished in %(t2c)d transcripts &
Detection controls present but authority controls absent \\
Deference narrows the option set &
\textbf{Not supported}: IRR %(opt_irr).2f [%(opt_lo).2f, %(opt_hi).2f] &
%(r8_agree).0f per cent agree; described at team level, not individual &
Not addressable from documents \\
Answerability suppresses deference &
Formal-route tick-box predicts nothing &
Forum-obliged-to-answer group defers at %(forum_rate).3f against %(forum_oth).3f &
The 3 cases where the objection carried had a statutory route \\
\bottomrule
\end{tabularx}
\end{table}
"""

vals = dict(
    raw_participants=R["raw_participants"], raw_observations=R["raw_observations"],
    excluded_total=R["excluded_total"], excl_rate_pct=R["excl_rate_pct"],
    N=R["N"], obs=R["obs"], median_page_seconds=R["median_page_seconds"],
    iqr_lo=R["iqr_page_seconds"][0], iqr_hi=R["iqr_page_seconds"][1],
    median_total_minutes=R["median_total_minutes"],
    over_reliance_overall=R["over_reliance_overall"], accuracy_overall=R["accuracy_overall"],
    or_hidden=R["or_hidden"], or_visible=R["or_visible"],
    or_auditable=R["or_auditable"], or_own=R["or_own"],
    acc_hidden=R["acc_hidden"], acc_visible=R["acc_visible"],
    acc_auditable=R["acc_auditable"], acc_own=R["acc_own"],
    icc_alpha=R["icc_alpha"],
    profile_table=profile_table, ratings_table=ratings_table,
    route_used_n=RT["formal route, used"]["n_participants"],
    route_used_pct=RT["formal route, used"]["pct"],
    route_paper_n=RT["route on paper, rarely used"]["n_participants"],
    route_none_n=RT["no formal route"]["n_participants"],
    route_dk_n=RT["do not know"]["n_participants"],
    pos_or=R["model_position"]["position"]["or"], pos_lo=R["model_position"]["position"]["lo"],
    pos_hi=R["model_position"]["position"]["hi"], pos_p=p(R["model_position"]["position"]["p"]),
    pos1_sec=R["by_position"]["1"]["seconds"], pos8_sec=R["by_position"]["8"]["seconds"],
    mc_immediate_pct=R["mc_immediate_pct"], mc_count_pct=R["mc_count_pct"],
    mc_count_median=R["mc_count_median"], suspicion_pct=R["suspicion_pct"],
    c_vo=f"{C['visible_own']['over_reliance']:.3f}",
    c_ha=f"{C['hidden_auditable']['over_reliance']:.3f}",
    never_overrelied=R["never_overrelied"], always_hi=R["always_hi"],
    mean_overrel_per_person=R["mean_overrel_per_person"],
    h1=orci(M["hidden"]), h2=orci(M["auditable"]), hxa=orci(M["hidden:auditable"]),
    mcnemar_more_hidden=R["mcnemar_more_hidden"], mcnemar_more_visible=R["mcnemar_more_visible"],
    mcnemar_tied=R["mcnemar_tied"], mcn_p=p(R["mcnemar_p"]),
    base=D["baseline"], det=D["detection"], auth=D["authority"], joint=D["joint"],
    resid=D["residual"], sum_parts=D["baseline"] + D["detection"] + D["authority"],
    det_share=D["detection_share"] * 100, auth_share=D["authority_share"] * 100,
    sa_vis=orci(R["simple_auditable_visible"]["auditable"]),
    sa_hid=orci(R["simple_auditable_hidden"]["auditable"]),
    sh_own=orci(R["simple_hidden_own"]["hidden"]),
    sh_aud=orci(R["simple_hidden_auditable"]["hidden"]),
    verify_visible=R["verify_visible"], verify_hidden=R["verify_hidden"],
    vh=orci(V["hidden"]), va=orci(V["auditable"]),
    conf_visible=R["conf_visible"], conf_hidden=R["conf_hidden"],
    a1=orci(A["hidden"]), a2=orci(A["auditable"]),
    conf_when_right=R["conf_when_right"], conf_when_wrong=R["conf_when_wrong"],
    calib_h_wrong=R["calib_hidden"]["wrong"], calib_v_right=R["calib_visible"]["right"],
    cf_acc_b=R["model_confidence"]["accuracy"]["b"], cf_acc_p=p(R["model_confidence"]["accuracy"]["p"]),
    cf_hid_b=R["model_confidence"]["hidden"]["b"], cf_hid_p=p(R["model_confidence"]["hidden"]["p"]),
    opt_obs=R["opt_obs"], opt_participants=R["opt_participants"], opt_mean=R["opt_mean"],
    opt_irr=R["model_options"]["over_reliance"]["irr"], opt_lo=R["model_options"]["over_reliance"]["lo"],
    opt_hi=R["model_options"]["over_reliance"]["hi"], opt_p=p(R["model_options"]["over_reliance"]["p"]),
    opt_disp=R["opt_dispersion"],
    h6=orci(R["model_expertise"]["hidden:exp_c"]), h6m=orci(R["model_expertise"]["exp_c"]),
    st=orci(R["model_stakes"]["stakes_c"]), stakes_mean=R["stakes_mean"], stakes_sd=R["stakes_sd"],
    n_low_stakes=R["n_low_stakes"],
    route_used_rate=R["route_mw"]["mean_used"], route_other_rate=R["route_mw"]["mean_other"],
    route_mw_p=p(R["route_mw"]["p"]), route_or=orci(R["model_route"]["route_used"]),
    n_suspicion=R["n_suspicion"], n_nosusp=R["n_nosusp"],
    rs_h=R["robust_nosuspicion"]["hidden"]["or"], rs_a=R["robust_nosuspicion"]["auditable"]["or"],
    adj_h=R["model_adjusted"]["hidden"]["or"], adj_a=R["model_adjusted"]["auditable"]["or"],
    n_followup_consent=R["n_followup_consent"], iv_n=R["iv_n"],
    iv_median_words=R["iv_median_words"],
    r3_agree=RG["R3"]["pct_agree"], r4_agree=RG["R4"]["pct_agree"],
    r5_agree=RG["R5"]["pct_agree"], r7_agree=RG["R7"]["pct_agree"], r8_agree=RG["R8"]["pct_agree"],
    bg_mean=R["blame_gap"]["mean"], bg_df=R["blame_gap"]["df"], bg_t=R["blame_gap"]["t"],
    bg_p=p(R["blame_gap"]["p"]), bg_d=R["blame_gap"]["d"], bg_pos=R["blame_gap"]["pct_positive"],
    t1a=R["iv_codes"]["T1_asymmetry_stated"]["n"], t2=R["iv_codes"]["T2_not_recorded"]["n"],
    t2b=R["iv_codes"]["T2_report_never_corrected"]["n"],
    t2c=R["iv_codes"]["T2_recording_not_answering"]["n"],
    t3=R["iv_codes"]["T3_defensive_paper"]["n"], t3b=R["iv_codes"]["T3_verbal_caveat"]["n"],
    t5=R["iv_reversal_n"], t6=R["iv_codes"]["T6_seniority_substitutes"]["n"],
    rev_sectors=len(R["iv_reversal_sectors"]),
    rev_bg_mean=R["iv_blame_by_reversal"]["reversal_mean"],
    oth_bg_mean=R["iv_blame_by_reversal"]["other_mean"],
    rev_bg_t=abs(R["iv_blame_by_reversal"]["t"]), rev_bg_p=p(R["iv_blame_by_reversal"]["p"]),
    rev_rate=IV["T5_asymmetry_reverses"]["mean_present"],
    oth_rate=IV["T5_asymmetry_reverses"]["mean_absent"],
    mw_rev=p(IV["T5_asymmetry_reverses"]["p"]),
    forum_rate=IV["T5_forum_makes_it_work"]["mean_present"],
    forum_oth=IV["T5_forum_makes_it_work"]["mean_absent"],
    mw_forum=p(IV["T5_forum_makes_it_work"]["p"]),
    nr_rate=IV["T2_not_recorded"]["mean_present"], nr_oth=IV["T2_not_recorded"]["mean_absent"],
    mw_nr=p(IV["T2_not_recorded"]["p"]),
    vc_rate=IV["T3_verbal_caveat"]["mean_present"], mw_vc=p(IV["T3_verbal_caveat"]["p"]),
    rho_bg=RB["blame_asymmetry_R5_minus_R4"]["rho"], rho_bg_p=p(RB["blame_asymmetry_R5_minus_R4"]["p"]),
    rho_r7=RB["R7"]["rho"], rho_r7_p=p(RB["R7"]["p"]),
    rho_r6=RB["R6"]["rho"], rho_r6_p=p(RB["R6"]["p"]), nbsp="~",
)
vals["joint_table"] = joint_table % vals
open("ch4_new.tex", "w", encoding="utf-8").write(T % vals)
print("wrote ch4_new.tex,", len(( T % vals).split()), "words")
