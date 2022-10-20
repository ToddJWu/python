# 操作 browser 的 API
from pickle import GLOBAL
from pydoc import Doc
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException

# 面對動態網頁，等待某個元素出現的工具，通常與 exptected_conditions 搭配
from selenium.webdriver.support.ui import WebDriverWait

# 搭配 WebDriverWait 使用，對元素狀態的一種期待條件，若條件發生，則等待結束，往下一行執行
from selenium.webdriver.support import expected_conditions as EC

# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By

# 加入行為鍊 ActionChain (在 WebDriver 中模擬滑鼠移動、點繫、拖曳、按右鍵出現選單，以及鍵盤輸入文字、按下鍵盤上的按鈕等)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# from webdriver_manager.chrome import ChromeDriverManager

# 強制等待 (執行期間休息一下)
import time

# 整理 json 使用的工具
import json

# 執行 command 的時候用的
import os

import re

import shutil

from webdriver_manager.chrome import ChromeDriverManager


URL = "https://www.gutenberg.org/browse/languages/zh"

driver = None


def initDirver():
    service = ChromeService(executable_path=ChromeDriverManager().install())
    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')

    global driver
    driver = webdriver.Chrome(options=options, service=service)


def getBookNames(num=10) -> list:
    print("Scraping Books' Name...")
    driver.get(URL)
    try:
        titles = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.pgdbetext > a")
            )
        )
    except TimeoutException:
        print("Books Meun Page 等待逾時!")

    bookNames = []
    for title in titles:
        if re.search(r"[\u4E00-\u9FFF]+", title.text):
            if title.text not in bookNames:
                bookNames.append(title.text)
                if len(bookNames) >= num:
                    break
    print("Done.\n")

    return bookNames


# def getBookContests(bookNames: list) -> dict:
#     books = {}

#     print("Scraping Books' Contests...")
#     for bookname in bookNames:
#         driver.get(URL)

#         # Click on The Book Name
#         try:
#             WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located(
#                     (By.LINK_TEXT, bookname)
#                 )
#             ).click()

#         except TimeoutException:
#             print("Books Meun Page 等待逾時!")

#         # Click on Selected Source(Plain Text UTF-8)
#         try:
#             WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located(
#                     (By.LINK_TEXT, "Plain Text UTF-8")
#                 )
#             ).click()

#         except TimeoutException:
#             print("Select Download Sources Page 等待逾時!")

#         # Get The Book Contest
#         try:
#             pre_texts = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located(
#                     (By.TAG_NAME, "pre")
#                 )
#             )
#             contents = re.findall("[\u4E00-\u9FFF]+[\W]+", pre_texts.text)

#         except TimeoutException:
#             print("Source Page 等待逾時!")

#         books[bookname] = contents

#     print("Done.\n")
#     return books

def getBookContests(name: str) -> list:
    # books = {}

    # print("Scraping Books' Contests...")
    # for bookname in bookNames:
    # driver.switch_to.new_window('tab')
    driver.get(URL)

    # Click on The Book Name
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, name)
            )
        ).click()

    except TimeoutException:
        print("Books Meun Page 等待逾時!")

    # Click on Selected Source(Plain Text UTF-8)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.LINK_TEXT, "Plain Text UTF-8")
            )
        ).click()

    except TimeoutException:
        print("Select Download Sources Page 等待逾時!")

    # Get The Book Contest
    try:
        pre_texts = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "pre")
            )
        )
        contents = re.findall("[\u4E00-\u9FFF]+[\W]+", pre_texts.text)

    except TimeoutException:
        print("Source Page 等待逾時!")

    # books[bookname] = contents

    # print("Done.\n")
    driver.close()
    return contents


def getBooks(books: dict, filePath) -> None:
    print("Initializing File...")
    if os.path.exists(filePath):
        # print("Removing Old File...")
        shutil.rmtree(filePath)

        # print("Creating New File...")
        os.mkdir(filePath)
    else:
        # print("Creating New File...")
        os.mkdir(filePath)

    print("Done.\n")
    print("Downloading Books to File...")
    for name, content in books.items():
        name_ = re.sub(r"\s|:", " ", name)
        with open(f"{filePath}/{name_}.txt", "ab") as f:
            f.write(" ".join(content).encode())

        # print(f"{name}", end=" ")

    print(f"{len(os.listdir(filePath))} Books Downloaded.")


def main():
    start_time = time.time()
    initDirver()

    book_names = getBookNames()

    driver.get(URL)
    ac = ActionChains(driver)
    # Click on The Book Name
    for name in book_names:
        try:
            a = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.LINK_TEXT, name)
                )
            )
        except TimeoutException:
            print("Books Meun Page 等待逾時!")

        ac.key_down(Keys.COMMAND).click(a).key_up(Keys.COMMAND).perform()

    txt = []
    for window_handle in driver.window_handles[1:]:
        driver.switch_to.window(window_handle)
        # Click on Selected Source(Plain Text UTF-8)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.LINK_TEXT, "Plain Text UTF-8")
                )
            ).click()

        except TimeoutException:
            print("Select Download Sources Page 等待逾時!")

    for window_handle in driver.window_handles[1:]:
        driver.switch_to.window(window_handle)
        # Get The Book Contest
        try:
            pre_texts = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, "pre")
                )
            )
            contents = re.findall("[\u4E00-\u9FFF]+[\W]+", pre_texts.text)

        except TimeoutException:
            print("Source Page 等待逾時!")
        
        txt.append(contents)
    print(len(txt))
    # books = getBookContests(book_names)

    # getBooks(books, "Bookshelf_Selenium")
    driver.quit()
    print(f"RunTime: {(time.time() - start_time):4.1f} s")


if __name__ == "__main__":
    main()
