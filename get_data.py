import json
import os


class Condition:
    """Возвращает данные для отчета"""
    def __init__(self, num_var: int, f_name: str):
        self.variant = str(num_var)
        self.get(f_name)

    def get(self, f_name: str):
        if os.path.exists(f_name):
            with open(f_name, 'r') as file:
                data = json.load(file)

        self.name = data[str(self.variant)][0]
        self.data = data[str(self.variant)][1]

    def __str__(self):
        return f'({self.variant}, {self.name}, {self.data})'


def get_conditions(num_var: int, f_name: str):
    return Condition(num_var, f_name)