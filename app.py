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
        # Filter out expiration data for 2024
        df = df[df['Organization Type'] != 'Regional']
        
        df_il = pd.DataFrame([{col: None for col in df.columns}])
        df_il["District Name"] = "State of Illinois"
        df_il["Organization Type"] = "State of Illinois"
        df_il["Total ASE"] = 1789162.03
        df_il["Adequacy Funding Gap"] = 5679275708.44
        df_il["Final Adequacy Level"] = 0.843432139259095
        df_il["Adequacy Funding Gap (Per Pupil)"] = 3174.26572507801
        # Concatenate df and df_il
        df = pd.concat([df, df_il], ignore_index=True)
        return df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please ensure the CSV files are in the correct location.")
        return None
    

def main():    
    # Load data
    df=load_data()

    if df is None:
        return

    # Main app
    st.set_page_config(page_title="EBF Lookup", layout="centered")

    st.header("CTU's Illinois School District Funding Needs Lookup")

    st.subheader("This is a tool to quickly look up your district's funding needs.")

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

# Create a drop down menu that allows the user to select multiple school districts. Set CITY OF CHICAGO SCHOOL DIST 299 as default

    selected_district = st.selectbox("**Select School District**", options=df['District Name'].unique().tolist(), index=300)

    if not selected_district:
        st.warning("Please select at least one school district.")
        return

# filter selected districts
    filtered_df = df[df['District Name'] == str(selected_district)]

# Write a dynamic statement

    value = float(filtered_df['Final Adequacy Level'].values[0])

    st.subheader(f"{selected_district} is {value:.0%} funded.") 
    st.write("")
    st.subheader(f"This district needs \\${filtered_df['Adequacy Funding Gap'].values[0]:,.0f} to be adequately funded. That amounts to \\${filtered_df['Adequacy Funding Gap (Per Pupil)'].values[0]:,.0f} per student.")

    

#     numeric_cols = ["CPS Surplus Revenue"]
#     # Calculate min and max across all numeric columns (overall)
#     min_value = table[numeric_cols].min().min()
#     max_value = table[numeric_cols].max().max()

#     st.subheader(f"CPS TIF surplus revenue estimates:")
#     st.write(f"Minimum: ${min_value:,.0f}")
#     st.write(f"Maximum: ${max_value:,.0f}")
    
    
#     # Center the table using columns - make it a bit wider
#     col1, col2, col3 = st.columns([.5, 20, .5])
#     with col2:
#         # Try a different approach - format numbers but keep them sortable
#         st.dataframe(
#             table.style.format({
#                 "Surplus Amount": "${:,.0f}",
#                 "CPS Surplus Revenue": "${:,.0f}",
#                 "City of Chicago Surplus Revenue": "${:,.0f}"
#             }), 
#             use_container_width=True, 
#             hide_index=True
#         )
#     st.header("TIF Surplus Estimates for 2025 by District")

# # Create a filter to select by TIF district default

#     tif_districts = sorted(df['tif_name_comptroller_report'].unique())
    
#     selected_district = st.selectbox("Select TIF District", tif_districts)

#     filtered_df = df[(df['tif_name_comptroller_report'] == selected_district)]

#     # Create a table where rows are unallocated funds, City Surplus Method, Declared surplus (IL Comptroller data), and CTU methods 1,2, and 3
#     unallocated = filtered_df['unallocated_funds_2025'].values[0]
#     surplus_city = filtered_df['surplus_2025'].values[0]
#     ctu_method1 = filtered_df['full_surplus_avg_method_25'].values[0]
#     ctu_method2 = filtered_df['full_surplus_poly_method_25'].values[0]
#     ctu_method3 = filtered_df['full_surplus_weighted_method_25'].values[0]
    
#     unallocated_cps = unallocated * cps
#     surplus_city_cps = surplus_city * cps
#     ctu_method1_cps = ctu_method1 * cps
#     ctu_method2_cps = ctu_method2 * cps
#     ctu_method3_cps = ctu_method3 * cps
#     unallocated_chi = unallocated * chi
#     surplus_city_chi = surplus_city * chi
#     ctu_method1_chi = ctu_method1 * chi
#     ctu_method2_chi = ctu_method2 * chi
#     ctu_method3_chi = ctu_method3 * chi
    
