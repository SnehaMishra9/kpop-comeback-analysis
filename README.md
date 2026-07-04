# Comeback Momentum, Chart Re-Entry, and Fandom Intensity Analysis of South Korea Top 50 Playlist

## Project Description

Unlike Western music markets — where success is largely measured by sustained
chart longevity — South Korea's K-Pop ecosystem is driven by **repeated momentum
bursts**: strong fandom-driven streaming behavior, frequent comeback cycles, and
songs that re-enter the charts multiple times around promotions, anniversaries,
and events.

This project analyzes 554 days (Jan 2024 – Dec 2025) of daily Top 50 playlist
snapshot data to uncover:

- Which songs experience multiple chart re-entries, and how often
- How comeback momentum differs from organic first-time popularity
- How long momentum spikes last after a re-entry, and how fast they decay
- Whether singles or album tracks benefit more from fandom-driven pushes
- How explicit vs. clean content behaves in a fandom-centric market

Built for **Atlantic Recording Corporation**, this project delivers a
momentum-and-re-entry framework that global labels can use to understand
K-Pop-specific engagement mechanics — insights that standard Western chart
analytics (built for gradual, linear popularity growth) fail to capture.

## What's Inside

- **Data pipeline**: cleaning, re-entry detection, momentum spike measurement,
  sustainability analysis, and content-attribute correlation (Python/Pandas)
- **KPIs**: Re-Entry Frequency, Momentum Spike Score, Post-Comeback Retention
  Days, Rank Recovery Speed, Album Comeback Advantage Index, Fandom Intensity
  Proxy Score
- **Interactive dashboard** (Streamlit + Plotly): re-entry timelines, momentum
  spike charts, first-entry vs. re-entry comparisons, content-attribute
  analysis, and a fandom-intensity leaderboard — filterable by date, artist,
  song, re-entry count, and album type

## Tech Stack
Python · Pandas · NumPy · Plotly · Streamlit

## How to Run Locally
```
pip install -r requirements.txt
streamlit run app.py
```

## Live Dashboard
[Add your Streamlit Cloud URL here after deployment]

## Data Source
Daily South Korea Top 50 playlist snapshots (Spotify-derived metadata):
date, rank, song, artist, popularity, duration, album type, track count,
explicit flag.

## Data Quality Notes
- Jan–Apr 2024: sparse sampling (only days 6–12 of each month captured)
- 3 Jan 2025: removed due to an overlapping duplicate playlist snapshot in source data
- 26 songs had inconsistent `album_type` metadata across snapshots (resolved
  using the most frequent value per song)
