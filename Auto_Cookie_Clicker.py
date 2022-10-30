# 操作 browser 的 API
from ast import Global
from msilib.schema import Upgrade
from selenium import webdriver

# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
import re

# 隨機取得 User-Agent
# from fake_useragent import UserAgent

# ua = UserAgent(cache=True)  # cache=True 表示從已經儲存的列表中提取

URL = "https://orteil.dashnet.org/cookieclicker/"

# Auto download driver
service = ChromeService(ChromeDriverManager().install())
options = ChromeOptions()
# options.add_argument("--headless")  # Run in Background
options.add_argument("--no-sandbox")
options.add_argument("--incognito")  # 開啟無痕模式
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")
# options.add_argument(f"--user-agent={ua.random}")

driver = webdriver.Chrome(options=options, service=service)
driver.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {
        "source": """
    Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
    })
"""
    },
)


def getCookiesCount() -> int:
    try:
        cookies = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#cookies")))
        temp = cookies.text.split(" ")[0]

    except TimeoutException:
        print("等待逾時!")

    cookieCount = int(re.sub(",", "", temp))

    return cookieCount


def getUpgradableItems():
    upgrade_lst = []

    try:
        items = driver.find_elements(
            By.CSS_SELECTOR, "div.product.unlocked.enabled")
        upgrade = driver.find_element(
            By.CSS_SELECTOR, "div.crate.upgrade.enabled")
    except NoSuchElementException:
        upgrade = ""

    upgrade_lst.append(upgrade)

    for item in items[::-1]:
        upgrade_lst.append(item)

    return upgrade_lst


def main():

    driver.get(URL)
    ac = ActionChains(driver)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div#langSelect-EN"))
        ).click()

    except TimeoutException:
        print("等待逾時!")

    try:
        bigCookie = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "bigCookie"))
        )
    except TimeoutException:
        print("等待逾時!")

    while getCookiesCount() < 100000:
        for item in getUpgradableItems():
            if item != "":
                ac.move_to_element(item).click()

        ac.move_to_element(bigCookie).click()

        ac.perform()

    print("Driver Closed")
    driver.quit()


main()
