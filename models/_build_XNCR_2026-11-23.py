#!/usr/bin/env python3
"""XNCR 2026-11-23 scenario values (Q3 2026 update).

Reads nothing from the network. Starting figures are from the Q3 2026 10-Q and
earnings release (accessions 0001326732-26-000063 and 0001326732-26-000062,
filed 2026-11-04), as recorded in data/XNCR/2026-11-23/inputs.json. Prints the
end-2029 bear/base/bull values that go into call.json and the tables in
research/updates/XNCR/2026-11-23.md. The workbook itself is rendered by
`python3 -m capital.workbook XNCR 2026-11-23`. The October initiation's
workbook script is models/_build_XNCR.py and is left as it was.

Method (three-year value at the end of 2029, undiscounted): sum of parts
  value per share = (end-2029 net cash
                     + XmAb819 value at end-2029 (peak sales x probability of
                       approval as seen at end-2029 x NPV-to-peak multiple)
                     + XmAb942 + other pipeline and platform
                     + partnered royalty and milestone portfolio
                     - capitalized corporate overhead beyond 2029) / end-2029 shares

End-2029 net cash starts from the year-end 2026 guide (midpoint of $480-500M of
cash, cash equivalents and marketable debt securities), subtracts each case's net cash burn for
2027-2029 (the second $52.5M Alexion installment, milestones, Monjuvi royalties
and interest income are netted into the burn), adds equity raised, and deducts
lease liabilities and what is left of the OMERS liability at end-2029. The OMERS royalty liability ($95.1M) is serviced by the
ex-U.S. Ultomiris royalties (OMERS takes up to $35M a year through 2028 and $12M a
year after), which are non-cash revenue in the burn; under the Alexion settlement
Xencor funds shortfalls against the $35M, charged at $11M a year in 2027-2028.
The Zenas stake ($27.0M at September 30) is left out in case the year-end guide
already counts a Q4 sale.
The NPV-to-peak multiple at end-2029 is October's today-multiple (2.0x bear,
2.5x base and bull) rolled forward three years at its 12% discount rate: 2.8x and
3.5x. It stays net of development and launch spending after 2029; spending through
2029 is in the burn, so the roll-forward is if anything conservative. Shares start at 78.353M (Q3 diluted weighted average, which
includes in-the-money options) and grow 2% a year from stock compensation.
"""

PRICE = 33.26  # 2026-11-20 close
CASH_YE26 = 490.0  # midpoint of the $480-500M year-end 2026 guide ($M)
LEASES = 55.0  # lease liabilities at end-2029, from $65.2M at Sept 30 less about $3.4M a year of principal
SHARES0 = 78.353  # Q3 2026 diluted weighted-average shares (M)
SBC_DIL = 0.02
# OMERS royalty liability left at end-2029 ($M): $95.1M at Sept 30, 2026, accreting at its 17.0% effective rate, less
# about $8.75M paid in Q4 2026, $35M a year in 2027-2028 and $12M in 2029 -> about $44M. October deducted the whole
# liability from net cash; this deducts what is left of it at the valuation date.
OMERS_YE29 = 44.0
YEARS = 3

CASES = {
    # Cases follow the 1H27 cohort update: bear if the confirmed ORR settles below about 25% or tolerability
    # fails, base for roughly 25-45%, bull at 45% or more with an accelerated path. The weighted end-2029
    # probability of approval (0.30 x 10% + 0.50 x 45% + 0.20 x 65% = 38.5%) is held near October's weighted
    # 36% today: with no new efficacy data, risk resolves by 2029 but does not shrink on average.
    "bear": dict(
        weight=0.30,
        raises=((100, 30.0), (50, 10.0)),  # ATM in 1H27 before the update, then a small raise after it
        peak=800, pos=0.10, mult=2.8,  # Phase 3 still run, or partnered, for a narrow refractory label
        xmab942=0, other=50, royalties=150, overhead=-250,
    ),
    "base": dict(
        weight=0.50,
        raises=((600, 32.0),),  # near the base path's 2027-28 prices, less an offering discount
        peak=2000, pos=0.45, mult=3.5,  # Phase 3 enrolled, accelerated-approval BLA filed by end-2029
        xmab942=200, other=150, royalties=200, overhead=-300,  # XmAb942 at about a 45% chance of a win
    ),
    "bull": dict(
        weight=0.20,
        raises=((400, 45.0), (400, 55.0)),  # half in 2027 near the bull path's $46, half in 2028
        peak=3000, pos=0.65, mult=3.5,  # accelerated approval around end-2029, earlier lines in Phase 3
        xmab942=900, other=350, royalties=280, overhead=-250,  # XENITH-UC wins
    ),
}

