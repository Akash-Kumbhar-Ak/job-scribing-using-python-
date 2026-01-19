import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
from urllib.parse import urljoin, urlparse
import logging

class JobScraper:
    def __init__(self, use_selenium=False, headless=True):
        self.use_selenium = use_selenium
        self.headless = headless
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.jobs = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_selenium(self):
        """Initialize Selenium WebDriver with better error handling"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-extensions')
            options.add_argument('--window-size=1920,1080')
            
            # Use webdriver-manager to handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            return self.driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium: {e}")
            self.logger.info("Falling back to requests mode")
            self.use_selenium = False
            return None
    
    def get_page_content(self, url, wait_for_element=None):
        """Get page content with better error handling"""
        try:
            if self.use_selenium:
                if not self.driver:
                    self.driver = self.setup_selenium()
                    if not self.driver:
                        # Fallback to requests
                        return self._get_with_requests(url)
                
                self.logger.info(f"Loading page with Selenium: {url}")
                self.driver.get(url)
                
                if wait_for_element:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                        )
                    except:
                        pass  # Continue even if wait element not found
                
                time.sleep(3)  # Wait for dynamic content
                return BeautifulSoup(self.driver.page_source, 'html.parser')
            else:
                return self._get_with_requests(url)
                
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            # Try fallback to requests if Selenium fails
            if self.use_selenium:
                self.logger.info("Trying fallback to requests...")
                return self._get_with_requests(url)
            return None
    
    def _get_with_requests(self, url):
        """Fallback method using requests"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            self.logger.error(f"Requests also failed for {url}: {e}")
            return None
    
    def find_job_links(self, career_url, job_link_selectors=None):
        """Enhanced job link discovery with better patterns"""
        if not job_link_selectors:
            job_link_selectors = [
                # Direct job link patterns
                'a[href*="/job/"]', 'a[href*="/jobs/"]', 'a[href*="/career/"]',
                'a[href*="/careers/"]', 'a[href*="/position/"]', 'a[href*="/positions/"]',
                'a[href*="/opening/"]', 'a[href*="/openings/"]', 'a[href*="/apply/"]',
                
                # Class-based selectors
                '.job-link', '.career-link', '.position-link', '.job-card a',
                '.job-listing a', '.position-card a', '.opening-link',
                
                # Data attribute selectors
                'a[data-job-id]', 'a[data-position-id]', 'a[data-career-id]',
                
                # Common job board patterns
                '.job-title a', '.position-title a', '.role-title a'
            ]
        
        soup = self.get_page_content(career_url, wait_for_element='.job, .career, .position')
        if not soup:
            return []
        
        job_links = set()
        
        # Try each selector pattern
        for selector in job_link_selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(career_url, href)
                        job_links.add(full_url)
            except Exception as e:
                continue
        
        # Enhanced filtering
        filtered_links = []
        job_keywords = ['job', 'career', 'position', 'apply', 'opening', 'role', 'vacancy']
        exclude_keywords = ['login', 'register', 'contact', 'about', 'privacy', 'terms']
        
        for link in job_links:
            link_lower = link.lower()
            if (any(keyword in link_lower for keyword in job_keywords) and
                not any(keyword in link_lower for keyword in exclude_keywords)):
                filtered_links.append(link)
        
        # Remove duplicates and limit
        filtered_links = list(set(filtered_links))[:100]  # Limit to 100 jobs
        
        self.logger.info(f"Found {len(filtered_links)} job links")
        return filtered_links
    
    def extract_job_data(self, job_url, selectors=None):
        """Enhanced job data extraction with smart fallbacks"""
        if not selectors:
            selectors = self.get_default_selectors()
        
        soup = self.get_page_content(job_url)
        if not soup:
            return None
        
        # Extract basic data
        job_data = {
            'company_name': self.extract_text(soup, selectors['company_name']),
            'job_title': self.extract_text(soup, selectors['job_title']),
            'work_location': self.extract_work_location(soup, selectors['work_location']),
            'job_location': self.extract_text(soup, selectors['job_location']),
            'experience': self.extract_experience(soup, selectors['experience']),
            'job_description': self.extract_long_text(soup, selectors['job_description']),
            'responsibilities': self.extract_long_text(soup, selectors['responsibilities']),
            'qualifications': self.extract_long_text(soup, selectors['qualifications']),
            'apply_link': job_url
        }
        
        # Smart fallbacks for missing data
        job_data = self.apply_smart_fallbacks(soup, job_data)
        job_data = self.clean_job_data(job_data)
        
        return job_data
    
    def extract_work_location(self, soup, selectors):
        """Extract work location with pattern matching"""
        text = self.extract_text(soup, selectors)
        if text == "Not specified":
            # Look for common remote/hybrid patterns in any text
            page_text = soup.get_text().lower()
            if 'remote' in page_text:
                return 'Remote'
            elif 'hybrid' in page_text:
                return 'Hybrid'
            elif 'on-site' in page_text or 'onsite' in page_text:
                return 'On-site'
        return text
    
    def extract_experience(self, soup, selectors):
        """Extract experience with pattern matching"""
        text = self.extract_text(soup, selectors)
        if text == "Not specified":
            # Look for experience patterns in page text
            page_text = soup.get_text()
            exp_patterns = [
                r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
                r'(\d+)\s*to\s*(\d+)\s*years?',
                r'entry\s*level|junior|senior|mid\s*level'
            ]
            for pattern in exp_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    return match.group(0)
        return text
    
    def extract_long_text(self, soup, selectors):
        """Extract longer text content like descriptions"""
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator='\n', strip=True)
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 50:  # Minimum length for meaningful content
                    return text[:2000]  # Limit length
        return "Not specified"
    
    def apply_smart_fallbacks(self, soup, job_data):
        """Apply smart fallbacks for missing data"""
        # If company name is missing, try to extract from URL or title
        if job_data['company_name'] == "Not specified":
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                # Common patterns: "Job Title - Company Name" or "Company Name | Job Title"
                if ' - ' in title_text:
                    job_data['company_name'] = title_text.split(' - ')[-1].strip()
                elif ' | ' in title_text:
                    job_data['company_name'] = title_text.split(' | ')[0].strip()
        
        # If job title is missing, try title tag
        if job_data['job_title'] == "Not specified":
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                if ' - ' in title_text:
                    job_data['job_title'] = title_text.split(' - ')[0].strip()
                elif ' | ' in title_text:
                    job_data['job_title'] = title_text.split(' | ')[-1].strip()
        
        return job_data
    
    def get_default_selectors(self):
        """Enhanced CSS selectors for better job data extraction"""
        return {
            'company_name': [
                'h1', '.company-name', '.company-title', '.employer-name',
                '[class*="company"]', '[data-testid*="company"]',
                '.brand-name', '.organization-name', 'title'
            ],
            'job_title': [
                'h1', 'h2', '.job-title', '.position-title', '.role-title',
                '[class*="title"]', '[class*="role"]', '[class*="position"]',
                '[data-testid*="title"]', '.posting-headline'
            ],
            'work_location': [
                '[class*="remote"]', '[class*="hybrid"]', '[class*="onsite"]',
                '[class*="work-type"]', '[class*="employment-type"]',
                '.location-type', '.work-arrangement'
            ],
            'job_location': [
                '[class*="location"]', '[class*="city"]', '[class*="address"]',
                '.job-location', '.office-location', '.workplace-location',
                '[data-testid*="location"]', '.geographic-location'
            ],
            'experience': [
                '[class*="experience"]', '[class*="years"]', '[class*="level"]',
                '.experience-level', '.seniority-level', '.career-level',
                '[class*="seniority"]', '.job-level'
            ],
            'job_description': [
                '[class*="description"]', '[class*="summary"]', '.job-content',
                '.posting-content', '.role-description', '.job-details',
                '.content', 'main', '.description-text'
            ],
            'responsibilities': [
                '[class*="responsibilities"]', '[class*="duties"]', 
                '[class*="role"]', '.what-you-will-do', '.key-responsibilities',
                '.job-responsibilities', '.role-duties'
            ],
            'qualifications': [
                '[class*="qualifications"]', '[class*="requirements"]', 
                '[class*="skills"]', '.what-we-need', '.required-skills',
                '.job-requirements', '.minimum-qualifications'
            ]
        }
    
    def extract_text(self, soup, selectors):
        """Enhanced text extraction with better filtering"""
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator=' ', strip=True)
                # Clean and validate text
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Skip if too short, too long, or contains unwanted content
                if (text and len(text) > 2 and len(text) < 5000 and 
                    not text.lower().startswith(('cookie', 'privacy', 'terms'))):
                    return text
        
        # Fallback: try to extract from page title or meta description
        if 'title' in str(selectors):
            title = soup.find('title')
            if title:
                return title.get_text(strip=True)
        
        return "Not specified"
    
    def clean_job_data(self, job_data):
        """Clean and validate extracted job data"""
        for key, value in job_data.items():
            if isinstance(value, str):
                # Remove extra whitespace and newlines
                value = re.sub(r'\s+', ' ', value).strip()
                # Limit description length
                if key in ['job_description', 'responsibilities', 'qualifications'] and len(value) > 1000:
                    value = value[:1000] + "..."
                job_data[key] = value
        
        return job_data
    
    def scrape_jobs(self, career_url, custom_selectors=None, max_jobs=50):
        """Main method to scrape all jobs from a career website"""
        self.logger.info(f"Starting job scraping for: {career_url}")
        
        # Find job links
        job_links = self.find_job_links(career_url)
        
        if not job_links:
            self.logger.warning("No job links found. Try using Selenium for dynamic content.")
            return []
        
        # Limit number of jobs to scrape
        job_links = job_links[:max_jobs]
        
        scraped_jobs = []
        for i, job_url in enumerate(job_links, 1):
            self.logger.info(f"Scraping job {i}/{len(job_links)}: {job_url}")
            
            job_data = self.extract_job_data(job_url, custom_selectors)
            if job_data:
                scraped_jobs.append(job_data)
            
            # Respectful delay
            time.sleep(1)
        
        self.jobs.extend(scraped_jobs)
        self.logger.info(f"Successfully scraped {len(scraped_jobs)} jobs")
        return scraped_jobs
    
    def save_to_excel(self, filename="job_postings.xlsx"):
        """Save scraped jobs to Excel file"""
        if not self.jobs:
            self.logger.warning("No jobs to save")
            return
        
        df = pd.DataFrame(self.jobs)
        
        # Reorder columns
        column_order = [
            'company_name', 'job_title', 'work_location', 'job_location',
            'experience', 'job_description', 'responsibilities', 
            'qualifications', 'apply_link'
        ]
        
        df = df.reindex(columns=column_order)
        
        # Remove duplicates based on job title and company
        df = df.drop_duplicates(subset=['job_title', 'company_name'], keep='first')
        
        df.to_excel(filename, index=False, engine='openpyxl')
        self.logger.info(f"Saved {len(df)} jobs to {filename}")
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

# Example usage and customization
def scrape_company_jobs(career_url, use_selenium=False, custom_selectors=None):
    """Convenience function to scrape jobs from a company career page"""
    scraper = JobScraper(use_selenium=use_selenium)
    
    try:
        jobs = scraper.scrape_jobs(career_url, custom_selectors)
        scraper.save_to_excel(f"jobs_{urlparse(career_url).netloc}.xlsx")
        return jobs
    finally:
        scraper.close()

if __name__ == "__main__":
    # Example usage
    career_url = input("Enter company career page URL: ")
    use_dynamic = input("Use Selenium for dynamic content? (y/n): ").lower() == 'y'
    
    jobs = scrape_company_jobs(career_url, use_selenium=use_dynamic)
    print(f"Scraped {len(jobs)} jobs successfully!")