# %%
import streamlit as st
import pandas as pd
import numpy as np
import requests
import geopandas as gpd
from shapely.geometry import shape

# Load data
@st.cache_data
def load_data():
    """Load the EBF data"""
    try:
        df = pd.read_csv(r"data.csv")
        df2 = pd.read_csv(r"data_clean_names.csv")
        df3 = pd.read_csv(r"ift_iea_crosswalk.csv")
#        print(df2.columns)
#        print(df.columns)
#        print(df3.columns)
        # Filter out Organization Type Regional and Labs
        df = df[df['Organization Type'] != 'Regional']
        df = df[df['Organization Type'] != 'Labs']
        # Strip all column names
        df.columns = df.columns.str.strip()

        print(df.head())


        # Prep df2 columns RCD, TYP, and School to join

        df2["District ID"] = df2['RCD'].astype(str)+df2['Type'].astype(str).str.zfill(2)+df2['School'].astype(str).str[:-2]
        # Keep if RecType is Dist
        df2 = df2[df2['RecType'] == 'Dist']
        df2 = df2[["District ID", "FacilityName"]]

        # Prep IFT/IEA local crosswalk to join 

        df3["RCDT Code"] = df3["RCDT Code"].astype(str).apply(lambda x: x.zfill(11) if len(x) == 10 else x)

        df3["RCDT Code"] = df3["RCDT Code"]+"00"
        df3 = df3[["RCDT Code", "Local Affiliation"]]
        print(df3.head())

    
        
        df = df.merge(df2,on="District ID",how="left")
        df = df.merge(df3,left_on="District ID",right_on="RCDT Code",how="left")
        df = df.drop(columns="District ID")
        df = df.drop(columns="RCDT Code")
        # Make district name = facility name
        df["District Name"] = df["FacilityName"]
        df = df.drop(columns="FacilityName")

        df["Adequacy Funding Gap"] = pd.to_numeric(df["Adequacy Funding Gap"], errors="coerce")
        df["New FY26 Funding"] = pd.to_numeric(df["New FY26 Funding"], errors="coerce")

        # Update Adequacy Gaps and Levels to reflect Fy26 New Appropriation
        df["Adequacy Funding Gap"] = df["Adequacy Funding Gap"] - df["New FY26 Funding"]
        df["Adequacy Funding Gap (Per Pupil)"] = df["Adequacy Funding Gap"] / df["Total ASE"]
        df["Final Resources"] = df["Final Resources"] + df["New FY26 Funding"]
        df["Final Adequacy Level"] = df["Final Resources"] / df["Final Adequacy Target"]

        # Drop New FY26 Funding, Final Resources, and Final Adequacy Target

        df = df[['District Name', 'County', 'Organization Type', 'Total ASE',
       'Adequacy Funding Gap', 'Final Adequacy Level',
       'Adequacy Funding Gap (Per Pupil)', 'Local Affiliation']]

        
        df_il = pd.DataFrame([{
            "District Name": "State of Illinois",
            "Organization Type": "State of Illinois",
            "Total ASE": 1789162.03,
            "Adequacy Funding Gap": 5377769817.10,
            "Final Adequacy Level": 0.843432139259095,
            "Adequacy Funding Gap (Per Pupil)":  3005.75,
            "Local Affiliation": None
        }])
        # Concatenate df and df_il
        
        df = pd.concat([df, df_il], ignore_index=False)
        return df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please ensure the CSV files are in the correct location.")
        return None
#%%
def main():    
    # Load data
    df=load_data()

    if df is None:
        return

    # Main app

    st.write(df)
    st.set_page_config(page_title="EBF Lookup", layout="centered")

    st.header("CTU's Illinois School District Funding Needs Lookup")

    st.markdown("""
    This tool allows you to:
    
    - Look up funding needs by district and union affiliation;

    - Compare funding needs of multiple districts; and

    - View the State of Illinois' funding needs along with the top 10 most underfunded districts.
    """, unsafe_allow_html=True)

