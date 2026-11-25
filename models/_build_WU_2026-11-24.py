#!/usr/bin/env python3
"""WU 2026-11-24 scenario values and projection tables (Q3 2026 update).

Reads nothing from the network. Starting figures are from the Q3 2026 earnings
release and 10-Q (accessions 0001193125-26-447234 and 0001193125-26-447662,
filed 2026-11-04) and the 8-Ks of 2026-11-12 (Intermex termination) and
2026-11-13 (term loan refinancing), as recorded in
data/WU/2026-11-24/inputs.json. Prints the end-2029 bear/base/bull values that
go into call.json, the sensitivities quoted in the update note, and the tables
in projections/WU.md. The workbook itself is rendered by
`python3 -m capital.workbook WU 2026-11-24`. The October initiation's script is
models/_build_WU.py and is left as it was.

Method: value per share at December 31, 2029, undiscounted =
  FY2029 adjusted EPS x exit P/E
  + dividends paid from the Q4 2026 payment through Q4 2029 (13 quarters)
  - any Intermex litigation payment per share.

Dividends: the bear halves the $0.235 quarterly dividend from Q2 2027 (Q4 2026
and Q1 2027 at $0.235, then eleven quarters at $0.1175). The base holds it with
an 85% chance and halves it from Q2 2027 with a 15% chance, a cut in an
otherwise base-case world (free cash flow covers the dividend only 0.94x in
2027 and gross leverage is above target), so base dividends are the
probability-weighted $2.86. Across the cases the chance of a cut before 2028 is
0.35 + 0.45 x 0.15 = 0.42. The bull holds it.

Intermex: the bear's $300M stands for a court-ordered close at $16 (about
$500M of cash plus Intermex's revolver for a business worth well under that to
Western Union at its own multiple) or damages of similar size; the base's $50M
is a settlement plus legal cost.

Adjusted EPS = (adjusted operating income - net interest expense + other
income) x (1 - adjusted tax rate) / diluted shares. Adjusted operating income
is revenue x adjusted operating margin; Western Union's adjusted figures exclude
the Beyond efficiency program, severance, acquisition costs and the non-cash
tax charge from its international reorganization, which is how the Street's
EPS and the company's guidance are stated. FY2026 is the guidance midpoint
($1.28-$1.38 adjusted EPS, revenue down 1-2% excluding Intermex).

Free cash flow is operating cash flow (taken as adjusted net income plus $60M
before one-off cash items, less cash restructuring: FY2025 OCF was $543.7M on
$574.6M of adjusted net income after about $200M of IRS settlement payments,
about +$170M before them; 2026 OCF of about $456M, 9M $321.2M plus a Q4 of
$135M, the median of the 2022-2025 fourth quarters of $59M / $265M / $134M /
$135M, sits about $37M above 2026 adjusted net income of about $419M after about
$30M of Beyond severance, about +$67M before it; the Street's $166.5M 2026 free
cash flow on StockAnalysis implies OCF near $357M, a much weaker Q4) less capital
expenditure including capitalized software and agent signing bonuses (about
$190M in 2026, a heavier renewal year). It feeds net debt and
the EV/EBITDA cross-check only. Rows after 2029 extrapolate: revenue growth
moves linearly to the 2036 rate and the margin holds at its 2029 level.
"""

PRICE = 6.24  # 2026-11-23 close
SHARES0 = 313.5  # Q3 2026 diluted weighted-average shares (M)
REV_2026 = 3990.0  # 9M $3,005.2M + Q4 about $985M (guide: -1% to -2% ex-Intermex on FY2025 $4,050.7M)
EPS_2026 = 1.33  # guidance midpoint, adjusted
NET_DEBT_2026 = 1800.0  # Sep 30: $2,900.2M borrowings at par - $1,098.0M cash; Q4 FCF about offsets the Q4 dividend
DA = 190.0  # D&A excluding acquired-intangible amortization (Q3 2026 $47.2M a quarter)
DPS_Q = 0.235
YEARS = list(range(2027, 2037))

