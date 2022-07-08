
NUM_FOR_ROUND = 5
NUM_EVENTS = 100

NUM_SMO = None  # количество доступных приборов
SERVICE_TIME = None  # время между приходом заявок
DELTA_T = None  # время между приходом заявок
LAMBD = None
MU = None  # параметр показательного распределения


def set_constants(num_smo, service_time, delta_t, lambd, mu):
    """Устанавливает значения констант."""
    global NUM_SMO, SERVICE_TIME, DELTA_T, LAMBD, MU
    NUM_SMO = num_smo
    SERVICE_TIME = service_time
    DELTA_T = delta_t
    LAMBD = lambd
    MU = mu
