from job_scraper import JobScraper, scrape_company_jobs

# Example 1: Basic usage for static websites
def example_basic_scraping():
    """Example of basic job scraping for static websites"""
    career_url = "https://example-company.com/careers"
    jobs = scrape_company_jobs(career_url, use_selenium=False)
    print(f"Found {len(jobs)} jobs")

# Example 2: Dynamic website with Selenium
def example_dynamic_scraping():
    """Example for JavaScript-heavy career pages"""
    career_url = "https://dynamic-company.com/jobs"
    jobs = scrape_company_jobs(career_url, use_selenium=True)
    print(f"Found {len(jobs)} jobs")

# Example 3: Custom selectors for specific websites
def example_custom_selectors():
    """Example with custom CSS selectors for specific website structure"""
    
    # Custom selectors for a specific company's career page
    custom_selectors = {
        'company_name': ['.company-header h1', '.brand-name'],
        'job_title': ['.job-posting-title', 'h1.title'],
        'work_location': ['.work-type', '.remote-indicator'],
        'job_location': ['.job-location', '.office-location'],
        'experience': ['.experience-level', '.years-required'],
        'job_description': ['.job-description', '.role-summary'],
        'responsibilities': ['.responsibilities', '.what-you-will-do'],
        'qualifications': ['.requirements', '.what-we-need']
    }
    
    scraper = JobScraper(use_selenium=True)
    try:
        jobs = scraper.scrape_jobs(
            "https://specific-company.com/careers", 
            custom_selectors=custom_selectors,
            max_jobs=30
        )
        scraper.save_to_excel("custom_company_jobs.xlsx")
    finally:
        scraper.close()

# Example 4: Batch scraping multiple companies
def example_batch_scraping():
    """Example of scraping multiple company career pages"""
    
    companies = [
        {"url": "https://company1.com/careers", "use_selenium": False},
        {"url": "https://company2.com/jobs", "use_selenium": True},
        {"url": "https://company3.com/opportunities", "use_selenium": False}
    ]
    
    all_jobs = []
    
    for company in companies:
        print(f"Scraping {company['url']}...")
        jobs = scrape_company_jobs(
            company['url'], 
            use_selenium=company['use_selenium']
        )
        all_jobs.extend(jobs)
    
    # Save all jobs to single file
    scraper = JobScraper()
    scraper.jobs = all_jobs
    scraper.save_to_excel("all_companies_jobs.xlsx")
    print(f"Total jobs scraped: {len(all_jobs)}")

# Example 5: Advanced configuration
def example_advanced_usage():
    """Example with advanced configuration options"""
    
    scraper = JobScraper(use_selenium=True, headless=False)  # Show browser
    
    try:
        # Custom job link selectors for finding job postings
        job_link_selectors = [
            'a[href*="/job/"]',
            '.job-card a',
            '.position-link'
        ]
        
        # Find job links with custom selectors
        career_url = "https://example.com/careers"
        soup = scraper.get_page_content(career_url)
        
        job_links = []
        for selector in job_link_selectors:
            links = soup.select(selector) if soup else []
            for link in links:
                href = link.get('href')
                if href:
                    from urllib.parse import urljoin
                    job_links.append(urljoin(career_url, href))
        
        # Scrape each job with custom data extraction
        for job_url in job_links[:10]:  # Limit to 10 jobs
            job_data = scraper.extract_job_data(job_url)
            if job_data:
                scraper.jobs.append(job_data)
        
        scraper.save_to_excel("advanced_scraping_results.xlsx")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    print("Job Scraper Examples")
    print("1. Basic static website scraping")
    print("2. Dynamic website with Selenium")
    print("3. Custom selectors example")
    print("4. Batch scraping multiple companies")
    print("5. Advanced configuration")
    
    choice = input("Choose example (1-5): ")
    
    if choice == "1":
        example_basic_scraping()
    elif choice == "2":
        example_dynamic_scraping()
    elif choice == "3":
        example_custom_selectors()
    elif choice == "4":
        example_batch_scraping()
    elif choice == "5":
        example_advanced_usage()
    else:
        print("Invalid choice")