---
name: drp-session
description: Prepare a session of Nazar's directed-reading project on Jaynes, "Probability Theory: The Logic of Science" (first-year Imperial maths students). Use when planning, building or revising slides, figures, interactive widgets or homework for a reading-group session, or when the user mentions the DRP, the Jaynes group, or "next session".
---

# DRP session builder

Builds a session as a Quarto revealjs deck made mostly of interactive Observable JS (OJS) widgets: many examples, little text. Every number gets checked in Wolfram Language (or sympy as a fallback).

## 1. Plan first, by interview
- Interview with AskUserQuestion rounds: recommended option first, at most 4 questions per round. Settle the whole slide plan before building.
- Ask: chapter just read, next reading, session length, which lecture prerequisites they have covered.
- Revision sessions: lots of examples, one-line captions, derivations in the speaker notes.
- No special roles or stretch tasks. Homework is minimal: 2–3 short computations, delivered as a PDF.

Group context (update as it changes): 4 first-years. Chapters read so far: 1, 2, 4 (skipped 3). Next: Ch 5, *Queer uses for probability theory*.

## 2. Notation (match Jaynes)
- Background information `X` appears in every conditional: `P(D|θX)`.
- Evidence: `e(H|DX) = 10 log10 O(H|DX)` in dB, defined in (4.8). Additivity is (4.13).
- Running examples:
  - the widgets: A = 1/3 defective, B = 1/6, prior −10 dB; a bad widget is +3.01 dB, a good one −0.97 dB
  - §4.4 C: 99/100 defective, prior 10⁻⁶
  - coin flips
  - exponential with prior ∝ 1/λ, i.e. flat in log λ
- Avoid symmetric Bernoulli pairs like (θ, 1−θ): they make KL symmetric.
- The book is an epub. Unzip it to the scratchpad, strip the HTML to text and grep for equation numbers.

## 3. Stack and layout
```
slides/index.qmd      revealjs 1280x720, KaTeX stored locally (html-math-method: {method: katex, url: "vendor/katex/"})
slides/_helpers.qmd   OJS: local libraries, house style P(), maths, T() for TeX, controls, historyWidget
slides/vendor/        d3, Plot (UMD, aliased via require.alias), Plotly (3D only), KaTeX: nothing loads from a CDN
slides/drp.scss       colours A #d55e00, B #0072b2, C #009e73; widget CSS
figures/              Matplotlib, appendix and static fallback figures only
homework/homework.qmd -> PDF
anim/                 old Manim scenes (archived, not in the build)
```
- No TeX macros (KaTeX doesn't share \newcommand across expressions). Write `D_{\mathrm{KL}}(p\,\|\,q)` in full.
- Preview with the user's own `quarto preview`, which re-renders on save. Then point the browser pane at its URL. The app's preview_start can keep using a stale launch.json from an old folder, so check `curl` output against the file on disk.

## 4. Slide structure
- **Title:** short and simple ("Two hypotheses", "Learning a rate"), never a sentence.
- **Intro line** (`::: {.intro}`) below the title: the model, with equations.
- **The graphs.** Each is captioned "plot of $f(\cdot)$ against $x$" with the exact quantity plotted.
- **Conclusion** (`::: {.concl}`): one line, if there is one.
- Anything vague gets its expanded equation, e.g. "predictive" becomes $p(x\mid DX)=\int p(x\mid\lambda)\,p(\lambda\mid DX)\,d\lambda$ (or a sum).
- Evidence plots may be clipped (−150 dB). Log-likelihood plots must not be: they fall O(n).

## 5. Widget rules
- One widget per slide, with descriptive control labels ("number of flips $n$", "true rate $\lambda^*$"). Use `$...$` everywhere TeX can render: captions, labels and buttons, via `T()`. Plot's axis labels stay Unicode.
- Sequential data: `historyWidget`. Buttons append data from a hidden truth, a history slider scrubs back, plus reset and "reveal truth". Add play/pause for slow animations.
- Rates and scales: logarithmic sliders down to 0.01. Use a literal change of variable (plot `z = log x` on a linear axis) rather than log-scaled axes when teaching it.
- State priors explicitly on the slide. Show numbers (log P, P, evidence) in a small table where hypotheses are compared. Clip runaway curves (e.g. at −150 dB).
- Build HTML `<option>`s and checkbox state through the DOM API, not template attributes. Template attributes broke here: an option value was cut at the first space, and `checked=false` still checked the box.
- Plotly 3D: use log10 coordinates with tickvals rather than log axis type. Set the camera perpendicular to any ridge.
- After rendering, check every slide in the browser pane at 1280×720 and run the overflow scan (element right/bottom divided by `Reveal.getScale()`; ignore KaTeX's off-screen MathML).

## 6. Checking
Put all numbers in one `WolframLanguageEvaluator` call returning an association, and record them in `notes/numbers.md`. No separate JS test suite: the maths is simple; spot-check in the browser.

## 7. Ending a session's deck
"For next time": the homework (also as a PDF) and the next reading. Older or optional material (tests, Fisher information, geometry) goes in the appendix.
- `quarto preview` does not re-render when only an included file (`_helpers.qmd`) changes: `touch slides/index.qmd`.