# Add a sidebar with methodology

    st.sidebar.header("Data source")
    st.sidebar.markdown("""
    The data comes from the Illinois State Board of Education's (ISBE's) [Evidence-Based Funding (EBF) distribution calculation FY26](https://www.isbe.net/ebfdist).

    The EBF distribution calcuation provides data on **adequacy funding gaps** and **final adequacy level** among other things.


    ---
    **ADEQUACY FUNDING GAP EXPLAINED**

    The **adequacy funding gap** refers to the gap between what a school district needs to be considered adequately funded (this is referred to as an **adequacy target**) and what districts have (this is referred to as **final resources**, which is local and state revenue). We provide the total and per pupil adequacy funding gap.

    The **adequacy target** is calculated by adding up all the resources a school district needs, such as teacher, nurses, counselors, technology and media equiptment, etc. The EBF formula provides additional funding based on need. It takes into account the additional resources necessary to teach low-income, English Learner, and SPED students. 

    >*Adequacy Funding Gap = Adequacy Target - Final Resources*

    If the adequacy target is positive it means your school district needs that much more funding.


    ---
    **FINAL ADEQUACY LEVEL EXPLAINED**

    **Final adequacy level** refers to the percent to the adequacy target. It is calculated by dividing **final resources** by **adequacy target** and multiplying by 100 to get a percentage.

    >*Final Adequacy Level = Final Resources / Adequacy Target X 100*

    If a school has an adequate funding level of 75% we would say X school district is 75% funded, in other words it has 75% of the funding it needs. 100% or above means that a district has above adequate funding.

    """)

    st.subheader("Look up by School District")

# Create a drop down menu that allows the user to select multiple school districts. Set CITY OF CHICAGO SCHOOL DIST 299 as default

    selected_district = st.selectbox("**Select School District**", options=df['District Name'].unique().tolist(), index=300)


    if not selected_district:
        st.warning("Please select at least one school district.")
        return

# filter selected districts
    filtered_df = df[df['District Name'] == str(selected_district)]

# Write a dynamic statement

    value = float(filtered_df['Final Adequacy Level'].values[0])
    if selected_district == "State of Illinois":
        st.write(f"The {selected_district} is {value:.0%} funded.")
    else:
        st.write(f"{selected_district} is {value:.0%} funded.")
    st.write("")
    if selected_district == "State of Illinois":
        st.write(f"The State of Illinois needs \\${filtered_df['Adequacy Funding Gap'].values[0]:,.0f} to adequately fund schools. That amounts to \\${filtered_df['Adequacy Funding Gap (Per Pupil)'].values[0]:,.0f} per student.")
    else:
        st.write(f"This district needs \\${filtered_df['Adequacy Funding Gap'].values[0]:,.0f} to be adequately funded. That amounts to \\${filtered_df['Adequacy Funding Gap (Per Pupil)'].values[0]:,.0f} per student.")
    if selected_district != "State of Illinois":
        if pd.isna(filtered_df['Local Affiliation'].values[0]):
            st.write(f"{selected_district} is not affiliated with any union.")
        else:
            st.markdown(f"""{selected_district} is affiliated with <b><span style="background-color: yellow">{filtered_df['Local Affiliation'].values[0]}</span></b>.""", unsafe_allow_html=True)

    st.subheader("Compare Multiple Districts")

    # Select multiple districts

    selected_districts = st.multiselect("**Select School Districts**", options=df['District Name'].unique().tolist(), default=["Chicago Public Schools District 299","State of Illinois"])

    if not selected_districts:
        st.warning("Please select at least one school district.")
        return

    # Filter selected districts
    filtered_dfs = df[df['District Name'].isin(selected_districts)]

    filtered_dfs = filtered_dfs[["District Name", "Adequacy Funding Gap", "Adequacy Funding Gap (Per Pupil)", "Final Adequacy Level"]]

    st.dataframe(
    filtered_dfs.style.format({
        "Adequacy Funding Gap": "${:,.0f}",
        "Adequacy Funding Gap (Per Pupil)": "${:,.0f}",
        "Final Adequacy Level": "{:.0%}"
    }),
    hide_index=True
)

    # SHow a table with the top 10 most underfunded school districts and Illinois
    # Sort by "Adequacy Funding Gap" most to least

    st.subheader("Underfunding in the State of Illinois and the Top 10 Most Underfunded School Districts in Illinois")

    top_10 = df.sort_values("Adequacy Funding Gap", ascending=False).head(10)

    top_10 = top_10[["District Name", "Adequacy Funding Gap", "Adequacy Funding Gap (Per Pupil)","Final Adequacy Level"]]

    def highlight_row(s):
        return ['background-color: yellow'] * len(s)

    st.dataframe(
        top_10.style.apply(lambda x: highlight_row(x) if x.name == 0 else ['']*len(x), axis=1).format({
            "Adequacy Funding Gap": "${:,.0f}",
            "Adequacy Funding Gap (Per Pupil)": "${:,.0f}",
            "Final Adequacy Level": "{:.0%}"
        }),
        hide_index=True
    )

if __name__ == "__main__":
    main()
# %%
