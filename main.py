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
import gspread
from oauth2client.service_account import ServiceAccountCredentials

raw_dict = {"Estee | Gulaq Gear 6": "https://estee.smallcase.com/smallcase/ESTMO_0001",
            "Estee | Gulaq Gear 5": "https://estee.smallcase.com/smallcase/ESTMO_0002",
            "Estee | Gulaq Gear 4": "https://estee.smallcase.com/smallcase/ESTMO_0007",
            "Finsharpe | Indian Bluechip Leaders": "https://finsharpe.smallcase.com/smallcase/FISHMO_0004",
            "Finsharpe | Large & Mid Cap Diversified": "https://finsharpe.smallcase.com/smallcase/FISHMO_0005",
            "Wright Research | Momentum": "https://wrightresearch.smallcase.com/smallcase/WRTMO_0018",
            "Niveshaay | Green Energy": "https://niveshaay.smallcase.com/smallcase/NIVTR_0001",
            "Niveshaay | Trends Trilogy": "https://niveshaay.smallcase.com/smallcase/NIVMO_0004",
            "Niveshaay | Make In India": "https://niveshaay.smallcase.com/smallcase/NIVNM_0001",
            "Niveshaay | Mid and Small Cap Focused Portfolio": "https://niveshaay.smallcase.com/smallcase/NIVMO_0001",
            "Niveshaay | Niveshaay Consumer Trends Portfolio": "https://niveshaay.smallcase.com/smallcase/NIVNM_0002"}

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

def update_google_sheet(dataframes_list, spreadsheet_id, sheet_name_prefix):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("https://docs.google.com/spreadsheets/d/1-kcJNtrhkU5g_rqRFigvIHVOcP-JGo1cvXYDlpZJsyo/edit?gid=0#gid=0")

    for i, (file, df) in enumerate(dataframes_list):
        sheet_name = f"{sheet_name_prefix}_{i+1}"
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=df.shape[0]+1, cols=df.shape[1])
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

def main():
    streamlit.title("Smallcase Data Fetcher")

    # Get unique names for dropdown
    unique_names_list = get_unique_names()

    # Create selectbox before update button
    selected_amc = streamlit.selectbox("Select AMC", unique_names_list)

    # Update button
    if streamlit.button("Update"):
        # Filter data based on selection
        filtered_results = filter_data(selected_amc)

        if not filtered_results:
            streamlit.error("No results found for the selected AMC")
            return

        # Create lists for navigation
        url_list = list(filtered_results.values())
        keys_list = list(filtered_results.keys())

        with streamlit.spinner("Fetching data..."):
            try:
                driver = create_driver()
                dataframes = login_and_navigate(driver, url_list, keys_list)

                streamlit.success("Data fetched successfully!")

                # Display results
                streamlit.write("### Downloaded Files:")
                for file, df in dataframes:
                    streamlit.write(f"**File:** {os.path.basename(file)}")
                    streamlit.dataframe(df)

                # Update Google Sheets
                spreadsheet_id = "your_spreadsheet_id"
                sheet_name_prefix = "Data"
                update_google_sheet(dataframes, spreadsheet_id, sheet_name_prefix)
                streamlit.success("Google Sheets updated successfully!")

            except Exception as e:
                streamlit.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
