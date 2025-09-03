import requests
from bs4 import BeautifulSoup
import csv
import time # Import the time module for delays

def scrape_all_internshala_pages():
    """
    Scrapes all pages of internship data from Internshala and saves it to a single CSV file.
    """
    # Open the CSV file once, before the loop starts
    with open('internships.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row only once
        writer.writerow(['Title', 'Company', 'Location', 'Stipend', 'Skills'])

        # Loop through a large range of pages. The loop will break when a page has no internships.
        for page_number in range(1, 101): # Assuming there are no more than 100 pages
            URL = f"https://internshala.com/internships/page-{page_number}"
            
            print(f"Scraping page {page_number}...")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
            }
            
            try:
                response = requests.get(URL, headers=headers)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error on page {page_number}: {e}")
                break # Stop if a page request fails

            soup = BeautifulSoup(response.content, 'html.parser')
            
            internship_container = soup.find('div', id='internship_list_container')
            if not internship_container:
                print(f"Could not find internship container on page {page_number}. Stopping.")
                break
                
            internships = internship_container.find_all('div', class_='internship_meta')

            # This is the crucial stopping condition
            if not internships:
                print(f"No more internships found on page {page_number}. Scraping finished.")
                break

            # Process all internships found on the current page
            for internship in internships:
                title_element = internship.select_one('h3')
                title = title_element.get_text(strip=True) if title_element else 'N/A'

                company_element = internship.find('div', class_='company_name')
                company = company_element.get_text(strip=True) if company_element else 'N/A'

                location_element = internship.find('div', class_='row-1-item locations')
                location = location_element.get_text(strip=True) if location_element else 'Work from Home'

                stipend_element = internship.find('a', class_='stipend')
                stipend = stipend_element.get_text(strip=True) if stipend_element else 'No Stipend'
                
                skills_container = internship.find('div', class_='job_skills')
                if skills_container:
                    skill_elements = skills_container.find_all('div', class_='skill_container')
                    skills = ', '.join([skill.get_text(strip=True) for skill in skill_elements])
                else:
                    skills = 'N/A'
                
                # Write the data for the current internship to the CSV
                writer.writerow([title, company, location, stipend, skills])
        
            # Be a polite scraper and wait for a second before the next page
            time.sleep(1)

    print(f"✅ All pages scraped successfully! Data saved to internships.csv")

if __name__ == '__main__':
    scrape_all_internshala_pages()