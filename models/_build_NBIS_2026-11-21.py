#!/usr/bin/env python3
"""NBIS 2026-11-21 scenario values (Q3 2026 update).

Reads nothing from the network. Every starting figure is from the Q3 2026 6-K
(accessions 0001104659-26-126008 and 0001104659-26-126238, filed 2026-11-12) or
the FY2025 20-F, as recorded in data/NBIS/2026-11-21/inputs.json. Prints the
end-2029 bear/base/bull values that go into call.json and the tables in
research/updates/NBIS/2026-11-21.md. The workbook itself is rendered by
`python3 -m capital.workbook NBIS 2026-11-21`. The October initiation's
workbook script is models/_build_NBIS.py and is left as it was.

Method (three-year value at the end of 2029, undiscounted):
  value per share = (2030 adjusted EBITDA x exit EV/EBITDA
                     - end-2029 net debt
                     - DEFERRED_HAIRCUT x end-2029 deferred revenue
                     + equity stakes at book) / end-2029 shares

Revenue is built from capacity: average megawatts billing in the year times a
blended annual revenue per MW. Capex is MW added times an all-in capex per MW,
half paid in the year before the MW bills; the rest of the 2030 capacity is
also charged by end-2029, so the forward EBITDA is fully paid for. Interest is
the cash coupon on the convertibles (accretion is already in the debt figure)
plus the case rate on the rest of net debt. Net debt rolls
forward from September 30, 2026 (unrestricted cash only):
  net debt += capex - EBITDA + interest on the average balance + VIE advances
              - deferred-revenue inflow - equity raised - debt converted
and receivables ($4,039.9M, 75% from one customer) normalize to 45 days of
revenue by end-2029. Shares grow 1.5% a year from stock compensation.
Customer prepayments are cash in hand but revenue later recognized from them
brings no new cash, so 75% of the end-2029 deferred-revenue balance is treated
as debt-like: Nebius accounts for them with a significant financing component
and accretes interest on them ($121.1M in nine months 2026). The other quarter
is float that the guided $17-20B a year of new prepayments keeps replacing; the
sensitivity prints 50% and 100%.
Equity value is floored at zero (limited liability). A convertible series
converts when the case's end-2029 value is above its conversion price times its
accretion ratio (solved by iteration); otherwise the accreted principal stays
in net debt.
"""

PRICE = 81.31  # 2026-11-20 close
# September 30, 2026 balance sheet ($M), 6-K Exhibit 99.2
DEBT_PRINCIPAL = 16_478.0  # convertible notes (accreted to date) + MUFG term loan
CASH = 7_425.6  # unrestricted cash; the $1,215.5M of restricted cash secures financings and is left out
AR0 = 4_039.9  # accounts receivable, 75% from one customer (Customer D): largely invoiced prepayments
AR_DAYS = 45  # receivables normalize to 45 days of revenue by end-2029
DEFERRED0 = 1_445.5 + 7_963.7  # deferred revenue, current + non-current
STAKES = 1_603.9  # investments in non-marketable equity securities (ClickHouse, Toloka, others), book
SHARES0 = 292.902405 + 21.065936 + 5.493478  # outstanding + NVIDIA pre-funded warrants + unvested RSUs (M)
SBC_DIL3 = 0.015  # stock-compensation dilution per year, 2027-2029
Q4_OTHER = 0.9e3  # VIE notes: $230.6M advanced Oct 1 plus up to $662.2M intended
DEFERRED_HAIRCUT = 0.75
GROSS_PPE0 = 21_000.0  # Sept 30 net PP&E $19,341.9M plus about $1.7B of depreciation taken to date (approximate)
GPU_SHARE, GPU_LIFE, OTHER_LIFE = 0.65, 5, 20  # cross-check only: share of capex in servers/network, useful lives

