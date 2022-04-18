import re
import os
import zipfile
import numpy as np
import pandas as pd
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

    def get_transaction(self):
        self.setup()
        self.get_url()
        self.fetch_data()
        self.quit()

def parse_address(df: pd.core.frame.DataFrame):
    division = pd.read_csv("./conf/administrative_division/administrative_division.csv")
    cities = []
    loactions = []
    IDs = []
    for address in df["土地位置建物門牌"]:
        city = address[:3]
        cities.append(city)

        if city[-1] == "市":
            pattern = re.compile(r"\w+[區]")
            loaction = pattern.search(address[3:7]).group(0)
            loactions.append(loaction)
        else:
            pattern = re.compile(r"\w+[市鎮鄉]")
            loaction = pattern.search(address[3:7]).group(0)
            loactions.append(loaction)

        IDs.append(division[(division.iloc[:, 1] == city) & (division.iloc[:, 3] == loaction)].ID.values[0])
    df["縣市"] = cities
    df["區市鎮鄉"] = loactions
    df["區域ID"] = IDs
    return df

def format_date(S: pd.core.series.Series):
    Dates = []
    for i in S:
        try:
            date = str(19110000 + int(i))
            Dates.append(f"{date[:4]}-{date[4:6]}-{date[6:]}")
        except:
            Dates.append(None)
    return Dates

def process_data(path: str):
    df = pd.read_csv(path)
    # delet column name in english
    df.drop([0], inplace=True)
    # 去除非住家用房屋交易資料
    df = df[(df["交易標的"] == "房地(土地+建物)+車位") | (df['交易標的'] == "房地(土地+建物)")]
    df = df[df["主要用途"] == "住家用"]
    # 計算主建物實坪單價 並加入dataframe
    df['主建物面積'] = df['主建物面積'].astype(np.int64)
    df = df[df['主建物面積'] != 0]
    tatal_prices = df['總價元'].astype(np.int64) - df['車位總價元'].astype(np.int64)
    df['主建物實坪單價'] =  tatal_prices/ (df['主建物面積']/3.30579)
    # 去除不重要 column
    df.drop(['交易標的', '鄉鎮市區', '土地移轉總面積平方公尺', '非都市土地使用分區', '非都市土地使用編定',
             '主要用途', '主要建材', '建物移轉總面積平方公尺', '建物現況格局-隔間', '總價元', 
             '單價元平方公尺', '交易筆棟數', '備註', '編號', '附屬建物面積', '陽台面積', '移轉編號',
             '車位類別', '車位總價元', '車位移轉總面積(平方公尺)'], axis=1, inplace=True)
    # 分析地址
    df = parse_address(df)
    # 轉換Date 資料
    df["交易年月日"] = format_date(df["交易年月日"])
    df["建築完成年月"] = format_date(df["建築完成年月"])

    return df