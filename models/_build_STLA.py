#!/usr/bin/env python3
"""STLA 2026-11-20 scenario values and projection tables.

Reads nothing from the network. Inputs are the figures recorded in
data/STLA/2026-11-20/inputs.json (FY2025 20-F, Q2 and Q3 2026 releases and the
Q3 2026 interim report filed on Form 6-K, the May 21, 2026 Investor Day
targets). Prints the bear/base/bull values that go into call.json and the
projection tables in projections/STLA.md. The workbook itself is rendered by
`python3 -m capital.workbook STLA 2026-11-20`.

Method: value per share at December 31, 2029 =
FY2029 adjusted net income to common / diluted shares x exit P/E, plus the
dividends paid in 2028 and 2029, converted to dollars at the November 19, 2026
EUR/USD rate (1.0972) and held there.

Adjusted net income = (adjusted operating income (AOI) - net financial expense
- a recurring allowance for restructuring and other unusual items) x (1 - 27%)
- coupons on the hybrid perpetual notes (EUR 4.9B issued March 2026, about
EUR 0.26B a year after tax). The allowance is deducted because Stellantis has
booked restructuring every year; the Street's adjusted EPS excludes it, so these
EPS figures sit below consensus on the same AOI.

Industrial free cash flow (IFCF) is set per case for 2027-2029 and only feeds
the industrial net cash path and the FCF-multiple cross-check printed below
(6.5x 2029 IFCF plus end-2029 industrial net cash less the hybrid notes and
the EUR 5.0B of employee benefit liabilities, plus dividends);
after 2029 it is 60-70% of net income (management's 2030 plan of EUR 6B IFCF on
7% AOI implies about 68%). Dividends follow the stated policy (25-30% payout
when industrial liquidity exceeds 25% of revenue), paid the year after the
profit. No buybacks; diluted shares grow 10M a year from stock awards.
Rows after 2029 extrapolate: revenue growth fades linearly to the 2036 rate,
the AOI margin moves to its terminal level by 2032.
"""

PRICE_USD = 3.54  # 2026-11-19 close
FX = 1.0972  # EUR/USD close 2026-11-19
PRICE_EUR = PRICE_USD / FX
SHARES0 = 2902.1  # Q3 2026 weighted average, millions
SHARE_GROWTH = 10.0
TAX = 0.27
HYBRID_COUPON = 255.0  # EUR 343.5M pre-tax (2,200 x 6.25% + 1,800 x 6.875% + 997 x 8.25%) after 27% tax; Q3 2026 EPS deduction EUR 65M
REV_2026 = 161090.0  # consensus, StockAnalysis 2026-11-20
AOI_2026 = 3220.0  # 9M 1,989 + Q4 about 1,230
NI_2026 = 900.0
NET_CASH_2026 = 6900.0  # Sep 30 5,400 + Q4 IFCF about 1,500
HYBRIDS = 4927.0
BENEFITS = 5003.0  # employee benefit liabilities, Sep 30, 2026
YEARS = list(range(2027, 2037))

CASES = {
    # rev, m (AOI margin), fin (net financial expense), unusual, ifcf: 2027-2029, EUR M
    "bear": dict(rev=[158000, 160000, 162000], m=[0.012, 0.018, 0.023], fin=[1000, 1100, 1200],
                 unusual=700, ifcf=[-2200, -1000, 0], extra_hybrid=3000, extra_coupon=240, payout=0.0,
                 g_term=0.015, m_term=0.028, conv=0.6, pe=4.0, weight=0.35),
    "base": dict(rev=[164500, 169500, 175000], m=[0.023, 0.036, 0.042], fin=[850, 900, 900],
                 unusual=500, ifcf=[0, 1500, 2500], extra_hybrid=0, extra_coupon=0, payout=0.27,
                 g_term=0.025, m_term=0.050, conv=0.7, pe=4.0, weight=0.45),
    "bull": dict(rev=[167000, 175000, 183000], m=[0.030, 0.046, 0.058], fin=[800, 800, 750],
                 unusual=400, ifcf=[1000, 3000, 4500], extra_hybrid=0, extra_coupon=0, payout=0.30,
                 g_term=0.030, m_term=0.070, conv=0.7, pe=5.5, weight=0.20),
}


