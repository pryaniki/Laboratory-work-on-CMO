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
from collections import deque

from Event import Event
from Application import Application
from Device import Device


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

    num_devices = 1
    type_system = 1
    devices_list: list[Device] = []
    q = deque()
    min_app_service_time = 0.
    selection = {}
    f_selection_to_file = True
    event_table: list[Event] = []
    application_table: list[Application] = []
    number_app_now = 0
    time_arrival_next_app = 0.
    event_start_time = 0.
    current_event_number = 1
    current_app_number = 1
    f_name_with_selection = 'selection.txt'
    device_id_completing_app = -1

    # Время обращения к прибору или время, через которое обратились к прибору

    def __init__(self, num: int, type_: int, f_name: str):

        self.num_devices = num
        self.devices_list = [Device(number=i) for i in range(num)]
        self.type_system = type_
        self._get_selection(f_name)
        self.f_name_with_selection = f_name

    def __repr__(self):
        return f'{self.devices_list}'

    def service_first_app(self):
        """Пришла заявка, обрабатываем ее"""

        # Получаем данные
        self.event_start_time = self.selection['1'][0]
        self.time_arrival_next_app = self.selection['1'][2]
        self.min_app_service_time = self.selection['1'][1]

        #   Заносим информацию о событии
        event = Event(1, self.event_start_time, 1, 1, self.min_app_service_time, self.time_arrival_next_app, 1)

        device = self._search_free_device()
        device.give_task(self.current_app_number, self.selection['1'][1])
        print(device)

        end_time = event.event_time + event.time_until_end_service

        app = Application(1, event.event_time, 0, 0, event.event_time, event.time_until_end_service, end_time)

        # Для дальнейшей работы
        self.number_app_now = 1
        self.current_event_number = 1

        self.event_table.append(event)
        self.application_table.append(app)

    def start_system(self, num_event: int):
        """Запустить моделирование событий"""
        # обработка 1-й заявки
        self.service_first_app()
        while self.current_event_number < num_event:
            self._define_event_type()

        _selection_to_file(self.selection, self.f_name_with_selection)
        return [self.event_table, self.application_table]

    def _define_event_type(self):
        """
        Определяет тип события
                1) СМО обрабатывает заявку
                    1.1 Поступившую заявку
                    1.2 Заявку из очереди
                2) СМО завершает работу над заявкой
                3) СМО добавляет поступившую заявку в очередь

            Есть свободный прибор
            - отдаем заявку ему на обработку
            - заявка отдается прибору, с наименьшим номером
        Нет свободных приборов
            - заносим заявку в очередь
            - ставим -1 в Таблице 2
        """

        if self._search_free_device():  # есть хоть 1 свободный прибор
            self._processing_application()
        elif self.min_app_service_time < self.time_arrival_next_app:  # Заявка завершится быстрее, чем придет новая
            self.current_event_number += 1
            self.number_app_now -= 1
            self._completes_app_processing(self.devices_list[self.device_id_completing_app])
        elif self.min_app_service_time > self.time_arrival_next_app:  # пришла заявка, но все приборы заняты
            self.current_event_number += 1
            self.current_app_number += 1
            self.number_app_now += 1

            self._add_app_to_queue()
        else:
            raise Exception('Необработанный случай')

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
                if self.min_app_service_time > value:
                    self.min_app_service_time = value
                    self.device_id_completing_app = devise.get_number()
        if np.inf == self.min_app_service_time:  # все приборы свободны
            self.min_app_service_time = -1
            self.device_id_completing_app = -1

    def _processing_application(self):
        """ Обрабатывает полученную заявку или достает ее из очереди"""
        device = self._search_free_device()
        if self.q:  # достаем заявку из очереди
            self._process_app_from_queue(device)
        else:  # пришла заявка
            self.current_event_number += 1
            self.current_app_number += 1
            self.number_app_now += 1
            self._process_current_app(device)

    def _process_current_app(self, device: Device):
        """ Отдаем заявку на обслуживание прибору """

        self.event_start_time = self.event_start_time + self.time_arrival_next_app

        if self.f_selection_to_file:
            time_until_end_service = _get_service_time_by_requests(self.type_system)
            self.time_arrival_next_app = _get_time_between_applications(self.type_system)
            self.selection[str(self.current_event_number)] = [time_until_end_service,
                                                              self.time_arrival_next_app,
                                                              ]
        else:
            time_until_end_service = self.selection[str(self.current_event_number)][0]
            self.time_arrival_next_app = self.selection[str(self.current_event_number)][1]

        device.give_task(self.current_app_number, time_until_end_service)

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

    def _process_app_from_queue(self, device: Device):
        """Обрабатывает заявку из очереди, возвращает номер обслуженной заявки"""

        num_app = self.q.popleft()
        if self.f_selection_to_file:
            time_until_end_service = _get_service_time_by_requests(self.type_system)
            self.selection[str(self.current_event_number)] = [time_until_end_service,
                                                              self.time_arrival_next_app]
        else:
            time_until_end_service = self.selection[str(self.current_event_number)][0]
            self.time_arrival_next_app = self.selection[str(self.current_event_number)][1]  # ???

        device.give_task(num_app, time_until_end_service)

        app = self.application_table[num_app - 1]
        app.start_service = self.event_start_time
        app.stay_in_queue = app.start_service - app.app_time
        app.service_time = time_until_end_service
        app.end_time = app.start_service + app.service_time

        self.application_table.append(app)

    def _completes_app_processing(self, device: Device):
        """Завершает обработку заявки"""
        print(device)
        device.end_task() # тут ли разместить?

        self.event_start_time = self.event_start_time + self.min_app_service_time

        self.time_arrival_next_app = self.time_arrival_next_app - self.min_app_service_time
        self._update_min_app_service_time(self.min_app_service_time)

        event = Event(number=self.current_event_number,
                      event_time=self.event_start_time,
                      event_type=2,
                      status_system=self.number_app_now,
                      time_until_end_service=self.min_app_service_time,
                      wait_time=self.time_arrival_next_app,
                      number_application=self.current_app_number,
                      )
        self.event_table.append(event)

    def _add_app_to_queue(self):
        """Добавляем заявку в очередь"""

        self.event_start_time = self.event_start_time + self.time_arrival_next_app
        self._update_min_app_service_time(self.time_arrival_next_app)

        if self.f_selection_to_file:
            service_time = _get_service_time_by_requests(self.type_system)
            self.time_arrival_next_app = _get_time_between_applications(self.type_system)
            self.selection[str(self.current_event_number)] = [service_time, self.time_arrival_next_app]
        else:
            self.time_arrival_next_app = self.selection[str(self.current_event_number)][1]

        self.q.append(self.current_app_number)

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
