/*´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•*/
/*                                                                                                            */
/*  Refcell Capital                                                                                           */
/*                                                                                                            */
/*  Deep Valuation Models.                                                                                    */
/*                                                                                                            */
/*  Not Financial Advice.                                                                                     */
/*                                                                                                            */
/*  https://refcell.substack.com                                                                              */
/*                                                                                                            */
/*´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•*/

THE LIBRARY

This repo is a research library and the store of record for its own data. Each
research run captures data once into committed, dated files; nothing downstream
re-fetches. Start at library/README.md.

  library/README.md         every covered company, its latest call, rule rating,
                            and how the call has done since
  library/<TICKER>.md       one page per company: current view, thesis, catalysts,
                            pre-mortem, kill criteria, SEC fundamentals as known on
                            the call date, earnings calendar, every dated call
  library/SCORECARD.md      calls marked against committed prices, by stance, rule
                            rating, and stated upside; Brier scores for claims
  library/BASE_RATES.md     five-year revenue growth base rates from SEC data, and
                            where each call's scenarios sit in them
  library/CALENDAR.md       estimated earnings releases and calls due an update
  research/<TICKER>.md      the full report; research/updates/<TICKER>/<date>.md
                            holds post-event updates
  data/<TICKER>/<date>/     call.json (stance, bear/base/bull, claims, ...),
                            inputs.json (every input with source and as-of date),
                            sources/ (saved pages and filings with SHA-256)
  data/calls.csv            ratings and price-target history, one row per call
  data/prices/              daily closes, append-only
  data/sec/                 point-in-time SEC XBRL facts and restatements
  data/calendar/            SEC earnings releases and periodic filings

RATINGS

Own: expected return of at least 15% a year over 3 years. Watch: 0% to 15%.
Avoid: below 0%. Benchmark: SPY. Thresholds live in capital/config.py.

COMMANDS

  python3 -m capital.validate     offline checks (CI runs these)
  python3 -m capital.build        regenerate data/calls.csv and library/
  python3 -m capital.next         today's task: an earnings update or a new name
  python3 -m capital.new T        scaffold a dated call from committed data
  python3 -m capital.pit T DATE   SEC fundamentals as known on DATE
  python3 -m capital.workbook T DATE   render models/T/DATE.xlsx from the data
  python3 -m capital.prices       capture closes      (network)
  python3 -m capital.sec          capture SEC data    (network; set CAPITAL_SEC_CONTACT)

The run procedure is .agents/skills/researching-companies/SKILL.md.
