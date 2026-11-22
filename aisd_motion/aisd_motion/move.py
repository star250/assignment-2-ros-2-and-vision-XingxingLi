import rclpy
from rclpy.node import Node
from aisd_msgs.msg import Hand
from geometry_msgs.msg import Twist


class Move(Node):

    def __init__(self):
        super().__init__('move')
        self.subscription = self.create_subscription(
            Hand,
            'cmd_hand',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)


    def listener_callback(self, msg):

        # Turn based on the index finger tip position in the image (0 = left, 1 = right):
        # right of 0.55 -> turn right, left of 0.45 -> turn left, in the middle -> no turn
        angle = 0.0
        linear = 0.0
        if msg.xindex > 0.55:
            self.get_logger().info('right')
            angle = -0.1
        elif msg.xindex < 0.45:
            self.get_logger().info('left')
            angle = 0.1
        else:
            angle = 0.0
        # Compare index tip and pinky tip: if the index is to the right of the pinky,
        # move forward ("come"), otherwise stop ("stay"). Which way the hand faces decides this
        if msg.xindex > msg.xpinky:
            self.get_logger().info('come')
            linear = 0.5
        else:
            self.get_logger().info('stay')
            linear = 0.0
        # Put the two speeds into a Twist message: linear.x = forward speed, angular.z = turning speed
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angle
        # Only publish if someone (the turtle) is subscribed to cmd_vel, otherwise log and wait
        if self.vel_publisher.get_subscription_count() > 0:
            self.vel_publisher.publish(twist)
        else:
            self.get_logger().info('waiting for subcriber')



def main(args=None):
    rclpy.init(args=args)

    move = Move()

    rclpy.spin(move)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    move.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
