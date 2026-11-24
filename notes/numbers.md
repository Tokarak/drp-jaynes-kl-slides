# Verified numbers (Wolfram Language, 22 Nov 2026)

Jaynes Ch 4 widget problem. X: 11 machines, 10 make 1/6 defective, 1 makes 1/3.
A = bad batch (1/3 defective), B = good batch (1/6). P(A|X) = 1/11 → e(A|X) = −10 dB (4.15).

| quantity | value |
|---|---|
| bad widget: 10 log10 2 | +3.0103 dB (4.19) |
| good widget: 10 log10 (4/5) | −0.9691 dB (4.21) |
| D_KL(P_A ‖ P_B) | 0.35737 dB/widget = 0.082287 nats |
| D_KL(P_B ‖ P_A) | 0.30587 dB/widget = 0.070428 nats |
| widgets to gain +10 dB if A true | 27.98 |
| widgets to lose 10 dB if B true | 32.69 |
| widgets to reach −13 dB from −10 dB if B true | 9.81 |
| exact threshold f_b = ln(5/4)/ln(5/2) (4.25) | 0.24353 |
| 12 widgets, 5 bad: e(A|DX) (4.23) | −1.732 dB → P(A|DX) = 0.402 |
| D_KL(Bern θ ‖ Bern θ+δ) | δ²/(2θ(1−θ)) + O(δ³) |
| Fisher length of [0,1]: ∫ dθ/√(θ(1−θ)) | π |
| D_KL(p ‖ uniform_n) | log n − H(p) |

Jaynes' decision rule (end of §4.2): reject if e(A|DX) > 0 dB, accept if e(A|DX) < −13 dB, else test another.

Notation: Jaynes writes "db" for decibels; slides use dB. Evidence is defined in (4.8) and is additive over data in (4.13).
