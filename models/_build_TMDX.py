#!/usr/bin/env python3
"""TMDX 2026-11-15 scenario values and projection tables.

Reads nothing from the network. Inputs are the figures recorded in
data/TMDX/2026-11-15/inputs.json (Q3 2026 10-Q and release). Prints the end-2029
bear/base/bull values that go into call.json and the projection tables in
projections/TMDX.md. The workbook itself is rendered by
`python3 -m capital.workbook TMDX 2026-11-15`.

Method: end-2029 value per share = (2029 GAAP operating income x exit EV/EBIT
+ end-2029 net cash) / diluted shares. Net cash starts at September 30, 2026
cash ($493.0M) less $889.6M of obligations due by mid-2028 (convertible
principal $460.0M, CIBC term loan $55.0M, headquarters purchase-option payment
$374.6M), assumed refinanced at no change in net debt, plus FCF from Q4 2026 on,
less the remaining headquarters buildout capex (10-Q: $200-240M through 2030,
$13.8M incurred; midpoint remainder $206M, outside the case FCF margins), plus
after-tax net interest at 3.5% on net cash.
Convertible principal is a cash obligation; the capped call offsets conversion
shares up to $141.88, and shares above the cap are added in the bull.
"""

PRICE = 91.38  # 2026-11-13 close
CASH0 = 492.962
OBLIGATIONS = 460.0 + 55.0 + 374.59
SHARES0 = 35.94  # diluted ex-convert, Q3 2026
CAP, CONV_SHARES = 141.88, 4.893848
TAX, RATE = 0.24, 0.035
YEARS = list(range(2027, 2037))
HQ_Q4_2026 = 10.0
HQ_CAPEX = {2027: 60.0, 2028: 60.0, 2029: 50.0, 2030: 26.0}  # remaining buildout, midpoint $206M

CASES = {
    # fy26 revenue, Q4-26 FCF, revenue growth 2027-29 then fade to terminal by 2036,
    # EBIT margin 2027-29 then path to terminal by 2033, FCF margin 2027-29 then terminal,
    # exit EV/EBIT, annual share growth
    "bear": dict(fy26=765, q4fcf=15, g=0.08, g_term=0.04, m=[0.105, 0.11, 0.12], m_term=0.12,
                 f=[0.05, 0.06, 0.07], f_term=0.07, x=15, dil=0.024, weight=0.30),
    "base": dict(fy26=770, q4fcf=25, g=0.15, g_term=0.07, m=[0.135, 0.165, 0.19], m_term=0.22,
                 f=[0.10, 0.13, 0.15], f_term=0.17, x=22, dil=0.018, weight=0.50),
    "bull": dict(fy26=775, q4fcf=30, g=0.23, g_term=0.10, m=[0.15, 0.195, 0.24], m_term=0.27,
                 f=[0.12, 0.15, 0.18], f_term=0.21, x=26, dil=0.0135, weight=0.20),
}


def path(c):
    rows, rev, net = [], c["fy26"], CASH0 - OBLIGATIONS + c["q4fcf"] - HQ_Q4_2026
    for i, y in enumerate(YEARS):
        if i < 3:
            g, m, f = c["g"], c["m"][i], c["f"][i]
        else:
            k = (i - 2) / 7  # 2030..2036 fade
            g = c["g"] + (c["g_term"] - c["g"]) * k
            m = c["m"][2] + (c["m_term"] - c["m"][2]) * min(1, (i - 2) / 4)
            f = c["f"][2] + (c["f_term"] - c["f"][2]) * min(1, (i - 2) / 4)
        prev = rev
        rev *= 1 + g
        ebit = rev * m
        interest = RATE * net
        ni = (ebit + interest) * (1 - TAX)
        fcf = rev * f
        net += fcf + interest * (1 - TAX) - HQ_CAPEX.get(y, 0.0)
        sh = SHARES0 * (1 + c["dil"]) ** (i + 1)
        rows.append(dict(year=y, rev=rev, g=rev / prev - 1, ebit=ebit, ni=ni, fcf=fcf, net=net, sh=sh))
    return rows


def value(c, rows):
    r = rows[2]
    eq = r["ebit"] * c["x"] + r["net"]
    p, extra = eq / r["sh"], 0.0
    for _ in range(50):
        extra = CONV_SHARES * (p - CAP) / p if p > CAP else 0.0
        p = eq / (r["sh"] + extra)
    return p, extra


def main():
    vals = {}
    for name, c in CASES.items():
        rows = path(c)
        v, extra = value(c, rows)
        vals[name] = v
        r = rows[2]
        print(f"{name}: 2029 revenue {r['rev']:.1f}, EBIT {r['ebit']:.1f}, EV {r['ebit'] * c['x']:.0f}, "
              f"net cash {r['net']:.1f}, shares {r['sh'] + extra:.2f}, value ${v:.2f} "
              f"({(v / PRICE) ** (1 / 3) - 1:+.1%} a year)")
        anchor = v / (r["ni"] / (r["sh"] + extra))
        print(f"\n### {name.capitalize()} (terminal P/E anchor {anchor:.1f}x, held from year 1)\n")
        print("| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) "
              "| EPS | FCF Yield | Stock Price | P/E | CAGR From Current |")
        print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for n in (1, 2, 3, 5, 10):
            r = rows[n - 1]
            sh = r["sh"] + (extra if r["year"] >= 2028 else 0)
            eps = r["ni"] / sh
            px = eps * anchor
            print(f"| {n} | FY{r['year']} | {r['rev']:,.0f} | {r['g']:+.1%} | {r['ebit']:,.0f} | {r['ni']:,.0f} | "
                  f"${eps:.2f} | {r['fcf'] / (px * sh):.1%} | ${px:,.2f} | {anchor:.1f}x | "
                  f"{(px / PRICE) ** (1 / n) - 1:+.1%} |")
        print()
    fv = sum(CASES[k]["weight"] * vals[k] for k in vals)
    print(f"weighted fair value ${fv:.2f} ({(fv / PRICE) ** (1 / 3) - 1:+.1%} a year)")


if __name__ == "__main__":
    main()
