import pandas as pd

# Read the Excel file
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# Convert to JSON (list of records)
json_data = df.to_json(orient="records", indent=4)

# Optionally save to a .json file
with open("data.json", "w") as f:
    f.write(json_data)

print(json_data)