# Projection rows (FY2027, FY2028, FY2029, FY2031, FY2036), $M. Revenue is royalties and milestones
# until XmAb819 launches (base: accelerated approval in 2030; bull: late 2029). FY2027 base revenue of $90M
# is below the S&P Global consensus ($115.79M): about $40M of royalties plus about $50M of milestones. Net income = operating income + net interest (10 / 5 / 0 in 2027-29,
# then 0), taxed at 21% once positive. Shares grow 2% a year to 2029 (half the new equity sold in 2027, the rest in 2028), 1% a year after. Every row after FY2027 is this
# call's extrapolation; no public estimate exists beyond FY2027.
PROJ_YEARS = ("FY2027", "FY2028", "FY2029", "FY2031", "FY2036")
PROJ = {
    "bear": dict(rev=(70, 60, 60, 80, 110), opex=(380, 260, 200, 170, 160), anchor=("value", 5.00)),
    "base": dict(rev=(90, 110, 140, 450, 2000), opex=(400, 440, 470, 600, 1100), anchor=("pe", 15.0)),
    "bull": dict(rev=(115, 150, 250, 1000, 3200), opex=(430, 520, 600, 800, 1400), anchor=("pe", 13.0)),
}
INTEREST = (10, 5, 0, 0, 0)
# Cash bridge 2027-2029: burn = opex - stock comp and D&A - (revenue - non-cash OMERS royalty revenue)
#                                - interest - Alexion's final installment + capex
NONCASH_OPEX = {"bear": (45, 40, 35), "base": (45, 45, 45), "bull": (45, 45, 45)}  # 9M 2026: SBC $28.2M, D&A $7.2M
NONCASH_REV = (24, 24, 12)  # ex-U.S. Ultomiris royalties (about $6.1M a quarter in Q3) go to OMERS, up to $35M a year
# through 2028 and $12M a year from 2029
SHORTFALL = (11, 11, 0)  # Xencor funds shortfalls against OMERS's $35M a year after the settlement; about $35M less $24M
ALEXION = (52.5, 0, 0)  # final settlement installment, Q3 2027 (recognized as revenue in Q3 2026)
CAPEX = 5


def burn(name):
    p = PROJ[name]
    return tuple(
        p["opex"][i] - NONCASH_OPEX[name][i] - (p["rev"][i] - NONCASH_REV[i]) - INTEREST[i] - ALEXION[i] + CAPEX + SHORTFALL[i]
        for i in range(3)
    )


for _k in CASES:
    CASES[_k]["name"] = _k


def projection(name):
    c, p, v = CASES[name], PROJ[name], value(CASES[name])
    out = []
    for i, fy in enumerate(PROJ_YEARS):
        oi = p["rev"][i] - p["opex"][i]
        pre = oi + INTEREST[i]
        ni = pre * 0.79 if pre > 0 else pre
        yrs_after = {"FY2031": 2, "FY2036": 7}.get(fy, 0)
        if yrs_after:
            shares = v["shares"] * 1.01 ** yrs_after
        else:  # stock comp each year; half the new shares sold in 2027, all by 2028
            shares = SHARES0 * (1 + SBC_DIL) ** (i + 1) + v["new_shares"] * (0.5, 1.0, 1.0)[i]
        out.append(dict(fy=fy, rev=p["rev"][i], oi=oi, ni=ni, eps=ni / shares, shares=shares))
    kind, anchor = p["anchor"]
    p10 = anchor * out[-1]["eps"] if kind == "pe" else anchor
    p3 = v["per_share"]
    g3 = (p3 / PRICE) ** (1 / 3)
    prices = [PRICE * g3, PRICE * g3**2, p3, p3 * ((p10 / p3) ** (1 / 7)) ** 2, p10]
    for row, px, n in zip(out, prices, (1, 2, 3, 5, 10)):
        row.update(price=px, n=n, cagr=(px / PRICE) ** (1 / n) - 1, fcf_yield=row["ni"] / (px * row["shares"]))
    return out, kind, anchor, p10


