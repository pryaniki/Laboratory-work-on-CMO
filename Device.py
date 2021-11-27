from DeviceData import DeviceData


class Device:
    """

       Класс для представлений прибор из системы массового обслуживания (СМО)

        ...

       Атрибуты
       --------
        _number : int (default 0)
                Номер прибора
        _num_app : int (default 0)
                Номер обслуживаемой заявки
        _free : bool (default True)
                True : Прибор свободен
                False : Прибор занят
        _time_until_end_service_app : float (default 0.)
                Время до окончания обслуживания заявки
        _num_serviced_applications : list (default [])
                Список заявок, которые были обслужены прибором

        _busy_time : float (default 0.)
                Время работы (занятости) прибора
        _idle_time : float (default 0.)
                Время бездействия (простоя) прибора



       Методы
       ------


       """

    def __init__(self, number=0):
        self._number = number
        self._num_app = 0
        self._free = True
        self._time_until_end_service_app = 0.0
        self._num_serviced_applications = []
        self.device_data = DeviceData(self._number)

    def __repr__(self):
        return f'device №{self._number} - {"free" if self._free else "busy"};' \
               f' app serviced through {self._time_until_end_service_app}  обслуживаю заявку №{self._num_app}'

    def is_free(self):
        return self._free

    def give_task(self, number_app, time):
        self._num_app = number_app
        self._time_until_end_service_app = time
        self._free = False

        self.device_data.num_applications_received += 1

    def end_task(self):
        self._num_serviced_applications.append(self._num_app)
        self.device_data.num_applications_served += 1
        tmp = self._num_app
        self._num_app = -1
        self._free = True
        self._time_until_end_service_app = 0
        return tmp

    def get_number(self):
        return self._number

    def get_number_app(self):
        return self._num_app

    def update_time_until_end_service_app(self, time: float) -> float:
        """Обновляет значение _time_until_end_service_app"""
        if self._time_until_end_service_app < time:
            raise Exception(f'У прибора №{self._number} получается отрицательное время до конца заявки'
                            f' \n{self._time_until_end_service_app} - { time}')
        if self._time_until_end_service_app != 0 and self._time_until_end_service_app != time:
            self._time_until_end_service_app = self._time_until_end_service_app - time
            self.device_data.operating_time += time
        else:
            return 0

        return self._time_until_end_service_app

    def get_time_until_end_service_app(self) -> float:
        """Обновляет значение _time_until_end_service_app и возвращает его"""
        return self._time_until_end_service_app
