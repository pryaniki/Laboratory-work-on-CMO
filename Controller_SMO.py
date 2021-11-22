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
        devices_list : list[Device]  (default [])
                Список подчиненных приборов
        q :   deque (default deque())
                Очередь заявок
        min_app_service_time : int (default 0)
                Минимальное время обслуживания заявки
        selection : dict (default {})
                Выборка данный, для работы приборов. Нужна чтоб повторить прошлый результат выполнения программы
        f_selection_to_file : bool (default True)
                Флаг, нужно ли записывать выборку в файл или нет.
                    True : Файл нужно записать
                    False : Файл с выборкой записан, записывать не надо
        event_table : list[Event] (default [])
                Таблица событий
        application_table : list[Application] (default [])
                Таблица заявок
        number_app_now : int (default 0)
                Количество заявок, находящихся в СМО в данный момент
        time_arrival_next_app : float (default 0.)
                Время прихода следующей заявки
        f_name_with_selection : str (default' selection.txt')
                Имя файла в котором, либо содержится выборка, либо ее надо в него записать
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
    min_app_service_time = 0
    selection = {}
    f_selection_to_file = True
    event_table: list[Event] = []
    application_table: list[Application] = []
    number_app_now = 0
    time_arrival_next_app = 0.
    f_name_with_selection = 'selection.txt'

    # Время обращения к прибору или время, через которое обратились к прибору

    def __init__(self, num: int, type_: int, f_name: str):

        self.num_devices = num
        self.devices_list = [Device(number=i) for i in range(num)]
        self.type_system = type_
        self._get_selection(f_name)
        self.time_arrival_next_app = self.selection['1'][2]
        self.f_name_with_selection = f_name

    def __repr__(self):
        return f'{self.devices_list}'

    def start_system(self, num_event: int):
        """Запустить моделирование событий"""

        event = Event(1, self.selection['1'][0], 1, 1, self.selection['1'][1], self.selection['1'][2], 1)

        end_time = event.event_time + event.remain_time
        app = Application(1, event.event_time, 0, 0, event.event_time, event.remain_time, end_time)
        self.event_table = [event]
        self.application_table = [app]
        self.min_app_service_time = event.remain_time
        self.number_app_now = 1
        # past_event: dict[Device, Event] = {Device(i): 0 for i in range(self.num_devices)}

        num_serviced_app = 1  # Номер обслуженной заявки
        num_processed_event = 1  # Номер обработанного события

        while num_processed_event < num_event:
            event = Event(number=event.num + 1)
            app = Application()
            self._define_event_type(num_processed_event, event, app)

            self.event_table.append(event)
        _selection_to_file(self.selection, self.f_name_with_selection)
        return [self.event_table, self.application_table]

    def _define_event_type(self, num_processed_event: int, event: Event, app: Application):
        """
        Определяет тип события
                1) СМО обрабатывает заявку
                    1.1 Поступившую заявку
                    1.2 Заявку из очереди
                2) СМО завершает работу над заявкой
                3) СМО добавляет поступившую заявку в очередь

        """

        #  Обновление self.min_app_service_time
        #  Обновление self.time_arrival_next_app
        if self._search_free_device():  # есть хоть 1 свободный прибор
            self._processing_application(event, app)
        elif self.min_app_service_time < self.time_arrival_next_app:  # Заявка завершится быстрее, чем придет новая
            pass
        elif self.min_app_service_time > self.time_arrival_next_app:  # пришла заявка, но все приборы заняты
            pass
            self._add_app_to_queue(event, app)
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
        """ Опрашивает все занятые приборы и получает минимальное время до завершения обслуживания заявки"""
        for devise in self.devices_list:
            if not devise.is_free():
                ### Узнать как посчитать время time
                value = devise.get_time_until_end_service_app(time)
                if self.min_app_service_time > value:
                    self.min_app_service_time = value
            else:
                break

    def _processing_application(self, event: Event, app: Application):
        """

        Обрабатывает полученную заявку

        Есть свободный прибор
            - отдаем заявку ему на обработку
            - заявка отдается прибору, с наименьшим номером
        Нет свободных приборов
            - заносим заявку в очередь
            - ставим -1 в Таблице 2
        
        """
        device = self._search_free_device()
        if self.q:  # достаем заявку из очереди
            return self._process_app_from_queue(event, device)
        else:  # пришла заявка
            return self._process_current_app(event, app, device)

    def _process_current_app(self, event: Event,  app: Application, device: Device) -> int:
        """ Отдаем заявку на обслуживание прибору """
        Device
        event.event_time = past_event.event_time + past_event.wait_time
        event.event_type = 1
        self.number_app_now += 1
        event.status_system = self.number_app_now

        event.remain_time = _get_service_time_by_requests(self.type_system)
        event.wait_time = _get_time_between_applications(self.type_system)
        if self.f_selection_to_file:
            event.remain_time = _get_service_time_by_requests(self.type_system)
            event.wait_time = _get_time_between_applications(self.type_system)
            self.selection[str(event.num)] = [event.event_time, event.remain_time, event.wait_time]
        else:
            event.remain_time = self.selection[str(event.num)][1]
            event.wait_time = self.selection[str(event.num)][2]
        app.number = len(self.application_table) + 1
        event.num_application = app.number

        app.app_time = event.event_time
        app.place_in_queue = 0
        app.stay_in_queue = 0
        app.start_service = event.event_time
        app.service_time = event.remain_time
        app.end_time = app.start_service + app.service_time
        self.application_table.append(app)
        return app.number

    def _process_app_from_queue(self, event: Event, device: Device) -> int:
        """Обрабатывает заявку из очереди, возвращает номер обслуженной заявки"""

        event.event_time = past_event.event_time
        event.event_type = 1

        if self.f_selection_to_file:
            event.remain_time = _get_service_time_by_requests(self.type_system)
            event.wait_time = past_event.wait_time
            self.selection[str(event.num)] = [event.event_time, event.remain_time, event.wait_time]

        else:
            event.remain_time = self.selection[str(event.num)][1]
            event.wait_time = self.selection[str(event.num)][2]
        event.num_application = self.q.popleft()
        event.status_system = self.number_app_now
        app = self.application_table[event.num_application - 1]  # !?????

        app.start_service = event.event_time
        app.stay_in_queue = app.start_service - app.app_time
        app.service_time = event.remain_time
        app.end_time = app.start_service + app.service_time
        return app.number

    def _completes_app_processing(self, event: Event, past_event: Event, num_serviced_app: int):
        """Завершает обработку заявки"""
        event.event_time = past_event.event_time + past_event.remain_time
        event.event_type = 2
        self.number_app_now -= 1
        event.status_system = self.number_app_now
        event.remain_time = -1
        event.wait_time = past_event.wait_time - past_event.remain_time
        event.num_application = num_serviced_app

    def _add_app_to_queue(self, event: Event, app: Application):
        """Добавляем заявку в очередь"""

        event.event_time = past_event.event_time + past_event.wait_time
        event.event_type = 1
        event.status_system = self.number_app_now
        if self.f_selection_to_file:
            event.remain_time = _get_service_time_by_requests(self.type_system)
            event.wait_time = _get_time_between_applications(self.type_system)
            self.selection[str(event.num)] = [event.event_time, event.remain_time, event.wait_time]
        else:
            event.wait_time = self.selection[str(event.num)][2]
        event.remain_time = past_event.remain_time - past_event.wait_time

        app.number = len(self.application_table) + 1
        self.q.append(app.number)
        self.number_app_now += 1
        event.status_system = self.number_app_now
        event.num_application = len(self.application_table) + 1
        app.app_time = event.event_time
        app.place_in_queue = len(self.q)
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