#     table = pd.DataFrame({
#         "Surplus Method": ["Unallocated funds", "City surplus method", "CTU method 1", "CTU method 2", "CTU method 3"],
#         "Surplus Amount": [unallocated, surplus_city, ctu_method1, ctu_method2, ctu_method3],
#         "CPS Surplus Revenue": [unallocated_cps, surplus_city_cps, ctu_method1_cps, ctu_method2_cps, ctu_method3_cps],
#         "City of Chicago Surplus Revenue": [unallocated_chi, surplus_city_chi, ctu_method1_chi, ctu_method2_chi, ctu_method3_chi]
#     })

#     numeric_cols = ["CPS Surplus Revenue"]
#     # Calculate min and max across all numeric columns (overall)
#     min_value = table[numeric_cols].min().min()
#     max_value = table[numeric_cols].max().max()

#     st.subheader(f"CPS TIF surplus revenue estimates for {selected_district}:")
#     st.write(f"Minimum: ${min_value:,.0f}")
#     st.write(f"Maximum: ${max_value:,.0f}")
    
    
#     # Center the table using columns - make it a bit wider
#     col1, col2, col3 = st.columns([.5, 20, .5])
#     with col2:
#         # Try a different approach - format numbers but keep them sortable
#         st.dataframe(
#             table.style.format({
#                 "Surplus Amount": "${:,.0f}",
#                 "CPS Surplus Revenue": "${:,.0f}",
#                 "City of Chicago Surplus Revenue": "${:,.0f}"
#             }), 
#             use_container_width=True, 
#             hide_index=True
#         )
        
#     st.header("Top 5 TIF Districts with Largest Surplus Estimates")
# # Filter for top 5 districts

#     tif_districts = df['tif_name_comptroller_report'].unique()
    
#     # Filter for districts with the top 5 largest fully_surplus_poly_method_25 amounts
#     top5 = df.nlargest(5, 'full_surplus_poly_method_25')
    
#     # Filter for needed columns
#     filter_cols = ['tif_name_comptroller_report', 'expiration_date','unallocated_funds_2025', 
#                    'surplus_2025','full_surplus_avg_method_25','full_surplus_poly_method_25',
#                    'full_surplus_weighted_method_25']
    
#     top5 = top5[filter_cols]
    
#     # Rename columns for clarity
#     top5.rename(columns={
#         'tif_name_comptroller_report': 'TIF District',
#         'expiration_date': 'Expiration Date',
#         'unallocated_funds_2025': 'Unallocated Funds',
#         'surplus_2025': 'City Surplus Method',
#         'full_surplus_avg_method_25': 'CTU Method 1',
#         'full_surplus_poly_method_25': 'CTU Method 2',
#         'full_surplus_weighted_method_25': 'CTU Method 3'
#     }, inplace=True)
    
#     # Center the table using columns - make it a bit wider
#     col1, col2, col3 = st.columns([.5, 20, .5])
#     with col2:
#         # Calculate min and max BEFORE formatting
#         # Get all the numeric columns for min/max calculation
#         numeric_cols = ['Unallocated Funds', 'City Surplus Method', 'CTU Method 1', 'CTU Method 2', 'CTU Method 3']
        
        
#         # Calculate min and max for each row (each TIF district)
#         row_min = top5[numeric_cols].min(axis=1)
#         row_max = top5[numeric_cols].max(axis=1)
        
#         # Calculate CPS and City portions for each row's min/max
#         top5['CPS Min Surplus Revenue'] = row_min * cps
#         top5['CPS Max Surplus Revenue'] = row_max * cps
#         top5['Chicago Min Surplus Revenue'] = row_min * chi
#         top5['Chicago Max Surplus Revenue'] = row_max * chi
        
#         # Calculate min and max total across all numeric columns (overall)
#         min_value = top5['CPS Min Surplus Revenue'].sum()
#         max_value = top5['CPS Max Surplus Revenue'].sum()
        