# Convertible series: (name, original principal $M, accreted principal at maturity $M, conversion price $)
# The 6-K's "principal amount outstanding" ($16,478M with the term loan) already equals each series'
# accreted amount at maturity (e.g. $3,450M x 110% = $3,795M), so no further accretion is added.
CONVERTS = [
    ("June 2029/2031 notes", 178.7, 214.4, 51.45),
    ("September 2030/2032 notes", 3_162.5, 3_636.8, 138.75),
    ("March 2031 notes", 2_590.0, 3_105.0, 183.22),
    ("March 2033 notes", 1_750.0, 2_100.0, 180.31),
    ("February 2030 notes", 3_450.0, 3_795.0, 313.46),
    ("February 2034 notes", 2_300.0, 2_875.0, 324.65),
]
# Cash coupons on the convertibles outstanding at Sept 30 ($M a year, stated coupon on original principal;
# accretion is already in DEBT_PRINCIPAL, so the case rate applies only to the rest of net debt).
CONV_ACCRETED = 16_478.0 - 751.8
CONV_COUPON = (0.02 * 87.5 + 0.03 * 87.5 + 0.01 * 1_581.25 + 0.0275 * 1_581.25 + 0.0125 * 2_590.0
               + 0.02625 * 1_750.0 + 0.005 * 3_450.0 + 0.045 * 2_300.0)
# Shares per $1,000 original principal = 1,000 / conversion price. Settlement in shares beats
# repaying the accreted principal only above conversion price x (accreted / original).

YEARS = [2027, 2028, 2029, 2030]
Q4_REV = 3_000.0 - 1_962.1  # FY2026 at the low end of $3.0-3.4B; nine months $1,962.1M
Q4_MARGIN = 0.36  # FY2026 adj. EBITDA ~40% of $3.0B less nine months' $831.5M

CASES = {
    # end-2026 MW billing; MW added per year 2027-2030; blended $M revenue per MW-year;
    # adj. EBITDA margin; capex per MW added ($M, all-in), spent half in the year before the MW bills;
    # net interest rate on average net debt; end-2029 deferred revenue $B;
    # equity raised $B 2027-2029 and average price; exit EV/EBITDA
    "bear": dict(mw0=300, add=[600, 450, 200, 100], rpm=[15.0, 13.0, 11.5, 10.5],
                 m=[0.30, 0.38, 0.41, 0.42], cpm=42.0, r=0.09,
                 deferred=14.0, equity=8.0, eq_price=35.0, x=5.0, weight=0.35),
    "base": dict(mw0=350, add=[750, 800, 700, 500], rpm=[17.0, 16.5, 15.5, 14.5],
                 m=[0.38, 0.46, 0.49, 0.50], cpm=40.0, r=0.075,
                 deferred=24.0, equity=8.0, eq_price=90.0, x=6.0, weight=0.50),
    "bull": dict(mw0=380, add=[900, 1_000, 1_000, 800], rpm=[18.5, 18.5, 18.0, 17.5],
                 m=[0.42, 0.50, 0.54, 0.56], cpm=40.0, r=0.07,
                 deferred=32.0, equity=6.0, eq_price=180.0, x=7.5, weight=0.15),
}
Q4_CAPEX = 11.6  # $B: FY2026 capex about $27B less $15.43B in nine months, same in every case


def capex_path(c):
    """$B for Q4 2026 and 2027-2029: half of each year's MW is paid the year before it bills."""
    a = c["add"]
    return [Q4_CAPEX] + [c["cpm"] * (0.5 * a[i] + 0.5 * a[i + 1]) / 1e3 for i in range(3)]


