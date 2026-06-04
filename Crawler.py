import datetime
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


# 1) 目标日期（可改）
TARGET = "20250812"        # 格式 yyyymmdd

driver = webdriver.Edge()
driver.maximize_window()

try:
    driver.get("http://www.gfex.com.cn/gfex/rihq/hqsj_tjsj.shtml")
    wait = WebDriverWait(driver, 15)

    # 2) 让日期控件可见（去掉 hide）
    driver.execute_script("""
        document.querySelector('.daterange').classList.remove('hide');
    """)

    # 3) 清空并写入日期范围（单日即 20250812 至 20250812）
    date_input = wait.until(EC.element_to_be_clickable((By.ID, "daterange")))
    date_input.clear()
    date_input.send_keys(f"{TARGET} 至 {TARGET}")

    # 4) 触发 laydate 的 done 事件，从而刷新表格
    driver.execute_script("""
        const inst = layui.laydate.getInst(document.getElementById('daterange'));
        if (inst && inst.done) {
            inst.done('${TARGET} 至 ${TARGET}');
        }
    """.replace("${TARGET}", TARGET))

    # 5) 等待表格重新渲染
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.layui-table-body.layui-table-main table")
        )
    )

    # 6) 解析并保存
    soup = BeautifulSoup(driver.page_source, "lxml")
    table = soup.select_one("div.layui-table-body.layui-table-main table")
    headers = [th.get_text(strip=True) for th in table.select("thead th")]
    rows = [[td.get_text(strip=True) for td in tr.select("td")] for tr in table.select("tbody tr")]
    df = pd.DataFrame(rows, columns=headers)

    file_name = f"gfex_rihq_{TARGET}.csv"
    df.to_csv(file_name, index=False, encoding="utf_8_sig")
    print(f"✅ {file_name} 已保存 {len(df)} 行")

finally:
    print(1)
    # driver.quit()
    
