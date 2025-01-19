# crawl_loop.py
import sharing as shg
import time
import os


def main():
    try:
        res_holding = []
        res_date = []
        tasks = [shg.t_url.format(etf) for etf in shg.etfs]
        for idx, task in enumerate(tasks):
            res = shg.scraping("loop", task, idx + 1)
            res_holding.append(res[0])
            res_date.append(res[1])
        shg.save_to_json_file(output_path, res_holding, res_date[0])
    except Exception as e:
        print(e)


if __name__ == "__main__":
    start = time.perf_counter()
    this_file = os.path.basename(__file__)
    output_path = f"outputs/{this_file[: this_file.find('.')]}.json"
    this_pid = os.getpid()
    print("-" * 30)
    print("PID:", this_pid, "\n")
    main()
    finish = time.perf_counter()
    print("PID:", this_pid)
    print(f"Time spent of the programming: {round(finish - start, 2)} (seconds)")
    print("-" * 30)
