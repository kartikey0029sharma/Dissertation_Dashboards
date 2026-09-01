#!/usr/bin/env python3
"""Regenerate the appendices that the revised design and the analysis changed."""
import json
R = json.load(open("results.json"))
def p(x): return "$<.001$" if x < .001 else f"${x:.3f}$".replace("0.", ".")

# ---------------------------------------------------------- Appendix E
def model_rows(model, keys, labels):
    out = []
    for k, lab in zip(keys, labels):
        v = model[k]
        out.append(f"{lab} & {v['b']:+.3f} & {v['se']:.3f} & {v['or']:.2f} & "
                   f"[{v['lo']:.2f}, {v['hi']:.2f}] & {p(v['p'])} \\\\")
    return "\n".join(out)

APP_E = r"""Experimental Factors and Measures, and the Design Revision}

Section 3.5.1 describes the instrument. This appendix records the factors as finally implemented,
the algebra behind the design revision, and the power grid on which the sample size rests.

\begin{table}[H]
\centering\footnotesize
\caption{Experimental factors, levels and how each is operationalised}
\label{tab:factors}
\rowcolors{2}{palegrey}{white}
\begin{tabularx}{\textwidth}{@{}p{3.0cm} p{3.1cm} X@{}}
\toprule
\rowcolor{palenavy}
\textbf{Factor} & \textbf{Levels} & \textbf{How it is operationalised} \\
\midrule
Data quality signal \emph{(within)} & Hidden or Visible & Presence or absence of a notice saying the
feed is stale and incomplete, as in Figure~\ref{fig:signal} \\
Accountability framing \emph{(within)} & Auditable or Own judgement & Whether the decision will be
recorded and reviewed against the dashboard, or recorded as the manager's own call \\
Scenario \emph{(within, crossed)} & Eight, one per sector & Latin square: scenario $j$ takes
condition $(j+V)\bmod 4$, $V$ drawn at random from 0 to 3 \\
\midrule
\rowcolor{paleamber}
\multicolumn{3}{@{}l}{\textbf{Withdrawn when the design was revised}}\\
Decision risk & \emph{withdrawn} & Aliased with the signal $\times$ accountability interaction
within a participant. Replaced by perceived stakes, measured after each vignette \\
Metric prominence & \emph{withdrawn} & Was between subjects and the weakest term; dropped to fund
four further within-participant observations \\
\midrule
\rowcolor{paleteal}
\multicolumn{3}{@{}l}{\textbf{Measured outcomes}}\\
Deference \emph{(primary)} & Binary & Chose the dashboard-consistent action despite the conflicting
local evidence \\
Decision accuracy & Binary & Chose the action defensible on all evidence available \\
Options generated & Count & Distinct alternative actions named; asked on a random three vignettes
of eight \\
Confidence & Seven point scale & Self-rated confidence in the action chosen \\
Perceived stakes & Seven point scale & How much the participant judges to be riding on the decision \\
Verification intent & Binary & Whether more data were requested before deciding \\
Seconds on page & Continuous & Time from render to submission \\
\midrule
\multicolumn{3}{@{}l}{\textbf{Covariates:} sector, years of experience, seniority, organisation size,
dashboard use frequency, analytics familiarity, dissent route}\\
\bottomrule
\end{tabularx}
\end{table}

\textbf{\emph{Why the original design could not work.}} Coding high risk, hidden fault and auditable
framing each as $+1$ and their opposites as $-1$, the eight cells of the original
$2\times2\times2$ split into two blocks of four. Block A is the $I = +ABC$ half fraction and Block B
is $I = -ABC$. Within any one participant, therefore, risk took the value $+1$ exactly when the
other two factors agreed in sign and $-1$ exactly when they disagreed. Risk and the two-factor
interaction are the same contrast inside a person, and can be separated only by comparing Block A
participants with Block B participants. A factor advertised as within-subjects was in fact
between-subjects.

Separately, each of the four cells inside a block carried a different scenario. The within-person
data-signal contrast was therefore (kovai + freight) $-$ (fraud + supplier) in Block A and the
reverse in Block B, so scenario cancelled only when the two blocks were averaged and could not be
entered in the model at all.

\textbf{\emph{Power simulation.}} Generalised estimating equation, logit link, exchangeable working
correlation clustered on participant. Participant SD 0.85 on the log-odds scale (ICC about .18),
scenario SD 0.35, baseline $p = .40$, hidden $+0.75$ log-odds, auditable $+0.95$, interaction 0.50.
Four hundred replications per cell; $k$ is vignettes per participant.

\begin{table}[H]
\centering\footnotesize
\caption{Simulated power by vignettes per participant and sample size}
\label{tab:power}
\rowcolors{2}{palegrey}{white}
\begin{tabularx}{\textwidth}{@{}r r r r r X@{}}
\toprule
\rowcolor{palenavy}
\textbf{k} & \textbf{N} & \textbf{obs} & \textbf{Power, main effect} & \textbf{Power, interaction} &
\textbf{Note} \\
\midrule
4 & 60 & 240 & .46 & .13 & \\
4 & 80 & 320 & .60 & .17 & \\
4 & 100 & 400 & .67 & .18 & \\
4 & 120 & 480 & .74 & .22 & the original design \\
6 & 80 & 480 & .74 & .19 & same power, fewer recruits \\
6 & 100 & 600 & .83 & .28 & \\
6 & 120 & 720 & .89 & .29 & \\
8 & 60 & 480 & .74 & .22 & same power again, half the recruits \\
8 & 80 & 640 & .87 & .29 & \textbf{adopted target} \\
8 & 100 & 800 & .94 & .35 & \\
8 & 120 & 960 & .95 & .40 & interaction still underpowered \\
\bottomrule
\end{tabularx}
\end{table}

Two conclusions follow. Power tracks total observations and is close to indifferent to how they are
split, so vignettes buy power more cheaply than recruits do. And the interaction never becomes well
powered within any feasible design, which is why it is declared exploratory in advance.

\newpage

"""

