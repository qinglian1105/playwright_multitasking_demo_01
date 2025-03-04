# crawl_mth.py
import sharing as shg
import threading
import queue
import time
import os


# Execute tasks
def mth_worker(task_queue, result_queue, thread_id):
    try:
        while True:
            try:
                task = task_queue.get(block=False)
            except queue.Empty:
                break
            result = shg.scraping("mth", task, thread_id)
            result_queue.put(result)
            task_queue.task_done()
    except Exception as e:
        print(e)


def main():
    try:
        task_queue = queue.Queue()
        result_queue = queue.Queue()
        tasks = [shg.t_url.format(etf) for etf in shg.etfs]
        for task in tasks:
            task_queue.put(task)

        num_threads = len(shg.etfs)
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(
                target=mth_worker, args=(task_queue, result_queue, i + 1)
            )
            threads.append(thread)
            thread.start()

        task_queue.join()
        for thread in threads:
            thread.join()

        res_q = []
        while not result_queue.empty():
            res_q.append(result_queue.get())

        res_holding = [re_q[0] for re_q in res_q]
        res_date = [re_q[1] for re_q in res_q]
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
