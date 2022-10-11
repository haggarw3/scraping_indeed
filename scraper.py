from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
import re


# This functions takes to the first page for scraping
def scrape_phase1(driver, home_url, location, keyword):
    trial_counter = 0
    while trial_counter < 3:
        driver.get(home_url)
        time.sleep(2)
        driver.find_element_by_class_name('jobs-search-box__inner').click()
        time.sleep(2)
        driver.switch_to.active_element.send_keys(keyword)
        time.sleep(2)
        # driver.find_element_by_class_name('jobs-search-box__inner').click()
        driver.switch_to.active_element.send_keys(Keys.TAB)
        time.sleep(2)
        driver.switch_to.active_element.send_keys(location)
        time.sleep(2)
        driver.switch_to.active_element.send_keys(Keys.ENTER)
        time.sleep(2)
        if ("keywords" in driver.current_url) and ("location" in driver.current_url):
            # # CLICK ON THE Experience Level drop down
            # driver.find_elements_by_class_name('search-reusables__pill-button-caret-icon')[1].click()
            # # this index 1 is for the second element on the page that has a down arrow (in the
            # # group of date posted, experience level, company, job type)
            # time.sleep(2)
            # # Selecting Entry Level Jobs
            # driver.find_elements_by_class_name('search-reusables__value-label')[5].click()
            # time.sleep(2)
            # driver.find_elements_by_class_name('search-reusables__pill-button-caret-icon')[1].click()
            # time.sleep(2)
            try:
                driver.find_element_by_css_selector('.msg-overlay-bubble-header__details').click()
            except Exception as e:
                print(e)
            time.sleep(2)
            return driver, driver.current_url
        else:
            trial_counter += 1

    raise AttributeError("Scrape 1 errored")
    return


