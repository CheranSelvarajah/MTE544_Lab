# Imports
import rclpy

from rclpy.node import Node

from utilities import Logger, euler_from_quaternion
from rclpy.qos import QoSProfile, ReliabilityPolicy

from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from rclpy.time import Time

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
        
        qos=QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,depth=10)

        # IMU subscription
        self.imu_subscriber=self.create_subscription(Imu, '/imu', self.imu_callback, qos)
        
        # ENCODER subscription
        self.encoder_subscriber=self.create_subscription(Odometry, '/odom', self.odom_callback, qos)

        # LaserScan subscription 
        self.imu_subscriber=self.create_subscription(LaserScan, '/scan', self.laser_callback, qos)

        # *** Defining Motion Constants ***

        # Case 1: Circle
        self.CIRCLE_ANGULAR_VELOCITY = 0.3
        self.CIRCLE_LINEAR_VELOCITY = 0.1

        # Case 2: Spiral
        self.SPIRAL_COUNT = 0
        self.INIT_SPIRAL_LIN_VELOCITY = 0.2
        self.SPIRAL_ANGULAR_VELOCITY = 0.7
        self.SPIRAL_LIN_INCREMENT = 0.001
        self.TARGET_SPIRAL_COUNT = 100

        # Case 3: Line
        self.LINE_COUNT = 0
        self.INIT_LINE_LIN_VELOCITY = 0.1
        self.LINE_LIN_INCREMENT = 0.01
        self.LINE_ANGULAR_VELOCITY = 0.0
        self.TARGET_LINE_COUNT = 100

        self.create_timer(0.1, self.timer_callback)

    def imu_callback(self, imu_msg: Imu):
        """
        Gets the data from the `/imu` topic and sends it to the logger
        """
        self.imu_initialized = True
        acc_x = imu_msg.linear_acceleration.x
        acc_y = imu_msg.linear_acceleration.y
        angular_z = imu_msg.angular_velocity.z
        stamp = Time.from_msg(imu_msg.header.stamp).nanoseconds
        self.imu_logger.log_values([acc_x, acc_y, angular_z, stamp])
        
    def odom_callback(self, odom_msg: Odometry):
        """
        Gets the data from the `/odom` topic and sends it to the logger
        """
        self.odom_initialized = True
        pos = odom_msg.pose.pose.position
        orientation = odom_msg.pose.pose.orientation
        yaw = euler_from_quaternion(orientation)
        stamp = Time.from_msg(odom_msg.header.stamp).nanoseconds
        self.odom_logger.log_values([pos.x, pos.y, yaw, stamp])
                
    def laser_callback(self, laser_msg: LaserScan):
        """
        Gets the data from the `/odom` topic and sends it to the logger
        """
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
        
        # print(self.type)
        if self.type==CIRCLE:
            print("Circle")
            cmd_vel_msg=self.make_circular_twist()
        
        elif self.type==SPIRAL:
            self.SPIRAL_COUNT += 1
            print("Spiral")
            cmd_vel_msg=self.make_spiral_twist(self.SPIRAL_COUNT)
                        
        elif self.type==ACC_LINE:
            self.LINE_COUNT += 1
            print("Line")
            cmd_vel_msg=self.make_acc_line_twist(self.LINE_COUNT)
            
        else:
            print("type not set successfully, 0: CIRCLE 1: SPIRAL and 2: ACCELERATED LINE")
            raise SystemExit 

        self.vel_publisher.publish(cmd_vel_msg)
        
    def make_circular_twist(self):
        """
        In the case of the circle, the robot has a constant non zero linear and angular velocity.
        The robot should be moving forward (setting linear.x) and also rotating around the z axes (setting angular.z)
        """
        msg=Twist()
        msg.linear.x = self.CIRCLE_LINEAR_VELOCITY
        msg.angular.z = self.CIRCLE_ANGULAR_VELOCITY
        return msg

    def make_spiral_twist(self, count):
        """
        In the case of the spiral, the robot can have a constant angular velocity and increase the linear velocity
        by `SPIRAL_LIN_INCREMENT`. This will decrease the radius of the circle in which the robot is travelling
        """
        msg=Twist()
        # if count >= self.TARGET_SPIRAL_COUNT:
        #     return msg
        msg.linear.x = self.INIT_SPIRAL_LIN_VELOCITY + (count*self.SPIRAL_LIN_INCREMENT)
        msg.angular.z = self.SPIRAL_ANGULAR_VELOCITY
        return msg
    
    def make_acc_line_twist(self, count):
        """
        To make the robot go in an accelerating line, there should be 0 angular velocity, 
        and the linear velocity should be increasing, in this case we just do it at a constant rate 
        """
        msg=Twist()
        if count >= self.TARGET_LINE_COUNT:
            msg.linear.x = 0
            msg.angular.z = 0
            return msg
        msg.linear.x = self.INIT_LINE_LIN_VELOCITY + (count*self.LINE_LIN_INCREMENT)
        msg.angular.z = self.LINE_ANGULAR_VELOCITY
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
        print(f"we don't have {args.motion.lower()} motion type")
    
    try:
        rclpy.spin(ME)
    except KeyboardInterrupt:
        print("Exiting")
