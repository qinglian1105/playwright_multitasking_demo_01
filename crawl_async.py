# crawl_async.py
from playwright.async_api import async_playwright
from share_vars import *
import asyncio
import time
import json
import os



# Write data into json-file 
def save_to_json_file(etfs_holding, holding_date): 
    try:
        start = time.perf_counter()  
        num_etfs = len(etfs_holding)      
        num_s = 0
        for etf in etfs_holding:
            num_s = num_s + len(etf['etf_holding'])                  
        etfs_daily = {"holding_date": holding_date,"etf_data": etfs_holding}                                                                   
        if os.path.isfile(output_path): 
            try:       
                with open(output_path, mode='r') as f:
                    ds = json.load(f)
                ds_dates = []
                for d in ds:
                    ds_dates.append(d['holding_date'])                         
                if holding_date not in ds_dates:
                    ds.append(etfs_daily)
                    with open(output_path, 'w', encoding='utf-8') as fp:                            
                        json.dump(ds, fp, ensure_ascii=False, indent=4)
                        print("-"*30)
                        print(f"{num_etfs} ETFs, including toatal records {num_s}, already written into '{output_path}'. Please check.") 
                else:
                    print("-"*30)
                    print(f"The file '{output_path}' already has the data of {holding_date}. Please check.")                                                        
            except Exception as e:
                print(e) 
        else:                    
            try:    
                with open(output_path, 'w', encoding='utf-8') as fp:                            
                    json.dump([etfs_daily], fp, ensure_ascii=False, indent=4)
                    print("-"*30)
                    print(f"{num_etfs} ETFs, including toatal records {num_s}, already written into '{output_path}'. Please check.") 
            except Exception as e:
                print(e)
        finish = time.perf_counter()    
        print(f'Time consuming of saving file: {round(finish-start,2)} (seconds)')        
    except Exception as e:
        print(e) 


# Execute tasks
async def worker(task_queue, results, worker_id):
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
            e_code = url[url.find("/tw/")+4:url.find("/fundholding?")]                                                    
            xpah_date_ele = await page.query_selector_all(xph_date)
            holding_date_ele = await xpah_date_ele[0].text_content()            
            holding_date = holding_date_ele[5:]  
            print(f"Worker_{worker_id} starts for task: {e_code} - <{holding_date_ele}>")                                                                                                                         
            
            # Get etf code and name              
            xpah_name_ele = await page.query_selector_all(xph_name)
            eles = await xpah_name_ele[0].text_content()           
            eles_list = eles.split("\n")
            etf_code = eles_list[2].strip() 
            etf_name = eles_list[1].strip()                                                          
            etf['etf_code'] = etf_code
            etf['etf_name'] = etf_name
            etf['scraping_time'] = time.strftime("%Y-%m-%d %H:%M:%S")                                  
            print(f"Worker_{worker_id} parsing data: {etf['etf_name']}({etf['etf_code']})")                                                        
            
            # Parse data                
            trs = await page.query_selector_all(xph_tb)  
            tr_list = [] 
            for tr in trs:                    
                tr_str = await tr.text_content()
                tr_list.append(tr_str.split("\n"))                    
            tb = []              
            for tl in tr_list:
                dic = {}
                dic['s_code'] = tl[0]
                dic['s_name'] = tl[1].strip()
                dic['holding_percentage'] = tl[3].strip()
                dic['holding_amount'] = tl[4][:-1].replace(",","").strip()
                dic['unit'] = tl[4][-1]
                tb.append(dic)  
            etf['etf_holding'] = tb                          
            results.append([etf, holding_date])             
            finish = time.perf_counter()                             
            print(f'Worker_{worker_id} - Time consuming of opening browser: {round(open_finish-open_start,2)} (seconds)')                    
            print(f'Worker_{worker_id} - Time consuming of scraping: {round(finish-start,2)} (seconds)')            
            await browser.close()            
        task_queue.task_done()                                            


async def main():    
    task_queue = asyncio.Queue()
    results = []
    
    tasks = [t_url.format(etf) for etf in etfs]  
    for task in tasks:
        await task_queue.put(task)
    
    num_workers = len(etfs)
    workers = [
        asyncio.create_task(worker(task_queue, results, i + 1))
        for i in range(num_workers)
    ]     
    
    await asyncio.gather(*workers)          
    res_holding = [re_q[0] for re_q in results]
    res_date = [re_q[1] for re_q in results] 
    save_to_json_file(res_holding, res_date[0])         
           


if __name__ == "__main__":
    start = time.perf_counter()
    output_path = "outputs/crawl_async.json"
    this_pid = os.getpid() 
    print("-"*30)  
    print("PID:", this_pid, "\n")         
    asyncio.run(main())
    finish = time.perf_counter()    
    print("PID:", this_pid)
    print(f'Time consuming of the programming: {round(finish-start,2)} (seconds)')
    print("-"*30) 