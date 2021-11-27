class DeviceData:
    """

    Хранит в себе информацию о приборе:

        ...

        Атрибуты
        --------
        number : int (default 0)
                Номер прибора
        number_applications_received : int (default 0)
                Число поступивших на обслуживание заявок
        num_applications_served : int (default 0)
                Число обслуженных заявок

        operating_time : float (default 0.)
                Время работы прибора
        downtime : float (default 0.)
                Время простоя прибора
        device_downtime_ratio : float (default 0.)
                Коэффициент простоя прибора


    """

    def __init__(self, number=0, num_applications_received=0, operating_time=0., downtime=0.,
                 num_applications_served=0):
        self.number = number
        self.num_applications_received = num_applications_received
        self.operating_time = operating_time
        self.downtime = downtime
        self.num_applications_served = num_applications_served

    def __repr__(self):
        return f'Прибор №{self.number}, поступило заявок: {self.num_applications_received},' \
               f' проработал: {self.operating_time}, время бездействия: {self.downtime}'

    def get_data_for_report(self):
        return [self.number, self.num_applications_received, self.operating_time, self.downtime]

    def get_device_downtime_ratio(self, time):
        return self.downtime/time
