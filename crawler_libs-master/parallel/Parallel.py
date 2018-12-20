import threading
import queue

DONE_COUNTER = 0
TOTAL_WORK = 0

PRINT_LOCK = threading.Lock()
RESULT_LOCK = threading.Lock()
DONE_COUNTER_LOCK = threading.Lock()


class Parallel:
    def __init__(self, func: callable, data_list: list = list()):
        """ func:           функция, которой нужно обрабатать каждый элемент списка
            data_list:      список элементов, которые необходимо обработать """
        self._func = func
        self._threads = []
        self._queue = queue.Queue()
        self._result_list = []

        for item in data_list:
            self._queue.put(item)

    @property
    def get_queue_size(self):
        return self._queue.qsize()

    def add_to_queue(self, item):
        self._queue.put(item)

    def start(self, th_count: int = 2) -> list:
        print('----------[parallel]----------')

        global TOTAL_WORK
        TOTAL_WORK = self.get_queue_size

        print('Всего работы: {0}'.format(TOTAL_WORK))
        print('Кол-во рабов: {0}'.format(th_count))

        for i in range(0, th_count):
            th = WorkThread(func=self._func, queue_ref=self._queue, result_ref=self._result_list)
            self._threads.append(th)
            th.start()
            if self._queue.empty():
                print("Очередь пустая. Хватит покупать рабов!")
                break

        for th in self._threads:
            th.join()

        print('----------[parallel]----------')
        return self._result_list


class WorkThread(threading.Thread):

    def __init__(self, func, queue_ref, result_ref):
        """ Объявляем раба
            func:           чем обрабатывать
            queue_ref:      откуда брать работу
            result_ref:     куда складывать результат """
        threading.Thread.__init__(self)
        self._func = func
        self._queue = queue_ref
        self._result = result_ref

    def run(self):
        while not self._queue.empty():

            try:
                cur_result = self._func(self._queue.get_nowait())
            except queue.Empty:
                break

            with RESULT_LOCK:
                self._result.append(cur_result)

            with DONE_COUNTER_LOCK:
                global DONE_COUNTER
                DONE_COUNTER += 1

            self.__check_progress()

    @staticmethod
    def __check_progress():
        if TOTAL_WORK < 100:
            return

        progress_percent = (DONE_COUNTER / round(TOTAL_WORK, -1)) * 100
        if progress_percent in range(0, 110, 10):
            with PRINT_LOCK:
                print('Обработано: [{1}/{2}] {0}%'.format(int(progress_percent), DONE_COUNTER, TOTAL_WORK))
