# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import re # For parsing dates
from datetime import datetime
import os # For directory and file operations

# Define the URL to scrape
URL = "https://myanimelist.net/topanime.php?type=airing"

def fetch_anime_page(url):
    """
    Fetches the content of the given URL.
    Adds a User-Agent header to the request.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def parse_anime_data(html_content):
    """
    Parses the HTML content of the main anime list page.
    Returns a list of dictionaries, each containing an anime's title and URL.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    ranking_list = soup.find_all('tr', class_='ranking-list')
    
    anime_list = []
    if not ranking_list:
        print("Could not find the anime ranking list on the page.")
        return anime_list

    for item in ranking_list:
        if len(anime_list) >= 50: # Limit to top 50 to get a good pool
            break
        
        title_element = item.find('h3', class_=re.compile(r'fl-l fs\d+ fw-b anime_ranking_h3'))
        if title_element and title_element.find('a'):
            title = title_element.get_text(strip=True)
            anime_url = title_element.find('a')['href']
            anime_list.append({'title': title, 'url': anime_url})
        elif item.find('div', class_='detail') and item.find('div', class_='detail').find('a', class_ = re.compile(r'hoverinfo_trigger.*')):
            detail_div = item.find('div', class_='detail')
            title_anchor = detail_div.find('a', class_=re.compile(r'hoverinfo_trigger.*'))
            if title_anchor:
                title = title_anchor.get_text(strip=True)
                anime_url = title_anchor['href']
                anime_list.append({'title': title, 'url': anime_url})
            
    return anime_list

