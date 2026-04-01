import os
os.environ["DASH_JUPYTER"] = "false"

import pandas as pd
from sqlalchemy import create_engine
import dash
from dash import html
import datetime

# 🔹 DB Connection
DATABASE_URL = "mysql+pymysql://ocean_crawling:OceanCrawling%409812@13.204.140.150:3306/mnm"
engine = create_engine(DATABASE_URL)

# 🔹 Yesterday Date
yesterday = datetime.date.today() - datetime.timedelta(days=1)

# 🔹 Tables
tables = ["rb_pdp_week"]

# 🔹 Store Results
result = []

# 🔹 Fetch Data
for table in tables:
    query = f"""
    SELECT 
        '{table}' AS table_name,
        DATE(created_on) AS date,
        pf_id,
        COUNT(*) AS total_count
    FROM {table}
    WHERE DATE(created_on) = '{yesterday}'
    GROUP BY pf_id, DATE(created_on)
    ORDER BY pf_id
    """

    try:
        df = pd.read_sql(query, engine)

        if df.empty:
            result.append({
                "table": table,
                "date": str(yesterday),
                "pf_id": "-",
                "count": 0
            })
        else:
            for _, row in df.iterrows():
                result.append({
                    "table": row["table_name"],
                    "date": str(row["date"]),
                    "pf_id": row["pf_id"],
                    "count": int(row["total_count"])
                })

    except Exception as e:
        print(f"Error in {table}: {e}")

# 🔹 Dash App
app = dash.Dash(__name__)
server = app.server

# 🔹 Layout
app.layout = html.Div([

    html.H1("📊 Yesterday MNM Report", style={
        "textAlign": "center",
        "marginBottom": "30px"
    }),

    html.Div([
        html.Table([

            # Header
            html.Thead(
                html.Tr([
                    html.Th("Table"),
                    html.Th("Date"),
                    html.Th("PF_ID"),
                    html.Th("Count")
                ])
            ),

            # Body
            html.Tbody([
                html.Tr([
                    html.Td(r["table"]),
                    html.Td(r["date"]),
                    html.Td(r["pf_id"]),
                    html.Td(r["count"])
                ]) for r in result
            ])

        ])
    ], style={"display": "flex", "justifyContent": "center"})

], style={
    "fontFamily": "Arial",
    "backgroundColor": "#f4f6f8",
    "padding": "30px"
})

# 🔹 Styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>MNM Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            table {
                border-collapse: collapse;
                width: 60%;
                background-color: white;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            }
            th {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                text-align: center;
            }
            td {
                padding: 10px;
                text-align: center;
                border-bottom: 1px solid #ddd;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# 🔹 Run App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
