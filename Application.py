class Application:
    """

    Класс для представления Заявки, поступившей в СМО

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

    def __init__(self, number=0, application_time=0, place_in_queue=0, staying_in_queue=-1, start_service=-1,
                 service_time=-1, end_time=-1):
        """

        :param number: номер заявки (default 0)
        :param application_time: момент появления заявки (default 0)
        :param place_in_queue: номер места в очереди (default 0)
        :param staying_in_queue: время пребывания заявки в очереди (default -1)
        :param start_service: момент начала обслуживания заявки (default -1)
        :param service_time: время обслуживания (default -1)
        :param end_time: момент окончания обслуживания заявки (default -1)

        """
        self.number = number
        self.app_time = application_time
        self.place_in_queue = place_in_queue
        self.stay_in_queue = staying_in_queue
        self.start_service = start_service
        self.service_time = service_time
        self.end_time = end_time
        self._data_len = 7

    def __len__(self):
        """Возвращает количество атрибутов в классе."""
        return self._data_len

    def get_data_for_report(self):
        """Возвращает список из всех атрибутов класса."""
        return [self.number, self.app_time, self.place_in_queue, self.stay_in_queue, self.start_service,
                self.service_time, self.end_time]

