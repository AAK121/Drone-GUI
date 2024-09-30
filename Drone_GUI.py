#!/usr/bin/env python3

import tkinter as tk
import rospy
from geometry_msgs.msg import TwistStamped
from mavros_msgs.srv import CommandBool, CommandBoolRequest, CommandTOL, CommandTOLRequest
from mavros_msgs.srv import SetMode, SetModeRequest, SetModeResponse
from geometry_msgs.msg import PoseStamped

class Drone_GUI:
    def __init__(self):
        rospy.init_node("drone_control_gui")

        # Initialize service proxies
        rospy.wait_for_service('/mavros/cmd/arming')
        rospy.wait_for_service('/mavros/cmd/takeoff')
        rospy.wait_for_service('/mavros/cmd/land')
        rospy.wait_for_service('/mavros/set_mode')

        self.arm_service = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
        self.takeoff_service = rospy.ServiceProxy('/mavros/cmd/takeoff', CommandTOL)
        self.land_service = rospy.ServiceProxy('/mavros/cmd/land', CommandTOL)
        self.set_mode_service = rospy.ServiceProxy('/mavros/set_mode', SetMode)
        
        # Publisher for TwistStamped
        self.command_velocity_pub = rospy.Publisher("/mavros/setpoint_velocity/cmd_vel", TwistStamped, queue_size=10)
        self.command_altitude_pub = rospy.Publisher("/mavros/local_position/pose",PoseStamped,queue_size=10)


        # Variables
        self.state = 0  # var for showing command given to drone 1--takeoff and 0--land
        self.slider1_force_value = None
        self.slider2_angle_value = None

        # The controller GUI window is referred to as root
        self.root = tk.Tk()
        self.root.geometry("800x1000")
        self.root.title("Drone Controller")

        # Takeoff and land controls - frame1
        self.frame1 = tk.Frame(self.root)
        self.takeoff_button = tk.Button(self.frame1, text="Takeoff/Land", font=('Arial', 18), command=self.change_state, height=3, width=12)
        self.takeoff_button.pack(padx=10, pady=10)
        self.takeoff_or_land_label = tk.Label(self.frame1, text="Drone state", font=('Arial', 15))
        self.takeoff_or_land_label.pack(padx=5, pady=10)
        self.frame1.pack()
                                   
        # Slider controls as a frame - slider_frame
        self.slider_frame = tk.Frame(self.root)
        self.mySlider1 = tk.Scale(self.slider_frame, command=self.slider1, orient="horizontal", from_=0, to=100)
        self.mySlider1.pack(pady=10)
        self.slider_label1 = tk.Label(self.slider_frame, text="Force", font=('Arial', 15))
        self.slider_label1.pack(pady=5)
        self.mySlider2 = tk.Scale(self.slider_frame, command=self.slider2, orient="horizontal", from_=-45, to=45)
        self.mySlider2.pack(pady=10)
        self.slider_label2 = tk.Label(self.slider_frame, text="Angle", font=('Arial', 15))
        self.slider_label2.pack(pady=5)
        self.slider_frame.pack()

        # Binding keypresses in root window to functionality key_pressed
        self.root.bind('<KeyPress>', self.key_pressed)
                           
        # Frame with buttons for nozzle movement - nozzle_frame
        self.nozzle_frame = tk.Frame(self.root)
        self.up_button = tk.Button(self.nozzle_frame, text="UP", font=('Arial', 18), command=self.up_key_pressed)
        self.down_button = tk.Button(self.nozzle_frame, text="DOWN", font=('Arial', 18), command=self.down_key_pressed)
        self.right_button = tk.Button(self.nozzle_frame, text="RIGHT", font=('Arial', 18), command=self.right_key_pressed)
        self.left_button = tk.Button(self.nozzle_frame, text="LEFT", font=('Arial', 18), command=self.left_key_pressed)
        self.up_button.grid(row=0, column=0, columnspan=2)
        self.left_button.grid(row=1, column=0)
        self.right_button.grid(row=1, column=1)
        self.down_button.grid(row=2, column=0, columnspan=2)
        self.nozzle_label = tk.Label(self.nozzle_frame, text="Nozzle controls", font=('Arial', 15))
        self.nozzle_label.grid(row=3, column=0, columnspan=2)
        self.nozzle_frame.pack(pady=10)

        # Drone controls - drone_control_frame
        self.drone_control_frame = tk.Frame(self.root)
        self.drone_up_button = tk.Button(self.drone_control_frame, command=self.w_key_pressed, text="UP (w)", font=('Arial', 18))
        self.drone_down_button = tk.Button(self.drone_control_frame, command=self.s_key_pressed, text="DOWN (s)", font=('Arial', 18))
        self.drone_up_button.grid(row=0, column=0, padx=20)
        self.drone_down_button.grid(row=1, column=0, padx=20)
        self.drone_forward_button = tk.Button(self.drone_control_frame, command=self.ctrl_up_pressed, text="FORWARD", font=('Arial', 18))
        self.drone_backward_button = tk.Button(self.drone_control_frame, command=self.ctrl_down_pressed, text="BACKWARD", font=('Arial', 18))
        self.drone_left_button = tk.Button(self.drone_control_frame, command=self.ctrl_left_pressed, text="LEFT", font=('Arial', 18))
        self.drone_right_button = tk.Button(self.drone_control_frame, command=self.ctrl_right_pressed, text="RIGHT", font=('Arial', 18))
        self.drone_forward_button.grid(row=0, column=2, columnspan=2, padx=20)
        self.drone_backward_button.grid(row=2, column=2, columnspan=2, padx=20)
        self.drone_left_button.grid(row=1, column=2)
        self.drone_right_button.grid(row=1, column=3)
        self.drone_control_label = tk.Label(self.drone_control_frame, text="Drone Controls\n(Use ctrl + arrow keys)", font=('Arial', 15))
        self.drone_control_label.grid(row=3, column=0, columnspan=4)
        self.drone_control_frame.pack(pady=10)

        self.root.mainloop()

    def change_state(self):
        if self.state == 0:
            self.takeoff_or_land_label.config(text="TAKEOFF")
            self.arm_drone(True)
            self.takeoff()
            self.state = 1
        elif self.state == 1:
            self.takeoff_or_land_label.config(text="LAND")
            self.land()
            self.arm_drone(False)
            self.state = 0

    def key_pressed(self, event):
        print(event.state, " ", event.keycode)
        if event.state == 4:  # Ctrl key is pressed
            if event.keycode == 111:
                self.ctrl_up_pressed()
            elif event.keycode == 116:
                self.ctrl_down_pressed()
            elif event.keycode == 114:
                self.ctrl_right_pressed()
            elif event.keycode == 113:
                self.ctrl_left_pressed()
        elif event.state == 0:  # No modifier key
            if event.keycode == 25:
                self.w_key_pressed()
            elif event.keycode == 39:
                self.s_key_pressed()

    def arm_drone(self, arm):
        req = CommandBoolRequest(value=arm)
        try:
            self.arm_service(req)
            rospy.loginfo("Drone armed" if arm else "Drone disarmed")
        except rospy.ServiceException as e:
            rospy.logerr(f"Failed to change arm state: {e}")

    def takeoff(self):
        req = CommandTOLRequest(altitude=3)  # Adjust altitude as needed
        self.set_flight_mode("GUIDED")
     
        try:
            self.takeoff_service(req)
            rospy.loginfo("Takeoff command sent")
        except rospy.ServiceException as e:
            rospy.logerr(f"Failed to send takeoff command: {e}")

    def land(self):
        self.set_flight_mode("LAND")
        req = CommandTOLRequest(altitude=0, min_pitch=0, yaw=0)  # CommandTOL for landing
        try:
            self.land_service(req)
            rospy.loginfo("Land command sent")
        except rospy.ServiceException as e:
            rospy.logerr(f"Failed to send land command: {e}")

    def send_velocity_command(self, linear_x=0, linear_y=0, angular_x=0, angular_y=0):
        vel_msg = TwistStamped()
        self.set_flight_mode("GUIDED")
        vel_msg.twist.linear.x = linear_x
        vel_msg.twist.linear.y = linear_y
        vel_msg.twist.angular.x = angular_x
        vel_msg.twist.angular.y = angular_y
        self.command_velocity_pub.publish(vel_msg)


    def change_altitude(self,sign):
        self.set_flight_mode("GUIDED")
        msg = PoseStamped()
        msg.pose.position.z += 0.5*sign
        self.command_altitude_pub(msg)

    def set_flight_mode(self, mode):
        try:
            req = SetModeRequest()
            req.custom_mode = mode
            response = self.set_mode_service(req)
            if response.mode_sent:
                rospy.loginfo(f"Mode set to {mode}")
            else:
                rospy.logwarn(f"Failed to set mode to {mode}")
        except rospy.ServiceException as e:
            rospy.logerr(f"Service call failed: {e}")

    def slider1(self, val):
        self.slider1_force_value = val
        print("Force slider value: ", val)

    def slider2(self, val):
        self.slider2_angle_value = val
        print("Angle slider value: ", val)

    def up_key_pressed(self):
        self.change_altitude(1)

    def down_key_pressed(self):
        self.change_altitude(-1)

    def left_key_pressed(self):
        self.send_velocity_command(linear_y=1.0)

    def right_key_pressed(self):
        self.send_velocity_command(linear_y=-1.0)

    def w_key_pressed(self):
        self.send_velocity_command(linear_x=1.0)

    def s_key_pressed(self):
        self.send_velocity_command(linear_x=-1.0)

    def ctrl_up_pressed(self):
        self.send_velocity_command(linear_x=0.5)

    def ctrl_down_pressed(self):
        self.send_velocity_command(linear_x=-0.5)

    def ctrl_left_pressed(self):
        self.send_velocity_command(linear_y=0.5)

    def ctrl_right_pressed(self):
        self.send_velocity_command(linear_y=-0.5)


if __name__ == "__main__":
    drone = Drone_GUI()
    rospy.spin()
