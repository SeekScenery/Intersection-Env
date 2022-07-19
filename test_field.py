import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

def risk_field():

    """
    生成风险域 与 车辆 图片合成到一起
    风险域 几个 参数 
    左右曲线的长度 front_length  a_right_left
    上曲线的 a_up  一共3个参数
    """

    front_length = 24
    a_right_left = 0.025
    a_up = a_right_left + 0.005

    fig, ax = plt.subplots()
    fig.set_size_inches(4, 4)

    # 定义自车轨迹  分段表示

    # 横纵坐标 等比
    ax_limit = 34
    ax.set_aspect(1)
    ax.set_ylim(-ax_limit, ax_limit)
    ax.set_xlim(-ax_limit, ax_limit)
    # 去掉边框
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # 标轴
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    vehicle_position = [0, 0, 0]

    # 确定感知的左右曲线的纵向边界
    x_lim_min = vehicle_position[0] - 5 # 5 作为参数 进行修改 
    x_lim_max = vehicle_position[0] + front_length # 5 作为参数 进行修改 
    x_array = np.linspace(x_lim_min, x_lim_max, 80)

    # 左右曲线参数
    a = a_right_left  
    b = vehicle_position[0]  # 
    c_left = vehicle_position[1] + 3
    c_right = vehicle_position[1] - 3

    # 左右曲线方程
    y_left = a * (x_array - b)**2 + c_left
    y_right = -a * (x_array - b)**2 + c_right

    # 上曲线
    # 确定上曲线的边界值
    y_lim_min = y_right[-1]
    y_lim_max = y_left[-1]
    y_array = np.linspace(y_lim_min, y_lim_max, 80)
    # 上曲线参数
    b_up = vehicle_position[1]
    y_up = -a_up * (y_array - b_up)**2 

    temp_difference = x_array[-1] - y_up[0] 
    y_up = temp_difference + y_up    # y_up 实际上代表 x 坐标

    # 连接 曲线  (右曲线 - 上曲线 - 左曲线)
    x_all = []
    y_all = []

    # x 连接
    x_all.extend(list(x_array))
    x_all.extend(list(y_up))
    temp = list(x_array)
    temp.reverse()
    x_all.extend(temp)
    # y 连接
    y_all.extend(list(y_right))
    y_all.extend(list(y_array))
    temp = list(y_left)
    temp.reverse()
    y_all.extend(temp)

    # 加载车辆图片
    vehicle_scale = 8
    img_vehicle = Image.open("./vehicle_img/ego.png")
    img_ego = img_vehicle.rotate(-90)
    img_l = vehicle_position[0] - vehicle_scale/2.0
    img_r = vehicle_position[0] + vehicle_scale/2.0
    img_b = vehicle_position[1] - vehicle_scale/2.0
    img_t = vehicle_position[1] + vehicle_scale/2.0
    ax.imshow(img_ego, extent=(img_l, img_r, img_b, img_t),zorder=6)
    # ax.plot(x_array, y_left, 'r')
    # ax.plot(x_array, y_right, 'r')
    # ax.plot(y_up, y_array, 'r')
    # ax.plot(x_all, y_all, 'r')

    ax.fill(x_all, y_all, alpha=0.5)
    fig.savefig("./vehicle_img/risk_field.png", transparent=True, bbox_inches="tight", dpi=600, format='png')

    plt.show()

risk_field()

        # print(turn_left_radius)
        # print(turn_left_center)
        # print(turn_right_radius)

        # # 计算轨迹的交点 圆 和 直线 的交点  圆和圆 的交点
        # circle_params = [min_, min_]
        # circle_params.append(turn_left_radius) 
        # # 左路口
        # result = utils.calculate_circle_point('y', self.road_net_center - self.road_width/2.0, circle_params)
        # cir_left_result = utils.circles_intersection_point(circle_params, [min_, max_, turn_left_radius])
        # print("left cross")
        # print(f"straight:{result}")
        # print(f"turn :{cir_left_result}")
        # # 右路口  
        # result = utils.calculate_circle_point('y', self.road_net_center + self.road_width/2.0, circle_params)
        # cir_left_result = utils.circles_intersection_point(circle_params, [max_, min_, turn_left_radius])
        # print("right cross")
        # print(f"straight:{result}")
        # print(f"turn :{cir_left_result}")
        # # 上路口
        # result = utils.calculate_circle_point('x', self.road_net_center - self.road_width/2.0, circle_params)
        # cir_left_result = utils.circles_intersection_point(circle_params, [min_, max_, turn_right_radius])
        # print("up cross")
        # print(f"straight:{result}")
        # print(f"turn :{cir_left_result}")