import streamlit as st
import pybaseball as pb
import altair as alt
import pandas as pd
import datetime

# consts

# functions
def __preprocess(data: pd.DataFrame) -> pd.DataFrame:
    data = __preprocess_bonus(data)
    return data


def __preprocess_bonus(data: pd.DataFrame) -> pd.DataFrame:
    if len(data[data["Bonus"].isna() == False]) != 0:
        data["Bonus"] = data["Bonus"].str.replace("$", "", regex=False)
        data["Bonus"] = data["Bonus"].str.replace(",", "", regex=False)
    data["Type"] = data["Type"].fillna("UND")
    data = data.fillna(0)
    data["Bonus"] = data["Bonus"].astype(int)
    return data


@st.cache(suppress_st_warning=True)
def __get_draft(year: int, rud: int) -> pd.DataFrame:
    try:
        data = pb.amateur_draft(year, rud)
    except:
        return pd.DataFrame()
    return __preprocess(data)


# page config
st.set_page_config(
    page_title="DraftGraphs", layout="wide", initial_sidebar_state="expanded"
)

# page style
st.markdown(
    """
    <style>
    .css-1y0tads {
        padding: 0rem 5rem 10rem
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# page contents
st.title("DraftGraphs")
st.subheader("Created by [@hctaw_srp](https://twitter.com/hctaw_srp)")

## sidebar
st.sidebar.markdown("# :mag_right: Search Conditions")
st.sidebar.markdown("## :calendar: Year")
year = st.sidebar.number_input("", min_value=1965, max_value=datetime.date.today().year)
st.sidebar.markdown("## :1234: Round")
rud = st.sidebar.number_input("", min_value=1, max_value=50)

## body
if st.sidebar.button("Submit!"):
    data = __get_draft(year, rud)
    if len(data) == 0:
        st.error(
            f"Draft of Year={year} Round={rud} is not found. Please change your search conditions."
        )
    else:
        ### table
        st.dataframe(data)

        st.markdown("---")

        pos, classtype = st.beta_columns(2)
        ### position
        with pos:
            pos_chart = (
                alt.Chart(
                    data.groupby("Pos")
                    .count()
                    .reset_index()[["Pos", "OvPck"]]
                    .rename(columns={"OvPck": "Count"}),
                    title=f"{year} | Round {rud} | Position",
                )
                .mark_bar()
                .encode(x=alt.X("Pos", sort="ascending"), y="Count")
                .properties(height=400)
            )
            st.altair_chart(pos_chart, use_container_width=True)

        ### class type
        with classtype:
            classtype_chart = (
                alt.Chart(
                    data.groupby("Type")
                    .count()
                    .reset_index()[["Type", "OvPck"]]
                    .rename(columns={"OvPck": "Count"}),
                    title=f"{year} | Round {rud} | Class Type",
                )
                .mark_bar()
                .encode(x=alt.X("Type", sort="ascending"), y="Count")
                .properties(height=400)
            )
            st.altair_chart(classtype_chart, use_container_width=True)

        st.markdown("---")

        ### bonus and war
        point_chart = (
            alt.Chart(data, title=f"{year} | Round {rud} | Singing Bonus and WAR")
            .mark_circle()
            .encode(
                x=alt.X(
                    "Name", sort=alt.EncodingSortField(field="OvPck", order="ascending")
                ),
                y="Bonus:Q",
                size="WAR:Q",
                color="WAR:Q",
                tooltip=["Name", "Bonus", "WAR"],
            )
            .properties(height=400)
        )
        line_chart = (
            alt.Chart(data)
            .mark_line()
            .encode(
                x=alt.X(
                    "Name", sort=alt.EncodingSortField(field="OvPck", order="ascending")
                ),
                y="Bonus:Q",
            )
        )
        bonus_war_summary = point_chart + line_chart
        st.altair_chart(bonus_war_summary, use_container_width=True)
