
import rclpy
from rclpy.node import Node
from aisd_msgs.msg import Hand
from geometry_msgs.msg import Twist


class Move(Node):

    def __init__(self):
        super().__init__('move')

        # Subscribe to the hand coordinates
        self.subscription = self.create_subscription(
            Hand,
            'cmd_hand',
            self.listener_callback,
            10
        )

        # Publish velocity commands to the robot
        self.vel_publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            10
        )

    def listener_callback(self, msg):

        # Initialize angular and linear velocities
        angle = 0.0
        linear = 0.0

        # Determine turning direction using index finger
        if msg.xindex > 0.55:
            self.get_logger().info('right')
            angle = -0.1

        elif msg.xindex < 0.45:
            self.get_logger().info('left')
            angle = 0.1

        else:
            angle = 0.0

        # Determine forward movement using finger positions
        if msg.xindex > msg.xpinky:
            self.get_logger().info('come')
            linear = 0.5

        else:
            self.get_logger().info('stay')
            linear = 0.0

        # Create a Twist message for robot movement
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angle

        # Publish velocity if a subscriber is available
        if self.vel_publisher.get_subscription_count() > 0:
            self.vel_publisher.publish(twist)
        else:
            self.get_logger().info('waiting for subscriber')


def main(args=None):
    rclpy.init(args=args)

    move = Move()

    try:
        rclpy.spin(move)
    except KeyboardInterrupt:
        pass
    finally:
        move.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
