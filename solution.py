"""

Содержит решение 1-3 задач
Вычисление таблиц аналитического раздела

"""
import math
from Controller_SMO import Controller_SMO


def event_handler(n_task: int):
    """Обработчик событий. Заполняет таблицы 1 и 2"""
    from constants import NUM_EVENTS, NUM_SMO

    f_name = f'table1_task{n_task}.txt'
    smo = Controller_SMO(NUM_SMO, n_task, f_name)
    result = smo.start_system(NUM_EVENTS)

    return smo, result


def get_table_with_device_data(smo):
    """ Собирает данными о приборах для таблицы 3"""
    t_device_data = smo.get_data_for_report()

    return t_device_data


def get_data_for_table_5(smo):
    return smo.get_column_for_table_5()


def get_frequency_table(smo):
    return smo.get_frequency_table()


def get_vector_r(length):
    from constants import MU, LAMBD, NUM_SMO
    print(f'length={length}')
    print(f'lambd = {LAMBD}, my = {MU}')
    vector = []
    p = LAMBD/MU
    v = p/NUM_SMO
    print(f'v = {v}')
    r0 = 0
    for k in range(NUM_SMO):
        r0 += p**k / math.factorial(k)
    r0 = (r0+(p**NUM_SMO/math.factorial(NUM_SMO))*(1/(1-v)))**(-1)

    print(f'r0 = {r0}')
    vector.append(r0)
    l = 0
    for k in range(1,  NUM_SMO+1):
        print(k)
        vector.append((r0 * p**k) / math.factorial(k))

    for l in range(1, length-NUM_SMO):
        print(k+l)
        vector.append((v**l)*vector[NUM_SMO])
    print(vector[NUM_SMO])
    print(vector)
    return vector


def get_frequency_table_task_3(vector_r, vector_v):
    table = []
    sum_r = 0
    sum_v = 0
    max_value = 0
    for i in range(len(vector_v)):
        sum_r += vector_r[i]
        sum_v += vector_v[i]
        value = abs(vector_v[i] - vector_r[i])
        if value > max_value:
            max_value = value
        table.append([i, vector_r[i], vector_v[i], value])
    table.append(['', sum_r, sum_v, max_value])
    return table


def get_data_for_an_calc(smo_list):
    """
    Формирует данные для отчета в аналитическом разделе

    В отчете 6 таблиц и 1 вектор r(список)

    """
    # с данными о приборах
    table_3 = []
    table_for_task_5 = []

    for i in range(3):
        table_3.append(get_table_with_device_data(smo_list[i]))
        table_for_task_5.append(get_data_for_table_5(smo_list[i]))

    frequency_tables = [get_frequency_table(smo) for smo in smo_list]

    vector_r = get_vector_r(len(frequency_tables[2]))  # !!!!!!!!!!!
    print(len(vector_r))
    frequency_table_task_3 = get_frequency_table_task_3(vector_r, frequency_tables[2])
    for row in frequency_table_task_3:
        print(row)
    return [table_3, vector_r, table_for_task_5, frequency_tables[:2], frequency_table_task_3]