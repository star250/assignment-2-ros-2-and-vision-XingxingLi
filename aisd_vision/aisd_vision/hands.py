import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import mediapipe as mp
mp_hands = mp.solutions.hands

from aisd_msgs.msg import Hand


class Hands(Node):

    def __init__(self):
        super().__init__('hands')
        self.subscription = self.create_subscription(
            Image,
            'video_frames',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        # A converter between ROS and OpenCV images
        self.br = CvBridge()
        self.hand_publisher = self.create_publisher(Hand, 'cmd_hand', 10)


    def listener_callback(self, msg):
        # convert the ROS Image message back to an OpenCV image
        image = self.br.imgmsg_to_cv2(msg)
        # MediaPipe numbers 21 points on a hand; 20 = pinky tip, 8 = index finger tip 
        PINKY_FINGER_TIP = 20
        INDEX_FINGER_TIP = 8
        # create a hand detector: complexity 0 = lightest and fastest model,
        # 0.5 = it must be at least 50% confident before it counts as a hand
        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as myhands:
    
          # To improve performance, optionally mark the image as not writeable to
          # pass by reference.
          # make the image read-only so it is passed without copying (faster)
          image.flags.writeable = False
          # OpenCV stores colours as BGR, but MediaPipe needs RGB
          image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
          # run hand detection; results holds the hands found and their 21 points
          results = myhands.process(image)
          if results.multi_hand_landmarks:
              #publish the hand position in terms of index finger and pinky
              msg = Hand()
              # build a Hand message with the left-right (x) position of the 
              # pinky tip and index tip of the first hand (0 = left, 1 = right)
              msg.xpinky = results.multi_hand_landmarks[0].landmark[PINKY_FINGER_TIP].x
              msg.xindex = results.multi_hand_landmarks[0].landmark[INDEX_FINGER_TIP].x
              # only publish if someone subscribes to cmd_hand, otherwise log a message
              if self.hand_publisher.get_subscription_count() > 0:
                  self.hand_publisher.publish(msg)
              else:
                  self.get_logger().info('waiting for subcriber')


def main(args=None):
    rclpy.init(args=args)

    hands = Hands()

    rclpy.spin(hands)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    hands.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

