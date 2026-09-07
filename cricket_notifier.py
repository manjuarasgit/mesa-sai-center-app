#!/usr/bin/env python3
"""
Cricket Match Scraper
Scrapes ESPN Cricinfo for upcoming India cricket matches and displays results.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time


class CricketScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Selenium."""
        self.base_url = "https://www.espncricinfo.com"
        self.headless = headless
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Make sure Chrome browser is installed on your system.")
            raise
    
    def __del__(self):
        """Clean up driver on deletion."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def scrape_upcoming_matches(self):
        """Scrape ESPN Cricinfo for upcoming matches using Selenium."""
        matches = []
        
        if not self.driver:
            print("Error: WebDriver not initialized")
            return matches
        
        # Try multiple URLs and strategies
        urls_to_try = [
            f"{self.base_url}/cricket/schedule",
            f"{self.base_url}/cricket/fixtures",
            f"{self.base_url}/team/india-6/matches",
        ]
        
        for url in urls_to_try:
            try:
                print(f"Trying URL: {url}")
                self.driver.get(url)
                
                # Wait for page to load
                time.sleep(3)
                
                # Wait for content to be present
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except TimeoutException:
                    print(f"  Timeout waiting for page to load")
                    continue
                
                # Get page source and parse with BeautifulSoup
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Strategy 1: Look for match cards/containers with various selectors
                match_containers = []
                
                # Try data-testid attributes (common in modern websites)
                match_containers.extend(soup.find_all(attrs={'data-testid': re.compile(r'match|fixture|schedule', re.I)}))
                
                # Try class-based selectors
                match_containers.extend(soup.find_all(['div', 'article', 'li', 'tr'], class_=re.compile(r'match|fixture|schedule|game|event', re.I)))
                
                # Try looking for all links that might be matches
                all_links = soup.find_all('a', href=re.compile(r'/series/|/match/|/cricket/|/fixtures/'))
                for link in all_links:
                    text = link.get_text(strip=True).lower()
                    if any(keyword in text for keyword in ['vs', 'v ', 'match', 'india', 'ind ']):
                        match_containers.append(link)
                
                # Also try table rows (schedules are often in tables)
                table_rows = soup.find_all('tr')
                for row in table_rows:
                    row_text = row.get_text(strip=True).lower()
                    if any(keyword in row_text for keyword in ['india', 'ind ', 'vs', 'match']):
                        match_containers.append(row)
                
                # Remove duplicates
                seen = set()
                unique_containers = []
                for container in match_containers:
                    container_id = id(container)
                    if container_id not in seen:
                        seen.add(container_id)
                        unique_containers.append(container)
                
                # Parse matches
                for container in unique_containers[:50]:  # Limit to first 50
                    match_info = self.parse_match_info(container)
                    if match_info and self.is_india_match(match_info):
                        # Check if we already have this match
                        match_text = match_info.get('text', '')[:50]
                        if not any(m.get('text', '')[:50] == match_text for m in matches):
                            matches.append(match_info)
                
                # If we found matches, break
                if matches:
                    print(f"  Found {len(matches)} match(es) from this URL")
                    break
                    
            except Exception as e:
                print(f"  Error scraping {url}: {e}")
                continue
        
        # If still no matches, try the India team page specifically
        if not matches:
            matches = self.search_india_matches()
        
        return matches
    
    def search_india_matches(self):
        """Alternative method to search for India matches."""
        matches = []
        if not self.driver:
            return matches
            
        try:
            # Try searching for India team page or upcoming matches
            search_url = f"{self.base_url}/team/india-6"
            print(f"Trying alternative URL: {search_url}")
            self.driver.get(search_url)
            time.sleep(3)
            
            # Wait for content
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                print("  Timeout waiting for page")
                return matches
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for upcoming fixtures section
            fixture_sections = soup.find_all(['div', 'section', 'tr'], class_=re.compile(r'fixture|upcoming|schedule|match', re.I))
            
            for section in fixture_sections:
                match_info = self.parse_match_info(section)
                if match_info and self.is_india_match(match_info):
                    matches.append(match_info)
            
        except Exception as e:
            print(f"Error in alternative search: {e}")
        
        return matches
    
    def parse_match_info(self, element):
        """Parse match information from HTML element."""
        try:
            match_info = {}
            
            # Extract text content - get text from element and its children
            text = element.get_text(separator=' ', strip=True)
            
            # Also check for title attribute or data attributes
            if element.name == 'a' and element.get('title'):
                text = element.get('title') + ' ' + text
            
            # Look for date/time patterns (more comprehensive)
            date_patterns = [
                r'((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,\s+)?(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})',  # Wed, 14 Jan 2026
                r'((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,\s+)?(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*',  # Wed, 14 Jan (current year)
                r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})',  # January 14, 2026
                r'(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',  # 14 Jan 2026
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
            ]
            
            time_patterns = [
                r'(\d{1,2}:\d{2}\s*(?:AM|PM|IST|UTC|GMT))',
                r'(\d{1,2}:\d{2})',
            ]
            
            # Try to extract date
            for i, pattern in enumerate(date_patterns):
                match = re.search(pattern, text, re.I)
                if match:
                    if i == 0:  # Wed, 14 Jan 2026 format
                        match_info['date_str'] = f"{match.group(2)} {match.group(3)} {match.group(4)}"
                    elif i == 1:  # Wed, 14 Jan (current year)
                        match_info['date_str'] = f"{match.group(2)} {match.group(3)} {datetime.now().year}"
                    elif i == 2:  # January 14, 2026 format
                        match_info['date_str'] = match.group(1)
                    else:
                        match_info['date_str'] = match.group(1) if match.lastindex else match.group(0)
                    break
            
            # Try to extract time
            for pattern in time_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    match_info['time_str'] = match.group(1)
                    break
            
            # Extract teams (look for "vs" or "v" - more flexible)
            # Also look for team abbreviations like IND, NZ, SA, etc.
            vs_patterns = [
                r'(India|IND)\s+(?:vs|v|VS|v\.)\s+([A-Za-z\s&]+)',  # India vs ...
                r'([A-Za-z\s&]+)\s+(?:vs|v|VS|v\.)\s+(India|IND)',  # ... vs India
                r'([A-Z]{2,4})\s+(?:vs|v|VS|v\.)\s+([A-Z]{2,4})',  # IND vs NZ
                r'([A-Za-z\s&]+?)\s+(?:vs|v|VS|v\.)\s+([A-Za-z\s&]+)',  # General pattern
            ]
            
            for pattern in vs_patterns:
                vs_match = re.search(pattern, text, re.I)
                if vs_match:
                    team1 = vs_match.group(1).strip()
                    team2 = vs_match.group(2).strip()
                    # Clean up team names
                    team1 = re.sub(r'\s+', ' ', team1)
                    team2 = re.sub(r'\s+', ' ', team2)
                    match_info['team1'] = team1
                    match_info['team2'] = team2
                    break
            
            # Store full text for reference
            match_info['text'] = text[:300]  # First 300 chars
            
            # Try to parse datetime
            if 'date_str' in match_info:
                match_info['datetime'] = self.parse_datetime(match_info.get('date_str'), match_info.get('time_str'))
            else:
                # If no date found, try to find relative dates like "Today", "Tomorrow"
                today_match = re.search(r'\b(today|tomorrow)\b', text, re.I)
                if today_match:
                    date_str = today_match.group(1).lower()
                    if date_str == 'today':
                        match_info['datetime'] = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
                    elif date_str == 'tomorrow':
                        match_info['datetime'] = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
            
            return match_info if match_info else None
            
        except Exception as e:
            print(f"Error parsing match info: {e}")
            return None
    
    def parse_datetime(self, date_str, time_str=None):
        """Parse date and time strings into datetime object."""
        try:
            # Try different date formats
            date_formats = [
                '%d %b %Y',      # 14 Jan 2026
                '%d %B %Y',      # 14 January 2026
                '%B %d, %Y',     # January 14, 2026
                '%d/%m/%Y',      # 14/01/2026
                '%Y-%m-%d',      # 2026-01-14
            ]
            
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue
            
            if not parsed_date:
                return None
            
            # Add time if available
            if time_str:
                time_formats = [
                    '%I:%M %p',
                    '%H:%M',
                ]
                for fmt in time_formats:
                    try:
                        parsed_time = datetime.strptime(time_str, fmt).time()
                        parsed_date = parsed_date.replace(hour=parsed_time.hour, minute=parsed_time.minute)
                        break
                    except:
                        continue
            
            return parsed_date
            
        except Exception as e:
            print(f"Error parsing datetime: {e}")
            return None
    
    def is_india_match(self, match_info):
        """Check if the match involves India."""
        text = match_info.get('text', '').lower()
        team1 = match_info.get('team1', '').lower()
        team2 = match_info.get('team2', '').lower()
        
        india_keywords = ['india', 'ind ', 'indian', 'ind vs', 'vs ind']
        
        for keyword in india_keywords:
            if keyword in text or keyword in team1 or keyword in team2:
                return True
        
        return False
    
    def is_within_24_hours(self, match_datetime):
        """Check if match is within 24 hours."""
        if not match_datetime:
            return False
        
        now = datetime.now()
        time_diff = match_datetime - now
        
        return timedelta(0) <= time_diff <= timedelta(hours=24)
    
    def format_match_output(self, match):
        """Format match information for display."""
        output = []
        
        # Teams
        if match.get('team1') and match.get('team2'):
            output.append(f"Teams: {match['team1']} vs {match['team2']}")
        else:
            output.append("Teams: Not specified")
        
        # Date
        if match.get('date_str'):
            output.append(f"Date: {match['date_str']}")
        else:
            output.append("Date: Not specified")
        
        # Time
        if match.get('time_str'):
            output.append(f"Time: {match['time_str']}")
        else:
            output.append("Time: Not specified")
        
        # Datetime
        if match.get('datetime'):
            dt = match['datetime']
            hours_until = (dt - datetime.now()).total_seconds() / 3600
            if hours_until < 0:
                output.append(f"Status: Match already started/passed")
            elif self.is_within_24_hours(dt):
                output.append(f"Status: *** WITHIN 24 HOURS! *** ({hours_until:.1f} hours from now)")
            else:
                output.append(f"Status: {hours_until:.1f} hours from now")
        
        # Full text
        if match.get('text'):
            output.append(f"Details: {match['text']}")
        
        return output
    
    def display_matches(self, matches):
        """Display all found matches in a formatted way."""
        print("\n" + "="*70)
        print("INDIA CRICKET MATCHES - RESULTS")
        print("="*70)
        
        if not matches:
            print("\nNo India matches found.")
            print("The website structure may have changed or there are no upcoming matches.")
            return
        
        print(f"\nFound {len(matches)} India match(es):\n")
        
        matches_within_24h = []
        matches_future = []
        matches_no_date = []
        
        # Categorize matches
        for match in matches:
            match_datetime = match.get('datetime')
            if match_datetime:
                if self.is_within_24_hours(match_datetime):
                    matches_within_24h.append(match)
                else:
                    matches_future.append(match)
            else:
                matches_no_date.append(match)
        
        # Display matches within 24 hours first
        if matches_within_24h:
            print("*** MATCHES WITHIN 24 HOURS ***")
            print("-" * 70)
            for i, match in enumerate(matches_within_24h, 1):
                print(f"\n[{i}]")
                for line in self.format_match_output(match):
                    print(f"  {line}")
                print()
        
        # Display future matches
        if matches_future:
            print("\n*** UPCOMING MATCHES (More than 24 hours away) ***")
            print("-" * 70)
            for i, match in enumerate(matches_future, 1):
                print(f"\n[{i}]")
                for line in self.format_match_output(match):
                    print(f"  {line}")
                print()
        
        # Display matches without dates
        if matches_no_date:
            print("\n*** MATCHES (Date/Time not parsed) ***")
            print("-" * 70)
            for i, match in enumerate(matches_no_date, 1):
                print(f"\n[{i}]")
                for line in self.format_match_output(match):
                    print(f"  {line}")
                print()
        
        print("="*70)
    
    def check_and_display(self):
        """Main method to check for matches and display results."""
        try:
            print("Checking for upcoming India cricket matches...")
            print("Scraping ESPN Cricinfo with Selenium...\n")
            
            matches = self.scrape_upcoming_matches()
            self.display_matches(matches)
        finally:
            # Always close the driver
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass


def main():
    """Main entry point."""
    scraper = CricketScraper()
    scraper.check_and_display()


if __name__ == "__main__":
    main()
