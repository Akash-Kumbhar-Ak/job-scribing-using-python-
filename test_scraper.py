from job_scraper import JobScraper
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_job_scraper():
    """Test the job scraper with a sample career page"""
    
    print("Testing Job Scraper...")
    print("=" * 50)
    
    # Test with a well-known career page
    test_urls = [
        "https://careers.google.com/jobs/results/",
        "https://www.microsoft.com/en-us/careers/search",
        "https://jobs.lever.co/",
        "https://boards.greenhouse.io/"
    ]
    
    scraper = JobScraper(use_selenium=True, headless=True)
    
    try:
        for url in test_urls:
            print(f"\nTesting URL: {url}")
            print("-" * 30)
            
            # Find job links
            job_links = scraper.find_job_links(url)
            print(f"Found {len(job_links)} job links")
            
            if job_links:
                # Test first job link
                first_job = job_links[0]
                print(f"Testing job extraction from: {first_job}")
                
                job_data = scraper.extract_job_data(first_job)
                
                if job_data:
                    print("Extracted data:")
                    for key, value in job_data.items():
                        print(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
                else:
                    print("No data extracted")
            else:
                print("No job links found")
            
            print("\n" + "="*50)
    
    except Exception as e:
        print(f"Error during testing: {e}")
    
    finally:
        scraper.close()

def interactive_test():
    """Interactive test mode"""
    print("Interactive Job Scraper Test")
    print("=" * 30)
    
    career_url = input("Enter career page URL: ").strip()
    if not career_url:
        print("No URL provided. Exiting.")
        return
    
    use_selenium = input("Use Selenium for dynamic content? (y/n): ").lower().startswith('y')
    
    scraper = JobScraper(use_selenium=use_selenium, headless=False)
    
    try:
        print(f"\nScraping jobs from: {career_url}")
        jobs = scraper.scrape_jobs(career_url, max_jobs=5)  # Limit to 5 for testing
        
        if jobs:
            print(f"\nSuccessfully scraped {len(jobs)} jobs:")
            for i, job in enumerate(jobs, 1):
                print(f"\nJob {i}:")
                print(f"  Title: {job.get('job_title', 'N/A')}")
                print(f"  Company: {job.get('company_name', 'N/A')}")
                print(f"  Location: {job.get('job_location', 'N/A')}")
                print(f"  Work Type: {job.get('work_location', 'N/A')}")
            
            # Save to Excel
            scraper.save_to_excel("test_jobs.xlsx")
            print(f"\nJobs saved to test_jobs.xlsx")
        else:
            print("No jobs found. Try using Selenium or check the URL.")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    print("Job Scraper Test Options:")
    print("1. Automated test with sample URLs")
    print("2. Interactive test with your URL")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        test_job_scraper()
    elif choice == "2":
        interactive_test()
    else:
        print("Invalid choice")