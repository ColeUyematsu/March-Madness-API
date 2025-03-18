import pandas as pd
import re
from fuzzywuzzy import process
import time
from bs4 import BeautifulSoup
from unidecode import unidecode
import random
import requests

# Load dataset
def make_matchups_table():
    file_path = "march_madness_2023.csv"
    df = pd.read_csv(file_path)

    # Drop unnecessary columns
    df = df.drop(columns=["conference", "ncaa_loss"], errors="ignore")

    # Normalize team names to fix inconsistencies
    def clean_team_name(name):
        """Standardizes team names for better matching"""
        if pd.isna(name):
            return ""
        name = name.lower().strip()  # Lowercase and trim spaces
        name = re.sub(r"\s*\(.*?\)", "", name)  # Remove text inside parentheses
        name = re.sub(r"[^\w\s-]", "", name)  # Remove special characters except hyphens
        name = name.replace("st ", "saint ")  # Standardize abbreviations
        return name

    # Apply name cleaning
    df["team"] = df["team"].apply(clean_team_name)

    # Store unique teams for matching
    team_list = df["team"].unique()

    # Create an empty list for matchups
    matchups = []
    recorded_games = set()  # To avoid duplicate matchups

    # Process each team's wins
    for _, row in df.iterrows():
        teamA = clean_team_name(row["team"])
        year = row["year"]

        if pd.isna(row["ncaa_wins"]) or row["ncaa_wins"] == "":
            continue  # Skip if no recorded wins

        # Normalize win list
        opponents = [clean_team_name(team) for team in row["ncaa_wins"].split(", ")]

        for teamB in opponents:
            # Find closest match for teamB
            best_match, score = process.extractOne(teamB, team_list)
            if score < 85:  # Set a similarity threshold
                print(f"Possible name mismatch: {teamB} → {best_match} (score: {score})")
            teamB = best_match  # Use corrected name

            # Locate opponent's stats
            opponent_row = df[(df["team"] == teamB) & (df["year"] == year)]
            if opponent_row.empty:
                print(f"No data found for matchup {teamA} vs {teamB} ({year})")
                continue  # Skip if opponent is missing

            teamB_data = opponent_row.iloc[0]

            # Ensure the game isn't duplicated
            game_key = (year, tuple(sorted([teamA, teamB])))
            if game_key in recorded_games:
                continue
            recorded_games.add(game_key)

            # Compute stat differences
            matchup_data = {
                "year": year,
                "teamA": row["team"],
                "teamB": teamB_data["team"],
                "winner": 1  # Since teamA won, we label it as 1
            }

            for col in df.columns:
                if col not in ["team", "year", "ncaa_wins", "wins", "losses"]:
                    diff = row[col] - teamB_data[col]
                    matchup_data[f"diff_{col}"] = round(diff, 3)  # Truncate to 3 decimals

            matchups.append(matchup_data)

    # Convert to DataFrame
    matchups_df = pd.DataFrame(matchups)

    # Save the processed dataset
    output_file = "march_madness_matchups.csv"
    matchups_df.to_csv(output_file, index=False)
    print(f"Matchup dataset saved to {output_file}")

# Load the dataset
def scrape_sports_reference():
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
        
    def extract_ncaa_results(summary_div):
        """
        Extracts all NCAA Tournament wins and losses correctly, ensuring that the last game is always a loss.
        """
        wins = []
        losses = []

        # Locate the NCAA Tournament paragraph
        ncaa_p = None
        for p in summary_div.find_all("p"):
            if "NCAA Tournament" in p.text:
                ncaa_p = p
                break
        
        if not ncaa_p:
            return None, None  # No NCAA data found

        # Extract all lines within the paragraph
        lines = ncaa_p.decode_contents().split("<br>")

        for line in lines:
            # Use BeautifulSoup to parse HTML content within the line
            line_soup = BeautifulSoup(line, "html.parser")
            text = line_soup.get_text(" ", strip=True)  # Extract text, preserving spacing

            # Find all opponent links inside the line
            team_links = line_soup.find_all("a", href=re.compile("/cbb/schools/"))

            for team_link in team_links:
                opponent = team_link.text.strip()
                opponent = re.sub(r"#\d+\s+", "", opponent)  # Remove any seed numbers

                if "Won" in text and "versus" in text:
                    wins.append(opponent)
                elif "Lost" in text and "versus" in text:
                    losses.append(opponent)

        # Ensure the last team is recorded as a loss if applicable
        if len(wins) == 6:
            return ", ".join(wins), None
        elif wins and not losses:
            # Move the last win into the loss column
            losses.append(wins.pop())

        return ", ".join(wins) if wins else None, ", ".join(losses) if losses else None

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
                        ncaa_wins, ncaa_losses = extract_ncaa_results(summary_div)
                        stats["ncaa_wins"] = ncaa_wins
                        stats["ncaa_loss"] = ncaa_losses
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

    # **Process all teams**
    all_stats = []
    for index, row in teams_df.iterrows():
        team = row["team"]
        year = row["year"]

        print(f"\nFetching stats for {team} ({year})...")
        stats = scrape_team_stats(team, year)

        if stats:
            all_stats.append(stats)
        else:
            print("No data found for", team, year)

        # Save progress every 50 teams
        if len(all_stats) % 50 == 0:
            pd.DataFrame(all_stats).to_csv("march_madness_with_stats_progress_with_wins.csv", index=False)
            print(f"Progress saved after {len(all_stats)} teams.")

        # Avoid getting blocked (random delay between 5-10 seconds)
        time.sleep(random.uniform(5, 10))

    # Final save
    stats_df = pd.DataFrame(all_stats)
    stats_df.to_csv("march_madness_with_full_stats.csv", index=False)
    print(f"\nFinal data saved to march_madness_with_full_stats.csv")


def scrape_wikipedia():
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

def flip_table():
    # Load the CSV file
    input_file = "march_madness.csv"  # Change this to your actual CSV filename
    output_file = "flipped_march_madness.csv"  # Output file with reversed rows

    # Read the CSV
    df = pd.read_csv(input_file)

    # Reverse the order of rows
    df = df.iloc[::-1].reset_index(drop=True)

    # Save to a new CSV file
    df.to_csv(output_file, index=False)

    print(f"Flipped CSV saved as {output_file}")

def merge_dfs():
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
        "team", "year", "conference", "seed", "wins", "losses", "win_pct",
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

    print("Merging complete! 'conference' column removed, and saved as 'march_madness_merged.csv'.")

def map_team_name():
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

def get_unique_teams(): 
    # Load the dataset
    df = pd.read_csv("march_madness_1991_2024_cleaned.csv")  # Adjust filename if needed

    # Extract unique team names
    unique_teams = df["team"].unique()

    # Convert to DataFrame
    unique_teams_df = pd.DataFrame(unique_teams, columns=["team"])

    # Sort alphabetically
    unique_teams_df = unique_teams_df.sort_values("team")

    # Save to CSV
    csv_filename = "unique_ncaa_teams.csv"
    unique_teams_df.to_csv(csv_filename, index=False)

    # Print confirmation
    print(f"\nExtracted {len(unique_teams_df)} unique teams that have made the tournament.")
    print(f"Data saved to {csv_filename}")

    # Display first 10 teams as a preview
    print(unique_teams_df.head(10))