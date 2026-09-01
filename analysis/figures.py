#!/usr/bin/env python3
"""Figures for Chapter 4, drawn from results.json at close to printed size."""
import json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
import matplotlib.patches as mpatches

NAVY, TEAL, AMBER, GREEN, RED, GREY = "#1F3A5F", "#2A7F7F", "#D99A2B", "#4A7C59", "#B5453F", "#9AA3AD"
PALEGREY = "#F4F6F8"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "font.size": 8.2, "axes.labelsize": 8.4, "axes.titlesize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.8,
    "axes.linewidth": 0.7, "axes.edgecolor": "#5a6472",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})
R = json.load(open("results.json"))
OUT = "fig_source/"


def watermark(fig, text="PRE-COLLECTION DATA"):
    """Diagonal marker on every figure drawn from the pre-collection dataset."""
    fig.text(0.5, 0.5, text, fontsize=26, color="#B5453F", alpha=0.13,
             ha="center", va="center", rotation=27, zorder=100,
             fontweight="bold", transform=fig.transFigure)


def grid(ax, axis="y"):
    ax.set_axisbelow(True)
    ax.grid(axis=axis, color="#dfe4ea", linewidth=0.55)


# ------------------------------------------------------- Fig 1: the four cells
def fig_cells():
    order = ["visible_own", "visible_auditable", "hidden_own", "hidden_auditable"]
    lab = ["Warning shown\nown judgement", "Warning shown\nauditable",
           "Fault hidden\nown judgement", "Fault hidden\nauditable"]
    orv = [R["cells"][k]["over_reliance"] for k in order]
    acc = [R["cells"][k]["accuracy"] for k in order]
    x = np.arange(4); w = 0.36
    fig, ax = plt.subplots(figsize=(6.3, 3.05))
    b1 = ax.bar(x - w/2, orv, w, color=NAVY, edgecolor="white", linewidth=1.1,
                label="Followed the screen against the local evidence")
    b2 = ax.bar(x + w/2, acc, w, color=TEAL, edgecolor="white", linewidth=1.1,
                hatch="///", label="Chose the defensible action")
    for b in list(b1) + list(b2):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.012,
                f"{b.get_height():.3f}", ha="center", va="bottom", fontsize=7.6,
                color="#2b3440")
    ax.set_xticks(x); ax.set_xticklabels(lab)
    ax.set_ylabel("Proportion of decisions"); ax.set_ylim(0, 0.66)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.02),
              ncol=2, handlelength=1.5)
    grid(ax)
    watermark(fig)
    fig.savefig(OUT + "f_cells.pdf"); plt.close(fig)


# ------------------------------------------------------- Fig 2: forest plot
def fig_forest():
    rows = [
        ("Followed the screen", "Fault hidden (vs warning shown)", R["model_primary"]["hidden"]),
        ("Followed the screen", "Auditable framing (vs own judgement)", R["model_primary"]["auditable"]),
        ("Followed the screen", "Hidden $\\times$ auditable", R["model_primary"]["hidden:auditable"]),
        ("Defensible choice", "Fault hidden", R["model_accuracy"]["hidden"]),
        ("Defensible choice", "Auditable framing", R["model_accuracy"]["auditable"]),
        ("Intention to verify", "Fault hidden", R["model_verify"]["hidden"]),
        ("Intention to verify", "Auditable framing", R["model_verify"]["auditable"]),
    ]
    fig, ax = plt.subplots(figsize=(6.3, 3.5))
    ax.set_xscale("log")                       # before any tick call
    ticks = [0.25, 0.5, 1, 2, 4]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(FixedFormatter([str(t) for t in ticks]))
    ax.xaxis.set_minor_locator(NullLocator())

    y = np.arange(len(rows))[::-1]
    for yi, (_, _, v) in zip(y, rows):
        col = NAVY if v["lo"] > 1 else (TEAL if v["hi"] < 1 else GREY)
        ax.plot([v["lo"], v["hi"]], [yi, yi], color=col, lw=1.7,
                solid_capstyle="round", zorder=3)
        ax.plot([v["or"]], [yi], "o", ms=6.5, color=col, mec="white", mew=1.1, zorder=4)
        ax.text(4.55, yi, f"{v['or']:.2f}  [{v['lo']:.2f}, {v['hi']:.2f}]",
                va="center", fontsize=7.6, color="#2b3440")
    ax.axvline(1, color=RED, lw=0.9, ls=(0, (4, 2.5)), zorder=2)
    ax.set_yticks(y); ax.set_yticklabels([r[1] for r in rows])
    ax.set_xlim(0.22, 4.4); ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlabel("Odds ratio (log scale), 95% confidence interval")

    prev = None
    for yi, (grp, _, _) in zip(y, rows):
        if grp != prev:
            ax.text(0.235, yi + 0.42, grp, fontsize=7.8, style="italic",
                    color=NAVY, va="bottom")
            prev = grp
    for yy in (y[2] - 0.5, y[4] - 0.5):
        ax.axhline(yy, color="#e2e6eb", lw=0.7)
    grid(ax, axis="x")
    ax.text(4.55, len(rows) - 0.55, "OR [95% CI]", fontsize=7.6,
            color="#5a6472", style="italic")
    watermark(fig)
    fig.savefig(OUT + "f_forest.pdf"); plt.close(fig)


