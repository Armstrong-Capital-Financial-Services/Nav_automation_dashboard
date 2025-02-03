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

data_dict = {
    "Estee | Gulaq Gear 6": "https://estee.smallcase.com/smallcase/ESTMO_0001",
    "Estee | Gulaq Gear 5": "https://estee.smallcase.com/smallcase/ESTMO_0002",
    "Estee | Gulaq Gear 4": "https://estee.smallcase.com/smallcase/ESTMO_0007",
    "Finsharpe | Indian Bluechip Leaders": "https://finsharpe.smallcase.com/smallcase/FISHMO_0004",
    "Finsharpe | Large & Mid Cap Diversified": "https://finsharpe.smallcase.com/smallcase/FISHMO_0005",
    "Wrightresearch | Smallcase": "https://wrightresearch.smallcase.com/smallcase/WRTMO_0018",
    "Niveshaay | Green Energy": "https://niveshaay.smallcase.com/smallcase/NIVTR_0001",
    "Niveshaay | Trends Trilogy": "https://niveshaay.smallcase.com/smallcase/NIVMO_0004",
    "Niveshaay | Make In India": "https://niveshaay.smallcase.com/smallcase/NIVNM_0001",
    "Niveshaay | Mid and Small Cap Focused Portfolio": "https://niveshaay.smallcase.com/smallcase/NIVMO_0001",
    "Niveshaay | Niveshaay Consumer Trends Portfolio": "https://niveshaay.smallcase.com/smallcase/NIVNM_0002"
}

def create_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
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
    time.sleep(2)  # Initial wait for download to start
    downloaded_files = []  # Store all downloaded files
    timeout = 13  # Maximum wait time in seconds
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

def login_and_navigate(driver):
    downloaded_file_list = []  # Store downloaded file paths
    dataframes_list = []  # Store DataFrames

    # Group URLs by AMC
    amc_groups = {}
    for key, url in data_dict.items():
        amc = key.split(' | ')[0]
        if amc not in amc_groups:
            amc_groups[amc] = []
        amc_groups[amc].append((key, url))

    for amc, key_url_pairs in amc_groups.items():
        first_key, first_url = key_url_pairs[0]
        remaining_keys_urls = key_url_pairs[1:]

        # Open all URLs in new tabs
        for key, url in key_url_pairs:
            driver.execute_script(f"window.open('{url}');")
            time.sleep(5)

        # Get all window handles
        windows = driver.window_handles

        # Process the first key
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
                downloaded_file_list.extend(downloaded_files)  # Collect file paths
                break

        # Process remaining keys
        for window in windows:
            driver.switch_to.window(window)
            for key, url in remaining_keys_urls:
                if key in driver.title:
                    wait = WebDriverWait(driver, 10)
                    button3 = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Download Chart')]"))
                    )
                    driver.execute_script("arguments[0].click();", button3)

                    downloaded_files = wait_for_download()
                    downloaded_file_list.extend(downloaded_files)  # Collect file paths

    driver.quit()

    # Read all downloaded files and store DataFrames
    for file in set(downloaded_file_list):  # Use `set` to remove duplicates
        try:
            df = pd.read_csv(file)
            dataframes_list.append((file, df))  # Store (filename, DataFrame) tuple
        except Exception as e:
            streamlit.write(f"Error reading {file}: {e}")

    return dataframes_list  # Return the list of DataFrames

def fetch_data():
    update_button = streamlit.button("Update")
    if update_button:
        driver = create_driver()
        dataframes = login_and_navigate(driver)

        streamlit.write("### All Downloaded Files:")
        for file, df in dataframes:
            streamlit.write(f"**File:** {file}")
            streamlit.dataframe(df)  # Display DataFrame in Streamlit

        streamlit.write("Data updated successfully")

if __name__ == "__main__":
    fetch_data()

