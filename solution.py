"""

Содержит решение 1-3 задач
Вычисление таблиц аналитического раздела

"""

import os
import json
import numpy as np


from collections import deque, Counter
from Controller_SMO import Controller_SMO
from Event import Event
from Application import Application
from ListWrapper import ListWrapper





def _get_initial_data(n_task: int, f_name: str) -> tuple[bool, dict]:
    """ Получаем начальные данные из файла или генерируем их"""

    if os.path.exists(f_name):
        is_write_to_file = False
        with open(f_name, 'r') as file:
            data = json.load(file)
    else:
        is_write_to_file = True
        data = {'1': [_get_time_between_applications(n_task), _get_service_time_by_requests(n_task),
                      _get_time_between_applications(n_task)]}

    return is_write_to_file, data


def process_app_from_queue(q: deque, n_task: int, event: Event, past_event: Event,
                           is_write_to_file: bool, data: dict, table2: list[Application]) -> int:
    """Обрабатывает заявку из очереди, возвращает номер обслуженной заявки"""
    event.event_time = past_event.event_time
    event.event_type = 1

    if is_write_to_file:
        event.remain_time = _get_service_time_by_requests(n_task)
        event.wait_time = past_event.wait_time
        data[str(event.num)] = [event.event_time, event.remain_time, event.wait_time]
    else:
        event.remain_time = data[str(event.num)][1]
        event.wait_time = data[str(event.num)][2]
    event.num_application = q.popleft()
    event.status_system = len(q) + 1
    app = table2[event.num_application - 1]  # !?????

    app.start_service = event.event_time
    app.stay_in_queue = app.start_service - app.app_time
    app.service_time = event.remain_time
    app.end_time = app.start_service + app.service_time
    return app.number


def process_current_app(q: deque, n_task: int, event: Event, past_event: Event, app: Application,
                        is_write_to_file: bool, data: dict, table2: list[Application]) -> int:
    """ Обрабатывает новую заявку,возвращает номер обслуженной заявки """
    event.event_time = past_event.event_time + past_event.wait_time
    event.event_type = 1
    event.status_system = len(q)+1

    event.remain_time = _get_service_time_by_requests(n_task)
    event.wait_time = _get_time_between_applications(n_task)
    if is_write_to_file:
        event.remain_time = _get_service_time_by_requests(n_task)
        event.wait_time = _get_time_between_applications(n_task)
        data[str(event.num)] = [event.event_time, event.remain_time, event.wait_time]
    else:
        event.remain_time = data[str(event.num)][1]
        event.wait_time = data[str(event.num)][2]
    app.number = len(table2) + 1
    event.num_application = app.number

    app.app_time = event.event_time
    app.place_in_queue = 0
    app.stay_in_queue = 0
    app.start_service = event.event_time
    app.service_time = event.remain_time
    app.end_time = app.start_service + app.service_time
    table2.append(app)
    return app.number


def process_application(q: deque, n_task: int, event: Event, past_event: Event, app: Application,
                        is_write_to_file: bool, data: dict, table2: list[Application]):
    """ Обработка заявки"""

    if q:  # достаем заявку из очереди
        return process_app_from_queue(q, n_task, event, past_event, is_write_to_file, data, table2)
    else:  # пришла заявка
        return process_current_app(q, n_task, event, past_event, app, is_write_to_file, data, table2)


def completes_app_processing(n_task, q: deque, event: Event, past_event: Event, num_serviced_app: int, table2, num_states_app):
    """Завершает обработку заявки"""
    from constants import NUM_EVENTS
    event.event_time = past_event.event_time + past_event.remain_time
    event.event_type = 2
    event.status_system = len(q)
    if q and num_states_app + 1 == NUM_EVENTS:
        event.remain_time = _get_service_time_by_requests(n_task)
        app = table2[num_serviced_app-1]  # !?????
        app.start_service = event.event_time
        app.stay_in_queue = app.start_service - app.app_time
        app.service_time = event.remain_time
        app.end_time = app.start_service + app.service_time
    else: #  очередь пуста
        event.remain_time = -1
    event.wait_time = past_event.wait_time - past_event.remain_time
    event.num_application = num_serviced_app


def add_app_to_queue(q: deque, n_task: int, event: Event, past_event: Event, app: Application,
                     is_write_to_file: bool, data: dict, table2: list[Application]):
    """Добавляем заявку в очередь"""

    event.event_time = past_event.event_time + past_event.wait_time
    event.event_type = 1
    event.status_system = len(q)
    if is_write_to_file:
        event.remain_time = _get_service_time_by_requests(n_task)
        event.wait_time = _get_time_between_applications(n_task)
        data[str(event.num)] = [event.event_time, event.remain_time, event.wait_time]
    else:
        event.wait_time = data[str(event.num)][2]
    event.remain_time = past_event.remain_time - past_event.wait_time

    app.number = len(table2) + 1
    q.append(app.number)
    event.status_system = past_event.status_system + 1  # len(q)+1
    event.num_application = len(table2) + 1
    app.app_time = event.event_time
    app.place_in_queue = len(q)  #

    table2.append(app)


def change_table_1(table, table2):
    """Убирает лишние строки из таблицы 1"""
    #  заменить -1 на время выполнения заявки из очереди
    num_row = 1
    new_table = []
    past_time = 0
    for event in table:

        if event.event_time != past_time:
            if event.status_system != 0 and event.remain_time == -1:
                #print(f'заявка {event.num_application+1}')

                #print(f'Меняю {event.remain_time} на {table2[event.num_application].service_time} ')
                event.remain_time = table2[event.num_application].service_time
                #print(f'В строке{num_row + 1}]\n\n')

            event.num = num_row
            new_table.append(event)
            num_row = num_row + 1


        past_time = event.event_time
    return new_table


def event_handler(n_task: int) -> list[list[Event] | list[Application]]:
    """Обработчик событий. Заполняет таблицы 1 и 2"""
    from constants import NUM_EVENTS, NUM_SMO

    f_name = f'table1_task{n_task}.txt'
    smo = Controller_SMO(NUM_SMO, n_task, f_name)
    print(smo)
    result = smo.start_system(NUM_EVENTS)

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
