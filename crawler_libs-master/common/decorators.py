import time


def calc_time_perfomance(function_to_wrap):
    """ Отображает время работы функции в секундах """
    def wrapper():
        start_ts = time.time()
        function_to_wrap()
        work_time = time.time() - start_ts
        print("Function [{0}] working time: {1}".format(function_to_wrap.__name__, work_time))
    return wrapper
