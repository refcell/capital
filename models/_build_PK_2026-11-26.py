#!/usr/bin/env python3
"""PK 2026-11-26 scenario values and projection tables (Q3 2026 update).

Reads nothing from the network. Starting figures are from the Q3 2026 earnings
release and 10-Q (accessions 0001617406-26-000047, filed 2026-11-04, and
0001617406-26-000050, filed 2026-11-05), the FY2025 release (0001617406-26-000003)
and the November 5, 2026 call transcript, as recorded in
data/PK/2026-11-26/inputs.json and data/PK/2026-11-26/sources/. Prints the
end-2029 bear/base/bull values that go into call.json, the sensitivities quoted
in the update note, and the tables in projections/PK.md. The workbook itself is
rendered by `python3 -m capital.workbook PK 2026-11-26`. The August initiation's
script is models/_build_PK.py and is left as it was.

Method: value per share at December 31, 2029, undiscounted =
  FY2029 Adjusted FFO per diluted share x exit P/FFO
  + dividends paid from the January 15, 2027 payment (Q4 2026 dividend, already
    declared) through the October 2029 payment (12 payments).

Adjusted FFO is the company's definition (Nareit FFO plus severance,
share-based compensation and other items; before capital expenditure). It is
built as Adjusted EBITDA - net interest expense - $18M of taxes, noncontrolling
interests and joint-venture items. The $18M is calibrated, not checked: it is
solved from the FY2026 guide midpoints ($640M - $215M net interest, which is
$222M interest expense less $7M interest income, - $18M = $407M, the midpoint of
the guide's $402-$412M, or $2.025 a share on the guide's 201M diluted shares).
It also stands in for distributions to noncontrolling interests ($10M in 9M
2026), so the net debt path does not deduct them again.

Adjusted EBITDA each year = FY2026 guide midpoint ($640M) grown at an organic
rate, plus the cumulative Royal Palm ramp (management: about $3M of hotel
EBITDA in 2026, at least $14M in 2027, about $28M stabilized by 2028) and the
cumulative Hawaii recapture after the Ali'i Tower renovation (management: about
$60M or more over the next couple of years, back to the 2023 peak). Remaining
Non-Core sales (five hotels; $37M of 2025 EBITDA in the release, about $34M on
the call, $20M of it Lake Buena Vista) are treated as
neutral to Adjusted FFO: at the 16x the program has averaged, proceeds retire
debt at about 6%, which saves about what the EBITDA earned.

Net interest: 2026 is $215M including about $13M of the $30M annual headwind
from the $1.5B of 2026 refinancing (call: debt at the low 4s replaced in the six
to low sixes); 2027 adds the other $17M. 2028 notes ($725M at 5.88%, October
2028) and 2029 notes ($750M at 4.88%, May 2029) refinance at case-specific rates.
$1.7B is floating at SOFR + 2.20-2.25%.

Exit P/FFO (on Adjusted FFO): bear 5.5x, base 7.5x, bull 9.0x. PK's own
year-end multiples on reported Adjusted FFO were 6.8x at end-2024 ($14.07 on
$2.06) and 5.3x at end-2025 ($10.46 on $1.97); today it is 7.85x on the 2026
guide midpoint, after the whole lodging group rerated in 2026 (end-2025 to
October 2026 closes: PK +59%, HST +43%, SHO +43%, PEB +90%). The base holds
close to today because leverage falls a turn, from 5.8x to about 4.8x EBITDA,
but stays a little below it because $1.7B floats and 4.8x is still above the
4x-or-less the lower-levered peers carry; the bull's 9.0x assumes deleveraging
toward 4x and growth that moves PK toward HST (7.9x net income plus D&A per
share at end-2025, about 11x at October 2026; neither is Adjusted FFO).

Dividends: $0.25 a quarter held in base and bull. In the bear the board cuts
the regular dividend to $0.18 from the October 2027 payment (declared about July
2027) with a 50% chance: EBITDA below the 2026 level, net debt near 5.7x EBITDA
and $1.5B of notes due in 2028-2029, though bear FCF still covers the $0.25
about 1.0x. The regular $0.25 has been unchanged since 2024; the higher 2024
total ($1.40) included special dividends (dividends payable $138M at end-2024
against $56M at end-2025), so it is not a precedent for a cut. Bear dividends
are the weighted value; the chance of a cut declared in 2027 is 0.30 x 0.50 =
0.15.

Interest on the 2028 notes ($725M at 5.88%, October 2028) and 2029 notes ($750M
at 4.88%, May 2029) repriced at r adds 725 x (r - 5.88%) + 750 x (r - 4.88%) x 8/12
to 2029. Base: 2027 is 2026's $215M plus the remaining $17M of the 2026
refinancing headwind ($232M); 2028 is $2M lower on spread relief as leverage
falls ($230M); 2029 adds $12.6M at r near 6.5% ($243M). Bear: 2027 and 2028 are
each about $4M above the base path on the $1.7B of floating debt (about 25bp
more of SOFR and spread, and no spread relief) ($236M / $240M); 2029 adds about
$28M over 2027 at r near 7.75% ($264M). Bull: leverage near 4.2x steps the
spread grid down ($222M / $218M); 2029 adds about $6.5M at r near 6.0%, the
bottom of the "six to low sixes" the CFO gave for new debt ($225M).

The net debt path carries no Non-Core sale proceeds: the timing is unknown and
the sales are modeled as neutral to Adjusted FFO, but each sale would lower net
debt (at 16x, the four smaller hotels' $14M of EBITDA is about $224M). The path
is year-end only; quarterly seasonality is not modeled.

Opening net debt: Net Debt was $3,725M at September 30. Q4 2026 Adjusted FFO
(guide implies about $98M) less the rest of the 2026 capex budget (about $70M)
less the dividend paid October 15 (about $50M) raises it about $20M, offset by
about $19M of proceeds from The Wade sale, so the model starts end-2026 at
$3,730M.

Free cash flow (net debt path only) = Adjusted FFO - capital expenditure
(2026 $270-280M; 2027 onward $175-185M per the call). Rows after 2029
extrapolate: organic growth moves linearly to a terminal rate and interest
holds at its 2029 level.
"""

