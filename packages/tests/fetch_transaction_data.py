import os
import zipfile
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

class fetch_transaction_data:
    def __init__(self, data_path):
        self.data_path = data_path
        self.url = "https://plvr.land.moi.gov.tw/DownloadOpenData"

    def setup(self):
        options = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : self.data_path + "\\downloads"}
        options.add_experimental_option("prefs",prefs)
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def get_url(self):
        self.driver.get(self.url)
        uselessWindows = self.driver.window_handles
        self.driver.switch_to.window(uselessWindows[-1])
        self.driver.close()
        self.driver.switch_to.window(uselessWindows[0])

    def fetch_data(self):
        element_history = self.driver.find_element(by=By.LINK_TEXT, value="非本期下載")
        element_history.click()
        sleep(5)
        # select csv format
        element_format = self.driver.find_element(by=By.ID, value="fileFormatId")
        select = Select(element_format)
        select.select_by_value("csv")
        # get history season
        element_season = self.driver.find_element(by=By.ID, value="historySeason_id")
        select = Select(element_season)
        list_historySeason = element_season.text.split()
        
        for historySeason in list_historySeason:
            # select history season
            select.select_by_visible_text(historySeason)
            # download the file
            element_download = self.driver.find_element(by=By.ID, value="downloadBtnId")
            element_download.click()
            # wait until finish the download progress
            file_path = self.data_path + "\\downloads\\lvr_landcsv.zip"
            while not os.path.exists(file_path):
                sleep(1)
            # extract zip file
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_path + f"\\transaction\\{historySeason}\\")
            # delete zip file
            os.remove(file_path)

    def quit(self):
        self.driver.quit()