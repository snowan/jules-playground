# Daily Trending Japanese Anime Reporter

This project contains a Python script that fetches the top 10 currently airing Japanese anime from MyAnimeList.net, extracts their details (synopsis, genres, source URL), and saves them into a Markdown file named with the current date in the `japanese-animes` folder.

## Features

- Fetches data from MyAnimeList's "Top Airing Anime" page.
- Filters for anime that are currently airing and likely of Japanese origin.
- Extracts title, synopsis, genres, and the MyAnimeList URL for each anime.
- Saves the collected data for the top 10 animes into a daily Markdown file (e.g., `japanese-animes/YYYY-MM-DD.md`).
- Uses AI-inspired heuristics for filtering and data extraction (though not a true AI model).

## Prerequisites

Before running the script, you need to have Python 3 installed.
You will also need to install the following Python libraries:

- `requests`
- `beautifulsoup4`

You can install them using pip:

```bash
pip install requests beautifulsoup4
```

## How to Run

1.  Clone this repository (if you haven't already).
2.  Navigate to the root directory of the project in your terminal.
3.  Install the required libraries (see Prerequisites).
4.  Run the script:

    ```bash
    python anime_scraper.py
    ```

5.  After the script completes, you will find a new Markdown file in the `japanese-animes` folder containing the report for the current day.

## Disclaimer

- This script relies on web scraping MyAnimeList.net. Changes to the website's structure may break the script.
- The determination of an anime's country of origin and "currently airing" status is based on heuristics and available data on MyAnimeList, which may not always be 100% accurate.