CASES = {
    # rev growth 2027-2029, adjusted operating margin 2027-2029, net interest 2027-2029 ($M), tax, share drift,
    # dividend per quarter from Q1 2027, litigation payment ($M), capex, exit P/E, terminal growth, weight
    "bear": dict(g=[-0.035, -0.02, -0.01], m=[0.145, 0.14, 0.14], intr=[150, 160, 170], tax=0.13, drift=0.015,
                 dps_q=0.1175, cut_prob=1.0, litigation=300, capex=[175, 175, 175], pe=3.5, g_term=-0.01, weight=0.35),
    "base": dict(g=[-0.02, 0.0, 0.01], m=[0.16, 0.165, 0.165], intr=[145, 150, 155], tax=0.12, drift=0.01,
                 dps_q=0.235, cut_prob=0.15, litigation=50, capex=[175, 170, 170], pe=5.0, g_term=0.01, weight=0.45),
    "bull": dict(g=[0.0, 0.02, 0.03], m=[0.17, 0.18, 0.185], intr=[140, 140, 140], tax=0.12, drift=0.0,
                 dps_q=0.235, cut_prob=0.0, litigation=0, capex=[180, 180, 180], pe=6.0, g_term=0.02, weight=0.20),
}
BULL_BUYBACK = 100.0  # $M a year in 2028-2029 at the path price, bull only (buybacks are paused while gross leverage is above 3.0x)


def path(c, pe=None):
    pe = pe or c["pe"]
    rows, rev, sh, nd = [], REV_2026, SHARES0, NET_DEBT_2026
    for i, y in enumerate(YEARS):
        if i < 3:
            g, m, intr = c["g"][i], c["m"][i], c["intr"][i]
        else:
            g = c["g"][2] + (c["g_term"] - c["g"][2]) * (i - 2) / 7
            m, intr = c["m"][2], c["intr"][2]
        rev *= 1 + g
        oi = rev * m
        ni = (oi - intr + 3.0) * (1 - c["tax"])
        sh *= 1 + c["drift"]
        restr = 30.0 if y == 2027 else 10.0
        fcf = ni + 60.0 - restr - c["capex"][min(i, 2)]
        # cash dividends for the net-debt path: a bear cut starts in Q2 2027 (Q1 2027 at $0.235)
        dps = (DPS_Q + 3 * c["dps_q"]) if (y == 2027 and c["cut_prob"] == 1.0) else 4 * c["dps_q"]
        lit = c["litigation"] if y == 2027 else 0.0
        bb = BULL_BUYBACK if (c is CASES["bull"] and y in (2028, 2029)) else 0.0
        if bb:
            sh -= bb / (ni / sh * pe)
        nd += dps * sh - fcf + lit + bb
        rows.append(dict(year=y, rev=rev, g=g, oi=oi, m=m, ni=ni, sh=sh, eps=ni / sh, fcf=fcf, dps=dps,
                         nd=nd, ebitda=oi + DA))
    return rows


def dividends(c, dps_q=None, cut_prob=None):
    """Dividends paid from the Q4 2026 payment through Q4 2029 (13 quarters)."""
    p = c["cut_prob"] if cut_prob is None else cut_prob
    held = 13 * DPS_Q
    cut = 2 * DPS_Q + 11 * (DPS_Q / 2 if dps_q is None else dps_q)  # cut from Q2 2027
    return (1 - p) * held + p * cut


def value(c, rows, pe=None, dps_q=None, cut_prob=None):
    pe = pe or c["pe"]
    r = rows[2]
    divs = dividends(c, dps_q, cut_prob)
    lit = c["litigation"] / SHARES0
    return r["eps"] * pe + divs - lit, divs, lit


def weighted(vals, weights):
    return sum(weights[k] * vals[k] for k in vals)


def ann(v):
    return (v / PRICE) ** (1 / 3) - 1


