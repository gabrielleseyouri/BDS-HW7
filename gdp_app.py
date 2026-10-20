from io import StringIO

import bs4
import pandas as pd
import plotly.express as px
import requests as rq
import streamlit as st

URL = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
# Older revision of the page that still has a "UN region" column
OLD_URL = ("https://en.wikipedia.org/w/index.php?"
           "title=List_of_countries_by_GDP_(nominal)&oldid=1187446467")
HEADERS = {"User-Agent": "Chrome"}

SOURCES = {"IMF": "IMF", "United Nations": "UN", "World Bank": "WorldBank"}

MISSING_REGIONS = {
    "Channel Islands": "Europe", "Isle of Man": "Europe", "Faroe Islands": "Europe",
    "Guam": "Oceania", "Northern Mariana Islands": "Oceania", "American Samoa": "Oceania",
    "U.S. Virgin Islands": "Americas", "Saint Martin": "Americas",
}


def get_gdp_table(url):
    page = rq.get(url, headers=HEADERS)
    soup = bs4.BeautifulSoup(page.text, "html.parser")
    table = [t for t in soup.find_all("table") if "IMF" in t.text][0]
    return pd.read_html(StringIO(str(table)))[0]


def find_col(df, prefix):
    """Find a column by its start, so footnote/year changes like
    'IMF (2026)[1]' -> 'IMF (2027)[2]' don't break the app."""
    return [c for c in df.columns if str(c).startswith(prefix)][0]


@st.cache_data(show_spinner="Scraping GDP data from Wikipedia...")
def load_data():
    gdp = get_gdp_table(URL)
    gdp = gdp[[find_col(gdp, "Country/Territory"), find_col(gdp, "IMF"),
               find_col(gdp, "World Bank"), find_col(gdp, "United Nations")]].copy()
    gdp.columns = ["Country", "IMF", "WorldBank", "UN"]

    for col in ["IMF", "WorldBank", "UN"]:
        gdp[col] = gdp[col].astype(str).str.split("(").str[0].str.replace(",", "")
        gdp[col] = pd.to_numeric(gdp[col], errors="coerce")

    gdp["Country"] = gdp["Country"].str.split("[").str[0].str.strip()
    gdp = gdp[gdp["Country"] != "World"]

    regions = get_gdp_table(OLD_URL)
    regions = regions[[("Country/Territory", "Country/Territory"),
                       ("UN region", "UN region")]].copy()
    regions.columns = ["Country", "Region"]
    regions["Country"] = regions["Country"].str.split("[").str[0].str.strip()
    regions = regions[regions["Country"] != "World"]

    dat = pd.merge(gdp, regions, on="Country", how="left")
    dat["Region"] = dat["Region"].fillna(dat["Country"].map(MISSING_REGIONS))
    return dat.dropna(subset=["Region"])


st.set_page_config(page_title="GDP by Region", layout="wide")
st.title("Nominal GDP by Region")
st.write("Country GDPs stacked within UN regions. Choose which source's "
         "estimates to display.")

dat = load_data()

source_label = st.radio("GDP source", list(SOURCES), horizontal=True)
col = SOURCES[source_label]

plot_dat = dat.dropna(subset=[col])

fig = px.bar(
    plot_dat, x="Region", y=col, color="Country",
    labels={col: "Nominal GDP (millions of US$)"},
    hover_data={col: ":,.0f"},
    title=f"Nominal GDP by Region ({source_label})",
)
fig.update_layout(showlegend=False, height=600)
fig.update_xaxes(categoryorder="total descending")

st.plotly_chart(fig, use_container_width=True)

total = plot_dat[col].sum() / 1e6
st.caption(f"{len(plot_dat)} countries with {source_label} data · "
           f"world total ≈ ${total:,.1f} trillion")