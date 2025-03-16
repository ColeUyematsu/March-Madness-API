import pandas as pd

# Load the CSV files
lower_ncaa_df = pd.read_csv("lower_ncaa_teams.csv")  # Contains "team-cleaned"
unique_ncaa_df = pd.read_csv("unique_ncaa_teams.csv")  # Contains "team"

# Print column names to verify
print("Lower NCAA Teams Columns:", lower_ncaa_df.columns.tolist())
print("Unique NCAA Teams Columns:", unique_ncaa_df.columns.tolist())

# Ensure correct column names
lower_ncaa_df.columns = lower_ncaa_df.columns.str.strip()
unique_ncaa_df.columns = unique_ncaa_df.columns.str.strip()

# Rename "team-cleaned" column in lower_ncaa_df for consistency
if "team-cleaned" in lower_ncaa_df.columns:
    lower_ncaa_df.rename(columns={"team-cleaned": "team_cleaned"}, inplace=True)

# Create a mapping dictionary
team_mapping = dict(zip(unique_ncaa_df["team"], lower_ncaa_df["team_cleaned"]))

# Save the mapping as a new CSV file
mapped_df = pd.DataFrame(list(team_mapping.items()), columns=["unique_ncaa_team", "lower_ncaa_team"])
mapped_df.to_csv("mapped_ncaa_teams.csv", index=False)

print("Mapping completed. File saved as mapped_ncaa_teams.csv")