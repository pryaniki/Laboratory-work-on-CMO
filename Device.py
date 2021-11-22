class Device:
    """

       Класс для представлений прибор из  системы массового обслуживания (СМО)

        ...

       Атрибуты
       --------
        _number : int (default 0)
                Номер прибора
        _num_app : int (default 0)
                Номер обслуживаемой заявки
        _num_applications_received : int (default 0)
                Число поступивших заявок в прибор
        _busy_time : float (default 0.)
                Время работы (занятости) прибора
        _idle_time : float (default 0.)
                Время бездействия (простоя) прибора
        _free : bool (default True)
                True : Прибор свободен
                False : Прибор занят
        _time_until_end_service_app : float (default 0.)
                Время до окончания обслуживания заявки
        _num_serviced_applications : list (default [])
                Список заявок, которые были обслужены прибором


       Методы
       ------


       """

    _number = 0
    _num_app = 0
    _num_applications_received = 0
    _busy_time = 0.
    _idle_time = 0.
    _free = True
    _time_until_end_service_app = 0.0
    _num_serviced_applications = []

    # Время обращения к прибору или время, через которое обратились к прибору

    def __init__(self, number=0):
        self._number = number

    def __repr__(self):
        return f'device №{self._number} - {"free" if self._free else "busy"};' \
               f' app serviced through {self._time_until_end_service_app} '

    def is_free(self):
        return self._free

    def give_task(self, number_app, time):
        self.

    def _update_time_until_end_service_app(self, time: float):
        """Обновляет значение _time_until_end_service_app"""
        self._time_until_end_service_app = self._time_until_end_service_app - time

    def get_time_until_end_service_app(self):
        """Обновляет значение _time_until_end_service_app и возвращает его"""
        return self._time_until_end_service_app
