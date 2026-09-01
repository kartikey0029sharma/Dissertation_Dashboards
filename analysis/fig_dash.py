#!/usr/bin/env python3
"""The two mock dashboard figures for Chapter 1, rebuilt so that the numbers,
the dates and the sort order are internally consistent."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

NAVY, TEAL, AMBER, GREEN, RED, GREY = "#1F3A5F", "#2A7F7F", "#D99A2B", "#4A7C59", "#B5453F", "#9AA3AD"
PALEG, PALEA, PALEN, INK, MUTED = "#F4F6F8", "#FBF0D8", "#E8EEF5", "#20272E", "#6B7683"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.03, "figure.dpi": 220})

KPI = [("NET REVENUE (90 DAYS)", "₹18.4 cr", "▲ 6.2% vs LY", GREEN),
       ("FOOTFALL", "4.21 lakh", "▲ 11.0% vs LY", GREEN),
       ("CONVERSION RATE", "21.4%", "▲ 0.8 pp vs LY", GREEN),
       ("SALES PER SQ FT", "₹1,240", "▲ 4.1% vs LY", GREEN)]
GROWTH = [("Tiruppur", 18.4), ("Salem", 11.2), ("Erode", 9.6),
          ("Thrissur", 5.1), ("Kollam", 3.8)]

def panel(ax, shortlist, banner=None, annotate=False, stale_row=None):
    ax.set_xlim(-4.5, 104.5); ax.set_ylim(0, 62); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 100, 62, fc="white", ec="#D3D9DF", lw=0.9))
    ax.add_patch(Rectangle((0, 56.5), 100, 5.5, fc=NAVY, ec="none"))
    ax.text(2, 59.2, "Kovai Footwear  |  Store Network Performance", color="white",
            fontsize=7.2, fontweight="bold", va="center")
    ax.text(74, 59.2, "Region: All", color="#C6D2E0", fontsize=6.2, va="center", ha="right")
    ax.text(97.5, 59.2, "Period: last 90 days", color="#C6D2E0", fontsize=6.2, va="center", ha="right")

    top = 54.5
    if banner:
        ax.add_patch(FancyBboxPatch((1.6, 47.6), 96.8, 6.4, boxstyle="round,pad=0.15,rounding_size=0.5",
                                    fc="#FBEDE8", ec=RED, lw=1.1))
        ax.text(3.2, 51.9, "⚠", color=RED, fontsize=9, va="center", fontweight="bold")
        ax.text(6.4, 52.6, banner[0], color=RED, fontsize=6.5, va="center", fontweight="bold")
        ax.text(6.4, 49.6, banner[1], color="#8A3A34", fontsize=6.2, va="center")
        top = 45.6

    w = 23.4
    for i, (lab, val, delta, col) in enumerate(KPI):
        x = 1.6 + i * (w + 1.1)
        ax.add_patch(Rectangle((x, top - 9.6), w, 9.6, fc=PALEG, ec="#E1E6EB", lw=0.7))
        ax.text(x + 1.2, top - 2.2, lab, fontsize=5.3, color=MUTED, va="center", fontweight="bold")
        ax.text(x + 1.2, top - 5.4, val, fontsize=10.5, color=INK, va="center", fontweight="bold")
        ax.text(x + 1.2, top - 8.2, delta, fontsize=5.6, color=col, va="center")

    ty = top - 12.4
    ax.text(1.6, ty, "EXPANSION SHORTLIST · by Site Score", fontsize=5.8,
            color=MUTED, fontweight="bold")
    ax.text(52, ty, "FOOTFALL GROWTH vs LAST YEAR (%)", fontsize=5.8,
            color=MUTED, fontweight="bold")
    ax.plot([1.6, 47], [ty - 1.5, ty - 1.5], color="#DDE2E7", lw=0.7)
    for c, x in [("Candidate town", 2.4), ("Site Score", 27), ("Action", 39)]:
        ax.text(x, ty - 3.4, c, fontsize=5.4, color=MUTED, fontweight="bold")

    for i, (town, score, action, col) in enumerate(shortlist):
        y = ty - 6.2 - i * 3.5
        if i == 0 and not banner:
            ax.add_patch(Rectangle((1.6, y - 1.3), 45.4, 3.1, fc="#EAF3EC", ec="none"))
        if stale_row is not None and town == stale_row:
            ax.add_patch(Rectangle((1.6, y - 1.3), 45.4, 3.1, fc="#FBEDE8", ec="none"))
        ax.text(2.4, y, town, fontsize=6.1, color=INK, va="center")
        ax.text(27, y, str(score), fontsize=6.1, color=INK, va="center", fontweight="bold")
        ax.add_patch(FancyBboxPatch((38.6, y - 1.0), 7.6, 2.0,
                                    boxstyle="round,pad=0.08,rounding_size=0.4",
                                    fc=col + "22", ec=col, lw=0.6))
        ax.text(42.4, y, action, fontsize=5.2, color=col, ha="center", va="center",
                fontweight="bold")

    bx, bw = 62, 33
    for i, (town, v) in enumerate(GROWTH):
        y = ty - 6.2 - i * 3.5
        ax.text(bx - 1.2, y, town, fontsize=5.8, color=INK, ha="right", va="center")
        ax.add_patch(Rectangle((bx, y - 0.9), bw * v / 20.0, 1.8, fc=TEAL, ec="none"))
        lbl = f"{v}%"
        if banner and town == "Tiruppur":
            ax.add_patch(Rectangle((bx, y - 0.9), bw * v / 20.0, 1.8,
                                   fc="none", ec=RED, lw=0.9, hatch="////"))
            lbl = "STALE FEED   " + lbl
        ax.text(bx + bw * v / 20.0 + 0.8, y, lbl, fontsize=5.5,
                color=RED if (banner and town == "Tiruppur") else MUTED, va="center")

    ax.text(52, 2.2, "Source: footfall counters, nightly extract", fontsize=5.2, color="#9AA3AD")

    if annotate:
        for tag, x, y in [("A", -2.3, top - 5.4), ("B", 102.3, 59.2),
                          ("C", -2.3, ty - 6.2), ("D", 102.3, ty - 13.2)]:
            ax.add_patch(plt.Circle((x, y), 1.9, fc=AMBER, ec="white", lw=0.8, zorder=9))
            ax.text(x, y, tag, fontsize=5.6, color="white", ha="center", va="center",
                    fontweight="bold", zorder=10)

SL_A = [("Tiruppur", 87, "Open Q3", GREEN), ("Salem", 74, "Watch", AMBER),
        ("Erode", 71, "Watch", AMBER), ("Thrissur", 63, "Hold", GREY),
        ("Kollam", 58, "Hold", GREY)]
# with the stale counter excluded, Tiruppur recomputes to 62 and falls to fourth
SL_B = [("Salem", 74, "Watch", AMBER), ("Erode", 71, "Watch", AMBER),
        ("Thrissur", 63, "Hold", GREY), ("Tiruppur", 62, "Hold", RED),
        ("Kollam", 58, "Hold", GREY)]

fig, ax = plt.subplots(figsize=(7.1, 4.4)); panel(ax, SL_A, annotate=True)
fig.savefig("fig_source/f_dash_anatomy.pdf"); plt.close(fig)

fig, axes = plt.subplots(2, 1, figsize=(6.6, 8.6))
axes[0].set_title("(a) The screen as the regional manager saw it on 3 June",
                  fontsize=7.4, color=NAVY, loc="left", pad=5)
panel(axes[0], SL_A)
axes[1].set_title("(b) The same screen with a data-provenance banner added",
                  fontsize=7.4, color=NAVY, loc="left", pad=5)
panel(axes[1], SL_B,
      banner=("Footfall feed: 3 of 22 counters are not reporting.",
              "Tiruppur counter offline since 12 May (22 days). Site Score recomputed on "
              "reporting counters only: 87 → 62."),
      stale_row="Tiruppur")
fig.subplots_adjust(hspace=0.16)
fig.savefig("fig_source/f_dash_signal.pdf"); plt.close(fig)
print("rebuilt f_dash_anatomy.pdf and f_dash_signal.pdf")
