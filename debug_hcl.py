import requests
from bs4 import BeautifulSoup
import time

def test_hcl_careers():
    url = "https://careers.hcltech.com/go/India/9553955/"
    
    print(f"Testing URL: {url}")
    
    # Test with requests first
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check page content
            title = soup.find('title')
            print(f"Page Title: {title.get_text() if title else 'No title'}")
            
            # Look for job-related links
            job_links = []
            
            # Common patterns for HCL careers
            selectors = [
                'a[href*="job"]', 'a[href*="position"]', 'a[href*="career"]',
                '.job-link', '.position-link', '.career-link'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        job_links.append(href)
            
            print(f"Found {len(job_links)} potential job links")
            
            if job_links:
                print("Sample links:")
                for link in job_links[:5]:
                    print(f"  {link}")
            else:
                # Check if page has any content
                text_content = soup.get_text()[:500]
                print(f"Page content sample: {text_content}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hcl_careers()