
# Phoenix Crime Dashboard - Package (CSV-based)

This package contains a cleaned extract of the Phoenix crime dataset and a Dash app skeleton ready to deploy.

## Files
- `cleaned_crimes.csv.gz` - cleaned dataset (gzip compressed)
- `agg_by_year.csv` - crimes per year
- `agg_by_year_type.csv` - crimes per year by category
- `agg_by_zip_top200.csv` - top 200 ZIPs by crime count
- `agg_by_grid_top200.csv` - top 200 GRIDs by crime count
- `app.py` - Dash app skeleton (reads the compressed CSV)
- `requirements.txt` - Python dependencies
- `Procfile` - for Render/Heroku style deployment

## Notes on cleaning
- `OCCURRED ON` and `UCR CRIME CATEGORY` were required; rows missing them were dropped.
- Date parts extracted: `year`, `month`, `day`, `hour`.
- ZIP codes standardized to 3-5 digit numeric strings where possible.
- String fields were stripped of whitespace.
- For detail-preserving work, most fields were kept; non-essential malformed rows were removed only when critical fields were missing.

## Deploying
1. Upload the `crime_dashboard_package` folder to your repository or hosting service.
2. For Render/Heroku:
   - Create a new web service, set Python runtime, and deploy.
   - Ensure `cleaned_crimes.csv.gz` stays in the same directory as `app.py`.
3. For larger scale or using geographic choropleths, consider enriching ZIPs with geo-centroids or shapefiles.

