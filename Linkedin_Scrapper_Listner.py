# Import necessary packages for web scraping and logging
import csv
import logging
import os
import random
import time
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import requests
import winsound

# Configure logging settings
logging.basicConfig(filename="scraping.log", level=logging.INFO)


def get_current_job_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("currentJobId", [None])[0]


def random_wait(min_seconds=15, max_seconds=60, message="Waiting"):
    """
    Wait for a random period of time.

    :param min_seconds: Minimum wait time in seconds.
    :param max_seconds: Maximum wait time in seconds.
    :param message: Message to display before waiting.
    """
    wait_time = random.uniform(min_seconds, max_seconds)
    print(f"{message} (Sec): {wait_time}")
    time.sleep(wait_time)


def random_scroll_in_element(driver, element_selector, scroll_count=5, min_wait=1, max_wait=3):
    """
    Perform random scrolling within a specified element on a webpage.

    :param driver: Selenium WebDriver instance.
    :param element_selector: CSS selector of the element to scroll within.
    :param scroll_count: Number of times to perform the scroll.
    :param min_wait: Minimum wait time in seconds between scrolls.
    :param max_wait: Maximum wait time in seconds between scrolls.
    """
    # JavaScript code to perform scrolling within an element
    scroll_script = """
        var element = arguments[0];
        var to = arguments[1];
        element.scrollTop = to;
    """

    # Find the element to scroll within
    scroll_element = driver.find_element(By.CSS_SELECTOR, element_selector)

    # Get the scroll height of the element
    scroll_height = driver.execute_script("return arguments[0].scrollHeight", scroll_element)

    # Perform random scrolling
    for _ in range(scroll_count):
        # Generate a random scroll position
        scroll_to = random.randint(0, scroll_height)

        # Scroll to the random position
        driver.execute_script(scroll_script, scroll_element, scroll_to)

        # Wait for a random time to mimic human behavior
        time.sleep(random.uniform(min_wait, max_wait))


def save_job_data(job_data, filename="jobs/jobs_data.csv"):
    # Define the path to the CSV file
    file_path = os.path.join(os.getcwd(), filename)

    # Check if file exists and if headers are needed
    file_exists = os.path.isfile(file_path)

    # Open the file in append mode
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=job_data.keys())

        # Write headers if the file is being created
        if not file_exists:
            writer.writeheader()

        # Write the job data
        writer.writerow(job_data)
        print("Job data appended to CSV.")


def check_for_429(driver):
    # You might need to adjust the detection logic based on the specific error page of the site
    if "429" in driver.title or "Too Many Requests" in driver.page_source:
        return True
    return False


def get_retry_after(url):
    try:
        response = requests.head(url)
        if response.status_code == 429:
            return response.headers.get('Retry-After', None)
    except requests.RequestException:
        return None

def play_beep():
    for _ in range(5):
        winsound.Beep(500, 1000)

def get_shuffled_job_ids_with_scroll_and_soup(driver):
    """
    Scrolls the job listing section, collects job IDs from LinkedIn job listing section using
    BeautifulSoup, and returns them shuffled.

    :param driver: Selenium WebDriver instance.
    :return: A shuffled list of job IDs.
    """
    # JavaScript function to scroll within an element
    scroll_script = """
        function scrollToEnd(element) {
            return new Promise((resolve, reject) => {
                let totalHeight = 0;
                let distance = 100; // Distance to scroll each step, can be adjusted
                let scrollInterval = setInterval(() => {
                    element.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= element.scrollHeight){
                        clearInterval(scrollInterval);
                        resolve();
                    }
                }, 100); // Interval time, can be adjusted
            });
        }
        return scrollToEnd(arguments[0]);
    """

    # Find the element containing the job listings
    job_listing_container = driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list")

    # Scroll to the end of the job listing container
    driver.execute_script(scroll_script, job_listing_container)

    # Wait for a moment to allow the page to load after scrolling
    time.sleep(5)  # Adjust this delay as necessary

    # Get page source and parse with BeautifulSoup
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')

    # Extract job IDs from the soup
    job_cards = soup.find_all("div", {"data-job-id": True})
    job_ids = [card['data-job-id'] for card in job_cards if 'data-job-id' in card.attrs]

    # Shuffle the list of job IDs
    random.shuffle(job_ids)
    print(f"Found : {len(job_ids)} Job IDs")

    return job_ids

