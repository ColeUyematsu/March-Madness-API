import pandas as pd

# Load the dataset
df = pd.read_csv("march_madness_1991_2024_cleaned.csv")  # Adjust filename if needed

# Extract unique team names
unique_teams = df["team"].unique()

# Convert to lowercase and replace spaces with dashes
formatted_teams = [team.lower().replace(" ", "-") for team in unique_teams]

# Convert to DataFrame
unique_teams_df = pd.DataFrame(formatted_teams, columns=["team"])

# Sort alphabetically
unique_teams_df = unique_teams_df.sort_values("team")

# Save to CSV
csv_filename = "lower_ncaa_teams.csv"
unique_teams_df.to_csv(csv_filename, index=False)

# Print confirmation
print(f"\n✅ Extracted {len(unique_teams_df)} unique teams that have made the tournament.")
print(f"✅ Data saved to {csv_filename}")

# Display first 10 teams as a preview
print(unique_teams_df.head(10))