#         st.subheader("CPS TIF surplus revenue estimates:")
#         st.write(f"Minimum: ${min_value:,.0f}")
#         st.write(f"Maximum: ${max_value:,.0f}")

#         # Try a different approach - format numbers but keep them sortable
#         # Formate the unallocated funds, surplus, and CTU methods as currency
#         top5['Unallocated Funds'] = top5['Unallocated Funds'].apply(lambda x: f"${x:,.0f}")
#         top5['City Surplus Method'] = top5['City Surplus Method'].apply(lambda x: f"${x:,.0f}")
#         top5['CTU Method 1'] = top5['CTU Method 1'].apply(lambda x: f"${x:,.0f}")
#         top5['CTU Method 2'] = top5['CTU Method 2'].apply(lambda x: f"${x:,.0f}")
#         top5['CTU Method 3'] = top5['CTU Method 3'].apply(lambda x: f"${x:,.0f}")
#         top5['CPS Min Surplus Revenue'] = top5['CPS Min Surplus Revenue'].apply(lambda x: f"${x:,.0f}")
#         top5['CPS Max Surplus Revenue'] = top5['CPS Max Surplus Revenue'].apply(lambda x: f"${x:,.0f}")
#         top5['Chicago Min Surplus Revenue'] = top5['Chicago Min Surplus Revenue'].apply(lambda x: f"${x:,.0f}")
#         top5['Chicago Max Surplus Revenue'] = top5['Chicago Max Surplus Revenue'].apply(lambda x: f"${x:,.0f}")

#         st.dataframe(top5,hide_index=True, use_container_width=True)

#     st.header("TIF Surplus Estimates by Ward")
# # Create a filter to select by TIF district default

#     # Change the tif_num column in df2 to match the format in df
    
#     df2 = df2.dropna(subset=['tif_num'])

#     df2['tif_num'] = df2['tif_num'].str[2:].astype(int)

#     df2['tif_num'] = df2['tif_num'].astype(str).str.strip()
    
#     df2['tif_num'] = "T-" + df2['tif_num'].str.zfill(3)

#     df3 = df.merge(df2, left_on='tif_num_ctu', right_on='tif_num', how='left')

#     # Drop missing values in 'ward_id' column
#     df3 = df3.dropna(subset=['ward_id'])
    
#     # Create a data set for export. 
#     # 1) First, multiply unallocated funds, surplus, and CTU methods by the CPS portion
#     # 2) Group by ward_id and sum the values for each ward
    
#     df3['unallocated_funds_rev_2025'] = df3['unallocated_funds_2025'] * cps
#     df3['surplus_rev_2025'] = df3['surplus_2025'] * cps
#     df3['full_surplus_avg_method_rev_25'] = df3['full_surplus_avg_method_25'] * cps
#     df3['full_surplus_poly_method_rev_25'] = df3['full_surplus_poly_method_25'] * cps
#     df3['full_surplus_weighted_method_rev_25'] = df3['full_surplus_weighted_method_25'] * cps
    
#     df4 = df3.groupby('ward_id').agg({
#         'unallocated_funds_2025': 'sum',
#         'surplus_2025': 'sum',
#         'full_surplus_avg_method_25': 'sum',
#         'full_surplus_poly_method_25': 'sum',
#         'full_surplus_weighted_method_25': 'sum',
#         'unallocated_funds_rev_2025': 'sum',
#         'surplus_rev_2025': 'sum',
#         'full_surplus_avg_method_rev_25': 'sum',
#         'full_surplus_poly_method_rev_25': 'sum',
#         'full_surplus_weighted_method_rev_25': 'sum'
#     }).reset_index()
    