# Use the function in your script
# job_ids_stack = get_shuffled_job_ids_with_scroll_and_soup(driver)

# def get_shuffled_job_ids_with_soup(driver):
#     """
#     Collects job IDs from LinkedIn job listing section using BeautifulSoup and returns them shuffled.
#
#     :param driver: Selenium WebDriver instance.
#     :return: A shuffled list of job IDs.
#     """
#     # Scroll to the bottom to ensure all jobs are loaded (may require fine-tuning)
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#
#     # Get page source and parse with BeautifulSoup
#     html_source = driver.page_source
#     soup = BeautifulSoup(html_source, 'html.parser')
#
#     # Extract job IDs from the soup
#     job_cards = soup.find_all("div", {"data-job-id": True})
#     job_ids = [card['data-job-id'] for card in job_cards if 'data-job-id' in card.attrs]
#
#     # Shuffle the list of job IDs
#     random.shuffle(job_ids)
#     print(f"Found : {len(job_ids)} Job IDs")
#     return job_ids

# def get_shuffled_job_ids(driver, scroll_pause_time=2):
#     """
#     Collects job IDs from LinkedIn job listing section and returns them shuffled.
#
#     :param driver: Selenium WebDriver instance.
#     :param scroll_pause_time: Time in seconds to pause after each scroll to allow content to load.
#     :return: A shuffled list of job IDs.
#     """
#     job_ids_set = set()
#     last_height = driver.execute_script("return document.body.scrollHeight")
#
#     while True:
#         # Scroll down to the bottom of the job listing section
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#
#         # Wait for new job cards to load
#         time.sleep(scroll_pause_time)
#
#         # Collect job card elements and job IDs
#         job_card_elements = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container--clickable")
#         for card in job_card_elements:
#             job_id = card.get_attribute('data-job-id')
#             if job_id:
#                 job_ids_set.add(job_id)
#
#         # Calculate new scroll height and compare with last scroll height
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height
#
#     # Convert set to list and shuffle
#     job_ids_list = list(job_ids_set)
#     random.shuffle(job_ids_list)
#     print(f"Found : {len(job_ids_list)} Job IDs")
#
#     return job_ids_list
def scroll_element(driver, element_selector):
    """
    Scroll an element to its bottom.

    :param driver: Selenium WebDriver instance.
    :param element_selector: CSS selector of the element to be scrolled.
    """
    scroll_script = "var element = document.querySelector(arguments[0]); element.scrollTop = element.scrollHeight;"
    driver.execute_script(scroll_script, element_selector)
def scrape_with_protection(driver, url, max_retries=5):
    base_wait = random.randint(300, 600)  # 10 minutes in seconds
    retry_wait = base_wait

    for attempt in range(max_retries):
        driver.get(url)
        if check_for_429(driver):
            retry_after = get_retry_after(url)
            if retry_after:
                wait_time = max(int(retry_after) + random.randint(300, 600),
                                retry_wait)  # Retry-After + 5 to 10 minutes
            else:
                wait_time = retry_wait

            print(f"429 detected. Waiting for {wait_time / 60} minutes before retrying.")
            time.sleep(wait_time)
            retry_wait += random.randint(300, 600)  # Increase by 5 to 10 minutes
        else:
            return  # Successful page load

    raise WebDriverException("Maximum retries reached for 429 handling.")