def print_projection():
    prev = 198.65  # FY2026 consensus revenue
    for name in ("bear", "base", "bull"):
        rows, kind, anchor, p10 = projection(name)
        print(f"\n{name}: anchor {kind} {anchor} -> year-10 price ${p10:.2f}")
        print("| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |")
        print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        last = prev
        for r in rows:
            span = {"FY2031": 2, "FY2036": 5}.get(r["fy"], 1)
            g = (r["rev"] / last) ** (1 / span) - 1
            gl = f"{g:+.1%}" + (" CAGR" if span > 1 else "")
            pe = f"{r['price'] / r['eps']:.1f}x" if r["eps"] > 0 else "n/m"
            print(f"| {r['n']} | {r['fy']} | {r['rev']:,.0f} | {gl} | {r['oi']:,.0f} | {r['ni']:,.0f} | ${r['eps']:.2f} | {r['fcf_yield']:.1%} | ${r['price']:.2f} | {pe} | {r['cagr']:+.1%} |")
            last = r["rev"]


def value(c):
    raised = sum(a for a, _ in c["raises"])
    new_shares = sum(a / p for a, p in c["raises"])
    cash = CASH_YE26 - sum(burn(c["name"])) + raised - LEASES - OMERS_YE29
    x819 = c["peak"] * c["pos"] * c["mult"]
    equity = cash + x819 + c["xmab942"] + c["other"] + c["royalties"] + c["overhead"]
    shares = SHARES0 * (1 + SBC_DIL) ** YEARS + new_shares
    return dict(cash=cash, x819=x819, equity=equity, shares=shares, new_shares=new_shares, per_share=max(equity, 0) / shares)


def weighted(cases, weights=None):
    w = weights or {k: c["weight"] for k, c in cases.items()}
    return sum(w[k] * value(c)["per_share"] for k, c in cases.items())


def annual(v, price=PRICE):
    return (v / price) ** (1 / YEARS) - 1


def tweak(case, **kw):
    out = {k: dict(v) for k, v in CASES.items()}
    out[case].update(kw)
    return out


