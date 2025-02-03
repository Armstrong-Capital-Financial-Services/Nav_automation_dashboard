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
from selenium.webdriver.common.by import By

data_dict = {#"Estee | Gulaq Gear 6": "https://estee.smallcase.com/smallcase/ESTMO_0001",
             #"Estee | Gulaq Gear 5": "https://estee.smallcase.com/smallcase/ESTMO_0002",
             #"Estee | Gulaq Gear 4": "https://estee.smallcase.com/smallcase/ESTMO_0007",
            #"Finsharpe | Indian Bluechip Leaders": "https://finsharpe.smallcase.com/smallcase/FISHMO_0004",
            # "Finsharpe | Large & Mid Cap Diversified": "https://finsharpe.smallcase.com/smallcase/FISHMO_0005",
           # "https://wrightresearch.smallcase.com/smallcase/WRTMO_0018"
             "Niveshaay | Green Energy":"https://niveshaay.smallcase.com/smallcase/NIVTR_0001",
             "Niveshaay | Trends Trilogy":"https://niveshaay.smallcase.com/smallcase/NIVMO_0004",
             "Niveshaay | Make In India" :"https://niveshaay.smallcase.com/smallcase/NIVNM_0001",
             "Niveshaay | Mid and Small Cap Focused Portfolio":"https://niveshaay.smallcase.com/smallcase/NIVMO_0001",
             "Niveshaay | Niveshaay Consumer Trends Portfolio":"https://niveshaay.smallcase.com/smallcase/NIVNM_0002"}
url_list = list(data_dict.values())

keys_list = list(data_dict.keys())
first_key= keys_list[0]
keys_from_second = keys_list[1:]


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

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROME).install()),
        options=options,
    )
    return driver
def wait_for_download( ):
    # Wait for download to complete
    time.sleep(2)  # Initial wait for download to start
    downloaded_file = None
    timeout = 13  # Maximum wait time in seconds
    start_time = time.time()

    while time.time() - start_time < timeout:
        files = os.listdir('/tmp')
        csv_files = [f for f in files if f.endswith('.csv')]
        crdownload_files = [f for f in files if f.endswith('.crdownload')]

        if csv_files and not crdownload_files:
            downloaded_file = os.path.join('/tmp', csv_files[0])
            break

        time.sleep(1)

    return downloaded_file


def switch_to_window_by_title(driver, title, timeout=10):
    """
    Switch to a window with the specified title
    Returns True if successful, False otherwise
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        for window in driver.window_handles:
            driver.switch_to.window(window)
            if driver.title == title:
                return True
        time.sleep(1)
    return False


def login_and_navigate(driver):

    #download_dir = os.path.join(os.getcwd(), "downloads")

    for url in url_list:
        driver.execute_script(f"window.open('{url}');")
        time.sleep(5)

    # Get all window handles
    windows = driver.window_handles

    # First find and process Gear 6
    for window in windows:
        driver.switch_to.window(window)
        current_handle = driver.current_window_handle
        driver.window_handles.index(current_handle)
        if driver.title == first_key:
            print("Processing Gear 6...")
            time.sleep(5)
            button = driver.find_element(By.CLASS_NAME, "LockedSCPerformance__continue-btn__3Hvi-")
            driver.execute_script("arguments[0].click();", button)

            wait = WebDriverWait(driver, 10)
            button2 = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "KeyTermsAndDetails__action-cta__ohJ_L")))
            button2.click()

            button3 = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Download Chart')]")))
            driver.execute_script("arguments[0].click();", button3)

            downloaded_file = wait_for_download(download_dir)
            print(f"Downloaded file from Gear 6: {downloaded_file}")
            break
    for window in windows:
        driver.switch_to.window(window)
        print(f"Checking window title: {driver.title}")
        for i in keys_from_second:
            if i in driver.title:
              wait = WebDriverWait(driver, 10)
              button3 = wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Download Chart')]")))
              driver.execute_script("arguments[0].click();", button3)

            downloaded_file = wait_for_download(download_dir)
            print(f"Downloaded file from Gear 5: {downloaded_file}")

    driver.quit()



def fetch_data():
    update_button=streamlit.button("Update")
    if update_button:
      driver = create_driver()
      login_and_navigate(driver)
      streamlit.write("Data updated successfully")


if __name__ == "__main__":
    fetch_data()
