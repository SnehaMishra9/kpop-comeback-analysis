"""
Comeback Momentum, Chart Re-Entry, and Fandom Intensity Dashboard
South Korea Top 50 Playlist Analysis

To run:
    pip install streamlit pandas plotly
    streamlit run app.py

Make sure these files are in the SAME folder as app.py:
    - cleaned_data.csv
    - combined_analysis.csv
    - final_kpi_table.csv
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="K-Pop Comeback & Fandom Intensity Dashboard", layout="wide")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    raw = pd.read_csv("cleaned_data.csv", parse_dates=["date"])
    runs = pd.read_csv("combined_analysis.csv", parse_dates=["entry_date", "exit_date"])
    kpi = pd.read_csv("final_kpi_table.csv")
    return raw, runs, kpi

raw_df, runs_df, kpi_df = load_data()

st.title("🎵 Comeback Momentum, Chart Re-Entry & Fandom Intensity")
st.caption("South Korea Top 50 Playlist Analysis — Atlantic Recording Corporation")

# ---------------------------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

min_date, max_date = raw_df["date"].min(), raw_df["date"].max()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

artist_options = sorted(raw_df["artist"].unique())
selected_artists = st.sidebar.multiselect("Artist", artist_options)

song_options = sorted(raw_df["song"].unique())
if selected_artists:
    song_options = sorted(raw_df[raw_df["artist"].isin(selected_artists)]["song"].unique())
selected_songs = st.sidebar.multiselect("Song", song_options)

min_reentry, max_reentry = int(kpi_df["total_reentries"].min()), int(kpi_df["total_reentries"].max())
reentry_range = st.sidebar.slider("Re-entry count", min_reentry, max_reentry, (min_reentry, max_reentry))

album_type_options = ["All"] + sorted(kpi_df["album_type"].dropna().unique().tolist())
album_type_filter = st.sidebar.radio("Album type", album_type_options)

explicit_filter = st.sidebar.radio("Content", ["All", "Clean only", "Explicit only"])

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
kpi_filtered = kpi_df[
    (kpi_df["total_reentries"] >= reentry_range[0]) & (kpi_df["total_reentries"] <= reentry_range[1])
]
if album_type_filter != "All":
    kpi_filtered = kpi_filtered[kpi_filtered["album_type"] == album_type_filter]
if explicit_filter == "Clean only":
    kpi_filtered = kpi_filtered[kpi_filtered["is_explicit"] == False]
elif explicit_filter == "Explicit only":
    kpi_filtered = kpi_filtered[kpi_filtered["is_explicit"] == True]
if selected_artists:
    kpi_filtered = kpi_filtered[kpi_filtered["artist"].isin(selected_artists)]
if selected_songs:
    kpi_filtered = kpi_filtered[kpi_filtered["song"].isin(selected_songs)]

runs_filtered = runs_df.copy()
if len(date_range) == 2:
    runs_filtered = runs_filtered[
        (runs_filtered["entry_date"] >= pd.Timestamp(date_range[0]))
        & (runs_filtered["entry_date"] <= pd.Timestamp(date_range[1]))
    ]
if selected_artists:
    runs_filtered = runs_filtered[runs_filtered["artist"].isin(selected_artists)]
if selected_songs:
    runs_filtered = runs_filtered[runs_filtered["song"].isin(selected_songs)]

# ---------------------------------------------------------------------------
# Top KPI summary cards
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Songs (filtered)", f"{kpi_filtered.shape[0]:,}")
c2.metric("Total Re-Entries", f"{int(kpi_filtered['total_reentries'].sum()):,}")
c3.metric("Avg Momentum Spike", f"{kpi_filtered['avg_momentum_spike_score'].mean():.2f}")
c4.metric("Avg Fandom Intensity", f"{kpi_filtered['fandom_intensity_proxy_score'].mean():.2f}")

st.divider()

# ---------------------------------------------------------------------------
# Module 1: Re-entry Timeline Visualizer
# ---------------------------------------------------------------------------
st.subheader("📅 Re-Entry Timeline Visualizer")
st.write("Each bar shows one continuous chart 'stay' for a song. Gaps between bars = time off the chart.")

timeline_songs = selected_songs if selected_songs else kpi_filtered.sort_values(
    "total_reentries", ascending=False
)["song"].head(10).tolist()

timeline_data = runs_filtered[runs_filtered["song"].isin(timeline_songs)]
if not timeline_data.empty:
    fig_timeline = px.timeline(
        timeline_data,
        x_start="entry_date",
        x_end="exit_date",
        y="song",
        color="is_reentry",
        hover_data=["artist", "peak_rank", "momentum_intensity_score"],
        color_discrete_map={True: "#e74c3c", False: "#3498db"},
        labels={"is_reentry": "Is Re-Entry"},
    )
    fig_timeline.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_timeline, use_container_width=True)
else:
    st.info("No data for current filter selection.")

st.divider()

# ---------------------------------------------------------------------------
# Module 2: Momentum Spike Detection Chart
# ---------------------------------------------------------------------------
st.subheader("⚡ Momentum Spike Detection")
col1, col2 = st.columns(2)

with col1:
    top_spikes = runs_filtered.sort_values("momentum_intensity_score", ascending=False).head(15)
    fig_spike = px.bar(
        top_spikes,
        x="momentum_intensity_score",
        y="song",
        color="is_reentry",
        orientation="h",
        title="Top 15 Momentum Spikes",
        color_discrete_map={True: "#e74c3c", False: "#3498db"},
    )
    fig_spike.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_spike, use_container_width=True)

with col2:
    fig_scatter = px.scatter(
        runs_filtered,
        x="rank_jump_magnitude",
        y="popularity_change_rate",
        color="is_reentry",
        size="momentum_intensity_score",
        hover_data=["song", "artist"],
        title="Rank Jump vs Popularity Change Rate",
        color_discrete_map={True: "#e74c3c", False: "#3498db"},
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Module 3: Comeback vs First-Entry Comparison
# ---------------------------------------------------------------------------
st.subheader("🔁 Comeback vs First-Entry Comparison")
compare = runs_filtered.groupby("is_reentry").agg(
    avg_momentum=("momentum_intensity_score", "mean"),
    avg_retention=("days_retained_after_peak", "mean"),
    avg_rank_decay=("rank_decay_speed", "mean"),
    count=("run_id", "count"),
).reset_index()
compare["is_reentry"] = compare["is_reentry"].map({True: "Re-Entry", False: "First Entry"})

col3, col4 = st.columns(2)
with col3:
    fig_compare = px.bar(
        compare, x="is_reentry", y="avg_momentum", color="is_reentry",
        title="Avg Momentum: First Entry vs Re-Entry",
        color_discrete_map={"Re-Entry": "#e74c3c", "First Entry": "#3498db"},
    )
    st.plotly_chart(fig_compare, use_container_width=True)
with col4:
    fig_retention = px.bar(
        compare, x="is_reentry", y="avg_retention", color="is_reentry",
        title="Avg Post-Peak Retention Days: First Entry vs Re-Entry",
        color_discrete_map={"Re-Entry": "#e74c3c", "First Entry": "#3498db"},
    )
    st.plotly_chart(fig_retention, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Module 4: Content Attribute vs Momentum Analysis
# ---------------------------------------------------------------------------
st.subheader("🎛️ Content Attribute vs Momentum Analysis")
col5, col6 = st.columns(2)

with col5:
    album_compare = runs_filtered.groupby("album_type")["momentum_intensity_score"].mean().reset_index()
    fig_album = px.bar(
        album_compare, x="album_type", y="momentum_intensity_score",
        title="Avg Momentum: Single vs Album",
        color="album_type",
    )
    st.plotly_chart(fig_album, use_container_width=True)

with col6:
    explicit_compare = runs_filtered.groupby("is_explicit")["momentum_intensity_score"].mean().reset_index()
    explicit_compare["is_explicit"] = explicit_compare["is_explicit"].map({True: "Explicit", False: "Clean"})
    fig_explicit = px.bar(
        explicit_compare, x="is_explicit", y="momentum_intensity_score",
        title="Avg Momentum: Explicit vs Clean",
        color="is_explicit",
    )
    st.plotly_chart(fig_explicit, use_container_width=True)

fig_duration = px.scatter(
    runs_filtered, x="duration_min", y="momentum_intensity_score",
    color="album_type", hover_data=["song", "artist"],
    title="Song Duration vs Momentum Spike",
)
st.plotly_chart(fig_duration, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Module 5: Fandom Intensity Leaderboard
# ---------------------------------------------------------------------------
st.subheader("🏆 Fandom Intensity Leaderboard")
leaderboard = kpi_filtered.sort_values("fandom_intensity_proxy_score", ascending=False).head(20)
fig_leader = px.bar(
    leaderboard,
    x="fandom_intensity_proxy_score",
    y="song",
    color="artist",
    orientation="h",
    hover_data=["total_reentries", "avg_momentum_spike_score", "avg_post_comeback_retention_days"],
    title="Top 20 Songs by Fandom Intensity Proxy Score",
)
fig_leader.update_yaxes(autorange="reversed")
st.plotly_chart(fig_leader, use_container_width=True)

st.dataframe(
    kpi_filtered[
        ["song", "artist", "album_type", "is_explicit", "total_reentries",
         "avg_momentum_spike_score", "avg_post_comeback_retention_days",
         "fandom_intensity_proxy_score"]
    ].sort_values("fandom_intensity_proxy_score", ascending=False),
    use_container_width=True,
    height=400,
)

st.caption(
    "Data quality note: Jan–Apr 2024 has sparse sampling (only days 6–12 of each month). "
    "3 Jan 2025 was removed from the dataset due to a duplicate/overlapping playlist snapshot."
)