PRICE = 15.89  # 2026-11-25 close
SHARES0 = 201.0  # diluted shares in the FY2026 Adjusted FFO guide (M); Q3 count 202, GAAP diluted 200, outstanding 202.08
EBITDA_2026 = 640.0  # FY2026 Adjusted EBITDA guide midpoint ($635-$645M)
AFFO_2026 = 2.025  # FY2026 Adjusted FFO per diluted share guide midpoint ($2.00-$2.05)
NET_DEBT_2026 = 3730.0  # Sep 30 Net Debt $3,725M (incl. $105M JV share); derivation in the docstring
OTHER = 18.0  # calibrated to the FY2026 guide: taxes, NCI and JV items between Adjusted EBITDA less net interest and Adjusted FFO
DPS_Q = 0.25
YEARS = list(range(2027, 2037))

CASES = {
    # organic Adjusted EBITDA growth 2027-2029, cumulative Royal Palm and Hawaii increments ($M) 2027-2029,
    # net interest 2027-2029 ($M), share drift, quarterly dividend from the October 2027 payment,
    # capex 2027-2029, exit P/FFO, terminal organic growth, weight
    "bear": dict(g=[-0.04, -0.02, 0.02], rp=[8, 14, 18], hi=[0, 10, 15], intr=[236, 240, 264], drift=0.005,
                 dps_cut=0.18, cut_prob=0.5, capex=[175, 175, 175], pffo=5.5, g_term=0.01, weight=0.30),
    "base": dict(g=[0.02, 0.02, 0.02], rp=[11, 21, 25], hi=[10, 20, 30], intr=[232, 230, 243], drift=0.005,
                 dps_cut=None, capex=[180, 180, 180], pffo=7.5, g_term=0.02, weight=0.50),
    "bull": dict(g=[0.04, 0.04, 0.035], rp=[11, 24, 28], hi=[20, 45, 60], intr=[222, 218, 225], drift=0.005,
                 dps_cut=None, capex=[185, 185, 185], pffo=9.0, g_term=0.025, weight=0.20),
}