def main():
    for k in CASES:
        print(f"{k} burn 2027-29: " + ", ".join(f"{b:,.1f}" for b in burn(k)))
    print(f"{'':28}{'bear':>10}{'base':>10}{'bull':>10}")
    rows = [
        ("Net burn 2027-29 ($M)", lambda c, v: sum(burn(c["name"]))),
        ("Equity raised ($M)", lambda c, v: sum(a for a, _ in c["raises"])),
        ("End-2029 net cash ($M)", lambda c, v: v["cash"]),
        ("XmAb819 peak sales ($M)", lambda c, v: c["peak"]),
        ("Probability of approval", lambda c, v: c["pos"]),
        ("NPV / peak multiple", lambda c, v: c["mult"]),
        ("XmAb819 value ($M)", lambda c, v: v["x819"]),
        ("XmAb942 ($M)", lambda c, v: c["xmab942"]),
        ("Other pipeline ($M)", lambda c, v: c["other"]),
        ("Royalties/milestones ($M)", lambda c, v: c["royalties"]),
        ("Corporate overhead ($M)", lambda c, v: c["overhead"]),
        ("Equity value ($M)", lambda c, v: v["equity"]),
        ("New shares (M)", lambda c, v: v["new_shares"]),
        ("End-2029 shares (M)", lambda c, v: v["shares"]),
        ("Value per share ($)", lambda c, v: v["per_share"]),
        ("Weight", lambda c, v: c["weight"]),
    ]
    vals = {k: value(c) for k, c in CASES.items()}
    for label, f in rows:
        print(f"{label:28}" + "".join(f"{f(CASES[k], vals[k]):>10,.2f}" for k in ("bear", "base", "bull")))
    fv = weighted(CASES)
    print(f"\nFair value (weighted, end-2029): ${fv:.2f}  annual from ${PRICE}: {annual(fv):.1%}")
    print(f"Own price (15%/yr): ${fv / 1.15 ** YEARS:.2f}   Avoid above: ${fv:.2f}")
    print(f"Discounted to today at 12%: ${fv / 1.12 ** YEARS:.2f} (October call: $34.71 today-value)")
    print("Weighted end-2029 probability of approval: " + f"{sum(c['weight'] * c['pos'] for c in CASES.values()):.1%}" + "; expected XmAb819 value $" + f"{sum(c['weight'] * value(c)['x819'] for c in CASES.values()):,.0f}M")
    print(f"Base alone: {annual(vals['base']['per_share']):.1%} a year; bull share of FV ${CASES['bull']['weight'] * vals['bull']['per_share']:.2f}")
    print("\nSensitivities (fair value, annual return):")
    sens = {
        "weights 25/50/25": weighted(CASES, {"bear": 0.25, "base": 0.50, "bull": 0.25}),
        "weights 35/45/20": weighted(CASES, {"bear": 0.35, "base": 0.45, "bull": 0.20}),
        "weights 40/45/15": weighted(CASES, {"bear": 0.40, "base": 0.45, "bull": 0.15}),
        "weights 20/55/25": weighted(CASES, {"bear": 0.20, "base": 0.55, "bull": 0.25}),
        "Zenas stake ($27.0M) added": weighted(CASES) + 27.0 * sum(c["weight"] / value(c)["shares"] for c in CASES.values()),
        "October XmAb819 inputs, rolled": weighted({k: dict(v, **o) for (k, v), o in zip(CASES.items(), (dict(peak=800, pos=0.20), dict(peak=2000, pos=0.40), dict(peak=3000, pos=0.45)))}),
        "base PoS 35%": weighted(tweak("base", pos=0.35)),
        "base PoS 60%": weighted(tweak("base", pos=0.60)),
        "base peak $1.5B": weighted(tweak("base", peak=1500)),
        "base peak $2.5B": weighted(tweak("base", peak=2500)),
        "base multiple 3.0x": weighted(tweak("base", mult=3.0)),
        "all multiples 3.0x / 2.5x bear": weighted({k: dict(v, mult=(2.5 if k == "bear" else 3.0)) for k, v in CASES.items()}),
        "base raise of $600M at $22": weighted(tweak("base", raises=((600, 22.0),))),
        "base raise of $600M at $40": weighted(tweak("base", raises=((600, 40.0),))),
        "no OMERS shortfall": weighted(CASES) + 22.0 * sum(c["weight"] / value(c)["shares"] for c in CASES.values()),
        "bull peak $3.5B, PoS 75%": weighted(tweak("bull", peak=3500, pos=0.75)),
        "20/55/25, bull $3.5B at 75%": weighted(tweak("bull", peak=3500, pos=0.75), {"bear": 0.20, "base": 0.55, "bull": 0.25}),
        "XmAb942 $300M in base": weighted(tweak("base", xmab942=300)),
        "XmAb942 zero in base": weighted(tweak("base", xmab942=0)),
    }
    for k, v in sens.items():
        print(f"  {k:28} ${v:6.2f}  {annual(v):6.1%}")
    # base multiple that returns today's price
    lo, hi = 0.5, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if value(tweak("base", mult=mid)["base"])["per_share"] < PRICE:
            lo = mid
        else:
            hi = mid
    print(f"\nBase NPV/peak multiple that returns ${PRICE}: {mid:.2f}x")


if __name__ == "__main__":
    import sys

    print_projection() if "--projection" in sys.argv else main()
