import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import SetBool  

class GoToGoal(Node):
    def __init__(self):
        super().__init__('go_to_goal')

        # Task 1: Declare Parameters
        self.declare_parameter('target_x', 10.0)
        self.declare_parameter('target_y', 10.0)
        self.declare_parameter('linear_gain', 1.5)
        self.declare_parameter('angular_gain', 6.0)
        self.declare_parameter('distance_tolerance', 0.1)
        self.declare_parameter('angle_tolerance', 0.05)
        self.declare_parameter('loop_rate_hz', 20)

        # Retrieve Parameters
        self.goal_x = self.get_parameter('target_x').value
        self.goal_y = self.get_parameter('target_y').value
        self.kp_linear = self.get_parameter('linear_gain').value
        self.kp_angular = self.get_parameter('angular_gain').value
        self.distance_tolerance = self.get_parameter('distance_tolerance').value
        self.angle_tolerance = self.get_parameter('angle_tolerance').value
        self.loop_rate = self.get_parameter('loop_rate_hz').value

        # State Variables
        self.current_pose = None
        self.goal_reached = False
        self.movement_active = False  # Task 2: Service flag

        # ROS 2 Publisher, Subscriber, & Service Server
        self.cmd_vel_publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_subscriber = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )
        
        # Task 2: Service Server implementation
        self.srv = self.create_service(SetBool, 'toggle_movement', self.toggle_callback)

        # Control Loop running at parameterized frequency
        self.timer = self.create_timer(1.0 / self.loop_rate, self.control_loop)

        self.get_logger().info(f'Node ready. Waiting for service call to navigate to: ({self.goal_x}, {self.goal_y})')

    def pose_callback(self, msg: Pose):
        """Update current position and heading from /turtle1/pose stream."""
        self.current_pose = msg
        
    def toggle_callback(self, request, response):
        """Task 2: Fast service callback that just flips a boolean flag."""
        self.movement_active = request.data
        if self.movement_active:
            self.goal_reached = False  # Reset so it can run again if toggled back on
            self.get_logger().info('Movement started via service.')
        else:
            self.get_logger().info('Movement stopped via service.')
            
        response.success = True
        response.message = "Movement activated" if request.data else "Movement deactivated"
        return response

    def normalize_angle(self, angle: float) -> float:
        """Keep heading angle within [-pi, pi] to avoid unnecessary 360-degree turns."""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def control_loop(self):
        """Proportional Control Loop."""
        # Task 2: Check the movement_active flag here
        if not self.movement_active or self.current_pose is None or self.goal_reached:
            return

        # 1. Calculate Cartesian Errors
        dx = self.goal_x - self.current_pose.x
        dy = self.goal_y - self.current_pose.y

        # Euclidean Distance Error: sqrt((x_g - x)^2 + (y_g - y)^2)
        distance_error = math.sqrt(dx**2 + dy**2)

        # Desired Heading Angle: atan2(dy, dx)
        target_angle = math.atan2(dy, dx)
        heading_error = self.normalize_angle(target_angle - self.current_pose.theta)

        msg = Twist()

        # 2. Check if Goal is Reached
        if distance_error < self.distance_tolerance:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.cmd_vel_publisher.publish(msg)
            self.goal_reached = True
            self.movement_active = False # Deactivate movement flag upon reaching goal
            self.get_logger().info('Goal Reached Successfully!')
            return

        # 3. Proportional Control Logic
        # If heading error is large, align facing direction first before moving forward
        if abs(heading_error) > self.angle_tolerance:
            msg.linear.x = 0.0
            msg.angular.z = self.kp_angular * heading_error
        else:
            # Scale forward speed and heading alignment concurrently
            msg.linear.x = min(self.kp_linear * distance_error, 2.0)  # Cap speed at 2.0 m/s
            msg.angular.z = self.kp_angular * heading_error

        self.cmd_vel_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = GoToGoal()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()