def scrape_phase2(driver, url, keyword, location):
    page1_url = url
    # This is for storing all the scraped data
    jobs_card_data = {}
    df = pd.DataFrame(columns=['company_name', 'position', 'location', 'url', 'date_posted', 'Number of applicants',
                              'full-time/part-time', 'seniority level', 'employees', 'descriptions',
                               'industry', 'top competitive skills', 'Hiring Trend Company Wide',
                               'Hiring Trend Company Wide-Engineering', 'Median Tenure'])

    # To find the max number of pages after the filter
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    time.sleep(2)
    try:
        max_pages = soup.find_all('button', {'aria-label': re.compile('Page*')})[-1].text
        max_pages = re.findall('\d+', max_pages)[0]
        max_pages = int(max_pages)
    except Exception as e:
        print(e)
        max_pages = 10
    print("maximum pages for this search: ", max_pages)

    # Incremental increase for each job posting - Will be used as the key for each key value pairs in job_cards_data
    counter = 1

    page = 1
    while page <= max_pages:  # scraping through all the pages
        print("Page: ", page)
        # time.sleep(2)
        # number of job cards in a page
        try:
            iterations_per_page = len(soup.find_all('li', {'class': re.compile('jobs-search-results*')}))
            print('Number of posting in this page: ', iterations_per_page)
        except AttributeError:
            print('Page did not load properly')
            try:
                driver.refresh()
                time.sleep(5)
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                iterations_per_page = len(soup.find_all('li', {'class': re.compile('jobs-search-results*')}))
                print('Number of posting in this page: ', iterations_per_page, '\n')
            except AttributeError:
                data = pd.DataFrame(jobs_card_data).T
                data.columns = ['company_name', 'position', 'location', 'url', 'date_posted', 'Number of applicants',
                              'full-time/part-time', 'seniority level', 'employees', 'descriptions',
                               'industry', 'top competitive skills', 'Hiring Trend Company Wide',
                               'Hiring Trend Company Wide-Engineering', 'Median Tenure']
                data = data.reset_index()
                data['search_keyword'] = keyword
                file = keyword + '_' + location + '.csv'
                data.to_csv(file)
                return data

        # html = driver.page_source
        # soup = BeautifulSoup(html, 'lxml')
        job_cards = soup.find_all('li', {'class': re.compile('jobs-search-results*')})

        # Now for each job card , we will start scraping the data
        for i in range(len(job_cards)):
            print('Job Card ', i+1, 'on Page ', page)
            try:
                job_card = job_cards[i]
                # Finding the ember ID to be able to click on it
                emberID = job_card.attrs['id']
                driver.find_element_by_id(emberID).click()
                time.sleep(1)

                # To scroll view so that the job card is on the top of the screen
                element = driver.find_element_by_id(emberID)
                driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(2)

                html_2 = driver.page_source
                soup_2 = BeautifulSoup(html_2, 'lxml')
                right_rail_soup = soup_2.find('section', {'class': 'jobs-search__right-rail'})
            except (AttributeError, IndexError):
                print('Page did not load')

            # Job position
            try:
                position = right_rail_soup.find('h2', {'class': 'jobs-details-top-card__job-title t-20 t-black t-normal'}).text
                position = re.findall('\w+', position)
                position = " ".join(position)
            except (AttributeError, IndexError):
                try:
                    position = right_rail_soup.find('h2', {'class': 't-24 t-bold'}).text
                    position = re.findall('\w+', position)
                    position = " ".join(position)
                except (AttributeError, IndexError):
                    print('Position not found for page: ', page, 'and job card #: ', i+1)
                    position = ''
            print(position)

            # company Name
            try:
                company_name = right_rail_soup.find('a', {'class': 'jobs-details-top-card__company-url t-black--light t-normal ember-view'}).text
                company_name = re.findall('\w+', company_name)
                company_name = " ".join(company_name)
            except (AttributeError, IndexError):
                company_name = ''
            if company_name == '':
                try:
                    company_name = right_rail_soup.find('a', {'class': 'ember-view t-black t-normal'}).text.strip()
                except (AttributeError, IndexError):
                    company_name = ''
                    print('Company Name not found for page: ', page, 'and job card #: ', i + 1)
            print(company_name)

            # location
            try:
                location = right_rail_soup.find_all('span', {'class': 'jobs-details-top-card__bullet'})[0].text.strip()
            except (AttributeError, IndexError):
                location = ''
            if location == '':
                try:
                    location = right_rail_soup.find_all('span', {'class': 'jobs-unified-top-card__bullet'})[0].text.strip()
                except (AttributeError, IndexError):
                    location = ''
                    print('Location not found for page: ', page, 'and job card #: ', i + 1)
            print(location)

            # Date posted
            try:
                span_texts = []
                for span in right_rail_soup.find_all('span'):
                    if not span.attrs.values():
                        span_texts.append(span.text)
                try:
                    date_posted_list = span_texts[0].split('\n')
                    date_posted = ''
                    for item in date_posted_list:
                        if 'ago' in item:
                            date_posted = item
                            break
                    if date_posted != '':
                        date_posted = date_posted.strip()
                except (AttributeError, IndexError):
                    date_posted = ''
                if date_posted == '':
                    try:
                        date_posted = right_rail_soup.find('span', {'class': 'jobs-unified-top-card__posted-date'}).text.strip()
                    except (AttributeError, IndexError):
                        date_posted = ''
            except (AttributeError, IndexError):
                date_posted = ''
                print('Date posted not found for page: ', page, 'and job card #: ', i + 1)
            print(date_posted)

            # Other job details
            try:
                job_details = right_rail_soup.find_all('span', {'class': 'jobs-details-job-summary__text--ellipsis'})
                # Number of applicants
                applicants = job_details[0].text
                applicants = re.findall('\w+', applicants)
                applicants = " ".join(applicants)
            except (AttributeError, IndexError):
                applicants = ''
            if applicants == '':
                try:
                    applicants = soup.find('span', {'class': re.compile('jobs-unified-top-card__applicant-count*')}).text.strip()
                except (AttributeError, IndexError):
                    applicants = ''
                    print('Applicants not found for page: ', page, 'and job card #: ', i + 1)
            print(applicants)

            # job type - Seniority Level and Full time vs part time etc
            try:
                job_type = soup.find_all('div', {'class': 'jobs-unified-top-card__job-insight'})[0].text.strip()
                job_type = job_type.replace('-', '')
                job_type = re.findall('\w+', job_type)
                if len(job_type) == 1:
                    ftpt = job_type[0]  # Variable for full time part time
                    seniority_level = ''
                elif len(job_type) == 2:
                    ftpt = job_type[0]  # Variable for full time part time
                    seniority_level = job_type[1]
                else:
                    ftpt = ''
                    seniority_level = ''
            except (AttributeError, IndexError):
                ftpt = ''  # Variable for full time part time
                seniority_level = ''
            print(ftpt)
            print(seniority_level)

            # Company Details: Number of employees
            try:
                employees = job_details[2].text
                employees = re.findall('\S+', employees)
                employees = " ".join(employees)
            except (AttributeError, IndexError):
                employees = ''
            if employees == '':
                try:
                    emp_industry = soup.find_all('div', {'class': 'jobs-unified-top-card__job-insight'})[1].text.strip()
                    employees = emp_industry.split(" ")[0]
                except (AttributeError, IndexError):
                    employees = ''
            print(employees)

            # Company Details: Industry
            try:
                industry = job_details[3].text
                industry = re.findall('\S+', industry)
                industry = " ".join(industry)
            except (AttributeError, IndexError):
                industry = ''
            if industry == '':
                try:
                    emp_industry = soup.find_all('div', {'class': 'jobs-unified-top-card__job-insight'})[1].text.strip()
                    industry = emp_industry.split(" ")[3]
                except (AttributeError, IndexError):
                    industry = ''
            print(industry)

            # Job posting details
            try:
                descriptions = right_rail_soup.find('div', {'id': 'job-details'}).find('span').text
                descriptions = re.findall('\w+', descriptions)
                descriptions = " ".join(descriptions)
            except (AttributeError, IndexError):
                descriptions = ''
            # print(descriptions)

            # Url links for job applications
            application_url = ''
            try:
                text = right_rail_soup.find_all('div', {'class': 'jobs-apply-button--top-card'})[0].find('span', {
                    'class': 'artdeco-button__text'}).text.strip()
                if (text == 'Easy Apply') or (text == 'Apply now') or (text == 'Apply Now'):
                    application_url = driver.current_url
                elif text == 'Apply':
                    driver.find_element_by_xpath(
                        '/html/body/div[6]/div[3]/div[3]/div/div/section[2]/div/div/div[1]/div/div[1]/div/div[2]/div[3]/div/div/div/button/span').click()
                    time.sleep(2)
                    # driver.find_element_by_class_name('jobs-apply-button--share').click()
                    if len(driver.window_handles) == 1:
                        application_url = url
                        try:
                            driver.find_element_by_xpath('/html/body/div[3]/div/div/button/li-icon').click()
                            driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[3]/button[2]/span').click()
                        except AttributeError:
                            driver.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/footer/div/div/button/span').click()
                    if len(driver.window_handles) == 2:
                        driver.switch_to.window(driver.window_handles[1])
                        time.sleep(2)
                        application_url = driver.current_url
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(2)
                    else:
                        application_url = driver.current_url
            except (AttributeError, IndexError):
                application_url = driver.current_url
            print(application_url)

            # top Skills + Hiring Trends
            skill_items = []
            hiring_trend_company_wide = ''
            hiring_trend_company_wide_engineering = ''
            median_tenure = ''
            try:
                x = driver.find_element_by_xpath('/html/body/div[6]/div[3]/div[3]/div/div/section[2]/div/div/div[1]/div/div[1]/div/div[2]/div[3]/div/div/div/button/span')
                driver.execute_script("arguments[0].scrollIntoView();", x)
                time.sleep(2)
                driver.execute_script("arguments[0].scrollIntoView();", driver.find_element_by_id('SALARY'))
                time.sleep(5)
                html_3 = driver.page_source
                soup_3 = BeautifulSoup(html_3, 'lxml')
                # TOP SKILLS
                try:
                    skills_soup = soup_3.find_all('li',
                                                  {'class': 'jobs-premium-applicant-insights__list-skill-item'})
                    skill_items = [item.text.strip() for item in skills_soup]
                except (AttributeError, IndexError):
                    skill_items = ''
                # MEDIAN TENURE
                try:
                    median_tenure = soup_3.find_all('span', {'class': 'jobs-premium-company-growth_average-tenure'})[
                        0].text.strip().split('∙')[1].strip()
                except (AttributeError, IndexError):
                    median_tenure = ''
                # HiIRING TREND COMPANY WIDE - ENGINEERING
                try:
                    hiring_trend_company_wide_engineering = soup_3.find_all('p', {'class': 't-16 t-black--light t-bold'})[2].text.strip()
                except (AttributeError, IndexError):
                    hiring_trend_company_wide_engineering = ''
                # HiIRING TREND COMPANY WIDE
                try:
                    hiring_trend_company_wide = soup_3.find_all('p', {'class': 't-16 t-black--light t-bold'})[
                        1].text.strip()
                except (AttributeError, IndexError):
                    hiring_trend_company_wide = ''
            except Exception as e:
                print(e)
                print('Info on skills not loaded')
            print(skill_items)
            print(hiring_trend_company_wide)
            print(hiring_trend_company_wide_engineering)
            print(median_tenure)

            jobs_card_data[counter] = [company_name, position, location, application_url, date_posted, applicants,
                                       ftpt, seniority_level, employees, descriptions, industry, skill_items, hiring_trend_company_wide,
                                       hiring_trend_company_wide_engineering, median_tenure]
            print(jobs_card_data[counter])
            print('-'*500)
            print('\n'*4)
            temp = pd.DataFrame({counter: jobs_card_data[counter]}).T
            df = pd.concat([temp, df])
            dummy_file = 'test_scrape' + keyword + location +'.csv'
            df.to_csv(dummy_file)
            # Now we increment the counter at
            # the end
            counter += 1

        if page == 1:
            new_url = page1_url + "&start=25"
        else:
            new_url = page1_url + "&start=" + str(page * 25)

        page += 1
        driver.get(new_url)
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

    data = pd.DataFrame(jobs_card_data).T
    data.columns = ['company_name', 'position', 'location', 'url', 'date_posted', 'Number of applicants',
                              'full-time/part-time', 'seniority level', 'employees', 'descriptions',
                               'industry', 'top competitive skills', 'Hiring Trend Company Wide',
                               'Hiring Trend Company Wide-Engineering', 'Median Tenure']
    data = data.reset_index(drop=True)
    data['search_keyword'] = keyword
    file = keyword + " " + location + '.csv'
    data.to_csv(file)

    return data

