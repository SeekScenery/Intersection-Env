## 自车感知域 环境类

```python
class EnvIntersection:
    def __init__(self):
        """
        一些参数初始化
        车道宽度 
        车道长度等
        """
        pass
    def road_line(self):
        """
        根据车道参数 计算车道边界list(array) 用于画车道线
        """
        pass
    def set_ego_spawn_position(self, position_index):
        """
        根据指定的 index 计算自车真实生成位置
        这里需要先定义 车辆生成轨迹 然后才能 根据index 选定车辆生成位置
        """
        pass
    def ego_vehicle_risk_function(self):
        """
        自车风险场函数
        """
        pass
    def other_vehicle_risk_function(self):
        """
       	其他车辆 风险场函数 与 自车 不一样 这里假定车辆速度和加速度是不变的
        """
        pass
    def load_vehicle_img(self):
        """
        加载 车辆图片 自车 其他车辆  
        可根据车辆具体位置 对其进行旋转操作(heading)
        """
        pass
    def generate_vehicle_trajectory(self):
        """
        根据车辆位置 轨迹类型（左转 右转 直行）轨迹长度 
        车道位置 （上 下 左 右） 进行旋转
        """
        pass
    def ego_conflict_point(self):
        """
       	根据路口 
       	生成对应的 冲突点
        """
    def risk_3D_point(self):
        """
        根据车辆类型 选用风险场
        """

    def test_git_use(self):
        "
        
        "
        pass
        
    
    
    
    
    
```

