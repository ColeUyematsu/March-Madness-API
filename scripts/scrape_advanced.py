import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from unidecode import unidecode
import re

# Load the dataset
input_csv = "march_madness_1991_2024_cleaned.csv"
teams_df = pd.read_csv(input_csv)

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

# Use a session for efficiency
session = requests.Session()
session.headers.update(HEADERS)

# Normalize team names for Sports-Reference URLs
def format_team_name(team):
    team = unidecode(team.lower())  # Convert to lowercase and remove accents
    team = team.replace(" ", "-").replace("&", "and")  # Format for URL
    return team

# Function to safely convert table values to float (handling empty values)
def safe_float(value):
    try:
        return float(value) if value.strip() else None  # Convert if non-empty, else None
    except ValueError:
        return None  # Handle non-numeric cases

# Function to scrape per-game and advanced stats from Sports-Reference
def scrape_team_stats(team, year):
    formatted_team = team_mapping.get(team, format_team_name(team))
    url = f"https://www.sports-reference.com/cbb/schools/{formatted_team}/men/{year}.html"

    retries = 3  # Number of retry attempts for 429 errors
    wait_time = 10  # Initial wait time for rate limiting

    while retries > 0:
        try:
            response = session.get(url, timeout=10)  # Timeout prevents hanging requests

            # Handle rate limiting (429) with exponential backoff
            if response.status_code == 429:
                print(f"Rate Limited (429): Waiting {wait_time}s before retrying...")
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
                retries -= 1
                continue  # Retry the request

            # Handle missing pages (404 errors)
            if response.status_code == 404:
                print(f"Page not found: {team} ({year}) - {url}")
                return None

            # Handle unexpected errors
            if response.status_code != 200:
                print(f"Failed to retrieve stats for {team} ({year}) - {url}")
                with open("error_log.txt", "a") as log_file:
                    log_file.write(f"{team}, {year}, {url}, HTTP {response.status_code}\n")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Locate the per-game stats table
            table_div = soup.find("div", id="all_per_game_team")
            if not table_div:
                print(f"No per-game stats found for {team} ({year}) - {url}")
                return None

            # Find the "Per Game Team and Opponent Stats" table
            stats_table = table_div.find("table", id="season-total_per_game")
            if not stats_table:
                print(f"Stats table missing for {team} ({year}) - {url}")
                return None

            # Extract table rows
            rows = stats_table.find_all("tr")
            stats = {"team": team, "year": year}

            for row in rows:
                cols = row.find_all("td")
                if not cols:
                    continue
                summary_div = soup.find("div", {"data-template": "Partials/Teams/Summary"})
                if summary_div:
                    for p in summary_div.find_all("p"):
                        text = p.get_text(strip=True)
                        if "PS/G:" in text:
                            stats["ps_per_game"] = safe_float(text.split("PS/G:")[-1].split(" ")[0])
                        elif "PA/G:" in text:
                            stats["pa_per_game"] = safe_float(text.split("PA/G:")[-1].split(" ")[0])
                        elif "SRS:" in text:
                            stats["srs"] = safe_float(text.split("SRS:")[-1].split(" ")[0])
                        elif "SOS:" in text:
                            stats["sos"] = safe_float(text.split("SOS:")[-1].split(" ")[0])
                        elif "ORtg:" in text:
                            stats["offensive_rating"] = safe_float(text.split("ORtg:")[-1].split(" ")[0])
                        elif "DRtg:" in text:
                            stats["defensive_rating"] = safe_float(text.split("DRtg:")[-1].split(" ")[0])
                        elif "NCAA Tournament" in text:
                            wins = []
                            losses = []

                            for line in text.split("<br>"):
                                line = line.strip()
                                if "Won" in line and "versus" in line:
                                    match = re.search(r"Won.*?versus\s+#?\d*\s*([\w\s'-]+)", line)
                                    if match:
                                        wins.append(match.group(1).strip())

                                elif "Lost" in line and "versus" in line:
                                    match = re.search(r"Lost.*?versus\s+#?\d*\s*([\w\s'-]+)", line)
                                    if match:
                                        losses.append(match.group(1).strip())

                            stats["ncaa_wins"] = ", ".join(wins) if wins else None
                            stats["ncaa_losses"] = ", ".join(losses) if losses else None
                # Identify the row labeled "Team" (ignoring "Opponent" and "Rank")
                label = row.find("th").text.strip()
                if label.lower() == "team":
                    stats["fg_per_game"] = safe_float(cols[2].text)
                    stats["fga_per_game"] = safe_float(cols[3].text)
                    stats["fg_pct"] = safe_float(cols[4].text)
                    stats["fg2_per_game"] = safe_float(cols[5].text)
                    stats["fg2a_per_game"] = safe_float(cols[6].text)
                    stats["fg2_pct"] = safe_float(cols[7].text)
                    stats["fg3_per_game"] = safe_float(cols[8].text)
                    stats["fg3a_per_game"] = safe_float(cols[9].text)
                    stats["fg3_pct"] = safe_float(cols[10].text)
                    stats["ft_per_game"] = safe_float(cols[11].text)
                    stats["fta_per_game"] = safe_float(cols[12].text)
                    stats["ft_pct"] = safe_float(cols[13].text)
                    stats["orb_per_game"] = safe_float(cols[14].text)
                    stats["drb_per_game"] = safe_float(cols[15].text)
                    stats["trb_per_game"] = safe_float(cols[16].text)
                    stats["ast_per_game"] = safe_float(cols[17].text)
                    stats["stl_per_game"] = safe_float(cols[18].text)
                    stats["blk_per_game"] = safe_float(cols[19].text)
                    stats["tov_per_game"] = safe_float(cols[20].text)
                    stats["pf_per_game"] = safe_float(cols[21].text)
                    break  

            return stats

        except requests.exceptions.RequestException as e:
            print(f"Request failed for {team} ({year}) - {url}: {str(e)}")
            with open("error_log.txt", "a") as log_file:
                log_file.write(f"{team}, {year}, {url}, Error: {str(e)}\n")
            return None

    return None