def path(c):
    rows, organic, sh, nd = [], EBITDA_2026, SHARES0, NET_DEBT_2026
    prev = EBITDA_2026
    for i, y in enumerate(YEARS):
        if i < 3:
            g, extra, intr, capex = c["g"][i], c["rp"][i] + c["hi"][i], c["intr"][i], c["capex"][i]
        else:
            g = c["g"][2] + (c["g_term"] - c["g"][2]) * (i - 2) / 7
            extra, intr, capex = c["rp"][2] + c["hi"][2], c["intr"][2], c["capex"][2]
        organic *= 1 + g
        ebitda = organic + extra
        affo = ebitda - intr - OTHER
        sh *= 1 + c["drift"]
        dps = annual_dividend(c, y)
        fcf = affo - capex
        nd += dps * sh - fcf
        rows.append(dict(year=y, ebitda=ebitda, growth=ebitda / prev - 1, intr=intr, affo=affo, sh=sh,
                         affo_ps=affo / sh, fcf=fcf, dps=dps, nd=nd))
        prev = ebitda
    return rows


def annual_dividend(c, y):
    """Cash dividends paid in calendar year y. A bear cut starts with the October 2027 payment."""
    if c["dps_cut"] is None:
        return 4 * DPS_Q
    p = c.get("cut_prob", 1.0)
    cut = 3 * DPS_Q + c["dps_cut"] if y == 2027 else 4 * c["dps_cut"]
    return (1 - p) * 4 * DPS_Q + p * cut


def dividends(c, dps_cut="case"):
    """Dividends paid from January 2027 through October 2029 (12 payments), probability-weighted."""
    cut, p = (c["dps_cut"], c.get("cut_prob", 1.0)) if dps_cut == "case" else (dps_cut, 1.0)
    if cut is None:
        return 12 * DPS_Q
    return (1 - p) * 12 * DPS_Q + p * (3 * DPS_Q + 9 * cut)


def value(c, rows, pffo=None, dps_cut="case"):
    pffo = pffo or c["pffo"]
    return rows[2]["affo_ps"] * pffo + dividends(c, dps_cut)


def weighted(vals, weights):
    return sum(weights[k] * vals[k] for k in vals)


def ann(v):
    return (v / PRICE) ** (1 / 3) - 1