def run(c, converted=()):
    """Roll the case forward; `converted` names the convertible series assumed to convert."""
    mw_end, rows = c["mw0"], []
    for i, y in enumerate(YEARS):
        start = mw_end
        mw_end += c["add"][i]
        avg = (start + mw_end) / 2
        rev = avg * c["rpm"][i]
        rows.append(dict(year=y, mw_end=mw_end, mw_avg=avg, rev=rev, ebitda=rev * c["m"][i]))
    net = DEBT_PRINCIPAL - CASH
    deferred = DEFERRED0
    capex = capex_path(c)
    # Q4 2026
    def charge(balance):  # coupon on the convertibles, case rate on the rest
        return CONV_COUPON + (balance - CONV_ACCRETED) * c["r"]
    net += capex[0] * 1e3 - Q4_REV * Q4_MARGIN + Q4_OTHER + charge(net) / 4
    # deferred revenue rises in a straight line to the case's end-2029 balance
    step = (c["deferred"] * 1e3 - deferred) / 3
    for i in range(3):
        y = rows[i]
        flow = capex[i + 1] * 1e3 - y["ebitda"] - step - c["equity"] * 1e3 / 3
        interest = charge(net + flow / 2)  # on the average balance
        net += flow + interest
        deferred += step
        y["capex"], y["interest"], y["net_debt"] = capex[i + 1] * 1e3, interest, net
    net += 0.5 * c["cpm"] * c["add"][3]  # rest of the 2030 capacity, paid by end-2029 so the forward EBITDA is fully funded
    ar_end = rows[2]["rev"] * AR_DAYS / 365
    net += ar_end - AR0  # receivables normalize: collection is cash in, growth is cash out
    conv_shares = 0.0
    for name, orig, acc, cp in CONVERTS:
        if name in converted:
            net -= acc
            conv_shares += orig / cp
    shares = SHARES0 * (1 + SBC_DIL3) ** 3 + c["equity"] * 1e3 / c["eq_price"] + conv_shares
    ebitda30 = rows[3]["ebitda"]
    ev = ebitda30 * c["x"]
    equity_value = ev - net - DEFERRED_HAIRCUT * deferred + STAKES
    gross = GROSS_PPE0 + sum(capex) * 1e3 + 0.5 * c["cpm"] * c["add"][3]
    da30 = gross * GPU_SHARE / GPU_LIFE + gross * (1 - GPU_SHARE) / OTHER_LIFE
    pretax30 = ebitda30 - da30 - (CONV_COUPON + (net - CONV_ACCRETED) * c["r"])
    return dict(rows=rows, net=net, deferred=deferred, shares=shares, ev=ev, ebitda30=ebitda30,
                value=max(equity_value, 0.0) / shares, conv_shares=conv_shares, da30=da30, pretax30=pretax30,
                equity_value=equity_value, capex=capex, ev_ebit=ev / max(ebitda30 - da30, 1))


TAIL = {  # 2031-2036: revenue growth by 2036, D&A share of revenue by 2036, terminal P/E (None: no equity)
    "bear": dict(g_term=0.03, da_term=0.36, pe=None),
    "base": dict(g_term=0.06, da_term=0.30, pe=16.0),
    "bull": dict(g_term=0.08, da_term=0.28, pe=18.0),
}
TAX, SBC_DIL = 0.21, 0.01


def projection(name, c, out):
    """Ten-year rows for projections/NBIS.md: 2027-2029 from the case, 2030-2036 faded."""
    t = TAIL[name]
    gross = GROSS_PPE0 + out["capex"][0] * 1e3
    rate = GPU_SHARE / GPU_LIFE + (1 - GPU_SHARE) / OTHER_LIFE
    rows, net = [], DEBT_PRINCIPAL - CASH
    for y in out["rows"][:3]:
        da = gross * rate
        gross += y["capex"]
        rows.append(dict(year=y["year"], rev=y["rev"], ebitda=y["ebitda"], da=da, interest=y["interest"],
                         capex=y["capex"], shares=None))
    r30 = out["rows"][3]
    da30_share = out["da30"] / r30["rev"]
    g30 = r30["rev"] / out["rows"][2]["rev"] - 1
    margin = r30["ebitda"] / r30["rev"]
    net, rev, shares = out["net"], r30["rev"], out["shares"]
    for i, y in enumerate(range(2030, 2037)):
        k = i / 6
        if y > 2030:
            rev *= 1 + g30 + (t["g_term"] - g30) * k
        da = rev * (da30_share + (t["da_term"] - da30_share) * k)
        ebitda = rev * margin
        interest = CONV_COUPON + (net - CONV_ACCRETED) * c["r"] if net > CONV_ACCRETED else net * c["r"]
        capex = da * 1.1
        net += capex - ebitda + interest
        shares *= 1 + SBC_DIL
        rows.append(dict(year=y, rev=rev, ebitda=ebitda, da=da, interest=interest, capex=capex, shares=shares))
    prev = 3_000.0
    for r in rows:
        r["g"] = r["rev"] / prev - 1
        prev = r["rev"]
        r["ebit"] = r["ebitda"] - r["da"]
        pre = r["ebit"] - r["interest"]
        r["ni"] = pre * (1 - TAX) if pre > 0 else pre
        r["fcf"] = r["ebitda"] - r["capex"] - r["interest"]
        r["shares"] = r["shares"] or out["shares"]
        r["eps"] = r["ni"] / r["shares"]
    return rows


