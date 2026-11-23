
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import mediapipe as mp

from aisd_msgs.msg import Hand

# MediaPipe hand detection module
mp_hands = mp.solutions.hands


class Hands(Node):

    def __init__(self):
        super().__init__('hands')

        # Subscribe to camera images from ImagePublisher
        self.subscription = self.create_subscription(
            Image,
            'video_frames',
            self.listener_callback,
            10
        )

        # Convert ROS images to OpenCV images
        self.br = CvBridge()

        # Publish hand coordinates to the cmd_hand topic
        self.hand_publisher = self.create_publisher(
            Hand,
            'cmd_hand',
            10
        )

    def listener_callback(self, msg):

        # Convert the received ROS Image to OpenCV format
        image = self.br.imgmsg_to_cv2(msg)

        # MediaPipe landmark indices
        PINKY_FINGER_TIP = 20
        INDEX_FINGER_TIP = 8

        # Create a MediaPipe hand detector
        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as myhands:

            # Improve processing performance
            image.flags.writeable = False

            # MediaPipe requires RGB images
            image = cv2.cvtColor(
                image, cv2.COLOR_BGR2RGB
            )

            # Detect hand landmarks
            results = myhands.process(image)

            # Check whether a hand was detected
            if results.multi_hand_landmarks:

                # Create a custom Hand message
                hand_msg = Hand()

                # Get normalized X coordinates
                hand_msg.xpinky = (
                    results.multi_hand_landmarks[0]
                    .landmark[PINKY_FINGER_TIP].x
                )

                hand_msg.xindex = (
                    results.multi_hand_landmarks[0]
                    .landmark[INDEX_FINGER_TIP].x
                )

                # Publish only when a subscriber exists
                if self.hand_publisher.get_subscription_count() > 0:
                    self.hand_publisher.publish(hand_msg)
                else:
                    self.get_logger().info(
                        'waiting for subscriber'
                    )


def main(args=None):
    rclpy.init(args=args)

    hands = Hands()

    try:
        rclpy.spin(hands)
    except KeyboardInterrupt:
        pass
    finally:
        hands.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
