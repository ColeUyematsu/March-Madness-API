import pandas as pd

# Load datasets
cleaned_df = pd.read_csv("march_madness_1991_2024_cleaned.csv")
sports_ref_df = pd.read_csv("march_madness_sports_reference.csv")

# Merge on 'team' and 'year'
merged_df = cleaned_df.merge(sports_ref_df, on=["team", "year"], how="left")

# Ensure 'wins' and 'losses' columns exist and convert to numeric
merged_df["wins"] = pd.to_numeric(merged_df["wins"], errors="coerce").fillna(0)
merged_df["losses"] = pd.to_numeric(merged_df["losses"], errors="coerce").fillna(0)

# Calculate win percentage and truncate to 3 decimals
merged_df["win_pct"] = (merged_df["wins"] / (merged_df["wins"] + merged_df["losses"])).fillna(0).round(3)


# Define the new column order
column_order = [
    "team", "conference", "seed", "wins", "losses", "year", "win_pct",
    "ps_per_game", "pa_per_game", "srs", "sos", "fg_per_game", "fga_per_game", "fg_pct", 
    "fg2_per_game", "fg2a_per_game", "fg2_pct", "fg3_per_game", "fg3a_per_game", "fg3_pct", 
    "ft_per_game", "fta_per_game", "ft_pct", "orb_per_game", "drb_per_game", "trb_per_game", 
    "ast_per_game", "stl_per_game", "blk_per_game", "tov_per_game", "pf_per_game", 
    "offensive_rating", "defensive_rating", "ncaa_wins", "ncaa_loss"
]

# Ensure all required columns exist, ignoring missing ones
existing_columns = [col for col in column_order if col in merged_df.columns]
merged_df = merged_df[existing_columns]

# Save the merged file
merged_df.to_csv("march_madness_merged.csv", index=False)

print("✅ Merging complete! 'conference' column removed, and saved as 'march_madness_merged.csv'.")