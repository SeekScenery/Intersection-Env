from matplotlib import animation
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from PIL import Image
import os
import matplotlib.animation as animation


NUM_SPAWN_POINT = 30

class EnvIntersection:
    """
    构建 十字路口环境 
    """
    def __init__(self) -> None:
        """
        一些参数 初始化
        车道宽度 
        车道长度等
        车辆的显示大小
        """
        # 道路结构设置
        self.road_width = 3.5  # -----------
        self.road_net_center = 0
        self.boundary_radius = 6.5 #-----------
        self.road_length = 28

        # 车辆图片路径 the path of vehicle image
        self.vehicle_img_path = os.path.join(os.getcwd(), "vehicle_img")
        # 车辆显示的大小
        self.vehicle_scale = 7   # 6 -> 5 调节车辆显示的大小
        self.risk_scale = 40   # 20 -> 15 调节显示的大小

        self.nums_spawn_point = NUM_SPAWN_POINT 
        self.isAnimate = False

        # 加载车辆图片 和 风险图片
        self.load_vehicle_img()
        # 创建画布
        self.create_figure_2Dax()
        self.is_create_3D = False

        # 生成车辆跟踪轨迹
        self.generate_follow_tr()
        # 动画
        self.is_vehicle_and_risk = False 
        self.img_list = []
        # 动画风险场的 参数设定 这和车辆的位置 和 速度 加速度相关
        self.risk_front_lengeth = 20
        self.risk_a_r_l = 0.03

        # 车辆位置 index_list   [road_cross_str, follow_tr, position_index, path_length]
        self.vehicles_spawn_info = []
        self.vehicles_spawn_position_list = []
        self.vehicles_path_info = []


    def load_vehicle_img(self):
        """
        加载 车辆图片 包括自车 和 其他车辆
        heading 沿x轴的正方向是为零 
        """
        self.ego_vehicle_img = Image.open(self.vehicle_img_path + "/ego.png")
        self.other_vehicle_img = Image.open(self.vehicle_img_path + "/other.png")
        self.ego_vehicle_img = self.ego_vehicle_img.rotate(-90)
        self.other_vehicle_img = self.other_vehicle_img.rotate(-90)
        self.vehicle_risk_field = Image.open(self.vehicle_img_path+"/risk_field.png")


    def create_figure_2Dax(self):
        """
        创建一个画板和坐标系 并设定一些参数 
        """
        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(10, 10)
        # 横纵坐标 等比
        ax_limit = 32
        self.ax.set_aspect(1)
        self.ax.set_ylim(-ax_limit, ax_limit)
        self.ax.set_xlim(-ax_limit, ax_limit)
        # 去掉边框 
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        # 去掉坐标轴
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

    def create_figure_3D_ax(self):
        """
        创建一个 3D 的坐标系
        """
        self.fig3D = plt.figure()
        self.fig3D.set_size_inches(10, 10)
        self.ax_3D = Axes3D(self.fig3D)
        # 求掉网格 坐标轴

        # self.ax_3D.set_aspect(1)
        self.ax_3D.set_zlim(-30, 200)
        # self.ax_3D.set_aspect("equal") 

        ax_limit = 32
        # ax.set_aspect(1)
        self.ax_3D.set_ylim(-ax_limit, ax_limit)
        self.ax_3D.set_xlim(-ax_limit, ax_limit)
        
        # # Hide grid lines 
        self.ax_3D.grid(False) 
        # Hide axes ticks 
        self.ax_3D.set_xticks([]) 
        self.ax_3D.set_yticks([]) 
        self.ax_3D.set_zticks([]) 

        self.ax_3D.axis('off')
        
        
    def road_line(self) -> None:
        """
        画车道边线 和 中心线  
        """
        # 设置车道线显示宽度
        line_visible_width = 2
        # 设置车道线颜色
        line_color = 'black'

        # 先画右上角的边线 在通过选择 画其他位置的边线 
        var_min = self.road_net_center + self.road_width + self.boundary_radius 
        var_max = var_min + self.road_length

        # 一个变化的array 和 一个固定的array 
        var_array = np.linspace(var_min, var_max, 30)
        fix_array = [self.road_net_center + self.road_width for i in range(len(var_array))]

        # 画圆弧边线
        theta_range = np.linspace(np.pi, np.pi + np.pi/2, 30)
        # 先画左上角
        x_circle_up_right = var_min + self.boundary_radius * np.cos(theta_range)
        y_circle_up_right = var_min + self.boundary_radius * np.sin(theta_range)

        # 连接直线圆弧直线车道边线
        x_line = fix_array.copy()
        x_line.extend(list(x_circle_up_right))
        x_line.extend(list(var_array))
        temp = list(var_array)
        temp.reverse()
        y_line = temp.copy()
        y_line.extend(list(y_circle_up_right))
        y_line.extend(list(fix_array))

        # 道路中心线
        x_center_line = [self.road_net_center for i in range(len(var_array))]
        y_center_line = list(var_array)
    
        # # 画车道边线 和 中心线 (右上角边界线)
        # self.ax.plot(x_line, y_line, color=line_color, linewidth=line_visible_width)
        # self.ax.plot(x_center_line, y_center_line, color=line_color, linestyle='--', linewidth=line_visible_width)

        # 3D 车道向下移动多少单位
        off_Z = -30
        off_ax3D_boundary_Z = [off_Z for i in range(len(x_line))]
        off_ax3D_mid_Z = [off_Z for i in range(len(x_center_line))]
     
        # 旋转90 画其他的边线 和 中心线
        for i in range(4):
            # 旋转 生成其他的边界 中心 线
            x_line_r, y_line_r = self.rotate_curve(x_line, y_line, [0, 0], i * np.pi/2)
            x_center_line_r, y_center_line_r = self.rotate_curve(x_center_line, y_center_line, [0, 0], i * np.pi/2)
            # 画车道边线
            self.ax.plot(x_line_r, y_line_r, color=line_color, linewidth=line_visible_width)
            # 画道路中心线
            self.ax.plot(x_center_line_r, y_center_line_r, color=line_color, linestyle='--', linewidth=line_visible_width)
            if self.is_create_3D:
                self.ax_3D.plot(x_line_r, y_line_r, off_ax3D_boundary_Z, color=line_color, linewidth=line_visible_width)
                self.ax_3D.plot(x_center_line_r, y_center_line_r, off_ax3D_mid_Z, linestyle='--', color=line_color, linewidth=line_visible_width)


    def rotate_curve(self, X, Y, center_point, angle:"float") -> list:
        """
        旋转 旋转

        """
        new_x = []
        new_y = []

        for x_, y_ in zip(X, Y):
            x = center_point[0] + (x_ - center_point[0]) * np.cos(angle) - (y_ - center_point[1]) * np.sin(angle)
            y = center_point[1] + (x_ - center_point[0]) * np.sin(angle) + (y_ - center_point[1]) * np.cos(angle)
            new_x.append(x)
            new_y.append(y)
        return new_x, new_y


    def generate_follow_tr(self):
        """
        根据自车的跟踪轨迹 设置自车的生成位置
        先 生成车辆位于 下方路口车辆左转 右转 直行的轨迹 然后通过旋转变换生成其他路口车辆的跟踪轨迹
        轨迹: 左转 直行 右转
        80 个车辆生成点
        """
        # 车辆左转 右转半径
        self.vehicle_follow_trs = {}

        turn_left_radius = self.boundary_radius + 1.5 * self.road_width 
        turn_right_radius = self.boundary_radius + 0.5 * self.road_width 
        # 左 右转 弧长增幅 微元
        self.ds_turn_left = (turn_left_radius * (np.pi/2 - 0.2)) / self.nums_spawn_point
        self.ds_turn_right = (turn_right_radius * (np.pi/2 - 0.2)) / self.nums_spawn_point
        # 转向直行微元 
        self.ds_turn_straight = self.road_length*1.0 / self.nums_spawn_point 

        turn_left_theta_range = np.linspace(0.1, np.pi/2-0.1, self.nums_spawn_point)
        turn_right_theta_range = np.linspace(np.pi-0.1, np.pi/2+0.1, self.nums_spawn_point)

        # 车辆左转的中心点 右转中心点
        min_ = self.road_net_center - self.road_width - self.boundary_radius 
        max_ = self.road_net_center + self.road_width + self.boundary_radius 
        turn_left_center = [min_, min_]
        turn_right_center = [max_, min_]
        # 左右转轨迹
        x_turn_left_tr = turn_left_center[0] + turn_left_radius * np.cos(turn_left_theta_range)
        y_turn_left_tr = turn_left_center[1] + turn_left_radius * np.sin(turn_left_theta_range)
        
        # 右转轨迹
        x_turn_right_tr = turn_right_center[0] + turn_right_radius * np.cos(turn_right_theta_range)
        y_turn_right_tr = turn_right_center[1] + turn_right_radius * np.sin(turn_right_theta_range)
        # 先画右转 跟踪直线 
        var_min = self.road_net_center + self.road_width + self.boundary_radius 
        var_max = var_min + self.road_length
        # 一个变化的array 和 一个固定的array 
        high_var_array = np.linspace(var_min, var_max, self.nums_spawn_point)
        low_fix_array = [self.road_net_center - self.road_width/2.0 for i in range(len(high_var_array))]
        # 左转 跟踪直线
        l_var_max = self.road_net_center - self.road_width - self.boundary_radius 
        l_var_min = l_var_max - self.road_length
        # 一个变化的array 和 一个固定的array 
        low_var_array = np.linspace(l_var_min, l_var_max, self.nums_spawn_point)
        high_fix_array = [self.road_net_center + self.road_width/2.0 for i in range(len(low_var_array))]
        
        # 左转结合曲线 直行+左转+直行 (x, y, theta)
        x_left_tr = high_fix_array.copy()
        x_left_tr.extend(list(x_turn_left_tr))
        temp = list(low_var_array)
        temp.reverse()
        x_left_tr.extend(list(temp))

        y_left_tr = list(low_var_array)
        y_left_tr.extend(list(y_turn_left_tr))
        y_left_tr.extend(high_fix_array)

        theta_left_tr = [np.pi/2 for i in range(len(high_fix_array))]
        theta_left_tr.extend(list(turn_left_theta_range+np.pi/2.0))
        theta_left_tr.extend([np.pi for i in range(len(low_var_array))])

        self.vehicle_follow_trs["left"] = [x_left_tr, y_left_tr, theta_left_tr]

        # 右转结合曲线 直行+右转+直行
        x_right_tr = high_fix_array.copy()
        x_right_tr.extend(list(x_turn_right_tr))
        x_right_tr.extend(list(high_var_array))

        y_right_tr = list(low_var_array)
        y_right_tr.extend(list(y_turn_right_tr))
        y_right_tr.extend(low_fix_array)

        theta_right_tr = [np.pi/2 for i in range(len(high_fix_array))]
        theta_right_tr.extend(list(turn_right_theta_range-np.pi/2.0))
        theta_right_tr.extend([0 for i in range(len(low_var_array))])

        self.vehicle_follow_trs["right"] = [x_right_tr, y_right_tr, theta_right_tr]
        # 直行 
        y_straight_tr = np.linspace(l_var_min, var_max, 3 * self.nums_spawn_point)
        x_straight_tr = [self.road_net_center + self.road_width/2.0 for i in range(len(y_straight_tr))]
        theta_straight_tr = [np.pi/2.0 for i in range(len(y_straight_tr))]
        # 直行时的微元
        self.ds_straight = (var_max - l_var_min)/ (3.0 * self.nums_spawn_point)

        self.vehicle_follow_trs["straight"] = [x_straight_tr, y_straight_tr, theta_straight_tr]

        # 显示一下 跟踪路线
        # self.ax.plot(x_left_tr, y_left_tr, color='red', linewidth=2)
        # self.ax.plot(x_right_tr, y_right_tr, color='red', linewidth=2)
        # self.ax.plot(x_straight_tr, y_straight_tr, color='red', linewidth=2)
    
    def get_vehicle_spawn_postion(self, road_cross_str:"str", follow_tr:"str", position_index, path_length=22, is_ego=False) -> "list":
        """
        根据自车的跟踪轨迹 设置自车的生成位置
        先 生成车辆位于 下方路口车辆左转 右转 直行的轨迹 然后通过旋转变换生成其他路口车辆的跟踪轨迹
        轨迹: 左转 直行 右转
        """

        # 根据 车辆所在路口 车辆跟踪路径 index 获取 车辆的spawn 位置 要显示的路径长度 
        # 判断 车辆要生成的路口 (down right up left )
        # 记录车辆生成信息
        self.vehicles_spawn_info.append([road_cross_str, follow_tr, position_index, path_length])
        X = []
        Y = []
        theta = []
        X, Y, theta = self.vehicle_follow_trs[follow_tr]

        # 可封装为函数 
        # 判断 车辆要跟踪的路径 
        if road_cross_str == "right":
            X, Y = self.rotate_curve(X, Y, [self.road_net_center, self.road_net_center], np.pi/2.0)
            theta = [i + np.pi/2.0 for i in theta] 
        elif road_cross_str == "up":
            X, Y = self.rotate_curve(X, Y, [self.road_net_center, self.road_net_center], np.pi)
            theta = [i + np.pi for i in theta] 
        elif road_cross_str == "left":
            X, Y = self.rotate_curve(X, Y, [self.road_net_center, self.road_net_center], np.pi+np.pi/2.0)
            theta = [i + np.pi+np.pi/2.0 for i in theta] 

        # self.ax.plot(X, Y, color='red', linewidth=2)

        # 根据 index 获取车辆位置  theta 为角度(360) 
        position_ = [X[position_index], Y[position_index], 180 * theta[position_index]/np.pi] 
        
        # self.spawn_vehicle(position_)

        self.vehicles_spawn_position_list.append([position_, is_ego]) 
        
        return position_


    def spawn_vehicle(self, position: "list", is_ego=False):
        """
        根据车辆位置(x, y, heading) 渲染 or 画车辆
        position:[x, y, heading]  
        is_ego: TrueTrue
        heading 沿x轴的正方向是为零 (0-360度) 
        """
        if is_ego:
            img = self.ego_vehicle_img
        else:
            img = self.other_vehicle_img    

        img2 = img.rotate(position[2])
        # extent = (L, R, B, T) 图片的left right buttom top 
        # vehicle img 是 正方形 占 5 x 5
        img_l = position[0] - self.vehicle_scale/2.0
        img_r = position[0] + self.vehicle_scale/2.0
        img_b = position[1] - self.vehicle_scale/2.0
        img_t = position[1] + self.vehicle_scale/2.0

        # 所以车辆位置 制作动画
        if self.isAnimate:
            # 不带风险场的 车辆动画 
            if self.is_vehicle_and_risk:
                # 更新 感知域+车辆 
                self.generate_img_vehicle_risk(self.risk_front_lengeth, self.risk_a_r_l)
                # 加载生成好的感知域+车辆
                self.vehicle_risk_field = Image.open(self.vehicle_img_path+"/risk_field.png")
                img_field = self.vehicle_risk_field.rotate(position[2])
                # vehicle + risk 是正方形 占 
                img_l = position[0] - self.risk_scale/2.0
                img_r = position[0] + self.risk_scale/2.0
                img_b = position[1] - self.risk_scale/2.0
                img_t = position[1] + self.risk_scale/2.0

                # 所以车辆位置 制作动画
                img_b = self.ax.imshow(img_field, extent=(img_l, img_r, img_b, img_t), animated=True)
                self.img_list.append([img_b])
            else:
                # 跟新车辆位置
                img_a = self.ax.imshow(img2, extent=(img_l, img_r, img_b, img_t), animated=True)
                self.img_list.append([img_a])
        else:
            self.ax.imshow(img2, extent=(img_l, img_r, img_b, img_t), zorder=6)
            # 渲染感知域 可设置判断 实时跟新感知域 但是无法实现动画效果
            # ------------------------------------
            if self.is_vehicle_and_risk:
                sensor_field_x, sensor_field_y = self.perception_interesting_field(position)
                self.ax.fill(sensor_field_x, sensor_field_y, alpha=0.5)
            # self.img_list.append([img_f])
            # ------------------------------------
            # self.fig.savefig("./output_img/spawn_vehicle.png", transparent=True, bbox_inches="tight", dpi=1200, format='png')

    def generate_animated_follow_tr(self, road_cross_str:"str", follow_tr:"str"):
        """
        生成沿轨迹的动画
        """
        self.isAnimate = True

        for i in range(3*NUM_SPAWN_POINT):
            self.risk_a_r_l += 0.0001
            self.risk_front_lengeth += 0.03
            position = self.get_vehicle_spawn_postion(road_cross_str, follow_tr,i)
            self.spawn_vehicle(position)
            


    def vehicle_risk_intensity(self, vehicle_path_info: "list") -> None:
        """
        车辆沿车辆路径 的固定方向的风险场函数        
        定义 自车的风险强度函数vehicle_postion:"list", vehicle_speed:"float"
        传入 自车的 弧长序列 
        返回 自车的沿固定路径的风险强度 
        """
        #  定义 风险函数 可整理为单独的函数 y = a*e^(-x+b) + c
        # 这几个参数 可右车辆的位置 速度决定
        a = 0.2
        b = 35
        c = 4
        arc = np.array(vehicle_path_info[3])
        # ego_y = a1 * np.exp(-ego_arc + b1) + c1
        # ego_y = np.power(2, -ego_arc)
        risk_intensity = a * (arc - b)**2 + c 
        # print(f"risk_intensity:{risk_intensity}")
        return risk_intensity

    # 生成热力图的辅助函数 传入参数 车辆轨迹 弧长变化 轨迹转角
    def risk_assist_to_xyz(self, vehicle_path_info: "list", is_ego=True):
        """
        生成三维曲面的各种坐标点
        """
        x_tr = vehicle_path_info[0]
        y_tr = vehicle_path_info[1]
        theta = vehicle_path_info[2]
        # arc = vehicle_path_info[3]

        # 选址风险场函数 
        if is_ego:
            risk_intensity = self.vehicle_risk_intensity(vehicle_path_info)
        else:
            risk_intensity = self.vehicle_risk_intensity(vehicle_path_info)
        X = []
        Y = []
        Z = []
        for i in range(len(x_tr)):
            cos_theta = np.cos(theta[i])
            sin_theta = np.sin(theta[i])
            y_ = np.linspace(-1.5, 1.5, 40)
            x_ = np.array([0 for i in range(len(y_))])
            x = x_ * cos_theta - y_ * sin_theta + x_tr[i]
            y = y_ * cos_theta + x_ * sin_theta + y_tr[i]
            z_h = risk_intensity[i] * np.exp(- y_ ** 2 / 2)

            X.append(x)
            Y.append(y)
            Z.append(z_h)
        X = np.array(X)
        Y = np.array(Y)
        Z = np.array(Z)
        alpha_risk = 0.8
        # 画图 测试
        self.ax.contourf(X, Y, Z, cmap=plt.get_cmap('rainbow'), zorder=1, alpha=alpha_risk)
        # self.generate_3D_risk(X, Y, Z)
        return X, Y, Z
    
    def generate_3D_risk(self, X, Y, Z):
        """
        生成3D risk 
        传入参数 坐标点 
        """
        as_ = self.ax_3D.plot_surface(X, Y, Z, rstride=1, cstride=1,
                cmap=plt.get_cmap('rainbow'))

        self.ax_3D.contourf(X, Y, Z, zdir='z', offset = -30, cmap=plt.get_cmap
        ('rainbow'))
        self.ax_3D.view_init(40, -114)    # 40 参数1 饶y轴旋转    参数2 绕z轴旋转
        
        # fig.add_axes([left, bottom, width, height])
        cax = self.fig3D.add_axes([0.01+0.8, 0.22, 0.03, 0.4])

        self.fig3D.colorbar(as_, cax=cax, shrink=0.8, orientation='vertical', ticks=np.array([ 0.1, 0.2]))

        self.fig3D.savefig("ego_vehicles_risk_3d.png",transparent=True, bbox_inches='tight', dpi=1500, format='png')
        
    
    def generate_vehicle_path(self, vehicle_info: "list"):
        """
        根据车辆位置 和 行驶方向  路径长度 生成路径
        先判断车辆 跟踪路径: straight  turn_right turn_left
        turn_right turn_left 判断车辆 车辆是位于: 直线段1  弧线段 直线段2
        vehicle_info = [road_cross_str, follow_tr, position_index]
        """
        # vehicle_info = self.vehicle_spawn_info[0]
        road_cross = vehicle_info[0] # 路口位置
        follow_tr = vehicle_info[1]     # 轨迹信息 左转 右转 直行 
        position_index = vehicle_info[2]
        path_length = vehicle_info[3]
        # 跟踪轨迹 theta -- np.pi/2   左转 np.pi/2 -> np.pi  右转 np.pi/2 -> 0
        X, Y, theta = self.vehicle_follow_trs[follow_tr]
        # 定义list 记录路径
        X_path = []
        Y_path = []
        theta_path = []
        arc_path = []
        total_s = 0
        # 左转 和 右转 计算 轨迹点
        while (position_index < 3*self.nums_spawn_point) and  total_s < path_length:

            theta_ = theta[position_index]
            X_path.append(X[position_index])
            Y_path.append(Y[position_index])
            theta_path.append(theta_)
            arc_path.append(total_s)

            if follow_tr == "straight":
                total_s += self.ds_straight
            else:
                # if theta_ == np.pi or theta_  == np.pi/2 or theta == 0:
                if theta_ > np.pi/2+0.05 and theta_ < np.pi-0.05:
                    total_s += self.ds_turn_left
                elif theta_ > 0 + 0.05 and theta_ < np.pi/2 -0.05:
                    total_s += self.ds_turn_right
                else:
                    total_s += self.ds_turn_straight

            position_index += 1
                    
        # 根据路口位置旋转轨迹点 
        if road_cross == "right":
            X_path, Y_path = self.rotate_curve(X_path, Y_path, [self.road_net_center, self.road_net_center], np.pi/2.0)
            theta_path = [i + np.pi/2.0 for i in theta_path] 
        elif road_cross == "up":
            X_path, Y_path = self.rotate_curve(X_path, Y_path, [self.road_net_center, self.road_net_center], np.pi)
            theta_path = [i + np.pi for i in theta_path] 
        elif road_cross == "left":
            X_path, Y_path = self.rotate_curve(X_path, Y_path, [self.road_net_center, self.road_net_center], np.pi+np.pi/2.0)
            theta_path = [i + np.pi+np.pi/2.0 for i in theta_path] 

        # 记录车辆的路径信息
        self.vehicles_path_info.append([X_path, Y_path, theta_path, arc_path])
        # 测试 一下 路径
        # self.ax.plot(X_path, Y_path, 'r')

    def generate_all_vehicle_risk(self):
        """
        生成所有车辆的risk 并显示
        """
        for vehicle_info in self.vehicles_path_info:
            self.risk_assist_to_xyz(vehicle_info)

    def generate_all_vehicle_path(self):
        """
        生成所有车辆的的路径
        """
        for vehicle_info in self.vehicles_spawn_info:
            self.generate_vehicle_path(vehicle_info)
        
    def spawn_all_vehicle(self):
        """
        渲染 所有添加的车辆
        """
        # [road_cross_str, follow_tr, position_index, path_length]
        for spawn_info in self.vehicles_spawn_position_list:
            self.spawn_vehicle(spawn_info[0], spawn_info[1])

    
    def vehicle_conflict_point(self, ego_position:"list"):
        """
        根据自车的位置 确定自车的与周边车辆的冲突点
        """

        
    def perception_interesting_field(self, vehicle_position:"list", front_length=15, a_r_l=0.03):
        """
        定义车辆的感知域 or 风险域 并生成感知域        
        """
        # 确定感知的左右曲线的纵向边界
        x_lim_min = vehicle_position[0] - 5 # 5 作为参数 进行修改 
        x_lim_max = vehicle_position[0] + front_length # 5 作为参数 进行修改 
        x_array = np.linspace(x_lim_min, x_lim_max, 80)

        # 左右曲线参数
        a = a_r_l
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
        a_up = a_r_l + 0.01
        b_up = vehicle_position[1]
        y_up = -a_up * (y_array - b_up)**2 

        temp_difference = x_array[-1] - y_up[0] 
        y_up = temp_difference + y_up    # y_up 实际上代表 x 坐标

        # 连接 曲线  (右曲线 - 上曲线 - 左曲线)
        X_all = []
        Y_all = []

        # x 连接
        X_all.extend(list(x_array))
        X_all.extend(list(y_up))
        temp = list(x_array)
        temp.reverse()
        X_all.extend(temp)
        # y 连接
        Y_all.extend(list(y_right))
        Y_all.extend(list(y_array))
        temp = list(y_left)
        temp.reverse()
        Y_all.extend(temp)

        rotate_center = [vehicle_position[0], vehicle_position[1]]
        theta = np.pi * vehicle_position[2] / 180.0

        # 根据车辆航向角 旋转感知域
        X, Y = self.rotate_curve(X_all, Y_all, rotate_center, theta)
        return X, Y


    def generate_img_vehicle_risk(self, front_length=20, a_right_left=0.03):
        """
        生成风险域 与 车辆 图片合成到一起
        风险域 几个 参数 
        左右曲线的长度 front_length  a_right_left
        上曲线的 a_up  一共3个参数
        """
        fig, ax = plt.subplots()
        fig.set_size_inches(4, 4)

        # 定义自车轨迹  分段表示

        # 横纵坐标 等比
        ax_limit = 40
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

        x_all, y_all = self.perception_interesting_field(vehicle_position, front_length, a_right_left)
        # 加载车辆图片
        vehicle_scale = 8
        img_vehicle = Image.open("./vehicle_img/ego.png")
        img_ego = img_vehicle.rotate(-90)
        img_l = vehicle_position[0] - vehicle_scale/2.0
        img_r = vehicle_position[0] + vehicle_scale/2.0
        img_b = vehicle_position[1] - vehicle_scale/2.0
        img_t = vehicle_position[1] + vehicle_scale/2.0
        ax.imshow(img_ego, extent=(img_l, img_r, img_b, img_t),zorder=6)
        # 显示车辆跟踪轨迹
        # ax.plot(x_array, y_left, 'r')
        # ax.plot(x_array, y_right, 'r')
        # ax.plot(y_up, y_array, 'r')
        # ax.plot(x_all, y_all, 'r')

        ax.fill(x_all, y_all, alpha=0.5)
        fig.savefig("./vehicle_img/risk_field.png", transparent=True, bbox_inches="tight", dpi=600, format='png')
        # 不让图片显示
        plt.close()
        # plt.show()

    def env_show(self):
        """
        最终调用显示 
        """
        if self.isAnimate:
            # ani = animation.ArtistAnimation(self.fig, self.img_list, interval=100, blit=True,
            #                         repeat_delay=0)

            ani = animation.ArtistAnimation(self.fig, self.img_list, interval=100, blit=True,
                                    repeat_delay=0)
        self.fig.savefig("./output_img/end.png", transparent=True, bbox_inches="tight", dpi=1200, format='png')
        plt.show()





test_env = EnvIntersection()

test_env.road_line()
# test_env.spawn_vehicle([1.75, -20, 90], True)
# test_env.spawn_vehicle([1.75, 20, -90])
# for i in range(3*NUM_SPAWN_POINT):
#     test_env.get_vehicle_spawn_postion("down", "left",i)
test_env.generate_animated_follow_tr("down", "left")
# test_env.risk_field()
# test_env.is_vehicle_and_risk = False
# position = test_env.get_vehicle_spawn_postion("down", "left",24, 28, True)
# # test_env.spawn_vehicle(position)
# position = test_env.get_vehicle_spawn_postion("right", "left", 23, 20)
# position = test_env.get_vehicle_spawn_postion("up", "right", 10, 30)
# position = test_env.get_vehicle_spawn_postion("left", "left", 26, 12)
# # test_env.spawn_vehicle(position)
# test_env.generate_vehicle_path(test_env.vehicle_spawn_info[0])
# test_env.spawn_all_vehicle()
# test_env.generate_all_vehicle_path()
# test_env.risk_assist_to_xyz(test_env.vehicles_path_info[0])
# test_env.generate_all_vehicle_risk()

test_env.env_show()
        