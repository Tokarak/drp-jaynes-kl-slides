"""Static figures for the KL-divergence session. Usage: python figures/make_figures.py [outdir]"""
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.stats import binom

sys.path.insert(0, str(Path(__file__).parent))
import style
from style import COL_A, COL_B, COL_GREY, CMAP

style.use()
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "slides/fig")
OUT.mkdir(parents=True, exist_ok=True)

pA, pB = 1 / 3, 1 / 6          # P(bad | A), P(bad | B)
E_BAD = 10 * np.log10(pA / pB)              # +3.01 dB
E_GOOD = 10 * np.log10((1 - pA) / (1 - pB))  # -0.97 dB


def db(x):
    return 10 * np.log10(x)


def kl_bern(a, b):
    """D_KL(Bern(a) || Bern(b)) in dB."""
    return a * db(a / b) + (1 - a) * db((1 - a) / (1 - b))


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg")
    fig.savefig(OUT / f"{name}.pdf")
    plt.close(fig)
    print("wrote", name)


# V1 (static fallback): one table, two slices -----------------------------------
def v1():
    n = 10
    th = np.linspace(0, 1, 201)
    k = np.arange(n + 1)
    T = binom.pmf(k[:, None], n, th[None, :])          # rows: data k, cols: theta
    th0, k0 = 0.3, 7
    fig = plt.figure(figsize=(13, 4.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.3, 1, 1], wspace=0.35)
    ax = fig.add_subplot(gs[0])
    ax.imshow(T, origin="lower", aspect="auto", cmap=CMAP, extent=[0, 1, -0.5, n + 0.5])
    ax.axvline(th0, color=COL_B, lw=2.5)
    ax.axhline(k0, color=COL_A, lw=2.5)
    ax.set(xlabel=r"$\theta$", ylabel=r"data $D$: # heads $k$", title=r"$P(D\mid\theta)$, $n=10$")
    ax2 = fig.add_subplot(gs[1])
    ax2.bar(k, binom.pmf(k, n, th0), color=COL_B)
    ax2.set(xlabel=r"$k$", title=rf"fix $\theta={th0}$: sampling dist.", ylabel="probability")
    ax2.text(0.97, 0.92, r"$\sum_k = 1$", transform=ax2.transAxes, ha="right")
    ax3 = fig.add_subplot(gs[2])
    L = binom.pmf(k0, n, th)
    ax3.plot(th, L, color=COL_A, lw=2.5)
    ax3.fill_between(th, L, alpha=0.15, color=COL_A)
    ax3.set(xlabel=r"$\theta$", title=rf"fix $k={k0}$: likelihood $L(\theta)$")
    ax3.text(0.03, 0.55, rf"$\int_0^1 L\,d\theta = {np.trapezoid(L, th):.3f}$" "\n" r"$= 1/(n+1)$, not 1",
             transform=ax3.transAxes, fontsize=13)
    save(fig, "v1_table_slices")


# V2 (static fallback): evidence random walks -------------------------------------
def v2(n_paths=40, n=60, seed=1):
    rng = np.random.default_rng(seed)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    for ax, (truth, p, col, drift) in zip(axes, [
            ("A", pA, COL_A, kl_bern(pA, pB)), ("B", pB, COL_B, -kl_bern(pB, pA))]):
        bad = rng.random((n_paths, n)) < p
        steps = np.where(bad, E_BAD, E_GOOD)
        paths = -10 + np.concatenate([np.zeros((n_paths, 1)), steps.cumsum(1)], 1)
        ax.plot(np.arange(n + 1), paths.T, color=col, alpha=0.25, lw=1)
        ax.plot([0, n], [-10, -10 + drift * n], color="k", lw=2.5, ls="--",
                label=rf"drift ${drift:+.3f}$ dB/widget")
        ax.axhspan(0, 30, color=COL_A, alpha=0.07)
        ax.axhspan(-40, -13, color=COL_B, alpha=0.07)
        ax.axhline(0, color=COL_GREY, lw=0.8)
        ax.axhline(-13, color=COL_GREY, lw=0.8)
        ax.set(title=f"{truth} true", xlabel="widgets tested $n$", ylim=(-40, 30))
        ax.legend(loc="upper left" if truth == "A" else "lower left")
    axes[0].set_ylabel(r"$e(A\mid DX)$ [dB]")
    axes[1].text(n, 2, "reject", ha="right", color=COL_A)
    axes[1].text(n, -16, "accept", ha="right", va="top", color=COL_B)
    save(fig, "v2_walks")


