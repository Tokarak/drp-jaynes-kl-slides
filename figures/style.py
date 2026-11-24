"""House style shared by Matplotlib figures (and mirrored in anim/ and slides/)."""
import matplotlib as mpl

# Hypothesis colours: A (bad batch / "truth") orange, B (good batch / alternative) blue.
COL_A = "#d55e00"
COL_B = "#0072b2"
COL_POST = "#009e73"
COL_GREY = "#666666"
CMAP = "viridis"


def use():
    mpl.rcParams.update({
        "figure.figsize": (8, 4.5),
        "figure.dpi": 100,
        "savefig.bbox": "tight",
        "savefig.transparent": False,
        "font.size": 15,
        "axes.titlesize": 16,
        "axes.labelsize": 15,
        "mathtext.fontset": "cm",
        "font.family": "serif",
        "font.serif": ["CMU Serif", "Computer Modern Roman", "DejaVu Serif"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "svg.fonttype": "path",
    })