#     # Format each column to be currency
#     df4['unallocated_funds_2025'] = df4['unallocated_funds_2025'].apply(lambda x: f"${x:,.0f}")
#     df4['surplus_2025'] = df4['surplus_2025'].apply(lambda x: f"${x:,.0f}")
#     df4['full_surplus_avg_method_25'] = df4['full_surplus_avg_method_25'].apply(lambda x: f"${x:,.0f}")
#     df4['full_surplus_poly_method_25'] = df4['full_surplus_poly_method_25'].apply(lambda x: f"${x:,.0f}")
#     df4['full_surplus_weighted_method_25'] = df4['full_surplus_weighted_method_25'].apply(lambda x: f"${x:,.0f}")    
#     df4['unallocated_funds_rev_2025'] = df4['unallocated_funds_rev_2025'].apply(lambda x: f"${x:,.0f}")
#     df4['surplus_rev_2025'] = df4['surplus_rev_2025'].apply(lambda x: f"${x:,.0f}")
#     df4['full_surplus_avg_method_rev_25'] = df4['full_surplus_avg_method_rev_25'].apply(lambda x: f"${x:,.0f}")
#     df4['full_surplus_poly_method_rev_25'] = df4['full_surplus_poly_method_rev_25'].apply(lambda x: f"${x:,.0f}")
#     df4['full_surplus_weighted_method_rev_25'] = df4['full_surplus_weighted_method_rev_25'].apply(lambda x: f"${x:,.0f}")
    
#     # Rename columns for clarity
#     df4.rename(columns={
#         'ward_id': 'Ward ID',
#         'unallocated_funds_2025': 'Surplus Est: Unallocated Funds',
#         'surplus_2025': 'Surplus est: City Surplus Method',
#         'full_surplus_avg_method_25': 'Surplus Est: CTU Method 1',
#         'full_surplus_poly_method_25': 'Surplus Est: CTU Method 2',
#         'full_surplus_weighted_method_25': 'Surplus Est: CTU Method 3',
#         'unallocated_funds_rev_2025': 'CPS Revenue Est: Unallocated Funds',
#         'surplus_rev_2025': 'CPS Revenue Est: City Surplus Method',
#         'full_surplus_avg_method_rev_25': 'CPS Revenue Est: CTU Method 1',
#         'full_surplus_poly_method_rev_25': 'CPS Revenue Est: CTU Method 2',
#         'full_surplus_weighted_method_rev_25': 'CPS Revenue Est: CTU Method 3'
#     }, inplace=True)

#     wards = sorted(df3['ward_id'].astype(int).unique())
    
#     # Convert ward_id to int for better display
#     df3['ward_id'] = df3['ward_id'].astype(int)
    
#     selected_wards = st.selectbox("Select a ward", wards)

#     filtered_df = df3[(df3['ward_id'] == selected_wards)]

#     # Filter for needed columns
#     filter_cols = ['tif_name_comptroller_report', 'tif_coverage','expiration_date','unallocated_funds_2025', 
#                    'surplus_2025','full_surplus_avg_method_25','full_surplus_poly_method_25',
#                    'full_surplus_weighted_method_25']
    
#     filtered_df = filtered_df[filter_cols]
    
#     # Rename columns for clarity
#     filtered_df.rename(columns={
#         'tif_name_comptroller_report': 'TIF District',
#         'tif_coverage': 'TIF Coverage',
#         'expiration_date': 'Expiration Date',
#         'unallocated_funds_2025': 'Unallocated Funds',
#         'surplus_2025': 'City Surplus Method',
#         'full_surplus_avg_method_25': 'CTU Method 1',
#         'full_surplus_poly_method_25': 'CTU Method 2',
#         'full_surplus_weighted_method_25': 'CTU Method 3'
#     }, inplace=True)
    
#     # Calculate min and max for each row (each TIF district)
#     row_min = filtered_df[numeric_cols].min(axis=1)
#     row_max = filtered_df[numeric_cols].max(axis=1)
        
#     # Calculate CPS and City portions for each row's min/max
#     filtered_df['CPS Min Surplus Revenue'] = row_min * cps
#     filtered_df['CPS Max Surplus Revenue'] = row_max * cps
#     filtered_df['Chicago Min Surplus Revenue'] = row_min * chi
#     filtered_df['Chicago Max Surplus Revenue'] = row_max * chi
    
#     # find min of CPS min and max
#     numeric_cols = ['CPS Min Surplus Revenue', 'CPS Max Surplus Revenue']
#     # Calculate min and max across all numeric columns (overall)
#     min_value = filtered_df['CPS Min Surplus Revenue'].sum().sum()
#     max_value = filtered_df['CPS Max Surplus Revenue'].sum().sum()

