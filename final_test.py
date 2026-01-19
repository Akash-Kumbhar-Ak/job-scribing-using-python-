from job_scraper import scrape_company_jobs

def test_working_scraper():
    """Demonstrate the working job scraper"""
    
    print("🚀 Job Scraper Test - HCL Technologies")
    print("=" * 50)
    
    # Test the scraper
    career_url = "https://careers.hcltech.com/go/India/9553955/"
    
    print(f"Scraping jobs from: {career_url}")
    print("Using Selenium for dynamic content...")
    
    try:
        jobs = scrape_company_jobs(career_url, use_selenium=True)
        
        if jobs:
            print(f"\n✅ SUCCESS! Found {len(jobs)} jobs")
            print("\nSample Jobs:")
            print("-" * 30)
            
            for i, job in enumerate(jobs[:3], 1):  # Show first 3 jobs
                print(f"\n{i}. {job.get('job_title', 'N/A')}")
                print(f"   Company: {job.get('company_name', 'N/A')}")
                print(f"   Location: {job.get('job_location', 'N/A')}")
                print(f"   Experience: {job.get('experience', 'N/A')}")
                
            print(f"\n📊 All jobs saved to: jobs_{career_url.split('//')[1].split('/')[0]}.xlsx")
            print("\n🎉 Job scraper is working perfectly!")
            print("\nYou can now use it with any company career page:")
            print("  python job_scraper.py")
            
        else:
            print("❌ No jobs found. The website might have changed structure.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_working_scraper()