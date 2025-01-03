#!/usr/bin/env python
# coding: utf-8

# In[51]:


from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
import undetected_chromedriver as uc
from time import sleep
import random
from datetime import datetime, timedelta
import pyodbc
import sys

# Database connection string
conn_str = (
    r"Driver=;"
    r"Server=;"
    r"Database=;"
    r"Trusted_Connection=yes;"
)

# Random cooldown time
def random_sleep(min_time=1, max_time=3):
    sleep(random.uniform(min_time, max_time))

# Database connection
def connect_to_db(conn_str):
    try:
        conn = pyodbc.connect(conn_str)
        print("Successfully connected to the database.")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Adding data to the database
def insert_into_db(data):
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        query = "INSERT INTO Prices (StartDate, EndDate, Price, RunDate) VALUES (?, ?, ?, ?)"
        cursor.executemany(query, data)
        conn.commit()
    except Exception as e:
        print(f"An error occurred while adding data: {e}")
    finally:
        if cursor is not None:
            cursor.close()

# WebDriverWait functions
def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def wait_for_element_to_be_clickable(driver, by, value, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))

# Browser settings
options = uc.ChromeOptions()
options.add_argument("--start-fullscreen")
driver = uc.Chrome(options=options)

# Click and page navigation functions
def open_holidays_page(driver):
    driver.get('https://www.easyjet.com/en/holidays')
    sleep(2)

def close_banner(driver):
    try:
        wait_for_element_to_be_clickable(driver, By.XPATH, '//*[@id="ensCloseBanner"]').click()
        random_sleep(2, 4)
    except TimeoutException:
        print("Banner could not be closed.")

def click_first_option(driver):
    wait_for_element_to_be_clickable(driver, By.XPATH, '//*[@id="sticky-box"]/div/div/div/div/div[1]/div/div/div/div[2]/div[1]/div/div/div[2]').click()
    random_sleep(2, 4)

def select_from_date(driver):
    wait_for_element_to_be_clickable(driver, By.XPATH, '//*[@id="search-from-dd"]/div[2]/div[1]/div[2]/div[1]/label').click()
    random_sleep(2, 4)

def enter_destination(driver):
    wait_for_element(driver, By.XPATH, '//*[@id="search-to"]').send_keys("Enter the hotel name here.")
    random_sleep(2, 4)

def click_search_button(driver):
    wait_for_element_to_be_clickable(driver, By.XPATH, '//*[@id="sticky-box"]/div/div/div/div/div[1]/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/button').click()
    random_sleep(2, 4)

def click_when_button(driver):
    wait_for_element_to_be_clickable(driver, By.XPATH, '//*[@id="search-when"]').click()
    random_sleep(2, 4)

# Date selection functions
def select_dates(driver, start_date, end_date):
    select_date_range(driver, start_date, end_date)
    wait_for_element_to_be_clickable(driver, By.XPATH, '//*[@id="search-button"]').click()
    random_sleep(2, 4)

def allow_button_click(driver):
    allow_button_xpath = '//*[contains(@id, "popup-dialog-")]/div/div/div[2]/button'
    try:
        wait_for_element(driver, By.XPATH, allow_button_xpath)
        wait_for_element_to_be_clickable(driver, By.XPATH, allow_button_xpath).click()
        random_sleep(4, 5)
    except TimeoutException:
        pass

def print_price(driver, start_date, end_date):
    price_xpath = '//*[@id="layout"]/main/div[1]/div/div[2]/div[1]/div[1]/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/span'
    run_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        price_element = driver.find_elements(By.XPATH, price_xpath)
        
        if price_element:
            price = price_element[0].text.replace('£', '').replace(',', '').strip()
            print(f"Date Range: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')} - Price: {price}")
            return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), price, run_date)
        else:
            print(f"Date Range: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')} - Price: 0")
            print("No price information could be found for the date above.")
            return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), '0', run_date)
    
    except Exception as e:
        print(f"An error occurred while obtaining price information.: {e}")
        return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), '0', run_date)

def select_date(driver, date_obj):
    month = date_obj.strftime("%B")
    day = date_obj.day
    year = date_obj.year

    try:
        wait_for_element(driver, By.CLASS_NAME, 'flatpickr-calendar')

        while True:
            current_month = driver.find_element(By.CLASS_NAME, 'cur-month').text.strip()
            current_year = driver.find_element(By.CLASS_NAME, 'cur-year').get_attribute('value')
            if current_month == month and int(current_year) == year:
                break
            else:
                driver.find_element(By.CLASS_NAME, 'flatpickr-next-month').click()
                random_sleep(1, 2)

        days = driver.find_elements(By.CLASS_NAME, 'flatpickr-day')
        for day_element in days:
            if day_element.get_attribute('aria-label') == f'{month} {day}, {year}':
                day_element.click()
                return
        print("No date information found.")
        driver.quit()
        sys.exit()

    except StaleElementReferenceException:
        select_date(driver, date_obj)

def select_date_range(driver, start_date_obj, end_date_obj):
    try:
        select_date(driver, start_date_obj)
        while True:
            current_month = driver.find_element(By.CLASS_NAME, 'cur-month').text.strip()
            current_year = driver.find_element(By.CLASS_NAME, 'cur-year').get_attribute('value')
            if current_month == end_date_obj.strftime("%B") and int(current_year) == end_date_obj.year:
                break
            else:
                driver.find_element(By.CLASS_NAME, 'flatpickr-next-month').click()
                random_sleep(1, 2)

        select_date(driver, end_date_obj)
    except Exception as e:
        print(f"Error selecting date range: {e}")
        driver.quit()
        sys.exit()

def main():
    data_to_insert = []
    try:
        open_holidays_page(driver)
        close_banner(driver)
        click_first_option(driver)
        select_from_date(driver)
        enter_destination(driver)
        click_search_button(driver)
        click_when_button(driver)

        today = datetime.today()
        days_until_saturday = (5 - today.weekday() + 7) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7

        start_date = today + timedelta(days=days_until_saturday)
        end_date = start_date + timedelta(days=7)

        for _ in range(24):
            select_dates(driver, start_date, end_date)
            allow_button_click(driver)
            price_data = print_price(driver, start_date, end_date)
            data_to_insert.append(price_data)

            try:
                button_xpath = '//*[@id="sticky-box"]/div/div/div/div/div/div[2]/button/span'
                alternative_xpath = '//*[@id="search-parameters-edit"]'
                
                try:
                    wait_for_element_to_be_clickable(driver, By.XPATH, button_xpath)
                    driver.find_element(By.XPATH, button_xpath).click()
                    random_sleep(2, 4)
                except (TimeoutException, ElementClickInterceptedException):
                    try:
                        wait_for_element_to_be_clickable(driver, By.XPATH, alternative_xpath)
                        driver.find_element(By.XPATH, alternative_xpath).click()
                        random_sleep(2, 4)
                    except TimeoutException:
                        print("Neither button is clickable.")

            except TimeoutException:
                print("The button is not clickable.")

            start_date += timedelta(weeks=1)
            end_date += timedelta(weeks=1)

            try:
                click_when_button(driver)
            except ElementClickInterceptedException:
                print("The button is not clickable. Program is closing...")
                driver.quit()
                sys.exit()

        try:
            insert_into_db(data_to_insert)
            print("The data has been added to the database.")
        except Exception as e:
            print(f"Error while adding data: {e}")

    finally:
        driver.quit()
        print("The process is complete.")

if __name__ == "__main__":
    main()

