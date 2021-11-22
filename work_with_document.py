"""
В модуле находятся функции для заполнения word документа

"""
import numpy as np

from ListWrapper import ListWrapper
from docx.shared import Pt, Inches
from docx.enum.table import WD_TABLE_ALIGNMENT

from constants import NUM_FOR_ROUND


def num_to_str(num: float | int, num_for_round=NUM_FOR_ROUND) -> str:
    """

    Преобразует число в строку округляя до NUM_FOR_ROUND знаков

    Если число -0.1**num_for_round < num < 0.1**num_for_round то возвращает '0'

    """

    if isinstance(num, str):
        return num
    else:
        eps = 0.1 ** num_for_round
        if -eps < num < eps:
            return '0'
        else:
            return str(np.round(num, num_for_round))


def _set_col_widths(table, widths):

    for row in table.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = width


def set_size_fount(paragraph, size: int):
    """Задает размер шрифта для параграфа"""
    for run in paragraph.runs:
        font = run.font
        font.size = Pt(size)


def fill_table_for_report(document, data, widths):
    """Создает таблицу в документе и заполняет ее."""
    table = document.add_table(rows=len(data) + 1, cols=len(data[0]), style='Table Grid')
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_col_widths(table, widths)
    for i, line in enumerate(data):
        for j, num in enumerate(line.get_data_for_report()):
            table.rows[i + 1].cells[j].text = num_to_str(num)

    return table


def reverse_table(data: list):
    """ Переворачивает таблицу и добавляет по 1 строке в начало каждой строки таблицы"""
    value_names = {
        0: 'число заявок J(100), поступивших в СМО на интервале [0,t_соб (100)]',
        1: 'число JF(100),  полностью обслуженных заявок на интервале  [0,t_соб (100)]',
        2: 'среднее число заявок, находившихся в СМО, на интервале[0,t_соб (100)]',
        3: 'среднее время пребывания заявок в очереди на интервале [0,t_соб (100)]',
        4: 'среднее время пребывания заявок в СМО на интервале [0,t_соб (100)]',
        5: 'коэффициент простоя прибора на интервале [0,t_соб (100)] к  t_соб (100)',
    }
    res = []

    for i, row in enumerate(zip(*data)):
        lst = list(row)
        lst.insert(0, value_names[i])
        res.append(ListWrapper(lst))
    return res


def fill_table_analysis_of_calculations(document, data: list[list[ListWrapper]]):
    """Заполнить анализ расчетов"""
    document.add_heading(' Анализ результатов', 1)

    data[0] = reverse_table(data[0])
    widths = (Inches(2), Inches(1), Inches(1), Inches(1))
    table = fill_table_for_report(document, data[0], widths)
    table.rows[0].cells[1].text = '(D|M|n)'
    table.rows[0].cells[2].text = '(M|D|n)'
    table.rows[0].cells[3].text = '(M|M|n)'
    document.add_paragraph(f'\nОтносительные частоты пребывания СМО в состояниях\n')

    max_len = len(data[1][0])
    for lst in data[1][1:]:
        if len(lst) > max_len:
            max_len = len(lst)

    ### заполнить 2-ю таблицу
    table = document.add_table(rows=max_len + 2, cols=len(data[1])+1, style='Table Grid')
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = (Inches(0.4), Inches(0.4), Inches(0.4), Inches(0.4))

    _set_col_widths(table, widths)
    table.rows[0].cells[1].text = '(D|M|n)'
    table.rows[0].cells[2].text = '(M|D|n)'
    table.rows[0].cells[3].text = '(M|M|n)'
    table.rows[1].cells[1].text = 'Vi(100)'
    table.rows[1].cells[2].text = 'Vi(100)'
    table.rows[1].cells[3].text = 'Vi(100)'

    for i, line in enumerate(data[1]):
        for j, num in enumerate(line):
            table.rows[j + 2].cells[0].text = num_to_str(j)
            table.rows[j + 2].cells[i+1].text = num_to_str(num)

    return table
