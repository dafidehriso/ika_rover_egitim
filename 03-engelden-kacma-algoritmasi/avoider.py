import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')

        # Parametreler
        self.declare_parameter('safe_distance', 0.5)         # Güvenli mesafe eşiği (m)
        self.declare_parameter('front_sector_deg', 15.0)     # Ön sektör yarı açısı (derece, ±15°)
        self.declare_parameter('forward_speed', 0.15)        # Düz gitme hızı (m/s)
        self.declare_parameter('turn_speed', 0.5)            # Dönüş açısal hızı (rad/s, pozitif = SOL)
        self.declare_parameter('scan_timeout_sec', 0.5)      # Watchdog zaman aşımı süresi (sn)

        # Gazebo diff_drive için ana hız yayını
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # MAVROS için hız yayını (Modül 6'da detaylandırılır)
        self.mavros_pub = self.create_publisher(
            Twist, '/mavros/setpoint_velocity/cmd_vel_unstamped', 10)

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        # Lidar veri tazeliği için Watchdog Zamanlayıcısı
        # Lidar verisi kesilirse robotun son komutla süresiz gitmesini engeller
        self.last_scan_time = None
        self.watchdog_timer = self.create_timer(0.1, self.watchdog_callback)

        self.get_logger().info('Obstacle Avoider node başladı (Dinamik Açı ve Watchdog Korumalı)')

    def normalize_angle(self, angle: float) -> float:
        """Açıyı [-pi, pi] aralığına normalize eder."""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def scan_callback(self, msg: LaserScan):
        self.last_scan_time = self.get_clock().now()

        safe_dist = self.get_parameter('safe_distance').value
        sector_rad = math.radians(self.get_parameter('front_sector_deg').value)

        # Işın sayısı ve açı kontrolü
        num_readings = len(msg.ranges)
        if num_readings == 0 or msg.angle_increment == 0.0:
            self.get_logger().warn('Boş veya geçersiz LaserScan verisi alındı! Robot durduruluyor.')
            self.publish_stop()
            return

        # Sadece robotun ön sektöründeki ([-sector_rad, +sector_rad]) ışınları dinamik olarak seç
        # Sabit dizi indeksi KULLANILMAZ; angle_min + i * angle_increment ile açı hesaplanır.
        front_valid_ranges = []
        has_valid_beam = False

        for i, r in enumerate(msg.ranges):
            beam_angle = self.normalize_angle(msg.angle_min + i * msg.angle_increment)

            # Sadece ön sektörde mi?
            if abs(beam_angle) <= sector_rad:
                # 1. NaN veya None kontrolü: Geçersiz veri, dikkate alınmaz
                if math.isnan(r) or r is None:
                    continue

                # 2. +Inf (Dönüşsüz ışın): Işın sensörün maksimum menzilinde hiçbir engele çarpmadı
                # Bu bir engel DEĞİLDİR; yolun açık olduğunu gösterir.
                if math.isinf(r) and r > 0:
                    has_valid_beam = True
                    continue

                # 3. Aralık kontrolü: range_min ile range_max arasındaki gerçek ölçümler
                if msg.range_min <= r <= msg.range_max:
                    has_valid_beam = True
                    front_valid_ranges.append(r)

        # Ön sektörde hiç geçerli ışın okunamadıysa (örneğin tüm ışınlar NaN ise) güvenlik için dur
        if not has_valid_beam:
            self.get_logger().warn('Ön sektörde hiç güvenilir lidar verisi yok! Robot durduruluyor.', throttle_duration_sec=2.0)
            self.publish_stop()
            return

        twist = Twist()

        # Engel kontrolü
        if front_valid_ranges and min(front_valid_ranges) < safe_dist:
            # Önde engel var: dur ve SOLA doğru dön (REP-103: pozitif angular.z = saat yönünün tersi / SOL)
            twist.linear.x = 0.0
            twist.angular.z = self.get_parameter('turn_speed').value
            self.get_logger().info(
                f'Önde engel algılandı ({min(front_valid_ranges):.2f} m < {safe_dist:.2f} m), sola dönülüyor',
                throttle_duration_sec=1.0)
        else:
            # Yol açık: düz git
            twist.linear.x = self.get_parameter('forward_speed').value
            twist.angular.z = 0.0

        self.cmd_vel_pub.publish(twist)
        self.mavros_pub.publish(twist)

    def watchdog_callback(self):
        """Lidar verisi gelmediğinde veya kesildiğinde robotu durduran güvenlik döngüsü."""
        if self.last_scan_time is None:
            return

        elapsed = (self.get_clock().now() - self.last_scan_time).nanoseconds * 1e-9
        timeout = self.get_parameter('scan_timeout_sec').value

        if elapsed > timeout:
            self.get_logger().warn(f'Lidar veri akışı kesildi! ({elapsed:.2f} sn > {timeout} sn). Güvenlik için duruluyor.',
                                   throttle_duration_sec=2.0)
            self.publish_stop()

    def publish_stop(self):
        """Robotu tamamen durduran sıfır hız mesajı yayınlar."""
        stop_twist = Twist()
        self.cmd_vel_pub.publish(stop_twist)
        self.mavros_pub.publish(stop_twist)

    def destroy_node(self):
        """Node kapatılırken robotun son komutla gitmesini önlemek için açıkça sıfır hız gönderir."""
        self.get_logger().info('Node kapatılıyor, sıfır hız gönderiliyor...')
        self.publish_stop()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Normal kapanışta açıkça sıfır hız komutu gönder
        node.publish_stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
