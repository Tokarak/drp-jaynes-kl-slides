"""Manim CE scenes for the KL-divergence session.

    manim -ql anim/kl_scenes.py BayesUpdate            # iterate
    manim -qh anim/kl_scenes.py BayesUpdate LikelihoodConcentration   # final
"""
import numpy as np
from scipy.special import betaln
from manim import *

# House style (matches figures/style.py)
COL_A = ManimColor("#d55e00")   # likelihood / truth
COL_B = ManimColor("#0072b2")   # prior
COL_POST = ManimColor("#009e73")
INK = ManimColor("#222222")
config.background_color = WHITE
for cls in (Tex, MathTex, Text, DecimalNumber, Integer):
    cls.set_default(color=INK)

THETA_STAR = 0.7
RNG = np.random.default_rng(7)
FLIPS = (RNG.random(600) < THETA_STAR).astype(int)
CUM_H = np.concatenate([[0], FLIPS.cumsum()])


def beta_pdf(x, a, b):
    x = np.clip(x, 1e-9, 1 - 1e-9)
    return np.exp((a - 1) * np.log(x) + (b - 1) * np.log1p(-x) - betaln(a, b))


def theta_axes(y_max, y_step, width=3.6, height=2.6):
    return Axes(
        x_range=[0, 1, 0.5], y_range=[0, y_max, y_step], x_length=width, y_length=height,
        axis_config={"color": INK, "include_tip": False, "font_size": 22},
        x_axis_config={"numbers_to_include": [0, 0.5, 1]},
        y_axis_config={"include_ticks": False},
    )


class BayesUpdate(Scene):
    """M1: prior (Beta(2,5), deliberately not flat) x likelihood -> posterior, as flips arrive."""
    A0, B0 = 2, 5

    def construct(self):
        h, t = ValueTracker(0), ValueTracker(0)

        ax_p, ax_l, ax_q = (theta_axes(3, 1), theta_axes(1.1, 1), theta_axes(12, 4))
        panels = VGroup(ax_p, ax_l, ax_q).arrange(RIGHT, buff=1.1).shift(0.4 * DOWN)
        times = MathTex(r"\times", font_size=60).move_to(midpoint(ax_p.get_right(), ax_l.get_left()))
        prop = MathTex(r"\propto", font_size=60).move_to(midpoint(ax_l.get_right(), ax_q.get_left()))

        titles = VGroup(
            MathTex(r"\text{prior } p(\theta\mid X)", color=COL_B),
            MathTex(r"\text{likelihood } L(\theta) \text{ (rescaled)}", color=COL_A),
            MathTex(r"\text{posterior } p(\theta\mid DX)", color=COL_POST),
        )
        for ttl, ax in zip(titles, panels):
            ttl.scale(0.62).next_to(ax, UP, buff=0.25)

        prior = ax_p.plot(lambda x: beta_pdf(x, self.A0, self.B0), x_range=[0.001, 0.999],
                          color=COL_B, stroke_width=5)
        prior_fill = ax_p.get_area(prior, x_range=[0, 1], color=COL_B, opacity=0.15)

        def lik_curve():
            hh, tt = h.get_value(), t.get_value()
            mode = hh / (hh + tt) if hh + tt > 0 else 0.5
            logmax = (hh * np.log(max(mode, 1e-12)) + tt * np.log(max(1 - mode, 1e-12))) if hh + tt else 0
            f = lambda x: np.exp(hh * np.log(x) + tt * np.log1p(-x) - logmax)
            return ax_l.plot(f, x_range=[0.001, 0.999, 0.002], use_smoothing=False, color=COL_A, stroke_width=5)

        def post_curve():
            return ax_q.plot(lambda x: min(beta_pdf(x, self.A0 + h.get_value(), self.B0 + t.get_value()), 12),
                             x_range=[0.001, 0.999, 0.002], use_smoothing=False, color=COL_POST, stroke_width=5)

        lik = always_redraw(lik_curve)
        post = always_redraw(post_curve)
        ghost_prior = ax_q.plot(lambda x: beta_pdf(x, self.A0, self.B0), x_range=[0.001, 0.999],
                                color=COL_B, stroke_width=2, stroke_opacity=0.35)
        truth = DashedLine(ax_q.c2p(THETA_STAR, 0), ax_q.c2p(THETA_STAR, 12), color=GREY_B)
        truth_lbl = MathTex(r"\theta^\ast", font_size=28, color=GREY_D).next_to(ax_q.c2p(THETA_STAR, 0), DOWN, buff=0.35)

        counter = always_redraw(lambda: MathTex(
            rf"n={int(round(h.get_value() + t.get_value()))},\quad "
            rf"\text{{heads}}={int(round(h.get_value()))},\quad \text{{tails}}={int(round(t.get_value()))}",
            font_size=36).to_edge(UP, buff=0.35))
        formula = MathTex(r"p(\theta\mid DX)=\mathrm{Beta}(2+\text{heads},\,5+\text{tails})",
                          r"\qquad\text{(posterior panel: 4$\times$ vertical scale)}",
                          font_size=32).to_edge(DOWN, buff=0.35)
        formula[1].set_color(GREY_D).scale(0.8)

        self.play(LaggedStart(*[Create(a) for a in panels], lag_ratio=0.2), run_time=1.5)
        self.play(FadeIn(titles[0]), Create(prior), FadeIn(prior_fill))
        self.play(FadeIn(titles[1]), Create(lik), Write(times))
        self.play(FadeIn(titles[2]), Create(post), Write(prop), FadeIn(ghost_prior))
        self.play(Create(truth), FadeIn(truth_lbl), FadeIn(counter), FadeIn(formula))
        self.wait()

        # one flip at a time, then accelerate
        schedule = [1] * 8 + [2] * 6 + [5] * 6 + [20] * 5     # total n = 8+12+30+100 = 150
        n = 0
        for k, step in enumerate(schedule):
            n += step
            rt = 0.7 if step == 1 else 0.9
            self.play(h.animate.set_value(CUM_H[n]), t.animate.set_value(n - CUM_H[n]),
                      run_time=rt, rate_func=smooth)
            if k == 7:
                self.wait(1.5)   # pause: prior still visibly pulls posterior left
        self.wait(2)


