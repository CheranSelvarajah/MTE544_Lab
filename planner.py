import numpy as np
import math

# Type of planner
POINT_PLANNER=0
TRAJECTORY_PLANNER=1

STEP = 0.01

PARABOLA = 0
PARABOLA_START = int(0.0/STEP)
PARABOLA_END = int(1.5/STEP)

ELLIPSOID = 1
ELLIPSOID_START = int(0.0/STEP)
ELLIPSOID_END = int(2.5/STEP)


class planner:
    def __init__(self, type_):

        self.type=type_
        self.trajectory = 1

    
    def plan(self, goalPoint=[-1.0, -1.0]):
        
        if self.type==POINT_PLANNER:
            return self.point_planner(goalPoint)
        
        elif self.type==TRAJECTORY_PLANNER:
            return self.trajectory_planner()


    def point_planner(self, goalPoint):
        x = goalPoint[0]
        y = goalPoint[1]
        return x, y

    def trajectory_planner(self):
        trajectory_list = []
        if self.trajectory == PARABOLA:
            for i in range(PARABOLA_START, PARABOLA_END, 1):
                x = i*STEP
                y = pow(x, 2)
                point = [x, y]
                trajectory_list.append(point)
            
            return trajectory_list
            
        elif self.trajectory == ELLIPSOID:
            for i in range(ELLIPSOID_START, ELLIPSOID_END, 1):
                x = i*STEP
                y = 2 / (1 + math.exp(-2*x)) - 1
                point = [x, y]
                trajectory_list.append(point)
            
            return trajectory_list
        else:
            pass
        # the return should be a list of trajectory points: [ [x1,y1], ..., [xn,yn]]
        # return 