def get_anime_details(anime_url):
    """
    Fetches and parses an individual anime page to extract details.
    """
    print(f"Fetching details for: {anime_url}")
    html_content = fetch_anime_page(anime_url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")
    details = {'synopsis': "Synopsis not found.", 'genres': [], 'aired_date_str': None, 'broadcast_info': None, 'country_info': None, 'type': None}

    synopsis_tag = soup.find('p', itemprop='description')
    if not synopsis_tag:
        synopsis_tag = soup.find('span', itemprop='description')
    if not synopsis_tag:
        synopsis_div = soup.find('div', class_='synopsis')
        if synopsis_div:
            story_div = synopsis_div.find('div', class_='story')
            if story_div:
                details['synopsis'] = story_div.get_text(separator='\n', strip=True)
            else: # Fallback if no specific 'story' div, take all text from 'synopsis' div
                details['synopsis'] = synopsis_div.get_text(separator='\n', strip=True)
    if synopsis_tag and (details['synopsis'] == "Synopsis not found." or not details['synopsis']): # Check if not already populated by div logic
        details['synopsis'] = synopsis_tag.get_text(separator='\n', strip=True)
    
    if not details['synopsis'] or details['synopsis'].strip() == "": # Final check for empty synopsis
        details['synopsis'] = "Synopsis not available on the page."


    genre_tags = soup.find_all('span', itemprop='genre')
    details['genres'] = [tag.get_text(strip=True) for tag in genre_tags if tag.get_text(strip=True)]
    if not details['genres']:
        details['genres'] = ["N/A"]


    def get_info_from_sidebar(label_text):
        span_tag = soup.find('span', class_='dark_text', string=re.compile(r'^\s*' + re.escape(label_text) + r'\s*$', re.IGNORECASE))
        if span_tag:
            next_sibling = span_tag.next_sibling
            value = ""
            if next_sibling and isinstance(next_sibling, str) and next_sibling.strip():
                value = next_sibling.strip()
            
            # If not found as direct sibling text, try to get from parent, excluding label
            if not value:
                parent_content = span_tag.parent.get_text(separator=' ', strip=True)
                value = parent_content.replace(span_tag.get_text(strip=True), "", 1).strip()
                if value.startswith(":"):
                     value = value[1:].strip()
            
            # If value is still empty, it might be in an 'a' tag within the parent
            if not value and span_tag.parent.find('a'):
                value = span_tag.parent.find('a').get_text(strip=True)

            return value if value else None
        return None

    details['aired_date_str'] = get_info_from_sidebar('Aired:')
    details['broadcast_info'] = get_info_from_sidebar('Broadcast:')
    details['country_info'] = get_info_from_sidebar('Country:')
    if not details['country_info']:
        studios_info = get_info_from_sidebar('Studios:')
        if studios_info and "Japan" in studios_info:
            details['country_info'] = "Japan (inferred from Studios)"
    
    details['type'] = get_info_from_sidebar('Type:')
    return details

def is_currently_airing_japan(aired_date_str, broadcast_info, country_info, anime_type, anime_title):
    if not aired_date_str:
        return False

    is_airing = False
    date_parts = [d.strip() for d in aired_date_str.split('to')]
    start_date_str = date_parts[0]
    end_date_str = date_parts[1] if len(date_parts) > 1 else None

    try:
        start_date = None
        possible_formats = ["%b %d, %Y", "%Y", "%b %Y", "%b, %Y"]
        for fmt in possible_formats:
            try:
                start_date = datetime.strptime(start_date_str, fmt)
                break
            except ValueError:
                continue
        
        if start_date and start_date > datetime.now(): return False # Future start date

        if end_date_str:
            end_date_str = end_date_str.strip()
            if end_date_str == "?" or end_date_str.lower() == "present":
                is_airing = True
            else:
                end_date = None
                for fmt in possible_formats:
                    try:
                        end_date = datetime.strptime(end_date_str, fmt)
                        break
                    except ValueError:
                        continue
                if end_date and end_date < datetime.now(): return False # Ended
                elif end_date and end_date >= datetime.now(): is_airing = True
        else: # No end date
            if anime_type in ["Movie", "Special", "OVA", "ONA"] and anime_type is not None: # Check anime_type is not None
                 # For these types, if start date is past, it's not "currently airing TV-style"
                 if start_date and start_date < datetime.now(): return False
                 elif start_date and start_date >= datetime.now(): is_airing = True # Airing now or upcoming
            elif anime_type == "TV" and start_date and start_date <= datetime.now(): # For TV, no end date implies airing
                is_airing = True


    except Exception as e:
        # print(f"Could not parse date string '{aired_date_str}' for {anime_title}: {e}")
        if "to ?" in aired_date_str: is_airing = True
        else: return False

    if not is_airing: return False

    is_japanese_broadcast = False
    if broadcast_info and "JST" in broadcast_info: is_japanese_broadcast = True
    if country_info and "Japan" in country_info: is_japanese_broadcast = True
    
    # Relaxing ONA filter slightly: if country is Japan, it's fine.
    if anime_type == "ONA" and not (country_info and "Japan" in country_info) and not (broadcast_info and "JST" in broadcast_info) :
        # print(f"Filtering ONA '{anime_title}' due to lack of clear Japanese broadcast/country.")
        return False

    if not is_japanese_broadcast:
        # print(f"Anime '{anime_title}' might not be a Japanese broadcast (Country: {country_info}, Broadcast: {broadcast_info}, Type: {anime_type}).")
        return False

    return True


# Main execution block
if __name__ == "__main__":
    print(f"Fetching initial anime list from: {URL}")
    main_page_html = fetch_anime_page(URL)
    
    detailed_animes = []
    MAX_JAPANESE_ANIMES_TO_COLLECT = 10 # Target for final list
    MAX_JAPANESE_ANIMES_TO_FIND_INTERNALLY = 15 # Intermediate target during scraping
    PROCESSED_ENTRIES_LIMIT = 50

    if main_page_html:
        anime_entries = parse_anime_data(main_page_html)
        print(f"Found {len(anime_entries)} initial anime entries from the main page (max {PROCESSED_ENTRIES_LIMIT} will be processed).")
        
        processed_count = 0
        for entry in anime_entries:
            if processed_count >= PROCESSED_ENTRIES_LIMIT or len(detailed_animes) >= MAX_JAPANESE_ANIMES_TO_FIND_INTERNALLY:
                print(f"Stopping processing: Reached {len(detailed_animes)} potential Japanese animes or processed {processed_count} entries.")
                break
            
            processed_count += 1
            print(f"\nProcessing entry {processed_count}/{min(len(anime_entries), PROCESSED_ENTRIES_LIMIT)}: {entry['title']}")
            details = get_anime_details(entry['url'])
            
            if details:
                if is_currently_airing_japan(details['aired_date_str'], details['broadcast_info'], details['country_info'], details['type'], entry['title']):
                    print(f"PASSED FILTER: '{entry['title']}' seems to be a currently airing Japanese anime.")
                    detailed_animes.append({
                        'title': entry['title'],
                        'url': entry['url'],
                        'synopsis': details['synopsis'],
                        'genres': details['genres']
                        # 'aired_date': details['aired_date_str'], # Keep for debugging if needed
                        # 'broadcast': details['broadcast_info'] # Keep for debugging if needed
                    })
                else:
                    print(f"FILTERED OUT: '{entry['title']}' (Aired: {details['aired_date_str']}, Broadcast: {details['broadcast_info']}, Country: {details['country_info']}, Type: {details['type']})")
            else:
                print(f"Could not fetch details for {entry['title']}")

        print("\n--- Collection Phase Complete ---")
        if detailed_animes:
            print(f"Found {len(detailed_animes)} Japanese animes matching criteria.")
            
            # Sort by original order (which is MAL rank), then take top N
            animes_to_save = detailed_animes[:MAX_JAPANESE_ANIMES_TO_COLLECT]
            print(f"Saving top {len(animes_to_save)} animes to Markdown file.")

            output_dir = "japanese-animes"
            os.makedirs(output_dir, exist_ok=True)
            
            current_date_str = datetime.now().strftime('%Y-%m-%d')
            output_filename = os.path.join(output_dir, f"{current_date_str}.md")

            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    for i, anime in enumerate(animes_to_save):
                        f.write(f"# {anime['title']}\n\n")
                        f.write(f"## Synopsis\n{anime['synopsis']}\n\n")
                        f.write(f"## Categories\n{', '.join(anime['genres'])}\n\n")
                        f.write(f"## Source\n{anime['url']}\n")
                        if i < len(animes_to_save) - 1:
                            f.write("\n---\n\n") # Horizontal rule between entries
                print(f"\nData successfully saved to: {output_filename}")
            except IOError as e:
                print(f"Error writing to file {output_filename}: {e}")

        else:
            print("No currently airing Japanese animes found matching the criteria from the processed entries. No file will be written.")

    else:
        print("Failed to fetch the main anime list. Cannot proceed.")

    print("\nReminder: To run this script, you need to install the following libraries if you haven't already:")
    print("pip install requests beautifulsoup4")
