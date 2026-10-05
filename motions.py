# Imports
import rclpy

from rclpy.node import Node

from utilities import Logger, euler_from_quaternion
from rclpy.qos import QoSProfile

from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

from rclpy.time import Time

# You may add any other imports you may need/want to use below
# import ...

# Define constants for the motion types

# Case 1: Circle
CIRCLE_ANGULAR_VELOCITY = 0.3
CIRCLE_LINEAR_VELOCITY = 0.1

# Case 2: Spiral
SPIRAL_LINEAR_VELOCITY = 0.1
SPIRAL_ANGULAR_VELOCITY = 0.1
SPIRAL_LIN_INCREMENT = 0.01
prev_spiral_linear_velocity = SPIRAL_LINEAR_VELOCITY

# Case 3: Accelerated Line
LINE_LINEAR_VELOCITY = 0.1
LINE_LIN_INCREMENT = 0.01
LINE_ANGULAR_VELOCITY = 0
prev_line_linear_velocity = LINE_LINEAR_VELOCITY

CIRCLE=0; SPIRAL=1; ACC_LINE=2
motion_types=['circle', 'spiral', 'line']

class motion_executioner(Node):
    
    def __init__(self, motion_type=0):
        
        super().__init__("motion_types")
        
        self.type=motion_type
        
        self.radius_=0.0
        
        self.successful_init=False
        self.imu_initialized=False
        self.odom_initialized=False
        self.laser_initialized=False
        
        self.vel_publisher=self.create_publisher(Twist, '/cmd_vel', 10)
                
        # loggers
        self.imu_logger=Logger('imu_content_'+str(motion_types[motion_type])+'.csv', headers=["acc_x", "acc_y", "angular_z", "stamp"])
        self.odom_logger=Logger('odom_content_'+str(motion_types[motion_type])+'.csv', headers=["x","y","th", "stamp"])
        self.laser_logger=Logger('laser_content_'+str(motion_types[motion_type])+'.csv', headers=["ranges", "angle_increment", "stamp"])
        
        qos=QoSProfile(depth=10)

        # IMU subscription
        self.imu_subscriber=self.create_subscription(Imu, '/imu', self.imu_callback, qos)
        
        # ENCODER subscription
        self.encoder_subscriber=self.create_subscription(Odometry, '/odom', self.odom_callback, qos)

        # LaserScan subscription 
        self.imu_subscriber=self.create_subscription(LaserScan, '/scan', self.laser_callback, qos)
        
        self.create_timer(0.1, self.timer_callback)

    def imu_callback(self, imu_msg: Imu):
        self.imu_initialized = True
        acc_x = imu_msg.linear_acceleration.x
        acc_y = imu_msg.linear_acceleration.y
        angular_z = imu_msg.angular_velocity.z
        stamp = Time.from_msg(imu_msg.header.stamp).nanoseconds
        self.imu_logger.log_values([acc_x, acc_y, angular_z, stamp])
        
    def odom_callback(self, odom_msg: Odometry):
        self.odom_initialized = True
        pos = odom_msg.pose.pose.position
        orientation = odom_msg.pose.pose.orientation
        yaw = euler_from_quaternion(orientation)
        stamp = Time.from_msg(odom_msg.header.stamp).nanoseconds
        self.odom_logger.log_values([pos.x, pos.y, yaw, stamp])
                
    def laser_callback(self, laser_msg: LaserScan):
        self.laser_initialized = True
        ranges = laser_msg.ranges
        angle_increment = laser_msg.angle_increment
        stamp = Time.from_msg(laser_msg.header.stamp).nanoseconds
        self.laser_logger.log_values([ranges, angle_increment, stamp])
                
    def timer_callback(self):
        
        if self.odom_initialized and self.laser_initialized and self.imu_initialized:
            self.successful_init=True
            
        if not self.successful_init:
            return
        
        cmd_vel_msg=Twist()
        
        if self.type==CIRCLE:
            cmd_vel_msg=self.make_circular_twist()
        
        elif self.type==SPIRAL:
            cmd_vel_msg=self.make_spiral_twist()
                        
        elif self.type==ACC_LINE:
            cmd_vel_msg=self.make_acc_line_twist()
            
        else:
            print("type not set successfully, 0: CIRCLE 1: SPIRAL and 2: ACCELERATED LINE")
            raise SystemExit 

        self.vel_publisher.publish(cmd_vel_msg)
        
    def make_circular_twist(self):
        msg=Twist()
        msg.linear.x = CIRCLE_LINEAR_VELOCITY
        msg.angular.z = CIRCLE_ANGULAR_VELOCITY
        return msg

    def make_spiral_twist(self):
        msg=Twist()
        msg.linear.x = prev_spiral_linear_velocity + SPIRAL_LIN_INCREMENT
        msg.angular.z = SPIRAL_ANGULAR_VELOCITY
        prev_spiral_linear_velocity = msg.linear.x
        return msg
    
    def make_acc_line_twist(self):
        msg=Twist()
        msg.linear.x = prev_line_linear_velocity + LINE_LIN_INCREMENT
        msg.angular.z = LINE_ANGULAR_VELOCITY
        prev_line_linear_velocity = msg.linear.x
        return msg

import argparse

if __name__=="__main__":
    

    argParser=argparse.ArgumentParser(description="input the motion type")


    argParser.add_argument("--motion", type=str, default="circle")



    rclpy.init()

    args = argParser.parse_args()

    if args.motion.lower() == "circle":

        ME=motion_executioner(motion_type=CIRCLE)
    elif args.motion.lower() == "line":
        ME=motion_executioner(motion_type=ACC_LINE)

    elif args.motion.lower() =="spiral":
        ME=motion_executioner(motion_type=SPIRAL)

    else:
        print(f"we don't have {arg.motion.lower()} motion type")


    
    try:
        rclpy.spin(ME)
    except KeyboardInterrupt:
        print("Exiting")