# V3: pointwise contributions p log(p/q) ----------------------------------------
def v3():
    n = 10
    k = np.arange(n + 1)
    p, q = binom.pmf(k, n, pA), binom.pmf(k, n, pB)
    c = p * db(p / q)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True,
                                   gridspec_kw={"height_ratios": [1, 1]})
    w = 0.4
    ax1.bar(k - w / 2, p, w, color=COL_A, label=r"$p = P(k\mid A)$")
    ax1.bar(k + w / 2, q, w, color=COL_B, label=r"$q = P(k\mid B)$")
    ax1.set(ylabel="probability", title="# bad widgets in a batch of 10")
    ax1.legend()
    ax2.bar(k, c, 0.8, color=np.where(c >= 0, COL_A, COL_B))
    ax2.axhline(0, color="k", lw=0.8)
    ax2.set(xlabel="$k$", ylabel=r"$p\cdot 10\log_{10}(p/q)$ [dB]")
    ax2.text(0.98, 0.85, rf"total $= D_{{KL}}(p\Vert q) = {c.sum():.2f}$ dB"
             "\n" rf"$= 10\times{kl_bern(pA, pB):.3f}$",
             transform=ax2.transAxes, ha="right", va="top")
    save(fig, "v3_pointwise")


# V4: KL(Bern a || Bern b) heatmap --------------------------------------------------
def v4():
    g = np.linspace(0.01, 0.99, 400)
    a, b = np.meshgrid(g, g, indexing="ij")
    K = kl_bern(a, b)
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    im = ax.pcolormesh(g, g, K.T, cmap=CMAP, norm=LogNorm(1e-2, 20), shading="auto")
    cs = ax.contour(g, g, K.T, levels=[0.1, 0.3, 1, 3, 10], colors="w", linewidths=0.8)
    ax.clabel(cs, fmt="%g", fontsize=10)
    ax.plot([0, 1], [0, 1], color="w", ls=":", lw=1)
    ax.plot(pA, pB, "o", color=COL_A, ms=9, mec="w")
    ax.plot(pB, pA, "o", color=COL_B, ms=9, mec="w")
    box = dict(boxstyle="round,pad=0.25", fc="w", ec="none", alpha=0.9)
    ax.annotate(rf"$D(A\Vert B)={kl_bern(pA, pB):.3f}$", (pA, pB), (0.5, 0.12), bbox=box,
                fontsize=13, arrowprops=dict(arrowstyle="-", color="w"))
    ax.annotate(rf"$D(B\Vert A)={kl_bern(pB, pA):.3f}$", (pB, pA), (0.04, 0.72), bbox=box,
                fontsize=13, arrowprops=dict(arrowstyle="-", color="w"))
    ax.set(xlabel=r"$a$ (truth)", ylabel=r"$b$ (model)", aspect="equal",
           title=r"$D_{KL}(\mathrm{Bern}(a)\,\Vert\,\mathrm{Bern}(b))$ [dB]")
    fig.colorbar(im, ax=ax, shrink=0.85)
    save(fig, "v4_kl_heatmap")


