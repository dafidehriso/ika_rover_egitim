import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_ros import TransformListener, Buffer

class TagFollower(Node):
    def __init__(self):
        super().__init__('tag_follower')

        # tf2 Buffer: ROS'un "hangi çerçeve nerede" bilgisini takip eden sistemi
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        # Saniyede 10 kez kontrol döngüsü çalıştır
        self.timer = self.create_timer(0.1, self.control_loop)

        self.target_distance = 1.0  # tag'in kaç metre önünde duracağız
        self.get_logger().info('Tag Follower başladı, tag36h11:0 aranıyor...')

    def control_loop(self):
        try:
            # camera_link'ten tag'e olan güncel dönüşümü (pose) sorgula
            transform = self.tf_buffer.lookup_transform(
                'camera_link', 'tag36h11:0', rclpy.time.Time())
        except Exception:
            # Tag şu an görünmüyor - dur ve bekle
            self.publisher_.publish(Twist())
            return

        # Kamera optik çerçevesinde: z = ileri mesafe, x = sağ/sol ofset
        forward_distance = transform.transform.translation.z
        lateral_offset = transform.transform.translation.x

        twist = Twist()
        distance_error = forward_distance - self.target_distance

        if abs(distance_error) < 0.05 and abs(lateral_offset) < 0.05:
            self.get_logger().info(
                f'Hedefe ulaşıldı! Mesafe: {forward_distance:.2f}m', throttle_duration_sec=2.0)
        else:
            # Basit oransal (proportional) kontrol
            twist.linear.x = max(-0.2, min(0.2, distance_error * 0.3))
            twist.angular.z = max(-0.3, min(0.3, -lateral_offset * 1.0))
            self.get_logger().info(
                f'Mesafe: {forward_distance:.2f}m, ofset: {lateral_offset:.2f}m',
                throttle_duration_sec=1.0)

        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = TagFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
