from job_scraper import JobScraper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def scrape_hcl_jobs():
    """Specific scraper for HCL careers page"""
    
    base_url = "https://careers.hcltech.com/go/India/9553955/"
    
    print("Scraping HCL Tech careers...")
    
    # Use requests first to check the page structure
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"Page loaded successfully: {soup.find('title').get_text()}")
        
        # Look for actual job postings - HCL might use different patterns
        job_elements = []
        
        # Try different selectors for HCL
        job_selectors = [
            '.job-item', '.position-item', '.career-item',
            '[class*="job"]', '[class*="position"]', '[class*="career"]',
            'div[data-job-id]', 'tr[data-job-id]',
            '.search-results .item', '.job-list .item'
        ]
        
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                job_elements.extend(elements)
        
        if not job_elements:
            # If no job elements found, the page might be dynamic
            print("No job elements found with static scraping. Trying Selenium...")
            return scrape_with_selenium(base_url)
        
        # Extract job data from found elements
        jobs = []
        for element in job_elements[:10]:  # Limit to 10 jobs
            job_data = extract_job_from_element(element, base_url)
            if job_data:
                jobs.append(job_data)
        
        if jobs:
            print(f"Successfully extracted {len(jobs)} jobs")
            save_jobs_to_excel(jobs, "hcl_jobs.xlsx")
            
            # Display sample jobs
            for i, job in enumerate(jobs[:3], 1):
                print(f"\nJob {i}:")
                print(f"  Title: {job.get('job_title', 'N/A')}")
                print(f"  Location: {job.get('job_location', 'N/A')}")
                print(f"  Experience: {job.get('experience', 'N/A')}")
        else:
            print("No job data could be extracted")
            
    except Exception as e:
        print(f"Error: {e}")

def extract_job_from_element(element, base_url):
    """Extract job data from a job element"""
    try:
        job_data = {
            'company_name': 'HCL Technologies',
            'job_title': 'Not specified',
            'work_location': 'Not specified',
            'job_location': 'Not specified',
            'experience': 'Not specified',
            'job_description': 'Not specified',
            'responsibilities': 'Not specified',
            'qualifications': 'Not specified',
            'apply_link': base_url
        }
        
        # Extract job title
        title_selectors = ['h3', 'h4', '.title', '.job-title', 'a']
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if title_text and len(title_text) > 3:
                    job_data['job_title'] = title_text
                    break
        
        # Extract location
        location_selectors = ['.location', '.job-location', '[class*="location"]']
        for selector in location_selectors:
            loc_elem = element.select_one(selector)
            if loc_elem:
                loc_text = loc_elem.get_text(strip=True)
                if loc_text:
                    job_data['job_location'] = loc_text
                    break
        
        # Extract apply link
        link_elem = element.select_one('a[href]')
        if link_elem:
            href = link_elem.get('href')
            if href:
                job_data['apply_link'] = urljoin(base_url, href)
        
        return job_data
        
    except Exception as e:
        print(f"Error extracting job data: {e}")
        return None

def scrape_with_selenium(url):
    """Fallback to Selenium for dynamic content"""
    print("Using Selenium for dynamic content...")
    
    scraper = JobScraper(use_selenium=True, headless=False)  # Show browser for debugging
    
    try:
        jobs = scraper.scrape_jobs(url, max_jobs=10)
        if jobs:
            scraper.save_to_excel("hcl_jobs_selenium.xlsx")
            print(f"Selenium found {len(jobs)} jobs")
            return jobs
        else:
            print("Selenium also found no jobs")
            return []
    finally:
        scraper.close()

def save_jobs_to_excel(jobs, filename):
    """Save jobs to Excel file"""
    import pandas as pd
    
    df = pd.DataFrame(jobs)
    df.to_excel(filename, index=False)
    print(f"Jobs saved to {filename}")

if __name__ == "__main__":
    scrape_hcl_jobs()