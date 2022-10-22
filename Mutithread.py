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

# 加入行為鍊 ActionChain (在 WebDriver 中模擬滑鼠移動、點繫、拖曳、按右鍵出現選單，以及鍵盤輸入文字、按下鍵盤上的按鈕等)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# from webdriver_manager.chrome import ChromeDriverManager

# 強制等待 (執行期間休息一下)
import time

# 執行 command 的時候用的
import os

import re

import shutil

from webdriver_manager.chrome import ChromeDriverManager

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


URL = "https://www.gutenberg.org/browse/languages/zh"


def initDirver():
    service = ChromeService(ChromeDriverManager().install())
    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')

    return webdriver.Chrome(options=options, service=service)


def getBookNames(driver, limit: int = 200) -> list:
    print("Scraping Names...", end="")
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
                if len(bookNames) >= limit:
                    break
    print("Done.")

    return bookNames


def getBookContests(driver, bookNames: list) -> dict:
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

        # print(f"{name}", end=" ")

    print(f"{len(os.listdir(filePath))} Books Downloaded.")


def mutithread(book_names: list, n=2) -> dict:
    driver = {}
    for i in range(n):
        driver["d"+str(i)] = initDirver()

    for d in driver.keys():
        driver[d].get(URL)

    temp = [book_names[i:i + n] for i in range(0, len(book_names), n)]

    with ThreadPoolExecutor() as executor:
        results = [executor.submit(getBookContests, driver[driver_], temp_)
                   for driver_, temp_ in zip(driver.keys(), temp)]

    for d in driver.keys():
        driver[d].quit()

    books = {}
    for future in as_completed(results):
        # books.update(future.result())
        print(type(future.result()))

    return books


def main():
    start_time = time.time()

    driver = initDirver()
    driver.get(URL)
    book_names = getBookNames(driver)
    driver.quit()

    books = mutithread(book_names, n=4)
    # half = len(book_names) // 2

    # with ThreadPoolExecutor() as executor:
    #     books_temp1 = executor.submit(
    #         getBookContests, driver1, book_names[:half])
    #     books_temp2 = executor.submit(
    #         getBookContests, driver2, book_names[half:])

    # books = books_temp1.result() | books_temp2.result()

    # driver1.quit()
    # driver2.quit()

    getBooks(books, "Bookshelf_Selenium")

    # books_temp1 = getBookContests(driver1, book_names[:half])
    # books_temp2 = getBookContests(driver2, book_names[half:])
    # books = books_temp1 | books_temp2

    # books = getBookContests(driver1, book_names)

    print(f"RunTime: {(time.time() - start_time):4.1f} s")


if __name__ == "__main__":
    main()
