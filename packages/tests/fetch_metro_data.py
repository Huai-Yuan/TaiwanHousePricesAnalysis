import json
import requests
import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

class fetch_metro_data:
    def __init__(self, data_path: str, API_Key: str):
        self.data_path = data_path + "\\metro_info"
        self.API_Key = API_Key

    def setup(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def get_longitude_and_latitude(self, Station: str):
        address = "捷運" + Station + "站"
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={self.API_Key}&language=zh"
        req = requests.get(url)
        geo_info = json.loads(req.text)
        if geo_info['status'] == 'ZERO_RESULTS':
            return [address, None, None]
        else:
            address = geo_info['results'][0]['formatted_address']
            lat_lng =  geo_info['results'][0]['geometry']['location']
            return [address, lat_lng['lat'], lat_lng['lng']]
    
    def save_data(self, StationNames: list, location: str):
        temp_list = []
        for Station in StationNames:
            temp_list.append(self.get_longitude_and_latitude(Station))
        df = pd.DataFrame(temp_list, columns=['地址', '緯度', '經度'])
        df.to_csv(self.data_path + f"\\{location}.csv")

    def get_taipei_metro_station_names(self):
        url = "https://web.metro.taipei/pages/tw/ticketroutetimesingle/071"
        self.driver.get(url)
        sleep(3)
        element_table = self.driver.find_element(by=By.TAG_NAME, value="table")
        element_table = element_table.find_elements(by=By.TAG_NAME, value="tr")
        StationNames = [i.text.split()[4] for i in element_table[2:]]
        self.save_data(StationNames, location="Taipei")

    def get_taoyuan_metro_station_names(self):
        url = "https://www.tymetro.com.tw/tymetro-new/tw/_pages/travel-guide/timetable-search.php"
        self.driver.get(url)
        StationNames = self.driver.find_element(by=By.ID, value="start_station").text
        StationNames = StationNames.split("\n")[1:-1]
        StationNames = [i.split()[1] for i in StationNames]
        self.save_data(StationNames, location="Taoyuan")

    def get_taichung_metro_station_names(self):
        url = "https://www.tmrt.com.tw/metro-life/ride-time-and-fare"
        self.driver.get(url)
        StationNames = self.driver.find_element(by=By.NAME, value="stationSelection").text
        StationNames = StationNames.split("\n")[1:-1]
        self.save_data(StationNames, location="Taichung")

    def get_kaohsiung_metro_station_names(self):
        url = "https://www.krtc.com.tw/"
        self.driver.get(url)
        StationNames = self.driver.find_element(by=By.ID, value="KRTCStartStation").text
        StationNames = StationNames.split("\n")[1:-1]
        StationNames = [i.strip() for i in StationNames]
        StationNames = [i.split()[1] for i in StationNames]
        self.save_data(StationNames, location="Kaohsiung")

    def quit(self):
        self.driver.quit()

    def get_metro(self):
        self.setup()
        self.get_taipei_metro_station_names()
        self.get_taoyuan_metro_station_names()
        self.get_taichung_metro_station_names()
        self.get_kaohsiung_metro_station_names()
        self.quit()