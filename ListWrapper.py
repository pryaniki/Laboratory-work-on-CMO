
class ListWrapper:
    """Обертка вокруг списка"""

    def __init__(self, lst: list[float | int]):
        self.lst = lst

    def get_data_for_report(self) -> list[float | int]:
        """Возвращает список"""
        return self.lst

    def __len__(self):
        """Возвращает количество атрибутов в классе."""
        return len(self.lst)

    def __iter__(self):
        return self.lst.__iter__()