# # **Process all teams**
# all_stats = []
# for index, row in teams_df.iterrows():
#     team = row["team"]
#     year = row["year"]

#     print(f"\nFetching stats for {team} ({year})...")
#     stats = scrape_team_stats(team, year)

#     if stats:
#         all_stats.append(stats)
#     else:
#         print("❌ No data found for", team, year)

#     # Save progress every 50 teams
#     if len(all_stats) % 50 == 0:
#         pd.DataFrame(all_stats).to_csv("march_madness_with_stats_progress.csv", index=False)
#         print(f"💾 Progress saved after {len(all_stats)} teams.")

#     # Avoid getting blocked (random delay between 5-10 seconds)
#     time.sleep(random.uniform(5, 10))

# # Final save
# stats_df = pd.DataFrame(all_stats)
# stats_df.to_csv("march_madness_with_full_stats.csv", index=False)
# print(f"\n✅ Final data saved to march_madness_with_full_stats.csv")

# **Process 5 Random Teams**
all_stats = []
random_teams = teams_df.sample(n=5, random_state=42)  # Select 5 random teams

for index, row in random_teams.iterrows():
    team = row["team"]
    year = row["year"]

    print(f"\nFetching stats for {team} ({year})...")
    stats = scrape_team_stats(team, year)

    if stats:
        all_stats.append(stats)
    else:
        print("❌ No data found for", team, year)

    # Avoid getting blocked (random delay between 5-10 seconds)
    time.sleep(random.uniform(5, 10))

# Final save
stats_df = pd.DataFrame(all_stats)
stats_df.to_csv("march_madness_with_full_stats.csv", index=False)
print(f"\n✅ Final data saved to march_madness_with_full_stats.csv")