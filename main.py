import streamlit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd
from selenium.webdriver.common.by import By

raw_dict = {"Estee | Gulaq Gear 6 Quant": "https://estee.smallcase.com/smallcase/ESTMO_0001",
            "Estee | Gulaq Gear 5 Quant": "https://estee.smallcase.com/smallcase/ESTMO_0002",
            "Estee | Gulaq Gear 4 Quant": "https://estee.smallcase.com/smallcase/ESTMO_0007",
            "Estee | Gulaq Gear 3 Quant":"https://estee.smallcase.com/smallcase/ESTMO_0003",
            "Finsharpe | Indian Bluechip Leaders": "https://finsharpe.smallcase.com/smallcase/FISHMO_0004",
            "Finsharpe | Large & Mid Cap Diversified": "https://finsharpe.smallcase.com/smallcase/FISHMO_0005",
            "Finsharpe | Mid & Small Cap Focus":"https://finsharpe.smallcase.com/smallcase/FISHMO_0008",
            "Wright Research | Wright Momentum Model":"https://wrightresearch.smallcase.com/smallcase/WRTNM_0001",
            "Wright Research | Alpha Prime Momentum Model":"https://wrightresearch.smallcase.com/smallcase/WRTMO_0018",
            "Wright Research | Wright New India Manufacturing Theme":"https://wrightresearch.smallcase.com/smallcase/WRTNM_0003",
            "Wright Research | Balanced Multi Factor Model":"https://wrightresearch.smallcase.com/smallcase/WRTMO_0003",
            "Wright Research | Wright Smallcaps Tracker":"https://wrightresearch.smallcase.com/smallcase/WRTMO_0007",
            "Wright Research | Wright Innovation Tracker":"https://wrightresearch.smallcase.com/smallcase/WRTNM_0004",
            "Niveshaay | Green Energy Theme": "https://niveshaay.smallcase.com/smallcase/NIVTR_0001",
            "Niveshaay | Trends Trilogy Fundamental": "https://niveshaay.smallcase.com/smallcase/NIVMO_0004",
            "Niveshaay | Make In India Theme": "https://niveshaay.smallcase.com/smallcase/NIVNM_0001",
            "Niveshaay | Mid and Small Cap Focused Portfolio Fundamental": "https://niveshaay.smallcase.com/smallcase/NIVMO_0001",
            "Niveshaay | Niveshaay Consumer Trends Portfolio Theme": "https://niveshaay.smallcase.com/smallcase/NIVNM_0002",
            "Marcellus | Marcellus MeritorQ- Fixed Fee plan Quant":"https://marcellus.smallcase.com/smallcase/MCELMO_0003",
            "Marcellus | Marcellus MeritorQ- AuA based Fee plan Quant":"https://marcellus.smallcase.com/smallcase/MCELMO_0008",
             "Omniscience Capital | Omni Bharat Defence Theme":"https://omniscience.smallcase.com/smallcase/OMNNM_0012",
             "Omniscience Capital | Omni Capital Enablers Theme":"https://omniscience.smallcase.com/smallcase/OMNNM_0003",
              "Omniscience Capital | Omni Power Theme":"https://omniscience.smallcase.com/smallcase/OMNNM_0004",
              "Omniscience Capital | Omni Bullet Train Theme":"https://omniscience.smallcase.com/smallcase/OMNMO_0006",
              "Omniscience Capital | Omni Super Dividend Theme":"https://omniscience.smallcase.com/smallcase/OMNMO_0005",
               "Omniscience Capital | Omni UP Rising Theme":"https://omniscience.smallcase.com/smallcase/OMNNM_0023",
               "Omniscience Capital | Omni DX Theme":"https://omniscience.smallcase.com/smallcase/OMNNM_0001",
               "Omniscience Capital | Omni Future of Mobility Theme":"https://omniscience.smallcase.com/smallcase/OMNMO_0018",
                "Omniscience Capital | Omni Bharat Amrit Kaal Theme":"https://omniscience.smallcase.com/smallcase/OMNNM_0010",
               "Omniscience Capital | Omni Royals - SuperNormal LargeCap Fundamental":"https://omniscience.smallcase.com/smallcase/OMNMO_0002",
               "Omniscience Capital | Omni AI-Tech Global Theme":"https://omniscience.smallcase.com/smallcase/OMNNM_0006",
               "Omniscience Capital | Omni Bank on Bharat Theme":"https://omniscience.smallcase.com/smallcase/OMNNM_0021",
               "Omniscience Capital | Omni FinTech, Digital Banking & Payments Theme":"https://omniscience.smallcase.com/smallcase/OMNNM_0009",
               "Omniscience Capital | Omni Knights - SuperNormal MidCap Fundamental":"https://omniscience.smallcase.com/smallcase/OMNMO_0003",
               "Omniscience Capital | Omni SuperStox - SuperNormal FlexiCaps Fundamental":"https://omniscience.smallcase.com/smallcase/OMNMO_0001",
               "Omniscience Capital | Omni Royals - SuperNormal LargeCap Fundamental":"https://omniscience.smallcase.com/smallcase/OMNMO_0002",}

