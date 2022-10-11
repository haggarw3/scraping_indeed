import logIn
import scraper
# import wrangling
import pandas as pd
import time
import os

# 'React native developer', 'Flutter development', 'Mobile development', 'iOS mobile development',
#'iOS developer', 'Android Developer', 'mobile development engineer', 'mobile engineer', 'iOS engineer',
                     # 'Android engineer', 'iOS software engineer', 'android software engineer',
scraping_keywords = ['"iOS"', '"android"', 'android software engineer', 'mobile app development', 'android software engineer',
                     'iOS software engineer','"mobile application"', '"mobile developer"', '"android"',
                     'kotlin developer', 'flutter developer', '"android engineer"']

locations = ['paris']
scraped_df = pd.DataFrame(
    columns=['company_name', 'position', 'location', 'url', 'date_posted', 'Number of applicants',
                              'full-time/part-time', 'seniority level', 'employees', 'descriptions',
                               'industry', 'top competitive skills', 'Hiring Trend Company Wide',
                               'Hiring Trend Company Wide-Engineering', 'Median Tenure', 'search_keyword'])

# Removing all the old data files / csv files
files = os.listdir()
for file in files:
    if file.endswith('.csv'):
        os.remove(file)

# driver, home_url = logIn.login()  # Later, will send masked credentials to the function instead of hard coding
for location in locations:
    for keyword in scraping_keywords:
        try:
            driver, home_url = logIn.login()
        except Exception as e:
            print(e)
            print('Error in Logging In the Website')
            print('Exiting Code')
            exit()
        try:
            driver, url = scraper.scrape_phase1(driver, home_url, location, keyword)
            if url == home_url:
                print('Script Errored for location:', location, ' and keyword: ', keyword)
                break
        except Exception as e:
            print(e)
        try:
            data = scraper.scrape_phase2(driver, url, keyword, location)
            print('Scraper ran for Location: ', location, "and Keyword: ", keyword)
            scraped_df = pd.concat([scraped_df, data], axis=0)  # This is for the final aggregated file
            scraped_df = scraped_df.reset_index(drop=True)
        except Exception as e:
            print(e)
            print('Errored in scrape phase 2')
        time.sleep(15)


scraped_df.to_csv('final_scrape.csv')