def main():
    vals, price_only = {}, {}
    for name, c in CASES.items():
        rows = path(c)
        v, divs, lit = value(c, rows)
        vals[name] = round(v, 2)
        r = rows[2]
        price_only[name] = r["eps"] * c["pe"]
        cagr = (r["rev"] / REV_2026) ** (1 / 3) - 1
        ev_cross = (r["ebitda"] * 5.0 - r["nd"]) / r["sh"] + divs - lit
        cover = [x["fcf"] / (x["dps"] * x["sh"]) for x in rows[:3]]
        print(f"{name}: 2029 revenue {r['rev']:,.0f} (2026-29 CAGR {cagr:+.1%}), adj OI {r['oi']:,.0f} ({r['m']:.1%}), "
              f"adj NI {r['ni']:,.0f}, shares {r['sh']:.1f}, adj EPS 2027-29 "
              f"{rows[0]['eps']:.2f}/{rows[1]['eps']:.2f}/{r['eps']:.2f} x {c['pe']} = {r['eps'] * c['pe']:.2f} "
              f"+ dividends {divs:.2f} - litigation {lit:.2f} = ${v:.2f} ({ann(v):+.1%} a year); "
              f"FCF/dividend 2027-29 {cover[0]:.2f}/{cover[1]:.2f}/{cover[2]:.2f}; end-2029 net debt {r['nd']:,.0f} "
              f"({r['nd'] / r['ebitda']:.1f}x EBITDA {r['ebitda']:,.0f}); cross-check 5.0x EBITDA less net debt "
              f"+ dividends - litigation = ${ev_cross:.2f}")
    w = {k: c["weight"] for k, c in CASES.items()}
    fv = round(weighted(vals, w), 2)
    print(f"\nweighted fair value ${fv:.2f} ({ann(fv):+.1%} a year from ${PRICE}); price-only weighted "
          f"${weighted(price_only, w):.2f}; Own below ${fv / 1.15 ** 3:.2f}, Avoid above ${fv:.2f}")

    print("\nsensitivities")
    for label, ww in [("30/50/20", dict(bear=0.30, base=0.50, bull=0.20)),
                      ("40/45/15", dict(bear=0.40, base=0.45, bull=0.15)),
                      ("45/40/15", dict(bear=0.45, base=0.40, bull=0.15)),
                      ("25/50/25", dict(bear=0.25, base=0.50, bull=0.25))]:
        f = weighted(vals, ww)
        print(f"  weights {label}: ${f:.2f} ({ann(f):+.1%})")
    base = CASES["base"]
    for pe in (4.0, 4.5, 5.5, 6.0):
        v2 = dict(vals, base=value(base, path(base), pe=pe)[0])  # base keeps its 15% cut chance
        f = weighted(v2, w)
        print(f"  base exit P/E {pe}x: base ${v2['base']:.2f}, fair value ${f:.2f} ({ann(f):+.1%})")
    for dq, label in ((0.1175, "halved from Q2 2027"), (0.0, "suspended from Q2 2027")):
        v2 = dict(vals, base=value(base, path(base), dps_q=dq, cut_prob=1.0)[0])
        f = weighted(v2, w)
        print(f"  base dividend {label}: base ${v2['base']:.2f}, fair value ${f:.2f} ({ann(f):+.1%})")
    for m in (0.15, 0.175):
        c2 = dict(base, m=[base["m"][0], m, m])
        v2 = dict(vals, base=value(c2, path(c2))[0])
        f = weighted(v2, w)
        print(f"  base 2028-29 margin {m:.1%}: base ${v2['base']:.2f}, fair value ${f:.2f} ({ann(f):+.1%})")
    c2 = dict(base, litigation=0)
    v2 = dict(vals, base=value(c2, path(c2))[0])
    print(f"  base litigation $0: fair value ${weighted(v2, w):.2f}")
    v2 = dict(vals, base=value(base, path(base), cut_prob=0.0)[0])
    f = weighted(v2, w)
    print(f"  base dividend held with certainty: base ${v2['base']:.2f}, fair value ${f:.2f} ({ann(f):+.1%})")
    c2 = dict(CASES["bear"], litigation=600)
    v2 = dict(vals, bear=value(c2, path(c2))[0])
    f = weighted(v2, w)
    print(f"  bear litigation $600M: bear ${v2['bear']:.2f}, fair value ${f:.2f} ({ann(f):+.1%})")
    pe_price = PRICE / path(base)[2]["eps"]
    print(f"  price / base 2029 EPS {pe_price:.2f}x; base exit P/E that returns the price with dividends: "
          f"{(PRICE - value(base, path(base))[1] + base['litigation'] / SHARES0) / path(base)[2]['eps']:.2f}x")

    for name, c in CASES.items():
        rows = path(c)
        anchor = vals[name] / rows[2]["eps"]
        print(f"\n### {name.capitalize()} (terminal P/E anchor {anchor:.2f}x, held from year 1)\n")
        print("| Years Out | Year | Revenue ($M) | Revenue Growth YoY | Adj. Operating Income ($M) | Adj. Net Income ($M) "
              "| Adj. EPS | FCF Yield | Stock Price | P/E | CAGR From Current |")
        print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for n in (1, 2, 3, 5, 10):
            r = rows[n - 1]
            px = r["eps"] * anchor
            print(f"| {n} | {r['year']} | {r['rev']:,.0f} | {r['g']:+.1%} | {r['oi']:,.0f} | {r['ni']:,.0f} | "
                  f"{r['eps']:.2f} | {r['fcf'] / (px * r['sh']):.1%} | ${px:,.2f} | {anchor:.2f}x | "
                  f"{(px / PRICE) ** (1 / n) - 1:+.1%} |")


if __name__ == "__main__":
    main()