# ------------------------------------------------------- Fig 3: decomposition
def fig_decomp():
    d = R["decomp"]
    steps = [("Warning shown,\nown judgement", d["baseline"], GREY, None),
             ("+ fault hidden\n(detection failure)", d["detection"], AMBER, "///"),
             ("+ auditable framing\n(authority failure)", d["authority"], TEAL, "\\\\\\"),
             ("Fault hidden and\nauditable", d["joint"], NAVY, None)]
    fig, ax = plt.subplots(figsize=(6.3, 3.2))
    bottoms = [0, d["baseline"], d["baseline"] + d["detection"], 0]
    for i, ((lab, val, col, hatch), bot) in enumerate(zip(steps, bottoms)):
        ax.bar(i, val, 0.56, bottom=bot, color=col, edgecolor="white",
               linewidth=1.2, hatch=hatch)
        ax.text(i, bot + val + 0.011,
                (f"+{val:.3f}" if i in (1, 2) else f"{val:.3f}"),
                ha="center", va="bottom", fontsize=8, color="#2b3440",
                fontweight="bold" if i in (0, 3) else "normal")
    for i, bot in [(0, d["baseline"]), (1, d["baseline"] + d["detection"]),
                   (2, d["baseline"] + d["detection"] + d["authority"])]:
        ax.plot([i - 0.28, i + 1 + 0.28], [bot, bot], color="#9aa3ad",
                lw=0.8, ls=(0, (3, 2.5)), zorder=1)
    ax.set_xticks(range(4)); ax.set_xticklabels([s[0] for s in steps])
    ax.set_ylabel("Proportion following the screen"); ax.set_ylim(0, 0.50)
    grid(ax)
    ax.text(1, 0.462, f"{d['detection_share']*100:.0f}% of the rise",
            ha="center", fontsize=7.5, color="#8a6318")
    ax.text(2, 0.462, f"{d['authority_share']*100:.0f}% of the rise",
            ha="center", fontsize=7.5, color="#1d5a5a")
    ax.text(3.0, 0.052, f"residual\n{d['residual']:+.3f}", ha="center",
            fontsize=7, color="white")
    watermark(fig)
    fig.savefig(OUT + "f_decomp.pdf"); plt.close(fig)


