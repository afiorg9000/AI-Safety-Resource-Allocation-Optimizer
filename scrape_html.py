import time
import requests
import openai
import csv
from bs4 import BeautifulSoup
import re

openai.api_key = os.environ.get("OPENAI_API_KEY")

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    for script_or_style in soup(['script', 'style']):
        script_or_style.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def parse_html_with_llm(html_content):
    try:
        chunk_size = 2000
        content_length = len(html_content)
        chunked_responses = []

        for i in range(0, content_length, chunk_size):
            chunk = html_content[i:i + chunk_size]
            
            retry = True
            while retry:
                try:
                    print(f"Processing chunk {i // chunk_size + 1} of {content_length // chunk_size + 1}...")
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that extracts information from HTML."},
                            {"role": "user", "content": f"Extract the project title, funding raised, funding goal, and project summary from the following HTML:\n\n{chunk}"}
                        ],
                        max_tokens=1000
                    )
                    chunked_responses.append(response['choices'][0]['message']['content'])
                    retry = False
                    print("Successfully processed chunk.")

                except openai.error.RateLimitError as e:
                    wait_time = float(re.search(r'Please try again in (\d+\.\d+)s', str(e)).group(1))
                    print(f"Rate limit error: {e}. Waiting for {wait_time} seconds before retrying.")
                    time.sleep(wait_time)

                except openai.error.InvalidRequestError as e:
                    print(f"Error during LLM parsing: {e}")
                    return None


        return "\n".join(chunked_responses)

    except openai.error.InvalidRequestError as e:
        print(f"Error during LLM parsing: {e}")
        return None


def extract_project_slugs(file_path):
    print(f"Extracting slugs from {file_path}...")
    slugs = []
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')


    projects = soup.find_all('div', class_='overflow-hidden')

    for project in projects:
        try:
            link = project.find('a', class_='group')['href']
            if link:
                slugs.append(link.split('/')[-1])
                print(f"Found slug: {link.split('/')[-1]}")
        except (AttributeError, TypeError) as e:
            print(f"Error extracting slug: {e}")

    print(f"Extracted {len(slugs)} slugs.")
    return slugs


def extract_project_details_with_llm(base_url, slugs, output_csv):
    print(f"Starting extraction of project details. Saving results to {output_csv}...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Project Title', 'Funding Raised', 'Funding Goal', 'Project Summary'])
        writer.writeheader()

        for slug in slugs:
            project_url = base_url + slug
            print(f"Fetching project page: {project_url}")
            response = requests.get(project_url)
            if response.status_code == 200:
                print(f"Successfully fetched {project_url}.")

                cleaned_html = clean_html(response.text)
                

                llm_result = parse_html_with_llm(cleaned_html)

                if llm_result:
                    project_data = {
                        'Project Title': '',
                        'Funding Raised': '',
                        'Funding Goal': '',
                        'Project Summary': ''
                    }

                    lines = llm_result.splitlines()
                    for line in lines:
                        if 'Title:' in line:
                            project_data['Project Title'] = line.split('Title:')[1].strip()
                        elif 'Funding Raised:' in line:
                            project_data['Funding Raised'] = line.split('Funding Raised:')[1].strip()
                        elif 'Funding Goal:' in line:
                            project_data['Funding Goal'] = line.split('Funding Goal:')[1].strip()
                        elif 'Summary:' in line or 'Project Summary:' in line:
                            project_data['Project Summary'] = line.split(':', 1)[1].strip()

                    if any(value for value in project_data.values()):
                        writer.writerow(project_data)
                        print(f"Successfully processed {slug}")
                else:
                    print(f"Failed to parse content from {project_url}")

            else:
                print(f"Failed to retrieve the project page. Status code: {response.status_code}")

    print(f"Scraping completed. Data saved to '{output_csv}'.")

base_url = 'https://manifund.org/projects/'

ai_gov_slugs = extract_project_slugs('ai-gov.html')
tais_slugs = extract_project_slugs('tais.html')

all_slugs = ai_gov_slugs + tais_slugs

extract_project_details_with_llm(base_url, all_slugs, 'aisf_projects.csv')
