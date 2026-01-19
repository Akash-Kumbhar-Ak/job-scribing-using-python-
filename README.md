# Web Job Scraping Tool

A comprehensive Python tool for scraping job postings from company career websites. Supports both static and JavaScript-rendered dynamic websites.

## Features

- **Dual Mode Support**: Works with both static (requests + BeautifulSoup) and dynamic (Selenium) websites
- **Automatic Job Discovery**: Finds job listing links from career pages automatically
- **Comprehensive Data Extraction**: Extracts 9 key job fields including title, location, requirements, etc.
- **Excel Export**: Saves results to formatted Excel files
- **Duplicate Prevention**: Removes duplicate job postings
- **Ethical Scraping**: Includes respectful delays and proper headers
- **Customizable Selectors**: Easy to adapt for different website structures

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Install ChromeDriver for Selenium:
```bash
pip install webdriver-manager
```

## Quick Start

### Basic Usage
```python
from job_scraper import scrape_company_jobs

# For static websites
jobs = scrape_company_jobs("https://company.com/careers", use_selenium=False)

# For dynamic websites
jobs = scrape_company_jobs("https://company.com/jobs", use_selenium=True)
```

### Interactive Mode
```bash
python job_scraper.py
```

## Extracted Job Fields

1. **Company Name** - Name of the hiring company
2. **Job Title** - Position title/role name
3. **Work Location** - Remote/Hybrid/On-site designation
4. **Job Location** - City, State, Country
5. **Experience** - Required years or experience level
6. **Job Description** - Full job description text
7. **Responsibilities** - Key job responsibilities
8. **Qualifications** - Required skills and qualifications
9. **Apply Link** - Direct link to job application

## Advanced Usage

### Custom Selectors
```python
from job_scraper import JobScraper

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
jobs = scraper.scrape_jobs("https://company.com/careers", custom_selectors)
scraper.save_to_excel("custom_jobs.xlsx")
scraper.close()
```

### Batch Scraping
```python
companies = [
    {"url": "https://company1.com/careers", "use_selenium": False},
    {"url": "https://company2.com/jobs", "use_selenium": True}
]

all_jobs = []
for company in companies:
    jobs = scrape_company_jobs(company['url'], company['use_selenium'])
    all_jobs.extend(jobs)
```

## Customization Guide

### For Different Career Websites

1. **Identify Website Type**:
   - Static: Content loads immediately with page
   - Dynamic: Content loads via JavaScript

2. **Find Job Link Patterns**:
   - Look for common URL patterns: `/job/`, `/career/`, `/position/`
   - Inspect job listing containers

3. **Customize Selectors**:
   - Use browser developer tools to find CSS selectors
   - Test selectors in browser console: `document.querySelector('selector')`

### Common Website Patterns

**LinkedIn-style**: 
```python
selectors = {
    'job_title': ['.job-title', 'h1'],
    'company_name': ['.company-name', '.hiring-company'],
    'job_location': ['.job-location', '.location']
}
```

**Greenhouse/Lever**:
```python
selectors = {
    'job_title': ['.posting-headline h2'],
    'job_location': ['.location'],
    'job_description': ['.posting-content']
}
```

## Configuration Options

### JobScraper Parameters
- `use_selenium`: Boolean - Use Selenium for dynamic content
- `headless`: Boolean - Run browser in headless mode
- `max_jobs`: Integer - Maximum number of jobs to scrape
- `custom_selectors`: Dict - Custom CSS selectors

### Selenium Options
- Headless mode (default: True)
- Custom wait times
- Browser window size
- User agent customization

## Troubleshooting

### Common Issues

1. **No jobs found**:
   - Try using Selenium (`use_selenium=True`)
   - Check if website requires login
   - Verify career page URL is correct

2. **Missing data fields**:
   - Customize selectors for specific website
   - Check if content is loaded dynamically

3. **ChromeDriver issues**:
   - Update Chrome browser
   - Reinstall webdriver-manager: `pip install --upgrade webdriver-manager`

4. **Rate limiting**:
   - Increase delays between requests
   - Use different user agents
   - Implement proxy rotation

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

scraper = JobScraper(use_selenium=True, headless=False)
# Browser will be visible for debugging
```

## Best Practices

1. **Respect robots.txt**: Check website's robots.txt file
2. **Use delays**: Don't overwhelm servers with rapid requests
3. **Handle errors**: Implement proper error handling
4. **Test selectors**: Verify selectors work before large scraping jobs
5. **Monitor changes**: Website structures change; update selectors accordingly

## Legal Considerations

- Always check website terms of service
- Respect rate limits and robots.txt
- Use scraped data responsibly
- Consider reaching out to companies for API access

## Output Format

Excel file contains columns:
- Company Name
- Job Title  
- Work Location
- Job Location
- Experience
- Job Description
- Responsibilities
- Qualifications
- Apply Link

## Examples

See `examples.py` for detailed usage examples including:
- Basic static website scraping
- Dynamic website handling
- Custom selector configuration
- Batch processing multiple companies
- Advanced configuration options

## Support

For issues or questions:
1. Check troubleshooting section
2. Review examples.py for usage patterns
3. Test with simple websites first
4. Use debug mode to identify issues