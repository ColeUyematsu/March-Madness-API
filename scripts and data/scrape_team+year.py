import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Define years to scrape
years = range(1991, 2025)  # 1991 to 2024

all_teams = []

for year in years:
    url = f"https://en.wikipedia.org/wiki/{year}_NCAA_Division_I_men%27s_basketball_tournament"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve data for {year}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find tables that likely contain team information
    tables = soup.find_all("table", {"class": "wikitable"})

    teams_data = []

    for table in tables:
        rows = table.find_all("tr")[1:]  # Skip header row

        for row in rows:
            cells = row.find_all(["th", "td"])  # Include both headers and data
            if len(cells) >= 4:
                try:
                    # Extract seed and clean it
                    seed_text = cells[0].text.strip().replace("#", "").replace("*", "")
                    if not seed_text or not seed_text[0].isdigit():
                        continue  # Skip rows without a valid seed

                    seed = int(seed_text)
                    if seed > 16:
                        continue

                    # Clean the team name by removing anything after "(vacated)"
                    team = re.sub(r"\(vacated.*$", "", cells[1].text.strip()).strip()

                    conference = cells[2].text.strip()

                    # Extract record (wins and losses)
                    record_text = cells[3].text.strip().replace("\n", "").replace("–", "-")
                    if "–" in record_text:
                        wins, losses = map(int, record_text.split("–"))
                    elif "-" in record_text:
                        wins, losses = map(int, record_text.split("-"))
                    else:
                        continue  # Skip if record is missing

                    teams_data.append({
                        "seed": seed,
                        "team": team,
                        "conference": conference,
                        "wins": wins,
                        "losses": losses,
                        "year": year
                    })
                except (ValueError, IndexError):
                    continue  # Skip rows that don’t match expected format

    if teams_data:
        all_teams.extend(teams_data)
        print(f"Scraped {len(teams_data)} teams for {year}")

# Convert to DataFrame
df = pd.DataFrame(all_teams)

# Save to CSV
csv_filename = "march_madness_1991_2024_cleaned.csv"
df.to_csv(csv_filename, index=False)

# Print confirmation
print(f"\nData saved to {csv_filename}")