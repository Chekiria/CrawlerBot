Либа позволяет легко распараллелить обработку большого объема данных

## Пример использования:
import parallel

def my_function(x): # Функция, которой необходимо обработать данные
    return x*x

big_data_list = [1,2,3,4,5,6,7,8,9,10] # Список данных

p = parallel.Parallel(func=my_function, data_list=big_data_list) # Создаем объект

print(p.get_queue_size) # Смотрим кол-во обьектов в очереди

p.add_to_queue(1) # Обьекты можно добавлять в очередь поштучно

result = p.start(th_count=5) # Запускаем обработку в 5 потоков(по-умолчанию указано 2) и получаем результат

print(result)