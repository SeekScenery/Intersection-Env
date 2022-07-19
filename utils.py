from configparser import NoSectionError
import math
import numpy as np
from pyparsing import nums


def calculate_circle_point(axis_label:'str', value:"float", circle_param:"list"):
    """
    axis_label: 'y, 'x'
    circle_param:[certer_x, certer_y, r]
    根据 圆上的一个点的 x or y 坐标位置 求 另一个坐标位置
    """
    result_point = []
    if axis_label == 'y':
        temp = np.sqrt((circle_param[2]**2 -(value - circle_param[1])**2))
        x = circle_param[0] + temp
        result_point.append((x, value))
        x = circle_param[0] - temp
        result_point.append((x, value))
    elif axis_label == 'x':
        pass
        temp = np.sqrt((circle_param[2]**2 -(value - circle_param[0])**2))
        y = circle_param[1] + temp
        result_point.append((value, y))
        y = circle_param[1] - temp
        result_point.append((value, y))
    else:
        print("the axis label of your enter is  incomfirmity")
        return None

    return result_point

def circles_intersection_point(circle_param_1:"list", circle_param_2:"list"):
    """
    calculate the intersection point of two  circle 
    """
    x = circle_param_1[0]
    y = circle_param_1[1]
    R = circle_param_1[2]
    a = circle_param_2[0]
    b = circle_param_2[1]
    S = circle_param_2[2] 

    d = math.sqrt((abs(a - x)) ** 2 + (abs(b - y)) ** 2)
    if d > (R + S) or d < (abs(R - S)):
        #print("Two circles have no intersection")
        return None,None
    elif d == 0:
        #print("Two circles have same center!")
        return None,None
    else:
        A = (R ** 2 - S ** 2 + d ** 2) / (2 * d)
        h = math.sqrt(R ** 2 - A ** 2)
        x2 = x + A * (a - x) / d
        y2 = y + A * (b - y) / d
        x3 = round(x2 - h * (b - y) / d, 2)
        y3 = round(y2 + h * (a - x) / d, 2)
        x4 = round(x2 + h * (b - y) / d, 2)
        y4 = round(y2 - h * (a - x) / d, 2)
        c1 = [x3, y3]
        c2 = [x4, y4]
        return c1, c2

# 直角坐标系 -> 极坐标系 圆 cartesian -> polar
def convert_cartesian_polar(params: "list", point: "list"):
    """
    将 圆的直角坐标 转换为 极坐标
    """
    theta = np.arcsin((point[1]-params[1]) * 1.0/ params[2])
    # print(theta)
    # print(theta*180/np.pi)
    return theta


def rotate_point(x, y, center_point, angle):
    """
    旋转 旋转

    """
    new_x = center_point[0] + (x - center_point[0]) * np.cos(angle) - (y - center_point[1]) * np.sin(angle)
    new_y = center_point[1] + (x - center_point[0]) * np.sin(angle) + (y - center_point[1]) * np.cos(angle)
    return [new_x, new_y]

     