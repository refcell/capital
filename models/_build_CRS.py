#!/usr/bin/env python3
"""CRS 2026-11-18 scenario values and projection tables.

Reads nothing from the network. Inputs are the figures recorded in
data/CRS/2026-11-18/inputs.json (Q1 FY2027 10-Q, Q1 FY2027 and Q4 FY2026
releases and decks). Prints the FY2029 bear/base/bull values that go into
call.json and the projection tables in projections/CRS.md. The workbook itself
is rendered by `python3 -m capital.workbook CRS 2026-11-18`.

Method: value per share at June 30, 2029 (end of FY2029) =
(FY2029 operating income x exit EV/EBIT + June 2029 net cash) / diluted shares,
plus dividends paid from Q2 FY2027 through FY2029. Net cash starts at
September 30, 2026: cash $159.5M less the $700.0M face of the 5.625% notes due
2034 less $109.4M of accrued pension ($85.6M) and postretirement ($23.8M) liabilities. It then changes by FCF from
Q2 FY2027 on, after-tax interest and dividends. FCF after dividends is kept as
cash rather than spent on buybacks at an assumed price, so the value does not
depend on the price paid for stock. FY2027 FCF is the full year less the Q1
actual (-$24.8M), which is already in the September 30 cash.

FCF = net income + D&A + stock compensation - capex - 20% of the revenue
increase (working capital) - $19M of pension cash above expense. Net income =
(operating income - net interest) x (1 - 21%). Net interest = 5.625% on $700M
less capitalized interest ($16M in FY2027 while the brownfield expansion is
built, none after) less 3.5% on positive cash. Diluted shares start at 50.0M
(Q1 FY2027) and grow 0.4% a year from stock awards, since FCF is kept as cash.
The FY2029 value is treated as a three-year value; it lands about five months
before November 2029, which understates the annual return slightly.
"""

PRICE = 269.68  # 2026-11-17 close
CASH0, NOTES, PENSION = 159.5, 700.0, 109.4  # pension and postretirement liabilities
Q1_FCF = -24.8
SHARES0, DIL = 50.0, 0.004
TAX, COUPON, CASH_RATE = 0.21, 0.05625, 0.035
DIV_Q = 0.20
DIVS_TO_FY29 = 11 * DIV_Q  # Q2 FY2027 through Q4 FY2029
FY26_REV = 3124.2
YEARS = list(range(2027, 2037))

CASES = {
    # rev: FY2027-29 revenue; oi: FY2027-29 operating income; capex: FY2027-29;
    # after FY2029 growth fades linearly to g_term by FY2036, margin moves to m_term by FY2032,
    # capex is cap_pct of revenue; x: exit EV/EBIT on FY2029 operating income
    "bear": dict(rev=[3300, 3250, 3200], oi=[800, 760, 720], capex=[355, 200, 160],
                 g_term=0.02, m_term=0.22, cap_pct=0.05, x=12, weight=0.30),
    "base": dict(rev=[3420, 3760, 4100], oi=[860, 1000, 1130], capex=[365, 220, 200],
                 g_term=0.05, m_term=0.28, cap_pct=0.05, x=17, weight=0.45),
    "bull": dict(rev=[3480, 3900, 4400], oi=[880, 1080, 1320], capex=[375, 230, 210],
                 g_term=0.07, m_term=0.30, cap_pct=0.05, x=22, weight=0.25),
}


def path(c):
    rows, prev_rev, cash = [], FY26_REV, CASH0
    sh = SHARES0
    for i, y in enumerate(YEARS):
        if i < 3:
            rev, oi, capex = c["rev"][i], c["oi"][i], c["capex"][i]
        else:
            g3 = c["rev"][2] / c["rev"][1] - 1
            k = (i - 2) / 7
            g = g3 + (c["g_term"] - g3) * k
            rev = prev_rev * (1 + g)
            m3 = c["oi"][2] / c["rev"][2]
            m = m3 + (c["m_term"] - m3) * min(1, (i - 2) / 3)
            oi = rev * m
            capex = rev * c["cap_pct"]
        dep = 150.0 if i == 0 else 0.043 * rev
        cap_int = 16.0 if i == 0 else 0.0
        net_interest = COUPON * NOTES - cap_int - CASH_RATE * max(cash, 0.0)
        ni = (oi - net_interest) * (1 - TAX)
        sbc = 0.009 * rev
        fcf = ni + dep + sbc - capex - 0.20 * (rev - prev_rev) - 19.0
        sh = sh * (1 + DIL)
        divs = 4 * DIV_Q * sh
        add = fcf - Q1_FCF if i == 0 else fcf  # Q1 FY2027 FCF is already in Sept 30 cash
        add_div = divs * 0.75 if i == 0 else divs  # three quarterly dividends left in FY2027
        cash += add - add_div
        rows.append(dict(year=y, rev=rev, g=rev / prev_rev - 1, oi=oi, ni=ni, fcf=fcf, cash=cash,
                         sh=sh, capex=capex, dep=dep))
        prev_rev = rev
    return rows


def value(c, rows):
    r = rows[2]
    ev = r["oi"] * c["x"]
    net = r["cash"] - NOTES - PENSION
    return (ev + net) / r["sh"] + DIVS_TO_FY29, ev, net


def main():
    vals = {}
    for name, c in CASES.items():
        rows = path(c)
        v, ev, net = value(c, rows)
        vals[name] = v
        r = rows[2]
        cagr3 = (c["rev"][2] / FY26_REV) ** (1 / 3) - 1
        print(f"{name}: FY2029 revenue {r['rev']:.0f} (FY26-29 CAGR {cagr3:.1%}), OI {r['oi']:.0f} "
              f"({r['oi'] / r['rev']:.1%}), EV {ev:,.0f} at {c['x']}x, June 2029 net cash {net:,.0f}, "
              f"shares {r['sh']:.2f}, FY27-29 FCF {rows[0]['fcf']:.0f}/{rows[1]['fcf']:.0f}/{rows[2]['fcf']:.0f}, "
              f"EPS {rows[0]['ni'] / rows[0]['sh']:.2f}/{rows[1]['ni'] / rows[1]['sh']:.2f}/{r['ni'] / r['sh']:.2f}, "
              f"value ${v:.2f} ({(v / PRICE) ** (1 / 3) - 1:+.1%} a year)")
        anchor = v / (r["ni"] / r["sh"])
        print(f"\n### {name.capitalize()} (terminal P/E anchor {anchor:.1f}x, held from year 1)\n")
        print("| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) "
              "| EPS | FCF Yield | Stock Price | P/E | CAGR From Current |")
        print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for n in (1, 2, 3, 5, 10):
            r = rows[n - 1]
            eps = r["ni"] / r["sh"]
            px = eps * anchor
            print(f"| {n} | FY{r['year']} | {r['rev']:,.0f} | {r['g']:+.1%} | {r['oi']:,.0f} | {r['ni']:,.0f} | "
                  f"${eps:.2f} | {r['fcf'] / (px * r['sh']):.1%} | ${px:,.2f} | {anchor:.1f}x | "
                  f"{(px / PRICE) ** (1 / n) - 1:+.1%} |")
        print()
    fv = sum(CASES[k]["weight"] * vals[k] for k in vals)
    print(f"weighted fair value ${fv:.2f} ({(fv / PRICE) ** (1 / 3) - 1:+.1%} a year); "
          f"15%-a-year entry price ${fv / 1.15 ** 3:.2f}")


if __name__ == "__main__":
    main()
