class Event:
    """

    Класс для представления события

    Атрибуты
    --------
    ...
    Методы
    ------
    __len__():
        Возвращает количество атрибутов в классе
    get_data_for_report(self):
        Возвращает список из всех атрибутов класса

    """

    def __init__(self, number=0, event_time=0, event_type=0, status_system=0, remain_time=0, wait_time=0,
                 number_application=0):
        """

        :param number: номер события (default 0)
        :param event_time: момент наступления события (default 0)
        :param event_type: тип события (default 0)
        :param status_system: состояния СМО (default 0)
        :param remain_time: оставшееся время обслуживания (default 0)
        :param wait_time: время ожидания новой заявки (default 0)
        :param number_application номер заявки, участвующей в событии (default 0)

        """
        self.num = number
        self.event_time = event_time
        self.event_type = event_type
        self.status_system = status_system
        self.remain_time = remain_time
        self.wait_time = wait_time
        self.num_application = number_application
        self._data_len = 7

    def __len__(self):
        """Возвращает количество атрибутов в классе."""
        return self._data_len

    def get_data_for_report(self):
        """Возвращает список из всех атрибутов класса."""
        return [self.num, self.event_time, self.event_type, self.status_system, self.remain_time,
                self.wait_time, self.num_application]