class LikelihoodConcentration(Scene):
    """M2: (1/n) log[L(theta)/L(theta*)] -> -D_KL(theta* || theta), curvature = Fisher information."""

    def construct(self):
        ts = THETA_STAR
        dB = 10 / np.log(10)
        ax = Axes(x_range=[0, 1, 0.1], y_range=[-6, 0.5, 1], x_length=10, y_length=5.4,
                  axis_config={"color": INK, "include_tip": False, "font_size": 24},
                  x_axis_config={"numbers_to_include": np.arange(0, 1.01, 0.2)},
                  y_axis_config={"numbers_to_include": np.arange(-6, 0.1, 2)}).shift(0.5 * DOWN)
        xl = MathTex(r"\theta").next_to(ax.x_axis, DOWN + RIGHT, buff=0.1).shift(0.3 * UP)
        yl = MathTex(r"\text{dB per flip}", font_size=28).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.55)

        def visible(f, lo=-6.0):
            xs = np.linspace(0.001, 0.999, 2000)
            ok = xs[np.array([f(x) for x in xs]) >= lo]
            return ok.min(), ok.max()

        def kl(x):
            return dB * (ts * np.log(ts / x) + (1 - ts) * np.log((1 - ts) / (1 - x)))

        target = ax.plot(lambda x: -kl(x), x_range=[*visible(lambda x: -kl(x)), 0.002],
                         use_smoothing=False, color=INK, stroke_width=3)
        target = DashedVMobject(target, num_dashes=60)
        target_lbl = MathTex(r"-D_{KL}(\theta^\ast\Vert\theta)", font_size=34).move_to(ax.c2p(0.3, -4.2))

        nt = ValueTracker(1)

        def avg_loglik():
            n = max(1, int(nt.get_value()))
            hh, tt = CUM_H[n], n - CUM_H[n]
            f = lambda x: dB * (hh * np.log(x / ts) + tt * np.log((1 - x) / (1 - ts))) / n
            return ax.plot(f, x_range=[*visible(f), 0.002], use_smoothing=False, color=COL_A, stroke_width=5)

        curve = always_redraw(avg_loglik)
        title = MathTex(r"\frac{1}{n}\,10\log_{10}\frac{L(\theta)}{L(\theta^\ast)}", color=COL_A,
                        font_size=40).to_corner(UL, buff=0.4)
        arrow = MathTex(r"\xrightarrow{\ n\to\infty\ }", font_size=40).next_to(title, RIGHT)
        lim = MathTex(r"-D_{KL}(\theta^\ast\Vert\theta)", font_size=40).next_to(arrow, RIGHT)
        n_lbl = always_redraw(lambda: MathTex(rf"n = {int(nt.get_value())}", font_size=36)
                              .to_corner(UR, buff=0.5))
        star = DashedLine(ax.c2p(ts, -1.2), ax.c2p(ts, 0.5), color=GREY_B)
        star_lbl = MathTex(r"\theta^\ast=0.7", font_size=28, color=GREY_D).next_to(star, UP, buff=0.05)

        self.play(Create(ax), FadeIn(xl), FadeIn(yl), Create(star), FadeIn(star_lbl))
        self.play(Write(title), FadeIn(n_lbl), Create(curve))
        self.wait()
        self.play(nt.animate.set_value(20), run_time=4, rate_func=linear)
        self.play(nt.animate.set_value(600), run_time=8, rate_func=lambda u: u ** 2)
        self.play(Create(target), FadeIn(target_lbl), Write(arrow), Write(lim))
        self.wait()

        # Fisher information = curvature at the peak
        fisher = 1 / (ts * (1 - ts))
        para = ax.plot(lambda x: -0.5 * dB * fisher * (x - ts) ** 2, x_range=[0.45, 0.95],
                       color=COL_B, stroke_width=4)
        para_lbl = MathTex(r"-\tfrac{10}{\ln 10}\cdot\tfrac12\, I(\theta^\ast)\,(\theta-\theta^\ast)^2", r",\quad I(\theta)=\frac{1}{\theta(1-\theta)}",
                           color=COL_B, font_size=32).move_to(ax.c2p(0.62, -2.6))
        self.play(Create(para), Write(para_lbl))
        self.wait(3)
