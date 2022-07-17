from configparser import NoSectionError
import numpy as np


def calculate_circle_point(axis_label:'str', value:"float", circle_param:"list"):
    """
    axis_label: 'y, 'x'
    circle_param:[certer_x, certer_y, r]
    根据 圆上的一个点的 x or y 坐标位置 求 另一个坐标位置
    """
    if axis_label == 'y':

        pass
    elif axis_label == 'x':
        pass
    else:
        return None
        