# ------------------------------------------------------- Fig 4: two mechanisms
def fig_mech():
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.85), sharey=False)
    panels = [
        ("(a) Hiding the fault", [("Followed the screen", R["or_hidden"], R["or_visible"]),
                                  ("Intended to verify", R["verify_hidden"], R["verify_visible"]),
                                  ("Mean confidence /7", R["conf_hidden"]/7, R["conf_visible"]/7)],
         AMBER, "fault hidden", "warning shown"),
        ("(b) Making it auditable", [("Followed the screen", R["or_auditable"], R["or_own"]),
                                     ("Intended to verify", 0, 0),
                                     ("Mean confidence /7", 0, 0)],
         TEAL, "auditable", "own judgement"),
    ]
    a = pd.read_csv("analysis_sample_long.csv")
    panels[1][1][1] = ("Intended to verify",
                       float(a[a.auditable == 1].verification_intent.mean()),
                       float(a[a.auditable == 0].verification_intent.mean()))
    panels[1][1][2] = ("Mean confidence /7",
                       float(a[a.auditable == 1].confidence.mean())/7,
                       float(a[a.auditable == 0].confidence.mean())/7)

    for ax, (title, rows, col, l1, l0) in zip(axes, panels):
        y = np.arange(len(rows))[::-1]
        for yi, (lab, v1, v0) in zip(y, rows):
            ax.plot([v0, v1], [yi, yi], color="#c8cfd6", lw=1.6, zorder=1)
            ax.plot([v0], [yi], "o", ms=6.5, color="white", mec=GREY, mew=1.6, zorder=3)
            ax.plot([v1], [yi], "o", ms=6.5, color=col, mec="white", mew=1.1, zorder=4)
            ax.text((v0 + v1) / 2, yi + 0.22, f"{v1-v0:+.3f}", ha="center",
                    fontsize=7.2, color="#2b3440")
        ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows])
        ax.set_xlim(0, 1.0); ax.set_ylim(-0.55, 2.75)
        ax.set_title(title, color=NAVY, loc="left", fontsize=8.6, pad=9)
        ax.set_xlabel("Proportion")
        grid(ax, axis="x")
    h = [plt.Line2D([], [], marker="o", ls="", ms=6.5, mfc="white", mec=GREY, mew=1.6,
                    label="reference level"),
         plt.Line2D([], [], marker="o", ls="", ms=6.5, color=AMBER, label="fault hidden"),
         plt.Line2D([], [], marker="o", ls="", ms=6.5, color=TEAL, label="auditable framing")]
    fig.legend(handles=h, frameon=False, ncol=3, loc="lower center",
               bbox_to_anchor=(0.5, -0.10))
    fig.tight_layout()
    watermark(fig)
    fig.savefig(OUT + "f_mech.pdf"); plt.close(fig)


# ------------------------------------------------------- Fig 5: integration
def fig_integration():
    keys = [("T5_asymmetry_reverses", "Describes the asymmetry as absent\nor reversed"),
            ("T5_forum_makes_it_work", "Describes a standing forum obliged\nto answer the objection"),
            ("T2_not_recorded", "Objection left no durable record"),
            ("T3_verbal_caveat", "Disagreement voiced only verbally"),
            ("T6_seniority_substitutes", "Objection carried by rank, not\nby any mechanism")]
    t = R["iv_behaviour_tests"]
    fig, ax = plt.subplots(figsize=(6.3, 3.0))
    y = np.arange(len(keys))[::-1]
    for yi, (k, lab) in zip(y, keys):
        v = t[k]
        ax.plot([v["mean_absent"], v["mean_present"]], [yi, yi],
                color="#c8cfd6", lw=1.6, zorder=1)
        ax.plot([v["mean_absent"]], [yi], "o", ms=6.5, color="white",
                mec=GREY, mew=1.6, zorder=3)
        ax.plot([v["mean_present"]], [yi], "o", ms=6.5, color=NAVY,
                mec="white", mew=1.1, zorder=4)
        star = "*" if v["p"] < .05 else ""
        ax.text(0.505, yi, f"{v['mean_present']:.3f} vs {v['mean_absent']:.3f}"
                           f"   $p$ = {v['p']:.3f}{star}",
                va="center", fontsize=7.4, color="#2b3440")
    ax.set_yticks(y); ax.set_yticklabels([k[1] for k in keys])
    ax.set_xlim(0, 0.50); ax.set_ylim(-0.65, len(keys) - 0.15)
    ax.axvline(R["over_reliance_overall"], color=RED, lw=0.9, ls=(0, (4, 2.5)))
    ax.text(R["over_reliance_overall"] + 0.006, -0.60,
            f"sample mean {R['over_reliance_overall']:.3f}", fontsize=7.2, color=RED)
    ax.set_xlabel("Mean proportion following the screen, in that participant's own experiment")
    grid(ax, axis="x")
    h = [plt.Line2D([], [], marker="o", ls="", ms=6.5, mfc="white", mec=GREY, mew=1.6,
                    label="theme absent"),
         plt.Line2D([], [], marker="o", ls="", ms=6.5, color=NAVY, label="theme present")]
    ax.legend(handles=h, frameon=False, ncol=2, loc="lower center",
              bbox_to_anchor=(0.5, 1.0))
    watermark(fig)
    fig.savefig(OUT + "f_integration.pdf"); plt.close(fig)


