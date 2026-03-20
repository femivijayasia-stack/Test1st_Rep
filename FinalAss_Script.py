import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Create app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# Read the wildfire data
df = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/Historical_Wildfires.csv"
)

# Extract month and year
df["Month"] = pd.to_datetime(df["Date"]).dt.month_name()
df["Year"] = pd.to_datetime(df["Date"]).dt.year

# Month order for proper display
month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# App layout
app.layout = html.Div(children=[
    html.H1(
        "Australia Wildfire Dashboard",
        style={
            "textAlign": "center",
            "color": "#503D36",
            "font-size": 26
        }
    ),

    html.Div([

        # Region selector
        html.Div([
            html.H2("Select Region:", style={"margin-right": "2em"}),
            dcc.RadioItems(
                id="region",
                options=[
                    {"label": "New South Wales", "value": "NSW"},
                    {"label": "Northern Territory", "value": "NT"},
                    {"label": "Queensland", "value": "QL"},
                    {"label": "South Australia", "value": "SA"},
                    {"label": "Tasmania", "value": "TA"},
                    {"label": "Victoria", "value": "VI"},
                    {"label": "Western Australia", "value": "WA"}
                ],
                value="NSW",
                inline=True
            )
        ], style={"margin": "20px"}),

        # Year selector
        html.Div([
            html.H2("Select Year:", style={"margin-right": "2em"}),
            dcc.Dropdown(
                id="year",
                options=[{"label": y, "value": y} for y in sorted(df["Year"].unique())],
                value=2005,
                clearable=False
            )
        ], style={"margin": "20px"}),

        # Statistics dropdown
        html.Div([
            html.H2("Select Statistics:", style={"margin-right": "2em"}),
            dcc.Dropdown(
                id="statistics",
                options=[
                    {"label": "Yearly Statistics", "value": "yearly"},
                    {"label": "Recession Period Statistics", "value": "recession"}
                ],
                value="yearly",
                clearable=False
            )
        ], style={"margin": "20px"}),

        # Output graphs
        html.Div(id="output-container", style={"margin": "20px"})

    ])
])

# Callback
@app.callback(
    Output("output-container", "children"),
    [
        Input("region", "value"),
        Input("year", "value"),
        Input("statistics", "value")
    ]
)
def reg_year_display(input_region, input_year, selected_statistics):

    region_data = df[df["Region"] == input_region]
    year_region_data = region_data[region_data["Year"] == input_year]

    # Yearly Statistics
    if selected_statistics == "yearly":
        est_data = (
            year_region_data.groupby("Month")["Estimated_fire_area"]
            .mean()
            .reindex(month_order)
            .reset_index()
        )

        fig1 = px.pie(
            est_data,
            values="Estimated_fire_area",
            names="Month",
            title=f"{input_region}: Monthly Average Estimated Fire Area in year {input_year}"
        )

        veg_data = (
            year_region_data.groupby("Month")["Count"]
            .mean()
            .reindex(month_order)
            .reset_index()
        )

        fig2 = px.bar(
            veg_data,
            x="Month",
            y="Count",
            title=f"{input_region}: Average Count of Pixels for Presumed Vegetation Fires in year {input_year}"
        )

        return html.Div([
            html.Div([
                dcc.Graph(figure=fig1)
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                dcc.Graph(figure=fig2)
            ], style={"width": "48%", "display": "inline-block", "float": "right"})
        ])

    # Recession Period Statistics
    elif selected_statistics == "recession":
        recession_years = [2001, 2002, 2008, 2009, 2010]
        recession_data = region_data[region_data["Year"].isin(recession_years)]

        # Graph 1: yearly average estimated fire area
        rec1 = (
            recession_data.groupby("Year")["Estimated_fire_area"]
            .mean()
            .reset_index()
        )

        fig1 = px.line(
            rec1,
            x="Year",
            y="Estimated_fire_area",
            markers=True,
            title=f"{input_region}: Average Estimated Fire Area during Recession Years"
        )

        # Graph 2: yearly average count of pixels
        rec2 = (
            recession_data.groupby("Year")["Count"]
            .mean()
            .reset_index()
        )

        fig2 = px.bar(
            rec2,
            x="Year",
            y="Count",
            title=f"{input_region}: Average Count of Pixels during Recession Years"
        )

        # Graph 3: monthly share of estimated fire area during recession period
        rec3 = (
            recession_data.groupby("Month")["Estimated_fire_area"]
            .mean()
            .reindex(month_order)
            .reset_index()
        )

        fig3 = px.pie(
            rec3,
            values="Estimated_fire_area",
            names="Month",
            title=f"{input_region}: Monthly Share of Estimated Fire Area during Recession Period"
        )

        # Graph 4: monthly average pixel count during recession period
        rec4 = (
            recession_data.groupby("Month")["Count"]
            .mean()
            .reindex(month_order)
            .reset_index()
        )

        fig4 = px.bar(
            rec4,
            x="Month",
            y="Count",
            title=f"{input_region}: Monthly Average Pixel Count during Recession Period"
        )

        return html.Div([
            html.Div([
                dcc.Graph(figure=fig1)
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                dcc.Graph(figure=fig2)
            ], style={"width": "48%", "display": "inline-block", "float": "right"}),

            html.Div([
                dcc.Graph(figure=fig3)
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                dcc.Graph(figure=fig4)
            ], style={"width": "48%", "display": "inline-block", "float": "right"})
        ])

if __name__ == "__main__":
    app.run(debug=True)