# ---------------------------------------------------------- Appendix P
M, A, V = R["model_primary"], R["model_accuracy"], R["model_verify"]
ADJ, EXP, ST = R["model_adjusted"], R["model_expertise"], R["model_stakes"]
APP_P = r"""Full Model Estimates \textcolor{redc}{[pre-collection dataset]}}

\simbox{\textbf{\textcolor{redc}{THESE ESTIMATES COME FROM THE PRE-COLLECTION DATASET DESCRIBED AT
SECTION 4.3.}} They are reported so that the specification can be checked, not as findings.}

All models are generalised estimating equations with robust standard errors, clustered on
participant, with an exchangeable working correlation unless stated. $N$ = %(N)d participants,
%(obs)d observations. Coefficients are on the log-odds scale.

\begin{table}[H]
\centering\footnotesize
\caption{\SIM Primary model: deference on data signal, accountability framing and their interaction}
\label{tab:m1}
\rowcolors{2}{palegrey}{white}
\begin{tabularx}{\textwidth}{@{}X r r r l l@{}}
\toprule
\rowcolor{palenavy}
\textbf{Term} & \textbf{$b$} & \textbf{SE} & \textbf{OR} & \textbf{95\%% CI} & \textbf{$p$} \\
\midrule
%(m1)s
\bottomrule
\end{tabularx}
\end{table}

\begin{table}[H]
\centering\footnotesize
\caption{\SIM Secondary outcomes: defensible choice and intention to verify}
\label{tab:m2}
\rowcolors{2}{palegrey}{white}
\begin{tabularx}{\textwidth}{@{}X r r r l l@{}}
\toprule
\rowcolor{palenavy}
\textbf{Term} & \textbf{$b$} & \textbf{SE} & \textbf{OR} & \textbf{95\%% CI} & \textbf{$p$} \\
\midrule
\rowcolor{paleteal}\multicolumn{6}{@{}l}{\textbf{Defensible choice}}\\
%(m2a)s
\rowcolor{paleteal}\multicolumn{6}{@{}l}{\textbf{Intention to verify}}\\
%(m2b)s
\bottomrule
\end{tabularx}
\end{table}

\begin{table}[H]
\centering\footnotesize
\caption{\SIM Covariate-adjusted model, with scenario fixed effects (scenario terms omitted)}
\label{tab:m3}
\rowcolors{2}{palegrey}{white}
\begin{tabularx}{\textwidth}{@{}X r r r l l@{}}
\toprule
\rowcolor{palenavy}
\textbf{Term} & \textbf{$b$} & \textbf{SE} & \textbf{OR} & \textbf{95\%% CI} & \textbf{$p$} \\
\midrule
%(m3)s
\bottomrule
\end{tabularx}
\end{table}

\begin{table}[H]
\centering\footnotesize
\caption{\SIM Exploratory and robustness models}
\label{tab:m4}
\rowcolors{2}{palegrey}{white}
\begin{tabularx}{\textwidth}{@{}X r r r l l@{}}
\toprule
\rowcolor{palenavy}
\textbf{Term} & \textbf{$b$} & \textbf{SE} & \textbf{OR} & \textbf{95\%% CI} & \textbf{$p$} \\
\midrule
\rowcolor{paleteal}\multicolumn{6}{@{}l}{\textbf{H6, expertise moderation (declared exploratory)}}\\
%(m4a)s
\rowcolor{paleteal}\multicolumn{6}{@{}l}{\textbf{Perceived stakes (measured, not manipulated)}}\\
%(m4b)s
\rowcolor{paleteal}\multicolumn{6}{@{}l}{\textbf{Excluding participants who inferred the design ($n$ = %(nosusp)d)}}\\
%(m4c)s
\bottomrule
\end{tabularx}
\end{table}

\textbf{\emph{Option counts.}} Poisson model clustered on participant, %(optobs)d observations:
deference IRR %(oi).2f [%(ol).2f, %(oh).2f], hidden IRR %(hi).2f [%(hl).2f, %(hh).2f], auditable
IRR %(ai).2f [%(al).2f, %(ah).2f]. Pearson dispersion %(disp).2f, so no negative binomial fallback
was required.

\textbf{\emph{Pre-committed fallback.}} Exact binomial on within-participant differences:
%(mh)d participants deferred more often under the hidden condition, %(mv)d more often under the
disclosed condition, %(mt)d tied, $p$ %(mp)s.

\newpage

""" % dict(
    N=R["N"], obs=R["obs"], nosusp=R["n_nosusp"],
    m1=model_rows(M, ["Intercept", "hidden", "auditable", "hidden:auditable"],
                  ["Intercept", "Fault hidden", "Auditable framing", "Hidden $\\times$ auditable"]),
    m2a=model_rows(A, ["Intercept", "hidden", "auditable", "hidden:auditable"],
                   ["Intercept", "Fault hidden", "Auditable framing", "Hidden $\\times$ auditable"]),
    m2b=model_rows(V, ["Intercept", "hidden", "auditable", "hidden:auditable"],
                   ["Intercept", "Fault hidden", "Auditable framing", "Hidden $\\times$ auditable"]),
    m3=model_rows(ADJ, ["Intercept", "hidden", "auditable", "hidden:auditable", "stakes_c",
                        "exp_c", "senior", "daily"],
                  ["Intercept", "Fault hidden", "Auditable framing", "Hidden $\\times$ auditable",
                   "Perceived stakes (centred)", "Experience (centred)", "Senior manager or above",
                   "Uses dashboards daily"]),
    m4a=model_rows(EXP, ["hidden", "exp_c", "hidden:exp_c", "auditable"],
                   ["Fault hidden", "Experience (centred)", "Hidden $\\times$ experience",
                    "Auditable framing"]),
    m4b=model_rows(ST, ["hidden", "auditable", "stakes_c"],
                   ["Fault hidden", "Auditable framing", "Perceived stakes (centred)"]),
    m4c=model_rows(R["robust_nosuspicion"], ["hidden", "auditable", "hidden:auditable"],
                   ["Fault hidden", "Auditable framing", "Hidden $\\times$ auditable"]),
    optobs=R["opt_obs"],
    oi=R["model_options"]["over_reliance"]["irr"], ol=R["model_options"]["over_reliance"]["lo"],
    oh=R["model_options"]["over_reliance"]["hi"],
    hi=R["model_options"]["hidden"]["irr"], hl=R["model_options"]["hidden"]["lo"],
    hh=R["model_options"]["hidden"]["hi"],
    ai=R["model_options"]["auditable"]["irr"], al=R["model_options"]["auditable"]["lo"],
    ah=R["model_options"]["auditable"]["hi"], disp=R["opt_dispersion"],
    mh=R["mcnemar_more_hidden"], mv=R["mcnemar_more_visible"], mt=R["mcnemar_tied"],
    mp=p(R["mcnemar_p"]),
)

open("app_E.tex", "w", encoding="utf-8").write(APP_E)
open("app_P.tex", "w", encoding="utf-8").write(APP_P)
print("wrote app_E.tex and app_P.tex")
