# sharing.py
from playwright.sync_api import sync_playwright
import time
import json
import os


etfs = ["0050", "00878", "0056", "00919", "00929", "006208", "00940", "00713"]
t_url = "https://www.pocket.tw/etf/tw/{}/fundholding?page&parent&source="
xph_name = '//*[@id="__layout"]/div/div/div[2]/main/div/div[1]/div/div/article/div[1]/div[1]/h1'
xph_date = '//*[@id="__layout"]/div/div/div[2]/main/div/div[4]/section/div[3]'
xph_tb = '//*[@id="__layout"]/div/div/div[2]/main/div/div[4]/section/div[2]/div/table/tbody/tr'


# Scrap data from website
def scraping(multi_task, url, multi_task_id):
    start = time.perf_counter()
    prcs_pid = os.getpid()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(0.5)
        etf = {}

        # Start to scrape data
        # Get holding_date
        e_code = url[url.find("/tw/") + 4 : url.find("/fundholding?")]
        xpah_date_ele = page.query_selector_all(xph_date)
        holding_date_ele = xpah_date_ele[0].text_content()
        holding_date = holding_date_ele[5:]
        if multi_task not in ["mth"]:
            print(
                f"PID_{prcs_pid} (Process_{multi_task_id}) starts for task: {e_code} - <{holding_date_ele}>"
            )
        else:
            print(
                f"Thread_{multi_task_id} starts for task: {e_code} - <{holding_date_ele}>"
            )

        # Get etf code and name
        xpah_name_ele = page.query_selector_all(xph_name)
        eles = xpah_name_ele[0].text_content()
        eles_list = eles.split("\n")
        etf_code = eles_list[2].strip()
        etf_name = eles_list[1].strip()
        etf["etf_code"] = etf_code
        etf["etf_name"] = etf_name
        etf["scraping_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        if multi_task not in ["mth"]:
            print(
                f"PID_{prcs_pid} (Process_{multi_task_id}) parsing data: {etf['etf_name']}({etf['etf_code']})"
            )
        else:
            print(
                f"Thread_{multi_task_id} parsing data: {etf['etf_name']}({etf['etf_code']})"
            )

        # Parse data
        trs = page.query_selector_all(xph_tb)
        tr_list = []
        for tr in trs:
            tr_str = tr.text_content()
            tr_list.append(tr_str.split("\n"))

        tb = []
        for tl in tr_list:
            dic = {}
            dic["s_code"] = tl[0]
            dic["s_name"] = tl[1].strip()
            dic["holding_percentage"] = tl[3].strip()
            dic["holding_amount"] = tl[4][:-1].replace(",", "").strip()
            dic["unit"] = tl[4][-1]
            tb.append(dic)

        etf["etf_holding"] = tb
        browser.close()
    finish = time.perf_counter()
    print(
        f"Time consuming of scraping ({etf_code}): {round(finish - start, 2)} (seconds)"
    )
    return [etf, holding_date]


# Write data into json-file
def save_to_json_file(output_path, etfs_holding, holding_date):
    try:
        start = time.perf_counter()
        num_etfs = len(etfs_holding)
        num_s = 0
        for etf in etfs_holding:
            num_s = num_s + len(etf["etf_holding"])
        etfs_daily = {"holding_date": holding_date, "etf_data": etfs_holding}
        if os.path.isfile(output_path):
            try:
                with open(output_path, mode="r") as f:
                    ds = json.load(f)
                ds_dates = []
                for d in ds:
                    ds_dates.append(d["holding_date"])
                if holding_date not in ds_dates:
                    ds.append(etfs_daily)
                    with open(output_path, "w", encoding="utf-8") as fp:
                        json.dump(ds, fp, ensure_ascii=False, indent=4)
                        print("-" * 30)
                        print(
                            f"{num_etfs} ETFs, including toatal records {num_s}, already written into '{output_path}'. Please check."
                        )
                else:
                    print("-" * 30)
                    print(
                        f"The file '{output_path}' already has the data of {holding_date}. Please check."
                    )
            except Exception as e:
                print(e)
        else:
            try:
                with open(output_path, "w", encoding="utf-8") as fp:
                    json.dump([etfs_daily], fp, ensure_ascii=False, indent=4)
                    print("-" * 30)
                    print(
                        f"{num_etfs} ETFs, including toatal records {num_s}, already written into '{output_path}'. Please check."
                    )
            except Exception as e:
                print(e)
        finish = time.perf_counter()
        print(f"Time consuming of saving file: {round(finish - start, 2)} (seconds)")
    except Exception as e:
        print(e)