# ------------------------------------------------------- Fig 6: options (null)
def fig_options():
    a = pd.read_csv("analysis_sample_long.csv")
    o = a[a.options_asked == 1]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.3, 2.6),
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    vals = sorted(o.options_generated.unique())
    for i, (lab, sub, col, hatch) in enumerate([
            ("Followed the screen", o[o.over_reliance == 1], NAVY, None),
            ("Did not", o[o.over_reliance == 0], TEAL, "///")]):
        c = sub.options_generated.value_counts(normalize=True).reindex(vals, fill_value=0)
        ax1.bar(np.array(vals) + (i - 0.5) * 0.36, c.values, 0.36, color=col,
                edgecolor="white", linewidth=1.0, hatch=hatch, label=lab)
    ax1.set_xticks(vals); ax1.set_xlabel("Distinct alternative actions named")
    ax1.set_ylabel("Proportion of responses")
    ax1.legend(frameon=False, handlelength=1.5); grid(ax1)

    m = R["model_options"]["over_reliance"]
    ax2.set_xscale("log")
    ticks = [0.5, 0.75, 1, 1.5]
    ax2.xaxis.set_major_locator(FixedLocator(ticks))
    ax2.xaxis.set_major_formatter(FixedFormatter([str(t) for t in ticks]))
    ax2.xaxis.set_minor_locator(NullLocator())
    ax2.plot([m["lo"], m["hi"]], [0, 0], color=GREY, lw=1.8, solid_capstyle="round")
    ax2.plot([m["irr"]], [0], "o", ms=7, color=GREY, mec="white", mew=1.1)
    ax2.axvline(1, color=RED, lw=0.9, ls=(0, (4, 2.5)))
    ax2.set_yticks([0]); ax2.set_yticklabels(["Followed the\nscreen"])
    ax2.set_ylim(-1, 1); ax2.set_xlim(0.45, 1.7)
    ax2.set_xlabel("Incidence rate ratio (log scale)")
    ax2.text(0.62, 0.42, f"IRR {m['irr']:.2f}  [{m['lo']:.2f}, {m['hi']:.2f}]",
             ha="center", fontsize=7.4, color="#2b3440")
    ax2.text(1.32, -0.55, "no difference", ha="center", fontsize=7.2, color=RED)
    grid(ax2, axis="x")
    fig.tight_layout()
    watermark(fig)
    fig.savefig(OUT + "f_options.pdf"); plt.close(fig)


# ------------------------------------------------------- Fig 7: calibration
def fig_calib():
    fig, ax = plt.subplots(figsize=(6.3, 2.6))
    groups = [("Warning shown", R["calib_visible"], TEAL, "///"),
              ("Fault hidden", R["calib_hidden"], AMBER, None)]
    x = np.arange(2); w = 0.34
    for i, (lab, v, col, hatch) in enumerate(groups):
        ax.bar(x[i] - w/2, v["right"], w, color=col, edgecolor="white", linewidth=1.1,
               hatch=hatch, label=None)
        ax.bar(x[i] + w/2, v["wrong"], w, color=col, alpha=0.45, edgecolor=col,
               linewidth=1.1, hatch=hatch)
        for xx, val in [(x[i] - w/2, v["right"]), (x[i] + w/2, v["wrong"])]:
            ax.text(xx, val + 0.03, f"{val:.2f}", ha="center", fontsize=7.8, color="#2b3440")
    ax.set_xticks(x); ax.set_xticklabels([g[0] for g in groups])
    ax.set_ylabel("Mean stated confidence (1 to 7)"); ax.set_ylim(4.4, 6.0)
    ax.axhline(R["calib_visible"]["right"], color=NAVY, lw=0.8, ls=(0, (4, 2.5)))
    ax.text(1.48, R["calib_visible"]["right"] + 0.03,
            "confidence when correct,\nwarning shown", fontsize=7, color=NAVY, va="bottom")
    h = [mpatches.Patch(facecolor="#7f8894", label="chose the defensible action"),
         mpatches.Patch(facecolor="#7f8894", alpha=0.45, label="did not")]
    ax.legend(handles=h, frameon=False, loc="upper left", handlelength=1.4)
    grid(ax)
    watermark(fig)
    fig.savefig(OUT + "f_calib.pdf"); plt.close(fig)


import os
os.makedirs(OUT, exist_ok=True)
for f in (fig_cells, fig_forest, fig_decomp, fig_mech, fig_integration,
          fig_options, fig_calib):
    f(); print("drew", f.__name__)
