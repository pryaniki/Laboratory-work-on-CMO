"""

Содержит решение 1-3 задач
Вычисление таблиц аналитического раздела

"""

import os
import json


from collections import deque, Counter
from Controller_SMO import Controller_SMO
from Event import Event
from Application import Application
from ListWrapper import ListWrapper


def event_handler(n_task: int) -> list[list[Event] | list[Application]]:
    """Обработчик событий. Заполняет таблицы 1 и 2"""
    from constants import NUM_EVENTS, NUM_SMO

    f_name = f'table1_task{n_task}.txt'
    result = Controller_SMO(NUM_SMO, n_task, f_name).start_system(NUM_EVENTS)

    return result


def get_downtime_SMO(table_1) -> float:
    """ Считает время простоя СМО"""
    downtime_SMO = 0  # Время простоя СМО
    for i, val in enumerate(table_1[4]):
        if val == -1:
            downtime_SMO += table_1[5][i]
    return downtime_SMO


def get_frequency_states(counter_states: dict) -> list:
    """ Находит частоты состояний СМО"""

    frequency_states_1 = {}
    frequency_states = []  # .clean
    for state in counter_states:
        frequency_states_1[state] = counter_states[state] / 100
    try:
        frequency_states_1[0]
    except:
        frequency_states_1[0] = 0.0

    for i in range(len(frequency_states_1)):
        frequency_states.append(frequency_states_1[i])

    return frequency_states


def get_data_for_row(table: list[list[Event | Application]]) -> tuple[ListWrapper, list]:
    """ Возвращает данные для аналитического раздела"""
    from constants import NUM_EVENTS
    table_1 = []
    reversed_table_1 = []
    table_2 = []
    reversed_table_2 = []
    for elem1 in table[0]:
        table_1.append(elem1.get_data_for_report())

    for elem2 in table[1]:
        table_2.append(elem2.get_data_for_report())

    for i, row in enumerate(zip(*table_1)):
        reversed_table_1.append(list(row))
    for i, row in enumerate(zip(*table_2)):
        reversed_table_2.append(list(row))

    app_counter = Counter(reversed_table_1[2])  # счетчик заявок(поступивших\обслуженных)
    average_num_apps = sum(reversed_table_1[3]) / 100  # среднее время пребывания заявок в очереди на интервале
    average_time_apps_in_queue = sum(reversed_table_2[3]) / app_counter[
        2]  # среднее время пребывания заявок в очереди на интервале
    border = Counter(reversed_table_2[6])[-1]
    average_time_apps_in_SMO = sum(list(map(lambda x, y: x - y, reversed_table_2[6][:len(reversed_table_2[6]) - border],
                                            reversed_table_2[1][:len(reversed_table_2[1]) - border]))) / app_counter[
                                   2]  # среднее время пребывания заявок в СМО на интервале

    downtime_SMO = get_downtime_SMO(reversed_table_1)  # Время простоя СМО
    downtime_ratio_SMO = downtime_SMO / reversed_table_1[1][
        NUM_EVENTS - 1]  # коэффициент простоя прибора на интервале
    counter_states = Counter(sorted(reversed_table_1[3]))  # количество входа в определенное состояние
    frequency_states = get_frequency_states(counter_states)[:]
    return ListWrapper([app_counter[1], app_counter[2], average_num_apps,
                        average_time_apps_in_queue, average_time_apps_in_SMO, downtime_ratio_SMO]), frequency_states


def get_data_for_an_calc(tables: list[list[list[Event] | list[Application]]]) -> list[list[ListWrapper | list]]:
    """Формирует таблицу для отчета в аналитическом разделе"""

    table_1 = []
    frequency_states = []

    for table in tables:
        row, frequency_state = get_data_for_row(table)
        table_1.append(row)
        frequency_states.append(frequency_state[:])

    return [table_1, frequency_states]
