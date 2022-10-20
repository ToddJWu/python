# 操作 browser 的 API
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

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

from webdriver_manager.chrome import ChromeDriverManager

# 強制等待 (執行期間休息一下)
import time

# 整理 json 使用的工具
import json

# 執行 command 的時候用的
import os

import re

import shutil

import concurrent.futures

URL = "https://www.gutenberg.org/browse/languages/zh"

def initDirver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    
    # Service(executable_path=ChromeDriverManager().install())
    # driver = webdriver.Chrome('chromedriver',options=options)
    return webdriver.Chrome(options=options)

def getTitles(driver) -> list:
    driver.get(URL)
    try:
        return WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.pgdbetext > a")
            )
        )
    except TimeoutException:
        print("Books Meun Page 等待逾時!")

def getBookNames(titles, num=10) -> list:
    # print("Booklist Downloading...")
    bookNames = []
    for title in titles:
        if re.search(r"[\u4E00-\u9FFF]+", title.text):
            if title.text not in bookNames:
                bookNames.append(title.text)
                if len(bookNames) >= num:
                    break
    # bookNames =  [title.text for title in titles if re.search(
    #     r"[\u4E00-\u9FFF]+", title.text) != None]

    # print("Finished.\n")

    return bookNames

def getContests(driver, bookNames: list) -> dict:
    books = {}
    
    print("Downloading books' contests...")
    # while len(books) < num:
    for bookname in bookNames:
        driver.get(URL)

        # Click on The Book Name
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.LINK_TEXT, bookname)
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
            contents =  re.findall("[\u4E00-\u9FFF]+[\W]+", pre_texts.text)

        except TimeoutException:
            print("Source Page 等待逾時!")

        books[bookname] = contents

    print("Finished.\n")
    return books

def getBooks(books: dict, filePath) -> None:
    print("Saving the Books...")
    for name, content in books.items():
        name_ = re.sub(r"\s|:", " ", name)
        with open(f"{filePath}/{name_}.txt", "ab") as f:
            f.write(" ".join(content).encode())

        # print(f"{name}", end=" ")

    print(f"{len(os.listdir(filePath))} Books Saved.")

def initDir(filePath: str) -> None:
    print("Initializing File...")
    if os.path.exists(filePath):
        print("Removing Old File...")
        shutil.rmtree(filePath)

        print("Creating New File...")
        os.mkdir(filePath)
    else:
        print("Creating New File...")
        os.mkdir(filePath)

    print("Finished.\n")

def main():
    # start_time = time.time()
    # filePath = "Bookshelf_Selenium"
    # initDir(filePath)
    driver = initDirver()
    
    title_list = getTitles(driver)
    

    # book_list = getBookNames(title_list)
    # book_contest = getContests(driver, book_list, num=20)


    # getBooks(book_contest, filePath)

    driver.quit()
    # print(f"Take: {(time.time() - start_time):4.1f} s")


if __name__ == "__main__":
    main()
    