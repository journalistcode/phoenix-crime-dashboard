
# Enhanced Dash app for Phoenix crime data visualization
# Reads cleaned_crimes.csv.gz and provides interactive charts and summary cards.
import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Load data
DF_PATH = "cleaned_crimes.csv.gz"
df = pd.read_csv(DF_PATH, compression="gzip", parse_dates=["OCCURRED ON"], low_memory=False)
df["year"] = df["OCCURRED ON"].dt.year
df["month"] = df["OCCURRED ON"].dt.month
df["day"] = df["OCCURRED ON"].dt.day
df["hour"] = df["OCCURRED ON"].dt.hour

# Precompute aggregates used in controls
years = sorted(df["year"].dropna().unique().astype(int).tolist())
categories = sorted(df["UCR CRIME CATEGORY"].dropna().unique().tolist())
zips = sorted(df["ZIP"].dropna().unique().tolist())[:200]
grids = sorted(df["GRID"].dropna().unique().tolist())[:200]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

def make_stat_card(title, value, delta=None, subtitle=None):
    delta_markup = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        delta_markup = f"{arrow} {abs(delta):.1f}%"
    return html.Div([
        html.Div(title, style={"fontSize":"14px", "color":"#666"}),
        html.Div(str(value), style={"fontSize":"28px", "fontWeight":"600"}),
        html.Div(delta_markup, style={"fontSize":"12px", "color":"#333"}),
        html.Div(subtitle or "", style={"fontSize":"12px", "color":"#999"})
    ], style={
        "border":"1px solid #e6e6e6", "borderRadius":"8px", "padding":"12px", "width":"200px", "boxShadow":"2px 2px 6px rgba(0,0,0,0.03)"
    })

app.layout = html.Div([
    html.H2("Phoenix Crime Dashboard (Enhanced)"),
    html.Div([
        html.Div([
            html.Label("Year (for monthly view / filters)"),
            dcc.Dropdown(id="year-filter", options=[{"label": int(y), "value": int(y)} for y in years], value=max(years)),
            html.Label("Crime Category"),
            dcc.Dropdown(id="category-filter", options=[{"label": c, "value": c} for c in categories], multi=True, placeholder="All categories"),
            html.Label("ZIP (top 200)"),
            dcc.Dropdown(id="zip-filter", options=[{"label": z, "value": z} for z in zips], multi=True, placeholder="All ZIPs"),
            html.Label("GRID (top 200)"),
            dcc.Dropdown(id="grid-filter", options=[{"label": g, "value": g} for g in grids], multi=True, placeholder="All GRID"),
            html.Br(),
            html.Button("Reset Filters", id="reset-filters", n_clicks=0)
        ], style={"width":"26%", "display":"inline-block", "verticalAlign":"top", "padding":"12px"}),
        html.Div([
            html.Div(id="cards-row", style={"display":"flex", "gap":"12px", "flexWrap":"wrap"}),
            html.Br(),
            dcc.Graph(id="yearly-line"),
            dcc.Graph(id="monthly-trend"),
            dcc.Graph(id="category-bar"),
        ], style={"width":"70%", "display":"inline-block", "padding":"12px", "verticalAlign":"top"})
    ])
], style={"fontFamily":"Arial, sans-serif", "padding":"12px"})

# Helper to filter df based on filters
def filter_df(year=None, categories=None, zips=None, grids=None):
    dff = df
    if year is not None:
        dff = dff[dff["year"] == int(year)]
    if categories:
        dff = dff[dff["UCR CRIME CATEGORY"].isin(categories)]
    if zips:
        dff = dff[dff["ZIP"].isin(zips)]
    if grids:
        dff = dff[dff["GRID"].isin(grids)]
    return dff

@callback(
    Output("cards-row", "children"),
    Output("yearly-line", "figure"),
    Output("monthly-trend", "figure"),
    Output("category-bar", "figure"),
    Input("year-filter", "value"),
    Input("category-filter", "value"),
    Input("zip-filter", "value"),
    Input("grid-filter", "value"),
    Input("reset-filters", "n_clicks")
)
def update_dashboard(year, categories, zips, grids, reset_clicks):
    # Apply filters for the cards (cards should reflect currently selected filters overall)
    filtered = filter_df(None, categories, zips, grids)  # cards show totals across years with current filters (except year)
    total_all = len(filtered)
    # For YOY comparison, compute total for selected year and previous year
    this_year = int(year) if year is not None else max(years)
    prev_year = this_year - 1
    total_this_year = len(filter_df(this_year, categories, zips, grids))
    total_prev_year = len(filter_df(prev_year, categories, zips, grids))
    # compute percent change (handle zero prev)
    pct_change = ( (total_this_year - total_prev_year) / total_prev_year * 100.0 ) if total_prev_year not in (0, None) else None
    pct_change_val = pct_change if pct_change is not None else 0.0

    # Card: Total crimes (all years with filters)
    card_total = make_stat_card("Total (all years, filters)", f"{total_all:,}", subtitle="Count across all years with current filters")

    # Card: This year total & YoY change
    delta_display = pct_change_val if pct_change is not None else 0.0
    card_year = make_stat_card(f"Total in {this_year}", f"{total_this_year:,}", delta=delta_display, subtitle=f"Compared to {prev_year}")

    # Card: Top category (current filters)
    top_cat = filtered["UCR CRIME CATEGORY"].value_counts().idxmax() if not filtered.empty else "N/A"
    top_cat_count = filtered["UCR CRIME CATEGORY"].value_counts().max() if not filtered.empty else 0
    card_topcat = make_stat_card("Top Category (filters)", f"{top_cat} ({top_cat_count:,})", subtitle="Most frequent category in selection")

    cards = [card_total, card_year, card_topcat]

    # Yearly line chart (multi-year trend) - show counts per year applying category/zip/grid filters (but not the year dropdown)
    yearly = filter_df(None, categories, zips, grids).groupby("year").size().reset_index(name="count").sort_values("year")
    fig_year = px.line(yearly, x="year", y="count", markers=True, title="Crimes per Year (with current filters)")
    fig_year.update_layout(xaxis=dict(dtick=1))

    # Monthly trend for the chosen year (applies all filters including year)
    monthly = filter_df(year, categories, zips, grids).groupby("month").size().reset_index(name="count").sort_values("month")
    if monthly.empty:
        monthly = pd.DataFrame({"month": list(range(1,13)), "count": [0]*12})
    else:
        # Ensure months 1..12 present
        monthly = monthly.set_index("month").reindex(range(1,13), fill_value=0).reset_index()
    fig_month = px.bar(monthly, x="month", y="count", title=f"Monthly counts in {year}", labels={"month":"Month", "count":"Count"})
    fig_month.update_layout(xaxis=dict(dtick=1))

    # Category bar chart (top categories for selected year and filters)
    cat_df = filter_df(year, categories, zips, grids)["UCR CRIME CATEGORY"].value_counts().reset_index()
    cat_df.columns = ["UCR CRIME CATEGORY", "count"]
    cat_df = cat_df.head(30)
    fig_cat = px.bar(cat_df, x="UCR CRIME CATEGORY", y="count", title=f"Top Categories in {year}", labels={"UCR CRIME CATEGORY":"Category"})
    fig_cat.update_layout(xaxis_tickangle=-45, height=500)

    return cards, fig_year, fig_month, fig_cat

# Optional: callback to reset filters (client-side JS would be ideal; here we rely on n_clicks to trigger)
# For simplicity, user can manually clear dropdowns; Reset button left for future clientside implementation.

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
