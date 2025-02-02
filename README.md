# **playwright_multitasking_demo_01**

## **Web scraping with Playwright by different methods of multitasking**

### **Ⅰ. Purpose** 
The content of this project is an experiment of comparing several multitasking methods, including multithreading, multiprocessing, asynchronous and synchronous, for web scraping with Playwright.<br><br>

### **Ⅱ. Tools or Packages**
Playwright, threading, multiprocessing and asyncio. <br><br>

### **Ⅲ. Statement**

__1. The data of web scraping__ <br>

The targeted data is the holding details, like stocks, bonds and so on, of exchange-traded fund (ETF) in Taiwan. The ETFs are selected according to the standard that they primarily invest in stocks and their asset value is more than one hundred billion (TWD). Therefore, 8 ETFs are selected in this project. Their security codes are '0050', '00878', '0056', '00919', '00929', '006208', '00940' and '00713' respectively.<br>
In addition, the information about ETF ranking by asset value, trading volume and so on, in Taiwan can be read on the website, Yahoo Finance (Taiwan). (Please refer to [details](<https://tw.stock.yahoo.com/tw-etf/total-assets>))。<br>
<br> 

__2. Data source__ <br>

Thanks for the website, "https://www.pocket.tw/etf/", provided by Pocket Securities. This company, one of the best Online Brokers in Taiwan, delivers high-quality services to customers, and its website makes it easier for investors to obtain financial data and useful information. <br>
<br>

__3. Results__ <br>

As you can see in the folder of this project, four methods, including multithreading, multiprocessing, asynchronous and synchronous, for web scraping are written into different files. (Please refer to "./\*.py" ) <br>
The content of html will be pared, processed, and then saved into a JSON file. (Please refer to "./outputs/\*.json" ) <br>
The time spent by the four methods is compared as follows.<br><br> 

| Method         | Package        | Python file   | Output file     | Time spent (s)|
| :---           | :---           | :----         | :---            | :---:         |
| Asynchronous   | asyncio        | crawl_async.py| crawl_async.json| 16.69         |
| Multithreading | threading      | crawl_mps.py  | crawl_mps.json  | 17.01         |
| Multiprocessing| multiprocessing| crawl_mps.py  | crawl_mth.json  | 17.03         |
| Synchronous    |                | crawl_loop.py | crawl_loop.json | 38.01         |

<br>
Obviously, except for the method of Synchronous, the other three are more than 2 times faster. The python code writing or style within this project may not be the most efficient.<br> 
In addition, the conditions at different points in time, such as the number of times the server that is accessed at the same time, may have different impacts.<br> 
To sum up, the other three methods are almost as fast, and the time difference is pretty small.<br><br>
( Dockerizing Playwright For Web Scraping, please refer to Dockerfile and docker-compose.yml )

<br><br><br>

---

### **Ⅳ. References**

[1] [Playwright for Python - Docs](<https://playwright.dev/python/docs/intro>)

[2] [Yahoo Finance (Taiwan) - ETF asset ranking](<https://tw.stock.yahoo.com/tw-etf/total-assets>)

[3] [Pocket Securities - ETF](<https://www.pocket.tw/etf/>)