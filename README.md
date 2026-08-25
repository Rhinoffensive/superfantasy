# superfantasy

A Streamlit app for reviewing a private Yahoo Fantasy Basketball league —
9-category head-to-head — with views Yahoo does not provide.

**Fantasy data provided by [Yahoo Fantasy](https://basketball.fantasysports.yahoo.com/).**

## Views

- **Alternate Universe** — for a given week, compares a team's category totals
  against every other team in the league, not only its actual opponent, giving
  the expected win-loss-tie record it would have had against the full field.
- **Alternate Universe – Matchups** — the same comparison against one chosen
  opponent, across every week.
- **Power Rankings** — that expected record aggregated over the season, which
  ranks teams by performance rather than by schedule luck.
- **Medal Board** — gold, silver and bronze per category per week.
- **Box Plots** — the distribution of each category across the league.
- **Total Stats** — season totals per team.

Read-only. The app never writes to Yahoo — no roster moves, add/drops, trades,
or lineup changes.

## Setup

```bash
cp .env.example .env      # then fill in your Yahoo consumer key and secret
pip install -r requirements.txt
streamlit run app.py
```

Create an app at [developer.yahoo.com/apps](https://developer.yahoo.com/apps/)
with **Fantasy Sports → Read** permission. Note that as of August 2026 that
permission is no longer self-serve and requires an approved application at
[sports.yahoo.com/developer/access](https://sports.yahoo.com/developer/access/).

The first run opens a Yahoo consent URL; the token is then cached in `.cache/`
and refreshed automatically.

## Credentials

`.env` and `.cache/` are gitignored and must stay that way. **Never commit a
credentials file.** Earlier revisions of this repository committed
`oauth2.json` containing a live consumer secret and refresh token; the app now
refuses to start if it finds that file, to stop it happening again.