def print_projection(name, c, out):
    rows = projection(name, c, out)
    by = {r["year"]: r for r in rows}
    v3 = out["value"]
    t = TAIL[name]
    p10 = by[2036]["eps"] * t["pe"] if t["pe"] and by[2036]["eps"] > 0 else None
    prices = {}
    if v3 > 0:
        cagr3 = (v3 / PRICE) ** (1 / 3) - 1
        for n, y in ((1, 2027), (2, 2028), (3, 2029)):
            prices[y] = PRICE * (1 + cagr3) ** n
        if p10:
            g = (p10 / v3) ** (1 / 7) - 1
            prices[2031] = v3 * (1 + g) ** 2
            prices[2036] = p10
    anchor = f"{t['pe']:.0f}x FY2036 EPS of ${by[2036]['eps']:.2f}, terminal price ${p10:,.2f}" if p10 else "none (equity worth nothing)"
    print(f"\n### {name.capitalize()} (terminal P/E anchor: {anchor})\n")
    print("| Years Out | Fiscal Year | Revenue ($M) | Revenue Growth YoY | Operating Income ($M) | Net Income ($M) | EPS | FCF Yield | Stock Price | P/E | CAGR From Current |")
    print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for n, y in ((1, 2027), (2, 2028), (3, 2029), (5, 2031), (10, 2036)):
        r = by[y]
        px = prices.get(y)
        if px is None and y == 2029:
            px = 0.0
        mcap = px * r["shares"] if px else None
        fy = f"{r['fcf'] / mcap:.1%}" if mcap else "n/m"
        pe = f"{px / r['eps']:.1f}x" if px and r["eps"] > 0 and px / r["eps"] < 200 else "n/m"
        cg = f"{(px / PRICE) ** (1 / n) - 1:+.1%}" if px else ("-100%" if px == 0.0 else "n/m")
        ps = f"${px:,.2f}" if px is not None else "n/m"
        print(f"| {n} | FY{y} | {r['rev']:,.0f} | {r['g']:+.1%} | {r['ebit']:,.0f} | {r['ni']:,.0f} | ${r['eps']:.2f} | {fy} | {ps} | {pe} | {cg} |")


def solve(c):
    converted = ()
    for _ in range(10):
        out = run(c, converted)
        nxt = tuple(n for n, orig, acc, cp in CONVERTS if out["value"] > cp * acc / orig)
        if nxt == converted:
            return out, converted
        converted = nxt
    return out, converted