def get_unique_names():
    unique_names = set()
    for key in raw_dict:
        if "|" in key:
            name = key.split("|")[0].strip()
            unique_names.add(name)
        else:
            name = key.split("smallcase.com")[0].split("//")[1].strip()
            unique_names.add(name)
    return sorted(list(unique_names))

def filter_data(keyword):
    filtered_data = {}
    for key, value in raw_dict.items():
        if "|" in key:
            name = key.split("|")[0].strip()
        else:
            name = key.split("smallcase.com")[0].split("//")[1].strip()
        
        if keyword.lower() in name.lower():
            filtered_data[key] = value
    return filtered_data

def create_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--window-size=1420,1080')        
    options.add_argument("--disable-dev-shm-usage")

    options.add_experimental_option("prefs", {
        "download.default_directory": "/tmp",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    return webdriver.Chrome(
        service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
        options=options,
    )

def wait_for_download():
    time.sleep(2)
    downloaded_files = []
    timeout = 13
    start_time = time.time()

    while time.time() - start_time < timeout:
        files = os.listdir('/tmp')
        csv_files = [f for f in files if f.endswith('.csv')]
        crdownload_files = [f for f in files if f.endswith('.crdownload')]

        if csv_files and not crdownload_files:
            downloaded_files = [os.path.join('/tmp', f) for f in csv_files]
            break

        time.sleep(1)

    return downloaded_files

def login_and_navigate(driver, url_list, keys_list):
    downloaded_file_list = []
    dataframes_list = []
    
    first_key = keys_list[0]
    keys_from_second = keys_list[1:]

    for url in url_list:
        driver.execute_script(f"window.open('{url}');")
        time.sleep(5)

    windows = driver.window_handles

    for window in windows:
        driver.switch_to.window(window)
        if driver.title == first_key:
            print(f"Processing {first_key}...")
            time.sleep(5)
            button = driver.find_element(By.CLASS_NAME, "LockedSCPerformance__continue-btn__3Hvi-")
            driver.execute_script("arguments[0].click();", button)

            wait = WebDriverWait(driver, 10)
            button2 = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "KeyTermsAndDetails__action-cta__ohJ_L"))
            )
            button2.click()

            button3 = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Download Chart')]"))
            )
            driver.execute_script("arguments[0].click();", button3)

            downloaded_files = wait_for_download()
            downloaded_file_list.extend(downloaded_files)
            break

    for window in windows:
        driver.switch_to.window(window)
        for i in keys_from_second:
            if i in driver.title:
                wait = WebDriverWait(driver, 10)
                button3 = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Download Chart')]"))
                )
                driver.execute_script("arguments[0].click();", button3)

                downloaded_files = wait_for_download()
                downloaded_file_list.extend(downloaded_files)

    driver.quit()

    for file in set(downloaded_file_list):
        try:
            df = pd.read_csv(file)
            dataframes_list.append((file, df))
        except Exception as e:
            streamlit.write(f"Error reading {file}: {e}")

    return dataframes_list

import streamlit as st
import os
import redis
import json

def main():
    st.title("Smallcase Data Fetcher")

    # Get unique names for dropdown
    unique_names_list = get_unique_names()

    # Create selectbox before update button
    selected_amc = st.selectbox("Select AMC", unique_names_list)

    # Update button
    if st.button("Update"):
        # Filter data based on selection
        filtered_results = filter_data(selected_amc)

        if not filtered_results:
            st.error("No results found for the selected AMC")
            return

        # Create lists for navigation
        url_list = list(filtered_results.values())
        keys_list = list(filtered_results.keys())

        with st.spinner("Fetching data..."):
            try:
                driver = create_driver()
                dataframes = login_and_navigate(driver, url_list, keys_list)

                st.success("Data fetched successfully!")

                # Connect to Redis using secrets
                redis_config = st.secrets["redis"]
                r = redis.Redis(
                    host=redis_config["host"],
                    port=redis_config["port"],
                    decode_responses=True,
                    username=redis_config["username"],
                    password=redis_config["password"],
                )

                # Display results and store in Redis
                st.write("### Downloaded Files:")
                for file, df in dataframes:
                    st.write(f"**File:** {os.path.basename(file)}")
                    st.dataframe(df)

                    # Convert DataFrame to JSON string
                    json_str = df.to_json(orient='records')

                    # Store JSON string in Redis
                    redis_key = f"dataframe:{os.path.basename(file)}"
                    r.set(redis_key, json_str)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