#     st.subheader(f"CPS TIF surplus revenue estimates for ward {selected_wards} range from:")
#     st.write(f"\\${min_value:,.0f} to \\${max_value:,.0f}")

#     # Center the table using columns - make it a bit wider
#     col1, col2, col3 = st.columns([.5, 20, .5])
#     with col2:
#         # Try a different approach - format numbers but keep them sortable
#         # Formate the unallocated funds, surplus, and CTU methods as currency
#         filtered_df['TIF Coverage'] = filtered_df['TIF Coverage'].apply(lambda x: f"{x:.0%}")
#         filtered_df['Unallocated Funds'] = filtered_df['Unallocated Funds'].apply(lambda x: f"${x:,.0f}")
#         filtered_df['City Surplus Method'] = filtered_df['City Surplus Method'].apply(lambda x: f"${x:,.0f}")
#         filtered_df['CTU Method 1'] = filtered_df['CTU Method 1'].apply(lambda x: f"${x:,.0f}")
#         filtered_df['CTU Method 2'] = filtered_df['CTU Method 2'].apply(lambda x: f"${x:,.0f}")
#         filtered_df['CTU Method 3'] = filtered_df['CTU Method 3'].apply(lambda x: f"${x:,.0f}")
#         filtered_df['CPS Min Surplus Revenue'] = filtered_df['CPS Min Surplus Revenue'].apply(lambda x: f"${x:,.0f}")
#         filtered_df['CPS Max Surplus Revenue'] = filtered_df['CPS Max Surplus Revenue'].apply(lambda x: f"${x:,.0f}")
#         filtered_df['Chicago Min Surplus Revenue'] = filtered_df['Chicago Min Surplus Revenue'].apply(lambda x: f"${x:,.0f}")
#         filtered_df['Chicago Max Surplus Revenue'] = filtered_df['Chicago Max Surplus Revenue'].apply(lambda x: f"${x:,.0f}")
#         st.dataframe(filtered_df,hide_index=True, use_container_width=True)
# # Download the data.csv file

#     # ensure df data is in currency
    
#     df['unallocated_funds_2025'] = df['unallocated_funds_2025'].apply(lambda x: f"${x:,.0f}")
#     df['surplus_2025'] = df['surplus_2025'].apply(lambda x: f"${x:,.0f}")
#     df['full_surplus_avg_method_25'] = df['full_surplus_avg_method_25'].apply(lambda x: f"${x:,.0f}")
#     df['full_surplus_poly_method_25'] = df['full_surplus_poly_method_25'].apply(lambda x: f"${x:,.0f}")
#     df['full_surplus_weighted_method_25'] = df['full_surplus_weighted_method_25'].apply(lambda x: f"${x:,.0f}")
    
#     # rename df columns for clarity
#     df.rename(columns={
#         'tif_name_comptroller_report': 'TIF District',
#         'tif_num_ctu': 'TIF Number',
#         'designation_date': 'Designation Date',
#         'expiration_date': 'Expiration Date',
#         'unallocated_funds_2025': 'Unallocated Funds',
#         'surplus_2025': 'City Surplus Method',
#         'full_surplus_avg_method_25': 'CTU Method 1',
#         'full_surplus_poly_method_25': 'CTU Method 2',
#         'full_surplus_weighted_method_25': 'CTU Method 3'
#     }, inplace=True)
    
#     st.header("Download Data")
#     st.markdown("You can download the full data used in this app as a CSV file.")
#     csv = df.to_csv(index=False)
#     csv_ward = df4.to_csv(index=False)

#     st.markdown("Download surplus estimates by TIF district")
#     st.download_button(
#         label="Download CSV",
#         data=csv,
#         file_name="tif_surplus_data.csv",
#         mime="text/csv"
#     )
    
#     st.markdown("Download surplus estimates by ward")
#     st.download_button(
#         label="Download CSV",
#         data=csv_ward,
#         file_name="tif_surplus_data_by_ward.csv",
#         mime="text/csv"
#     )


if __name__ == "__main__":
    main()