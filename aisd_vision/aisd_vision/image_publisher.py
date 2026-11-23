
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class ImagePublisher(Node):

    def __init__(self):
        super().__init__('image_publisher')

        # Create a publisher for camera images
        self.publisher_ = self.create_publisher(
            Image, 'video_frames', 10
        )

        # Publish an image every 0.1 seconds
        timer_period = 0.1
        self.timer = self.create_timer(
            timer_period, self.timer_callback
        )

        # Open the default camera
        self.cap = cv2.VideoCapture(0)

        # Convert OpenCV images to ROS Image messages
        self.br = CvBridge()

    def timer_callback(self):
        # Read a frame from the camera
        ret, frame = self.cap.read()

        # Publish the frame if captured successfully
        if ret == True:
            self.publisher_.publish(
                self.br.cv2_to_imgmsg(frame)
            )


def main(args=None):
    rclpy.init(args=args)

    image_publisher = ImagePublisher()

    try:
        rclpy.spin(image_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        image_publisher.cap.release()
        image_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