def main():
    vals, price_only = {}, {}
    for name, c in CASES.items():
        rows = path(c)
        v = value(c, rows)
        vals[name] = round(v, 2)
        r = rows[2]
        price_only[name] = r["affo_ps"] * c["pffo"]
        cagr = (r["ebitda"] / EBITDA_2026) ** (1 / 3) - 1
        affo_cagr = (r["affo_ps"] / AFFO_2026) ** (1 / 3) - 1
        cover = [x["fcf"] / (x["dps"] * x["sh"]) for x in rows[:3]]
        ev_mult = (PRICE * SHARES0 + NET_DEBT_2026) / EBITDA_2026
        ev_cross = (r["ebitda"] * {"bear": 9.0, "base": 10.5, "bull": 12.0}[name] - r["nd"]) / r["sh"] + dividends(c)
        print(f"{name}: 2029 Adj EBITDA {r['ebitda']:,.0f} (2026-29 CAGR {cagr:+.1%}), net interest {r['intr']:.0f}, "
              f"Adj FFO {r['affo']:,.0f}, shares {r['sh']:.1f}, Adj FFO/share 2027-29 "
              f"{rows[0]['affo_ps']:.2f}/{rows[1]['affo_ps']:.2f}/{r['affo_ps']:.2f} (CAGR {affo_cagr:+.1%}) "
              f"x {c['pffo']} = {price_only[name]:.2f} + dividends {dividends(c):.2f} = ${v:.2f} "
              f"({ann(v):+.1%} a year); FCF/dividend 2027-29 {cover[0]:.2f}/{cover[1]:.2f}/{cover[2]:.2f}; "
              f"end-2029 net debt {r['nd']:,.0f} ({r['nd'] / r['ebitda']:.1f}x EBITDA); "
              f"EV/EBITDA cross-check (9.0x/10.5x/12.0x) plus dividends ${ev_cross:.2f}; "
              f"exit P/FFO implies {(price_only[name] * r['sh'] + r['nd']) / r['ebitda']:.1f}x end-2029 EV/EBITDA; "
              f"end-2027 net debt {rows[0]['nd']:,.0f}")
    print(f"current EV/EBITDA on the 2026 guide: {(PRICE * SHARES0 + NET_DEBT_2026) / EBITDA_2026:.1f}x; "
          f"P/FFO on the 2026 guide {PRICE / AFFO_2026:.2f}x")
    w = {k: c["weight"] for k, c in CASES.items()}
    fv = round(weighted(vals, w), 2)
    print(f"\nweighted fair value ${fv:.2f} ({ann(fv):+.1%} a year from ${PRICE}); price-only weighted "
          f"${weighted(price_only, w):.2f}; Own below ${fv / 1.15 ** 3:.2f}, Avoid above ${fv:.2f}")

    print("\nsensitivities")
    for label, ww in [("40/45/15", dict(bear=0.40, base=0.45, bull=0.15)),
                      ("50/40/10", dict(bear=0.50, base=0.40, bull=0.10)),
                      ("25/50/25", dict(bear=0.25, base=0.50, bull=0.25))]:
        f = weighted(vals, ww)
        print(f"  weights {label}: ${f:.2f} ({ann(f):+.1%})")
    base = CASES["base"]
    for pffo in (6.5, 7.0, 7.85, 8.5):
        v2 = dict(vals, base=value(base, path(base), pffo=pffo))
        f = weighted(v2, w)
        print(f"  base exit P/FFO {pffo}x: base ${v2['base']:.2f}, fair value ${f:.2f} ({ann(f):+.1%})")
    c2 = dict(base, hi=[0, 0, 0])
    v2 = dict(vals, base=value(c2, path(c2)))
    f = weighted(v2, w)
    print(f"  base with no Hawaii recapture: base ${v2['base']:.2f}, fair value ${f:.2f} ({ann(f):+.1%})")
    c2 = dict(base, g=[0.0, 0.0, 0.0])
    v2 = dict(vals, base=value(c2, path(c2)))
    f = weighted(v2, w)
    print(f"  base with 0% organic growth: base ${v2['base']:.2f}, fair value ${f:.2f} ({ann(f):+.1%})")
    c2 = dict(base, intr=[x + 20 for x in base["intr"]])
    v2 = dict(vals, base=value(c2, path(c2)))
    f = weighted(v2, w)
    print(f"  base net interest +$20M a year: base ${v2['base']:.2f}, fair value ${f:.2f} ({ann(f):+.1%})")
    v2 = dict(vals, base=value(base, path(base), dps_cut=0.18))
    f = weighted(v2, w)
    print(f"  base dividend cut to $0.18 from October 2027: base ${v2['base']:.2f}, fair value ${f:.2f}")
    r = path(base)[2]
    print(f"  base exit P/FFO that returns the price with dividends: {(PRICE - dividends(base)) / r['affo_ps']:.2f}x")

    for name, c in CASES.items():
        rows = path(c)
        anchor = vals[name] / rows[2]["affo_ps"]  # year-3 price equals the call value, dividends included
        print(f"\n### {name.capitalize()} (terminal P/FFO anchor {anchor:.2f}x, held from year 1)\n")
        print("| Years Out | Year | Adj. EBITDA ($M) | EBITDA Growth YoY | Net Interest ($M) | Adj. FFO ($M) "
              "| Adj. FFO/Share | FCF Yield | Stock Price | P/FFO | CAGR From Current |")
        print("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for n in (1, 2, 3, 5, 10):
            r = rows[n - 1]
            px = r["affo_ps"] * anchor
            print(f"| {n} | {r['year']} | {r['ebitda']:,.0f} | {r['growth']:+.1%} | {r['intr']:.0f} | "
                  f"{r['affo']:,.0f} | {r['affo_ps']:.2f} | {r['fcf'] / (px * r['sh']):.1%} | ${px:,.2f} | "
                  f"{anchor:.2f}x | {(px / PRICE) ** (1 / n) - 1:+.1%} |")


if __name__ == "__main__":
    main()
