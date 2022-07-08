"""
    Обрабатывает полученные заявки
        - следит за очередью заявок
        - хранит наименьшее время, оставшееся до завершения заявки прибором
    - поручает приборам выполнение заявок
    - записывает результаты в таблицу 1, 2
    - собирает данные для аналитической части
        - собирает частоту пребывания СМО в состояниях

"""
import numpy as np
import json
import os
from collections import deque, Counter

from Event import Event
from Application import Application
from Device import Device
from DeviceData import DeviceData


class Controller_SMO:
    """

       Класс для управления приборами из системы массового обслуживания (СМО)

        ...

       Атрибуты
       --------
        num_devices : int (default 1)
                Количество приборов, находящихся в подчинении
        type_system : int (default 1)
                Тип системы
                1 : Система массового обслуживания (D|M|n)
                2 : Система массового обслуживания (M|D|n)
                3 : Система массового обслуживания (M|M|n)


        device_id_completing_app : ind (default -1)
            Номер прибора, который быстрее всех заканчивает обслуживание заявки
        number_app_now : int (default 0)
                Количество заявок, находящихся в СМО в данный момент
        current_event_number : int (default 1)
                Номер события, которое обслуживается сейчас
        current_app_number : int (default 1)
                Номер заявки, которая обслуживается сейчас

        min_app_service_time : float (default 0.)
                Минимальное время обслуживания заявки
        time_arrival_next_app : float (default 0.)
                Время прихода следующей заявки
        event_start_time : float (default 0.)
                Время наступления события

        devices_list : list[Device]  (default [])
                Список подчиненных приборов
        event_table : list[Event] (default [])
                Таблица событий
        application_table : list[Application] (default [])
                Таблица заявок
        _app_list_need_to_complete : list[int] (default [])
                Номера заявок, которые надо завершить

        q :   deque (default deque())
                Очередь заявок

        selection : dict (default {})
                Выборка данный, для работы приборов. Нужна чтоб повторить прошлый результат выполнения программы

        f_selection_to_file : bool (default True)
                Флаг, нужно ли записывать выборку в файл или нет.
                    True : Файл нужно записать
                    False : Файл с выборкой записан, записывать не надо

        f_name_with_selection : str (default' selection.txt')
                Имя файла в котором, либо содержится выборка, либо ее надо в него записать\
       Методы
       ------
        ***
                Обрабатывает пришедшую заявку

        ***
                Собирает данные для отчета
        ****

       """
    selection = {}
    f_selection_to_file = True

    def __init__(self, num: int, type_: int, f_name: str):

        self.num_devices = num
        self.devices_list: list[Device] = [Device(number=i) for i in range(num)]
        self.type_system = type_
        self.selection = {}
        self._get_selection(f_name)
        self.f_name_with_selection = f_name
        self.event_table: list[Event] = []
        self.application_table: list[Application] = []
        self.q = deque()

        self.min_app_service_time = 0.
        self.number_app_now = 0
        self.time_arrival_next_app = 0.
        self.event_start_time = 0.
        self.current_event_number = 1
        self.current_app_number = 1
        self.device_id_completing_app = 0
        self._app_list_need_to_complete = []

    def __repr__(self):
        return f'{self.devices_list}'

    def service_first_app(self):
        """Пришла заявка, обрабатываем ее"""

        self.event_start_time = self.selection['1'][0]
        self.min_app_service_time = self.selection['1'][1]
        self.time_arrival_next_app = self.selection['1'][2]

        event = Event(self.current_event_number, self.event_start_time, 1, 1, self.min_app_service_time, self.time_arrival_next_app, 1)

        device = self._search_free_device()
        device.give_task(self.current_app_number, self.min_app_service_time)

        end_time = event.event_time + event.time_until_end_service
        self.number_app_now = 1
        app = Application(self.number_app_now, event.event_time, 0, 0, event.event_time, event.time_until_end_service, end_time)
        self._app_list_need_to_complete.append(self.current_app_number)
        self.event_table.append(event)
        self.application_table.append(app)

    def _get_selection(self, f_name: str):
        """
        Получаем начальные данные из файла или генерируем их

        Меняет значение self.f_selection_to_file

        """

        if os.path.exists(f_name):
            self.f_selection_to_file = False
            self.selection = _load_selection(f_name)
        else:
            self.f_selection_to_file = True
            self.selection = {'1': [_get_time_between_applications(self.type_system),
                                    _get_service_time_by_requests(self.type_system),
                                    _get_time_between_applications(self.type_system)]}

    def start_system(self, num_event: int):
        """Запустить моделирование событий"""

        self.service_first_app()  # обработка 1-й заявки
        while self.current_event_number < num_event:
            self._define_event_type()

        _selection_to_file(self.selection, self.f_name_with_selection)
        return [self.event_table, self.application_table]

    def _define_event_type(self):
        """
        Определяет тип события
                1) СМО обрабатывает заявку
                    1.1) В СМО нет заявок, которые были обслужены
                        1.1.1) Поступившую заявку
                        1.1.2) Заявку из очереди
                    1.2) В СМО есть заявки, которые были обслужены и их нужно завершить
                        1.2.1 Завершаем работу над заявкой
                2) СМО завершает работу над заявкой
                3) СМО добавляет поступившую заявку в очередь
        В функции происходит:

        - генерация событий;
        - заполнение таблицы event_table
        - заполнение таблицы application_table

        """
        device = self._search_free_device()
        self._update_min_app_service_time(0)

        if device:  # есть хоть 1 свободный прибор
            # если есть свободный прибор, то берем заявку из очереди
            # очередь пуста, принимаем заявку без очереди
            # В очереди есть заявки и скоро прейдет новая:
            #       - достаем заявку из очереди и даем ее на обслуживание
            #       - новую заявку отправляем в очередь

            if self.q:  # достаем заявку из очереди
                while device:  # раскидываем все заявки по свободным приборам
                    self._process_app_from_queue(device)
                    self._update_min_app_service_time(0)
                    device = self._search_free_device()
                if self.min_app_service_time > self.time_arrival_next_app:
                    self._add_app_to_queue()
                else:
                    self._completes_app_processing(self.devices_list[self.device_id_completing_app])
            else:  # очередь пуста
                if self.min_app_service_time == -1 or \
                        self.min_app_service_time > self.time_arrival_next_app:  # Все приборы свободны
                    self._process_current_app(device)
                else:
                    self._completes_app_processing(self.devices_list[self.device_id_completing_app])

        elif self.min_app_service_time < self.time_arrival_next_app:  # Заявка завершится быстрее, чем придет новая
            self._completes_app_processing(self.devices_list[self.device_id_completing_app])
        elif self.min_app_service_time > self.time_arrival_next_app:  # пришла заявка, но все приборы заняты
            self._add_app_to_queue()
        else:
            raise Exception('Необработанный случай')

    def _search_free_device(self) -> Device | None:
        """ Опрос приборов о выполнении заявок """
        for device in self.devices_list:
            if device.is_free():
                return device

        return None

    def _ger_app_service_time_devises(self) -> dict[Device, float]:
        """Спрашивает у приборов время окончания обслуживания заявки"""
        result = {}
        for devise in self.devices_list:
            if not devise.is_free():  # прибор занят
                result[devise] = devise.get_time_until_end_service_app()

        return result

    def _update_min_app_service_time(self, time):
        """
        Опрашивает все занятые приборы и получает номер  прибора и минимальное время до завершения обслуживания заявки

        Изменяет
            self.min_app_service_time
            self.device_id_completing_app
        """
        self.min_app_service_time = np.inf
        for devise in self.devices_list:
            if not devise.is_free():  # прибор работает над заявкой
                value = devise.update_time_until_end_service_app(time)
                if self.min_app_service_time > value > 0:  # 0 - прибор закончил работу
                    self.min_app_service_time = value
                    self.device_id_completing_app = devise.get_number()
        if np.inf == self.min_app_service_time:  # все приборы свободны
            self.min_app_service_time = -1
            self.device_id_completing_app = -1

    def _processing_application(self, device):
        """ Обрабатывает полученную заявку или достает ее из очереди"""
        pass

    def _process_current_app(self, device: Device):
        """ Отдаем заявку на обслуживание прибору """
        self.current_event_number += 1
        self.current_app_number += 1
        self.number_app_now += 1

        self.event_start_time = self.event_start_time + self.time_arrival_next_app
        if self._app_list_need_to_complete:
            self._update_min_app_service_time(self.time_arrival_next_app)
        else:
            self._update_min_app_service_time(0)

        if self.f_selection_to_file:
            time_until_end_service = _get_service_time_by_requests(self.type_system)
            self.time_arrival_next_app = _get_time_between_applications(self.type_system)
            self.selection[str(self.current_event_number)] = [time_until_end_service, self.time_arrival_next_app]
        else:
            time_until_end_service = self.selection[str(self.current_event_number)][0]
            self.time_arrival_next_app = self.selection[str(self.current_event_number)][1]
        self._app_list_need_to_complete.append(self.current_app_number)

        device.give_task(self.current_app_number, time_until_end_service)
        self._update_min_app_service_time(0)
        event = Event(number=self.current_event_number,
                      event_time=self.event_start_time,
                      event_type=1,
                      status_system=self.number_app_now,
                      time_until_end_service=self.min_app_service_time,
                      wait_time=self.time_arrival_next_app,
                      number_application=self.current_app_number,
                      )
        app = Application(number=self.current_app_number,
                          application_time=self.event_start_time,
                          place_in_queue=0,
                          staying_in_queue=0,
                          start_service=self.event_start_time,
                          service_time=time_until_end_service,
                          end_time=self.event_start_time + time_until_end_service,
                          )
        self.event_table.append(event)
        self.application_table.append(app)

    def _completes_app_processing(self, device: Device):
        """Завершает обработку заявки"""
        self.current_event_number += 1
        self.number_app_now -= 1

        self.event_start_time = self.event_start_time + self.min_app_service_time
        self.time_arrival_next_app = self.time_arrival_next_app - self.min_app_service_time
        self._update_min_app_service_time(self.min_app_service_time)
        app_num = device.end_task()
        event = Event(number=self.current_event_number,
                      event_time=self.event_start_time,
                      event_type=2,
                      status_system=self.number_app_now,
                      time_until_end_service=self.min_app_service_time,
                      wait_time=self.time_arrival_next_app,
                      number_application=app_num,
                      )
        self.event_table.append(event)
        self._app_list_need_to_complete.remove(app_num)

    def _process_app_from_queue(self, device: Device):
        """Обрабатывает заявку из очереди"""
        num_app, num_event = self.q.popleft()
        if self.f_selection_to_file:
            service_time = self.selection[str(num_event)][0]
            self.selection[str(num_event)] = [service_time, self.selection[str(num_event)][1]]
        else:
            service_time = self.selection[str(num_event)][0]

        device.give_task(num_app, service_time)
        self._app_list_need_to_complete.append(num_app)
        app = self.application_table[num_app - 1]
        app.start_service = self.event_start_time
        app.stay_in_queue = app.start_service - app.app_time
        app.service_time = service_time
        app.end_time = app.start_service + app.service_time

    def _add_app_to_queue(self):
        """Добавляем заявку в очередь"""
        self.current_event_number += 1
        self.current_app_number += 1
        self.number_app_now += 1

        self.event_start_time = self.event_start_time + self.time_arrival_next_app
        self._update_min_app_service_time(self.time_arrival_next_app)
        if self.f_selection_to_file:
            service_time = _get_service_time_by_requests(self.type_system)
            self.time_arrival_next_app = _get_time_between_applications(self.type_system)
            self.selection[str(self.current_event_number)] = [service_time, self.time_arrival_next_app]
        else:
            self.time_arrival_next_app = self.selection[str(self.current_event_number)][1]

        self.q.append((self.current_app_number, self.current_event_number))

        event = Event(number=self.current_event_number,
                      event_time=self.event_start_time,
                      event_type=1,
                      status_system=self.number_app_now,
                      time_until_end_service=self.min_app_service_time,
                      wait_time=self.time_arrival_next_app,
                      number_application=self.current_app_number,
                      )
        app = Application(number=self.current_app_number,
                          application_time=self.event_start_time,
                          place_in_queue=len(self.q),
                          )
        self.event_table.append(event)
        self.application_table.append(app)

    def get_frequency_table(self):

        table_1 = []
        reversed_table_1 = []
        for elem1 in self.event_table:
            table_1.append(elem1.get_data_for_report())
        for i, row in enumerate(zip(*table_1)):
            reversed_table_1.append(list(row))
        counter_states = Counter(sorted(reversed_table_1[3]))  # количество входа в определенное состояние

        frequency_states = _get_frequency_states(counter_states)[:]

        return frequency_states

    def get_data_for_report(self):
        """Собирает с прибора данные, необходимые для отчета"""
        table: list[DeviceData] = []
        for device in self.devices_list:
            work_time = self.event_table[-1].event_time
            device.device_data.calculate_device_downtime_ratio(work_time)
            table.append(device.device_data.get_data_for_report())
        return table

    def get_column_for_table_5(self):
        num_apps_received = 0  # Число поступивших на обслуживание заявок
        num_apps_served = 0  # Число обслуженных заявок
        for device in self.devices_list:
            num_apps_received += device.device_data.num_applications_received
            num_apps_served += device.device_data.num_applications_served
        num_apps_received += len(self.q)

        sum_column_status_system = 0.
        queue_time = 0.
        application_time_in_smp = 0.
        for event in self.event_table:
            sum_column_status_system += event.status_system
        for app in self.application_table:
            if app.stay_in_queue != -1:
                queue_time += app.stay_in_queue
                application_time_in_smp += app.service_time

        return [num_apps_received, num_apps_served,
                sum_column_status_system / 100,
                queue_time / num_apps_served,
                application_time_in_smp / num_apps_served,
                ]


def _get_frequency_states(counter_states: dict) -> list:
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


def _get_time_between_applications(data):
    """получить время между заявками."""
    from constants import DELTA_T, LAMBD
    if data in (2, 3):
        return abs(np.random.exponential(1 / LAMBD))
    elif data == 1:
        return DELTA_T


def _get_service_time_by_requests(data):
    """получить время обслуживания заявками."""
    from constants import SERVICE_TIME, MU
    if data in (1, 3):
        return abs(np.random.exponential(1 / MU))
    elif data == 2:
        return SERVICE_TIME


def _load_selection(f_name, dir_='') -> dict[str: float]:
    """Загружает выборку из файла"""
    if os.path.exists(dir_ + f_name):
        with open(dir_+f_name, 'r') as file:
            return json.load(file)
    else:
        raise Exception(f'Не могу найти {dir_ + f_name}')


def _selection_to_file(data, f_name, dir_=''):
    """ Записывает выборку в файл"""
    if not os.path.exists(dir_ + f_name):
        with open(dir_ + f_name, 'w') as file:
            json.dump(data, file)
