import requests
import pandas as pd
import time
import random
from unidecode import unidecode

# Load the Wikipedia dataset with teams (1985-2024)
teams_df = pd.read_csv("march_madness_1991_2024_cleaned.csv")  # Adjust filename if needed

# Load the mapping file
mapping_df = pd.read_csv("mapped_ncaa_teams.csv")  # Contains unique_ncaa_team → lower_ncaa_team
team_mapping = dict(zip(mapping_df["unique_ncaa_team"], mapping_df["lower_ncaa_team"]))

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

# Use a session to improve efficiency
session = requests.Session()
session.headers.update(HEADERS)

# Normalize team names for Sports-Reference URLs
def format_team_name(team):
    team = unidecode(team.lower())  # Convert to lowercase and remove accents
    team = team.replace(" ", "-").replace("&", "and")  # Format for URL
    return team

# Function to check for 404 errors
def check_team_page(team, year):
    formatted_team = team_mapping.get(team, format_team_name(team))
    url = f"https://www.sports-reference.com/cbb/schools/{formatted_team}/men/{year}.html"

    retries = 3  # Number of retry attempts for 429 errors
    while retries > 0:
        try:
            response = session.get(url, timeout=10)  # Timeout prevents hanging requests

            # Handle rate limit (429) by waiting & retrying
            if response.status_code == 429:
                wait_time = random.uniform(60, 90)  # Wait 1-1.5 minutes
                print(f"⚠ Rate Limited (429): Waiting {round(wait_time, 2)}s before retrying...")
                time.sleep(wait_time)
                retries -= 1
                continue  # Retry the request

            # Handle 404 errors
            if response.status_code == 404:
                print(f"🚫 404 Not Found: {team} ({year}) - {url}")
                return {"team": team, "year": year, "url": url}

            # Break out if successful
            break

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed for {team} ({year}) - {url}: {str(e)}")
            with open("error_log.txt", "a") as log_file:
                log_file.write(f"{team}, {year}, {url}, Error: {str(e)}\n")
            return None

    return None

# List to store missing teams
missing_teams = []

# Loop through every team in the dataset and check for 404 errors
for index, row in teams_df.iterrows():
    team = row["team"]
    year = row["year"]

    missing_entry = check_team_page(team, year)
    if missing_entry:
        missing_teams.append(missing_entry)

    # Avoid getting blocked (random delay between requests)
    time.sleep(random.uniform(5, 15))

# Save missing teams to a CSV file
missing_teams_df = pd.DataFrame(missing_teams)
csv_filename = "missing_ncaa_teams.csv"
missing_teams_df.to_csv(csv_filename, index=False)

# Print confirmation
print(f"\n✅ Logged {len(missing_teams)} missing teams to {csv_filename}")