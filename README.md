# Daily Trending Japanese Anime Reporter

This project contains a Python script that fetches the top 10 currently airing Japanese anime from MyAnimeList.net, extracts their details (synopsis, genres, source URL), and saves them into a Markdown file named with the current date in the `japanese-animes` folder.

## Features

- Fetches data from MyAnimeList's "Top Airing Anime" page.
- Filters for currently airing Japanese anime using data-driven heuristics.
- Extracts title, MyAnimeList URL, genres, and generates an AI summary for each anime's synopsis.
- Saves the collected data for the top 10 animes into a daily Markdown file (e.g., `japanese-animes/YYYY-MM-DD.md`).

## Prerequisites

Before running the script, you need to have Python 3 installed.
You will also need to install the following Python libraries:

- `requests` (for fetching web pages)
- `beautifulsoup4` (for parsing HTML)
- `transformers` (for AI-powered text summarization)
- `torch` (PyTorch, a backend for the Transformers model) 
  *Alternatively, `tensorflow` can be used if you configure Transformers accordingly, but `torch` is common with the default model used.*

You can install them using pip:

```bash
pip install requests beautifulsoup4 transformers torch
```
*(Note: If you prefer TensorFlow and have it installed, `transformers` may use it. However, the default model `sshleifer/distilbart-cnn-6-6` is typically used with PyTorch. Ensure your environment is set up accordingly if you deviate from `torch`.)*

## How to Run

1.  Clone this repository (if you haven't already).
2.  Navigate to the root directory of the project in your terminal.
3.  Install the required libraries (see Prerequisites).
4.  Run the script:

    ```bash
    python anime_scraper.py
    ```

5.  After the script completes, you will find a new Markdown file in the `japanese-animes` folder containing the report for the current day. The first run involving AI summarization might take longer as the model needs to be downloaded.

## Model Information

The AI summarization uses the `sshleifer/distilbart-cnn-6-6` model from the Hugging Face Transformers library. This model is automatically downloaded by the `transformers` library the first time the script is run with AI capabilities enabled and cached for future use.

## Disclaimer

- This script relies on web scraping MyAnimeList.net. Changes to the website's structure may break the script.
- The determination of an anime's country of origin and "currently airing" status is based on heuristics and available data on MyAnimeList, which may not always be 100% accurate.
- AI-generated summaries are based on the model's interpretation of the synopsis and may not always be perfectly accurate or capture all nuances.