def path(c):
    rows, prev_rev, prev_ni, cash, sh = [], REV_2026, NI_2026, NET_CASH_2026, SHARES0
    for i, y in enumerate(YEARS):
        if i < 3:
            rev, m, fin = c["rev"][i], c["m"][i], c["fin"][i]
        else:
            g3 = c["rev"][2] / c["rev"][1] - 1
            g = g3 + (c["g_term"] - g3) * (i - 2) / 7
            rev = prev_rev * (1 + g)
            m = c["m"][2] + (c["m_term"] - c["m"][2]) * min(1, (i - 2) / 3)
            fin = c["fin"][2]
        aoi = rev * m
        coupon = HYBRID_COUPON + c["extra_coupon"]  # bear: a further EUR 3B hybrid at 8% in 2027
        ni = (aoi - fin - c["unusual"]) * (1 - TAX) - coupon
        sh += SHARE_GROWTH
        ifcf = c["ifcf"][i] if i < 3 else c["conv"] * ni
        dps = c["payout"] * max(prev_ni, 0) / sh if y >= 2028 else 0.0
        cash += ifcf - dps * sh + (c["extra_hybrid"] if i == 0 else 0)
        rows.append(dict(year=y, rev=rev, g=rev / prev_rev - 1, aoi=aoi, m=m, ni=ni, sh=sh,
                         eps=ni / sh, ifcf=ifcf, dps=dps, cash=cash))
        prev_rev, prev_ni = rev, ni
    return rows


def value(c, rows):
    r = rows[2]
    divs = rows[1]["dps"] + rows[2]["dps"]
    eur = r["eps"] * c["pe"] + divs
    return eur * FX, eur, divs


def main():
    vals = {}
    for name, c in CASES.items():
        rows = path(c)
        v, eur, divs = value(c, rows)
        vals[name] = round(v, 2)  # call.json carries cents
        r = rows[2]
        cagr = (r["rev"] / REV_2026) ** (1 / 3) - 1
        cross = (r["ifcf"] * 6.5 + r["cash"] - HYBRIDS - c["extra_hybrid"] - BENEFITS) / r["sh"] + divs
        print(f"{name}: 2029 revenue {r['rev']:,.0f} (2026-29 CAGR {cagr:.1%}), AOI {r['aoi']:,.0f} ({r['m']:.1%}), "
              f"NI {r['ni']:,.0f}, shares {r['sh']:,.0f}, EPS 2027-29 "
              f"{rows[0]['eps']:.2f}/{rows[1]['eps']:.2f}/{r['eps']:.2f} EUR, x{c['pe']} + dividends {divs:.2f} "
              f"= EUR {eur:.2f} = ${v:.2f} ({(v / PRICE_USD) ** (1 / 3) - 1:+.1%} a year); "
              f"end-2029 industrial net cash {r['cash']:,.0f}; cross-check 6.5x IFCF + net cash - hybrids - benefits "
              f"= EUR {cross:.2f} (${cross * FX:.2f})")
        anchor = eur / r["eps"]
        print(f"\n### {name.capitalize()} (terminal P/E anchor {anchor:.2f}x, held from year 1)\n")
        print("| Years Out | Year | Revenue (EUR M) | Revenue Growth YoY | AOI (EUR M) | Net Income (EUR M) "
              "| EPS (EUR) | FCF Yield | Stock Price (USD) | P/E | CAGR From Current |")
        print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for n in (1, 2, 3, 5, 10):
            r = rows[n - 1]
            px_eur = r["eps"] * anchor
            px = px_eur * FX
            if px_eur > 0:
                cells = (f"{r['ifcf'] / (px_eur * r['sh']):.1%} | ${px:,.2f} | {anchor:.2f}x | "
                         f"{(px / PRICE_USD) ** (1 / n) - 1:+.1%}")
            else:  # a P/E on a loss gives no price
                cells = "n.m. | n.m. | n.m. | n.m."
            print(f"| {n} | {r['year']} | {r['rev']:,.0f} | {r['g']:+.1%} | {r['aoi']:,.0f} | {r['ni']:,.0f} | "
                  f"{r['eps']:.2f} | {cells} |")
        print()
    fv = round(sum(CASES[k]["weight"] * vals[k] for k in vals), 2)
    print(f"price EUR {PRICE_EUR:.2f}; weighted fair value ${fv:.2f} ({(fv / PRICE_USD) ** (1 / 3) - 1:+.1%} a year); "
          f"15%-a-year entry price ${fv / 1.15 ** 3:.2f}")


if __name__ == "__main__":
    main()
