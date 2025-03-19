# March Madness API

Empowering data-driven analysis for NCAA tournament games!

## Overview

The March Madness API provides historical NCAA tournament matchup data and team statistics. It’s designed for machine learning labeling tasks, sports analytics, and predictive modeling. This API does not provide real-time data but serves as a historical dataset that can be used to analyze and compare teams based on their past performances.
	- Historical matchups (1991-2024)
	- Team statistics (1991-2025)
	- Unlabeled 2025 matchup data for predictive modeling
	- Built with FastAPI & PostgreSQL, deployed on Render

⸻

## Data Collection Process

1.) Scraping Data with BeautifulSoup

To construct this dataset, BeautifulSoup was used to scrape historical NCAA tournament data from various sources, primarily targeting team statistics and game results. The process included:
	- Finding structured data sources (e.g., Wikipedia, sports databases).
	- Parsing HTML tables to extract relevant stats.
	- Cleaning and storing data in a structured format.

2.) Constructing the Matchups Data

Once team statistics were collected, we mapped game results by iterating through the winners and losers of each game in the NCAA tournament. The key steps included:
	- Extracting tournament brackets for each year.
	- Pairing teams to form matchups.
	- Computing feature differences for statistical comparison.
	- Labeling the winner (1 for teamA win, 0 for teamB win).

## API Endpoints
- GET /matchups/?start_year={year}&end_year={year}
- GET /matchups/{year}
- GET /matchups/2025?teamA={team}&teamB={team}
- GET /stats/?start_year={year}&end_year={year}
- GET /stats/{year}
