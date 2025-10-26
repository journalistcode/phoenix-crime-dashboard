
# Streamlit app for Phoenix Crime Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

@st.cache_data
def load_data(path="cleaned_crimes.csv.gz"):
    df = pd.read_csv(path, compression="gzip", parse_dates=["OCCURRED ON"], low_memory=False)
    df["year"] = df["OCCURRED ON"].dt.year
    df["month"] = df["OCCURRED ON"].dt.month
    df["day"] = df["OCCURRED ON"].dt.day
    df["hour"] = df["OCCURRED ON"].dt.hour
    return df

df = load_data()

st.set_page_config(page_title="Phoenix Crime Dashboard", layout="wide")
st.title("Phoenix Crime Dashboard — Streamlit")

# Sidebar filters
st.sidebar.header("Filters")
years = sorted(df["year"].dropna().unique().astype(int).tolist())
selected_year = st.sidebar.selectbox("Year (for monthly view)", years, index=len(years)-1)

categories = sorted(df["UCR CRIME CATEGORY"].dropna().unique().tolist())
selected_cats = st.sidebar.multiselect("Crime Category (multi)", options=categories, default=None)

zips = sorted(df["ZIP"].dropna().unique().tolist())[:200]
selected_zips = st.sidebar.multiselect("ZIP (top 200)", options=zips, default=None)

grids = sorted(df["GRID"].dropna().unique().tolist())[:200]
selected_grids = st.sidebar.multiselect("GRID (top 200)", options=grids, default=None)

def filter_df(df, year=None, cats=None, zips=None, grids=None):
    dff = df
    if year is not None:
        dff = dff[dff["year"] == int(year)]
    if cats:
        dff = dff[dff["UCR CRIME CATEGORY"].isin(cats)]
    if zips:
        dff = dff[dff["ZIP"].isin(zips)]
    if grids:
        dff = dff[dff["GRID"].isin(grids)]
    return dff

# Top KPI row
col1, col2, col3, col4 = st.columns([1,1,1,1])
total_all = len(filter_df(df, None, selected_cats, selected_zips, selected_grids))
total_year = len(filter_df(df, selected_year, selected_cats, selected_zips, selected_grids))
prev_year = selected_year - 1
total_prev = len(filter_df(df, prev_year, selected_cats, selected_zips, selected_grids))
pct_change = ( (total_year - total_prev) / total_prev * 100.0 ) if total_prev not in (0, None) else None

col1.metric("Total (all years, current filters)", f"{total_all:,}")
if pct_change is None:
    col2.metric(f"Total in {selected_year}", f"{total_year:,}", delta="N/A")
else:
    delta_str = f"{pct_change:.1f}%"
    col2.metric(f"Total in {selected_year}", f"{total_year:,}", delta=delta_str)
# Top category and top ZIP
filtered_all = filter_df(df, None, selected_cats, selected_zips, selected_grids)
top_cat = filtered_all["UCR CRIME CATEGORY"].value_counts().idxmax() if not filtered_all.empty else "N/A"
top_cat_count = filtered_all["UCR CRIME CATEGORY"].value_counts().max() if not filtered_all.empty else 0
col3.metric("Top category (filters)", f"{top_cat}", delta=f"{top_cat_count:,}")
top_zip = filtered_all["ZIP"].value_counts().idxmax() if not filtered_all.empty else "N/A"
top_zip_count = filtered_all["ZIP"].value_counts().max() if not filtered_all.empty else 0
col4.metric("Top ZIP (filters)", f"{top_zip}", delta=f"{top_zip_count:,}")

st.markdown("---")

# Yearly trend (multi-year)
yearly = filter_df(df, None, selected_cats, selected_zips, selected_grids).groupby("year").size().reset_index(name="count").sort_values("year")
fig_year = px.line(yearly, x="year", y="count", markers=True, title="Crimes per Year (current filters)")
fig_year.update_layout(xaxis=dict(dtick=1))
st.plotly_chart(fig_year, use_container_width=True)

# Monthly trend for selected year
monthly = filter_df(df, selected_year, selected_cats, selected_zips, selected_grids).groupby("month").size().reset_index(name="count").sort_values("month")
if monthly.empty:
    monthly = pd.DataFrame({"month": list(range(1,13)), "count": [0]*12})
else:
    monthly = monthly.set_index("month").reindex(range(1,13), fill_value=0).reset_index()
fig_month = px.bar(monthly, x="month", y="count", title=f"Monthly counts in {selected_year}", labels={"month":"Month", "count":"Count"})
fig_month.update_layout(xaxis=dict(dtick=1))
st.plotly_chart(fig_month, use_container_width=True)

# Top categories (for selected year)
cat_df = filter_df(df, selected_year, selected_cats, selected_zips, selected_grids)["UCR CRIME CATEGORY"].value_counts().reset_index()
cat_df.columns = ["UCR CRIME CATEGORY", "count"]
cat_df = cat_df.head(30)
fig_cat = px.bar(cat_df, x="UCR CRIME CATEGORY", y="count", title=f"Top Categories in {selected_year}")
fig_cat.update_layout(xaxis_tickangle=-45, height=500)
st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("### Aggregates (download)")
st.write("You can download the prepared aggregates for offline analysis.")
csv1 = yearly.to_csv(index=False).encode("utf-8")
st.download_button("Download crimes-per-year CSV", data=csv1, file_name="agg_by_year.csv", mime="text/csv")

csv2 = cat_df.to_csv(index=False).encode("utf-8")
st.download_button("Download top-categories CSV", data=csv2, file_name=f"top_categories_{selected_year}.csv", mime="text/csv")

st.markdown("### Notes & Next steps")
st.write("- This dataset preserves detail. If you want maps, provide lat/lon or ask me to geocode addresses (may require API keys).")
st.write("- I can add more charts (heatmaps, rolling averages, normalization per 100k residents) if desired.")