def start_scrape_listener(job_title: str, location: str):
    logging.info(f'Starting LinkedIn job scrape for "{job_title}" in "{location}"...')


    user_data_path = r"C:\Users\DamithWarnakulasuriy\AppData\Local\Google\Chrome\User Data"
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={user_data_path}")
    options.add_argument("profile-directory=Default")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    # options.add_argument("--disable-dev-shm-usage")

    chromedriver_path = r"C:\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=chromedriver_path)

    driver = webdriver.Chrome(service=service, options=options)
    try:
        scrape_with_protection(driver, f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}")
        random_wait(message="First Page Loading")
        get_shuffled_job_ids_with_scroll_and_soup(driver)
        last_job_id = None
        job_ids_stack = None
        while True:

            if job_ids_stack is None or len(job_ids_stack) == 0:
                job_ids_stack = get_shuffled_job_ids_with_scroll_and_soup(driver)
                #job_ids_stack = get_shuffled_job_ids(driver, random.randint(2,5))

                if last_job_id in job_ids_stack:
                    random_wait(message="Job Id Stack Waiting")

                    # Paginate to next page
                    page_buttons = driver.find_elements(By.CSS_SELECTOR,
                                                        "li.artdeco-pagination__indicator--number button")
                    current_page = driver.find_element(By.CSS_SELECTOR,
                                                       "li.artdeco-pagination__indicator--number.active").text
                    next_page = str(int(current_page) + 1)
                    next_page_button = next((btn for btn in page_buttons if btn.text == next_page), None)
                    if next_page_button:
                        # Click the next page button
                        next_page_button.click()
                        random_wait(message="Paginate Waiting", min_seconds=60, max_seconds=300)
                        job_ids_stack = get_shuffled_job_ids_with_scroll_and_soup(driver)
                        # job_ids_stack = get_shuffled_job_ids(driver, random.randint(2,5))

            current_url = driver.current_url
            current_job_id = get_current_job_id(current_url)

            if current_job_id is not None and current_job_id == last_job_id:
                # Change the Page Here
                job_id = job_ids_stack.pop()
                print(f"Job Ids Stack Size {len(job_ids_stack)}.")

                try:
                    card = driver.find_element(By.CSS_SELECTOR, f"div[data-job-id='{job_id}']")
                    driver.execute_script("arguments[0].scrollIntoView();", card)
                    card.click()
                    random_wait(message="Scroll to Job")

                except Exception as e:
                    print(f"Error processing card with job ID {job_id}: {e}")

            if current_job_id is not None and current_job_id != last_job_id:
                print(f"Job ID changed to {current_job_id}.")
                # Scrolling the job details section
                scroll_element(driver, ".jobs-search__job-details--wrapper")

                # Wait for the content to load after scrolling
                random_wait(message="Ready to Scrape Waiting")

                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract title
                title_tag = soup.find("span", class_="job-details-jobs-unified-top-card__job-title-link")
                title = title_tag.text.strip() if title_tag else ""

                # Extract company, location, published date, and number of applicants
                info_tag = soup.find("div",
                                     class_="job-details-jobs-unified-top-card__primary-description-without-tagline")
                if info_tag:
                    info_parts = [part.strip() for part in info_tag.text.split('·')]
                    company = info_parts[0] if len(info_parts) > 0 else ""
                    location = info_parts[1] if len(info_parts) > 1 else ""
                    published_date = info_parts[2] if len(info_parts) > 2 else ""
                    num_applicants = info_parts[3] if len(info_parts) > 3 else ""

                else:
                    company, location, published_date, num_applicants = "", "", "", ""

                # Extract job description
                desc_tag = soup.find("div", class_="jobs-description__content jobs-description-content")
                job_description = desc_tag.text.strip() if desc_tag else ""

                # Find all skills tags
                skills_tags = soup.find_all(lambda tag: tag.name == "a" and any(
                    "job-details-how-you-match__skills" in class_ for class_ in tag.get("class", [])))

                # Extract skills text from each tag and concatenate
                skills = ', '.join(tag.get_text().strip() for tag in skills_tags) if skills_tags else ""

                # Print extracted data
                print(f"Title: {title}")
                print(f"Company: {company}")
                print(f"Location: {location}")
                print(f"Published Date: {published_date}")
                print(f"Number of Applicants: {num_applicants}")
                print(f"Job Description: {job_description}")
                print(f"Skills: {skills}")
                print(f"Job URL: {current_url}")

                last_job_id = current_job_id

                job_data = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "published_date": published_date,
                    "num_applicants": num_applicants,
                    "description": job_description,
                    "skills": skills,
                    "url": current_url
                }

                # Save the data to a CSV file
                save_job_data(job_data)
                random_scroll_in_element(driver, "div.scaffold-layout__detail")
                random_wait(message="Wait ofter completion")
            random_wait(1,5,message="Next Try Waiting")

    finally:
        play_beep()
        driver.quit()


start_scrape_listener("", "Sri Lanka")
