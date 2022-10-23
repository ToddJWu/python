# 操作 browser 的 API
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

# 強制等待 (執行期間休息一下)
import time

# 執行 command 的時候用的
import os

import re

import shutil

from webdriver_manager.chrome import ChromeDriverManager

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


URL = "https://www.gutenberg.org/browse/languages/zh"
fileName = "Bookshelf_Selenium"


def initDirver():
    service = ChromeService(ChromeDriverManager().install())
    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')

    return webdriver.Chrome(options=options, service=service)


def getBookNames(limit: int = 200) -> list:
    print("Scraping Names...")
    driver = initDirver()
    driver.get(URL)
    try:
        titles = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.pgdbetext > a")
            )
        )
    except TimeoutException:
        print("Books Meun Page 等待逾時!")
    driver.quit()

    bookNames = []
    for title in titles:
        if re.search(r"[\u4E00-\u9FFF]+", title.text):
            if title.text not in bookNames:
                bookNames.append(title.text)
                if len(bookNames) >= limit:
                    break
    print("Done.")

    return bookNames


def getBookContests(driver: webdriver, bookNames: list) -> dict:
    books = {}

    print("Scraping Contests...")
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
            contents = re.findall("[\u4E00-\u9FFF]+[\W]+", pre_texts.text)

        except TimeoutException:
            print("Source Page 等待逾時!")

        books[bookname] = contents

    print("Done.")
    return books


def getBooks(books: dict, filePath) -> None:
    print("Initializing File...")
    if os.path.exists(filePath):
        print("Removing Old File...")
        shutil.rmtree(filePath)

        print("Creating New File...", end="")
        os.mkdir(filePath)
    else:
        print("Creating New File...", end="")
        os.mkdir(filePath)
    print("Done.")

    for name, content in books.items():
        name_ = re.sub(r"\s|:", " ", name)
        with open(f"{filePath}/{name_}.txt", "ab") as f:
            f.write(" ".join(content).encode())

    print(f"{len(os.listdir(filePath))} Books Downloaded.")


def multiThread(book_names: list, driver_numbers: int = 2) -> dict:
    driver = {}
    for i in range(driver_numbers):
        driver["d"+str(i)] = initDirver()

    for driver_ in driver.keys():
        driver[driver_].get(URL)

    size = len(book_names) // driver_numbers
    temp = [book_names[i:i + size] for i in range(0, len(book_names), size)]

    with ThreadPoolExecutor() as executor:
        results = [executor.submit(getBookContests, driver[driver_], temp_)
                   for driver_, temp_ in zip(driver.keys(), temp)]

    for driver_ in driver.keys():
        driver[driver_].quit()

    books = {}
    for future in as_completed(results):
        books.update(future.result())

    return books


def main() -> None:
    start_time = time.time()

    book_names = getBookNames()

    books = multiThread(book_names, driver_numbers=4)

    getBooks(books, fileName)

    print(f"RunTime: {(time.time() - start_time):4.1f} s")


if __name__ == "__main__":
    main()
