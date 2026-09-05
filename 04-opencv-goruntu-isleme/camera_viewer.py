import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class CameraViewer(Node):
    def __init__(self):
        super().__init__('camera_viewer')
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/ika_rover/camera_sensor/image_raw',
            self.image_callback,
            10)
        self.get_logger().info('Camera Viewer (renk tespitli) başladı')

    def image_callback(self, msg: Image):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # 1. BGR -> HSV dönüşümü (renk tespiti için çok daha kolay)
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # 2. Kırmızı renk aralığı (HSV'de kırmızı, 0 civarı VE 180 civarında
        #    olmak üzere iki parçaya bölünür, çünkü Hue dairesel bir değerdir)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        red_mask = mask1 + mask2  # iki maskeyi birleştir

        # 3. Maskedeki en büyük "kontur" (şeklin dış hattı) kırmızı kutumuzdur
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            if area > 300:  # gürültü filtresi
                x, y, w, h = cv2.boundingRect(largest)
                cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cx = x + w // 2
                cv2.putText(cv_image, f'KIRMIZI (alan={int(area)})', (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                image_center = cv_image.shape[1] // 2
                if cx < image_center - 30:
                    self.get_logger().info('Kırmızı kutu SOLDA', throttle_duration_sec=1.0)
                elif cx > image_center + 30:
                    self.get_logger().info('Kırmızı kutu SAĞDA', throttle_duration_sec=1.0)
                else:
                    self.get_logger().info('Kırmızı kutu ORTADA', throttle_duration_sec=1.0)

        cv2.imshow('ika_rover kamerasi', cv_image)
        cv2.imshow('kirmizi maske', red_mask)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = CameraViewer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
