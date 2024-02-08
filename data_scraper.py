import requests
from bs4 import BeautifulSoup
import json
import os
from model.job import Job


def get_job_description(job_url):
    response = requests.get(job_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', type='application/ld+json')
    if script_tag:
        json_content = script_tag.string.strip()
        job_data = json.loads(json_content)
        description = job_data.get('description', 'Description not available')
        description_text = BeautifulSoup(description, 'html.parser').get_text(separator=" ")
        return description_text
    else:
        return "Description not available"


def extract_job_details(element):
    parent = element.parent
    if parent and len(parent.contents) >= 2:
        job_name_tag = parent.find('h2')
        location_span = parent.find('span', class_='job-location-search')
        if job_name_tag and location_span:
            job_name = job_name_tag.text.strip()
            location_text = location_span.text.strip()
            if 'Remote -' in location_text:
                location_text = location_text.replace('Remote - ', '')
            location_parts = location_text.split(',')
            if len(location_parts) == 2:
                city, country = location_parts
            elif len(location_parts) == 1:
                city = ''
                country = location_parts[0]
            else:
                city = ''
                country = ''
            job_url = f"https://jobs.dell.com{parent.find('a')['href']}"
            job_description = get_job_description(job_url)

            return {
                'Job Title': job_name,
                'City': city.strip(),
                'Country': country.strip(),
                'Job Description': job_description
            }
    return None


def scrape_job_details(url):
    job_details = []
    page_num = 1

    while True:
        page_url = f"{url}?p={page_num}"
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        elements_with_data_job_id = soup.find_all(attrs={'data-job-id': True, 'data-org-id': True})

        if not elements_with_data_job_id:
            break

        for element in elements_with_data_job_id:
            job_detail = extract_job_details(element)
            if job_detail:
                job_details.append(job_detail)

        page_num += 1

    return job_details


def save_to_json(job_details):
    if not os.path.exists('json_files'):
        os.makedirs('json_files')

    filename = "json_files/all_jobs.json"
    with open(filename, 'w') as f:
        json.dump(job_details, f, indent=4)


def insert_jobs_from_json(json_file):
    with open(json_file, 'r') as f:
        job_details_list = json.load(f)

    for job_details in job_details_list:
        job_title = job_details.get('Job Title', '')
        country = job_details.get('Country', '')
        city = job_details.get('City', '')
        job_description = job_details.get('Job Description', '')
        job_model = Job()
        job_model.add_job(job_title, country, city, job_description)

if __name__ == "__main__":
    base_url = "https://jobs.dell.com/search-jobs"
    all_job_details = scrape_job_details(base_url)
    save_to_json(all_job_details)
    insert_jobs_from_json("json_files/all_jobs.json")