# V5: Stein's lemma -------------------------------------------------------------------
def stein_beta(n, p0, p1, alpha=0.05):
    """Most powerful (non-randomised) test of H0: theta=p0 vs H1: theta=p1, size <= alpha.
    Returns type II error beta = P(accept H0 | H1)."""
    k = np.arange(n + 1)
    if p1 > p0:   # reject for large k
        tail = binom.sf(k - 1, n, p0)              # P0(K >= c)
        c = k[np.argmax(tail <= alpha)] if (tail <= alpha).any() else n + 1
        return binom.cdf(c - 1, n, p1)
    tail = binom.cdf(k, n, p0)                     # P0(K <= c)
    ok = k[tail <= alpha]
    c = ok.max() if ok.size else -1
    return binom.sf(c, n, p1)


def v5():
    ns_a = np.arange(1, 301)
    ns_b = np.unique(np.geomspace(5, 5000, 120).astype(int))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))
    for p0, p1, col, lab in [(pB, pA, COL_B, r"$H_0=B$, $H_1=A$"),
                             (pA, pB, COL_A, r"$H_0=A$, $H_1=B$")]:
        s_ = kl_bern(p0, p1)
        y = db(np.array([stein_beta(n, p0, p1) for n in ns_a]))
        ax1.plot(ns_a, y, color=col, lw=1.5, label=lab)
        r = -db(np.array([stein_beta(n, p0, p1) for n in ns_b])) / ns_b
        ax2.plot(ns_b, r, color=col, lw=2)
        ax2.axhline(s_, color=col, ls="--", lw=1)
        ax2.text(5200, s_, rf"$D(P_{{H_0}}\Vert P_{{H_1}})={s_:.3f}$", color=col, va="center", fontsize=12)
    ax1.set(xlabel="widgets tested $n$", ylabel=r"$10\log_{10}\beta_n$ [dB]",
            title=r"type II error, type I fixed at $\alpha=0.05$")
    ax1.legend(loc="lower left")
    ax2.set(xscale="log", xlabel="$n$", ylabel=r"$-\frac{1}{n}\,10\log_{10}\beta_n$ [dB/widget]",
            title="Stein: exponent $\\to D_{KL}$", ylim=(0, 0.4), xlim=(5, 5000))
    save(fig, "v5_stein")


# Gibbs' inequality via ln x <= x - 1 ------------------------------------------------
def gibbs():
    x = np.linspace(0.05, 3, 300)
    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.plot(x, np.log(x), color=COL_A, lw=2.5, label=r"$\ln x$")
    ax.plot(x, x - 1, color=COL_B, lw=2.5, label=r"$x-1$")
    ax.plot(1, 0, "ko")
    ax.axhline(0, color=COL_GREY, lw=0.6)
    ax.axvline(0, color=COL_GREY, lw=0.6)
    ax.set(xlabel="$x$", ylim=(-3, 2.1))
    ax.legend(loc="lower right")
    ax.text(1.08, -0.35, "equality only at $x=1$", fontsize=12)
    save(fig, "gibbs_tangent")


# Geometry teaser: Bernoulli family as a quarter circle -------------------------------
def geometry():
    th = np.linspace(0, 1, 400)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
    ticks = np.linspace(0, 1, 11)
    ax1.plot(th, 0 * th, color="k", lw=2)
    ax1.plot(ticks, 0 * ticks, "|", color=COL_A, ms=18, mew=2)
    ax1.set(xlabel=r"$\theta$", yticks=[], title=r"$\theta\in[0,1]$, equal $\Delta\theta$")
    ax1.spines["left"].set_visible(False)
    x, y = 2 * np.sqrt(th), 2 * np.sqrt(1 - th)
    ax2.plot(x, y, color="k", lw=2)
    ax2.plot(2 * np.sqrt(ticks), 2 * np.sqrt(1 - ticks), "o", color=COL_A)
    ax2.set(aspect="equal", xlabel=r"$2\sqrt{\theta}$", ylabel=r"$2\sqrt{1-\theta}$",
            title="same points: arc length = Fisher distance")
    ax2.text(1.5, 1.5, r"total length $\pi$", fontsize=13)
    save(fig, "geometry_quarter_circle")


if __name__ == "__main__":
    for f in (v1, v2, v3, v4, v5, gibbs, geometry):
        f()
