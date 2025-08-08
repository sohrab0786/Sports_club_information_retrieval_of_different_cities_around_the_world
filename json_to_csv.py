import pandas as pd
import json

# Load JSON file
json_file = "Pune/venues_data.json"  # Update with your actual file name
csv_file = "Pune/Pune_venues_data.csv"
excel_file = "Pune/Pune_venues_data.xlsx"

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert JSON to DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv(csv_file, index=False, encoding="utf-8")
print(f"✅ JSON converted to CSV: {csv_file}")

# Save to Excel
df.to_excel(excel_file, index=False)
print(f"✅ JSON converted to Excel: {excel_file}")
