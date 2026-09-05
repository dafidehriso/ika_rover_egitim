import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')

        # Gazebo/robot için ana yayın
        self.gazebo_publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        # MAVROS üzerinden ArduPilot SITL'e (Pixhawk simülasyonu) aynı komut
        # (Modül 6'ya kadar bu satırlar olmadan da çalışır, sadece publish edilmez)
        self.mavros_publisher_ = self.create_publisher(
            Twist, '/mavros/setpoint_velocity/cmd_vel_unstamped', 10)

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        self.safe_distance = 0.5  # metre cinsinden güvenli mesafe eşiği
        self.get_logger().info('Obstacle Avoider node başladı')

    def scan_callback(self, msg: LaserScan):
        # Lidar taramasının tam önündeki (0 derece) mesafeyi alıyoruz
        # index 0 tam ön, dizinin başı ve sonu robotun hemen önündeki açıları temsil eder
        front_ranges = msg.ranges[0:15] + msg.ranges[-15:]
        # inf veya nan değerlerini filtrele
        valid_ranges = [r for r in front_ranges if r > 0.01 and r < float('inf')]

        twist = Twist()

        if valid_ranges and min(valid_ranges) < self.safe_distance:
            # Önde engel var: dur ve sağa doğru dön
            twist.linear.x = 0.0
            twist.angular.z = 0.5
            self.get_logger().info(f'Engel algılandı ({min(valid_ranges):.2f} m), dönülüyor')
        else:
            # Yol açık: düz git
            twist.linear.x = 0.15
            twist.angular.z = 0.0

        self.gazebo_publisher_.publish(twist)
        self.mavros_publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