def main():
    global DEFERRED_HAIRCUT
    results = {}
    for name, c in CASES.items():
        out, conv = solve(c)
        results[name] = out
        r = out["rows"]
        rev26 = 3_000.0
        cagr = (r[2]["rev"] / rev26) ** (1 / 3) - 1
        print(f"\n{name.upper()}  weight {c['weight']:.0%}  exit {c['x']}x  converted: {', '.join(conv) or 'none'}")
        for y in r:
            extra = f" capex {y['capex']:>8,.0f} interest {y['interest']:>6,.0f} net debt {y['net_debt']:>8,.0f}" if "capex" in y else ""
            print(f"  {y['year']}: MW end {y['mw_end']:>5,.0f} avg {y['mw_avg']:>6,.0f}  revenue {y['rev']:>8,.0f}  EBITDA {y['ebitda']:>7,.0f}{extra}")
        print(f"  revenue CAGR 2026-29 {cagr:.1%}; 2030 EBITDA {out['ebitda30']:,.0f} x {c['x']} = EV {out['ev']:,.0f}")
        print(f"  end-2029 net debt {out['net']:,.0f}; deferred {out['deferred']:,.0f} x {DEFERRED_HAIRCUT}; stakes {STAKES:,.0f}")
        print(f"  cross-check: 2030 D&A ~{out['da30']:,.0f}, EBIT ~{out['ebitda30'] - out['da30']:,.0f} (EV/EBIT {out['ev'] / max(out['ebitda30'] - out['da30'], 1):.0f}x), pre-tax ~{out['pretax30']:,.0f}; capex/MW added 2027-29 {sum(out['capex'][1:]) * 1e3 / sum(c['add'][:3]):.1f}M")
        print(f"  equity value {out['equity_value']:,.0f}; shares {out['shares']:.1f}M (conversion {out['conv_shares']:.1f}M); value ${out['value']:.2f}")
        capex_total = sum(out["capex"])
        print(f"  capex Q4-26..2029 ${capex_total:.1f}B for {sum(c['add'][:3]):,} MW added 2027-29")
    fv = sum(CASES[n]["weight"] * results[n]["value"] for n in CASES)
    print(f"\nweighted fair value ${fv:.2f}; {((fv / PRICE) ** (1 / 3) - 1):+.1%} a year from ${PRICE}")
    # sensitivities
    for h in (0.5, 1.0):
        DEFERRED_HAIRCUT = h
        vals = {n: solve(CASES[n])[0]["value"] for n in CASES}
        f = sum(CASES[n]["weight"] * vals[n] for n in CASES)
        print(f"deferred haircut {h:.0%}: " + " / ".join(f"${vals[n]:.2f}" for n in CASES) + f"  fair ${f:.2f} ({((max(f, 0.01) / PRICE) ** (1 / 3) - 1):+.1%})")
    DEFERRED_HAIRCUT = 0.75
    base = dict(CASES["base"])
    for x in (5.5, 6.0, 7.0, 8.0):
        b = solve(dict(base, x=x))[0]["value"]
        f = CASES["bear"]["weight"] * results["bear"]["value"] + 0.5 * b + CASES["bull"]["weight"] * results["bull"]["value"]
        print(f"base exit {x}x: base ${b:.2f}, fair ${f:.2f} ({((f / PRICE) ** (1 / 3) - 1):+.1%})")
    for r in (0.10,):
        vals = {n: solve(dict(CASES[n], r=r))[0]["value"] for n in CASES}
        f = sum(CASES[n]["weight"] * vals[n] for n in CASES)
        print(f"all cases at {r:.0%} interest: " + " / ".join(f"${vals[n]:.2f}" for n in CASES) + f"  fair ${f:.2f} ({((f / PRICE) ** (1 / 3) - 1):+.1%})")
    for cpm in (35.0, 45.0):
        vals = {n: solve(dict(CASES[n], cpm=cpm + (2.0 if n == "bear" else 0.0)))[0]["value"] for n in CASES}
        f = sum(CASES[n]["weight"] * vals[n] for n in CASES)
        print(f"capex ${cpm:.0f}M per MW (bear +$2M): " + " / ".join(f"${vals[n]:.2f}" for n in CASES) + f"  fair ${f:.2f} ({((f / PRICE) ** (1 / 3) - 1):+.1%})")
    b = solve(dict(base, m=base["m"][:3] + [0.46]))[0]["value"]
    print(f"base 2030 margin 46%: base ${b:.2f}")
    b = solve(dict(base, equity=15.0, eq_price=50.0))[0]["value"]
    print(f"base with $15B of equity at $50: base ${b:.2f}")
    for rpm_cut in (1.0, 2.0):
        b = solve(dict(base, rpm=[v - rpm_cut for v in base["rpm"]]))[0]["value"]
        f = CASES["bear"]["weight"] * results["bear"]["value"] + 0.5 * b + CASES["bull"]["weight"] * results["bull"]["value"]
        print(f"base revenue/MW -${rpm_cut:.0f}M: base ${b:.2f}, fair ${f:.2f} ({((f / PRICE) ** (1 / 3) - 1):+.1%})")
    for w in ((0.30, 0.50, 0.20), (0.40, 0.50, 0.10), (0.40, 0.45, 0.15), (0.45, 0.45, 0.10)):
        f = sum(wi * results[n]["value"] for wi, n in zip(w, CASES))
        print(f"weights {'/'.join(f'{v:.0%}' for v in w)}: fair ${f:.2f} ({((f / PRICE) ** (1 / 3) - 1):+.1%})")


if __name__ == "__main__":
    import sys
    if "--projection" in sys.argv:
        for n, c in CASES.items():
            print_projection(n, c, solve(c)[0])
    else:
        main()
