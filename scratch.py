# %%
import pandas as pd

df = pd.read_csv(r"C:\Users\christopherpoulos\work\projects\ebf_lookup\data.csv")
df2 = pd.read_csv(r"C:\Users\christopherpoulos\work\projects\ebf_lookup\data_clean_names.csv")
print(df2.columns)
print(df.columns)
# Filter out Organization Type Regional and Labs
df = df[df['Organization Type'] != 'Regional']
df = df[df['Organization Type'] != 'Labs']
# Join df2 columns RCD, TYP, and School
# %%
df2["District ID"] = df2['RCD'].astype(str)+df2['Type'].astype(str).str.zfill(2)+df2['School'].astype(str).str[:-2]
# Keep if RecType is Dist
df2 = df2[df2['RecType'] == 'Dist']
df2 = df2[["District ID", "FacilityName"]]

print(df2.head())
# %%
df = df.merge(df2,on="District ID",how="left")
df = df.drop(columns="District ID")
# Make district name = facility name
df["District Name"] = df["FacilityName"]
df = df.drop(columns="FacilityName")
# %%
df_il = pd.DataFrame([{
    "District Name": "State of Illinois",
    "Organization Type": "State of Illinois",
    "Total ASE": 1789162.03,
    "Adequacy Funding Gap": 5679275708.44,
    "Final Adequacy Level": 0.843432139259095,
    "Adequacy Funding Gap (Per Pupil)": 3174.26572507801
}])
# Concatenate df and df_il
# %%
df = pd.concat([df, df_il], ignore_index=False)

#Drop the last column (final adequacy level keeps duplicating)
#df = df.iloc[:, :-1]
# %%
