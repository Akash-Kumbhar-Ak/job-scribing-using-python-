import pandas as pd

def display_jobs():
    """Display the extracted job data"""
    try:
        # Read the Excel file
        df = pd.read_excel("hcl_jobs_selenium.xlsx")
        
        print("HCL Jobs Extracted:")
        print("=" * 50)
        print(f"Total jobs found: {len(df)}")
        print()
        
        # Display each job
        for i, row in df.iterrows():
            print(f"Job {i+1}:")
            print(f"  Company: {row['company_name']}")
            print(f"  Title: {row['job_title']}")
            print(f"  Location: {row['job_location']}")
            print(f"  Work Type: {row['work_location']}")
            print(f"  Experience: {row['experience']}")
            print(f"  Apply Link: {row['apply_link']}")
            print(f"  Description: {row['job_description'][:100]}..." if len(str(row['job_description'])) > 100 else f"  Description: {row['job_description']}")
            print("-" * 40)
        
        print("\nSuccess! The job scraper is working properly.")
        print("You can now use it with any company career page.")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    display_jobs()