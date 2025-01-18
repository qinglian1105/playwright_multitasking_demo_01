# crawl_async.py
from playwright.async_api import async_playwright
import sharing as shg
import asyncio
import time
import os


# Execute tasks
async def async_worker(task_queue, results, worker_id):
    while not task_queue.empty():
        try:
            task = await task_queue.get()
        except asyncio.QueueEmpty:
            break

        # Playwright runs the browsers
        async with async_playwright() as p:
            url = task
            open_start = time.perf_counter()
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(0.5)
            open_finish = time.perf_counter()

            # Start to scrape data
            start = time.perf_counter()
            etf = {}
            # Get holding_date
            e_code = url[url.find("/tw/") + 4 : url.find("/fundholding?")]
            xpah_date_ele = await page.query_selector_all(shg.xph_date)
            holding_date_ele = await xpah_date_ele[0].text_content()
            holding_date = holding_date_ele[5:]
            print(
                f"Worker_{worker_id} starts for task: {e_code} - <{holding_date_ele}>"
            )

            # Get etf code and name
            xpah_name_ele = await page.query_selector_all(shg.xph_name)
            eles = await xpah_name_ele[0].text_content()
            eles_list = eles.split("\n")
            etf_code = eles_list[2].strip()
            etf_name = eles_list[1].strip()
            etf["etf_code"] = etf_code
            etf["etf_name"] = etf_name
            etf["scraping_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"Worker_{worker_id} parsing data: {etf['etf_name']}({etf['etf_code']})"
            )

            # Parse data
            trs = await page.query_selector_all(shg.xph_tb)
            tr_list = []
            for tr in trs:
                tr_str = await tr.text_content()
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
            results.append([etf, holding_date])
            finish = time.perf_counter()
            print(
                f"Worker_{worker_id} - Time consuming of opening browser: {round(open_finish - open_start, 2)} (seconds)"
            )
            print(
                f"Worker_{worker_id} - Time consuming of scraping: {round(finish - start, 2)} (seconds)"
            )
            await browser.close()
        task_queue.task_done()


async def main():
    task_queue = asyncio.Queue()
    results = []

    tasks = [shg.t_url.format(etf) for etf in shg.etfs]
    for task in tasks:
        await task_queue.put(task)

    num_workers = len(shg.etfs)
    workers = [
        asyncio.create_task(async_worker(task_queue, results, i + 1))
        for i in range(num_workers)
    ]

    await asyncio.gather(*workers)
    res_holding = [re_q[0] for re_q in results]
    res_date = [re_q[1] for re_q in results]
    shg.save_to_json_file(output_path, res_holding, res_date[0])


if __name__ == "__main__":
    start = time.perf_counter()
    this_file = os.path.basename(__file__)
    output_path = f"outputs/{this_file[: this_file.find('.')]}.json"
    this_pid = os.getpid()
    print("-" * 30)
    print("PID:", this_pid, "\n")
    asyncio.run(main())
    finish = time.perf_counter()
    print("PID:", this_pid)
    print(f"Time consuming of the programming: {round(finish - start, 2)} (seconds)")
    print("-" * 30)
