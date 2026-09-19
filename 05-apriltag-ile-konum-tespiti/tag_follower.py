import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.duration import Duration
from geometry_msgs.msg import Twist
from tf2_ros import TransformListener, Buffer, TransformException


class TagFollower(Node):
    def __init__(self):
        super().__init__('tag_follower')

        # Parametreler
        self.declare_parameter('target_frame', 'camera_optical_frame')  # 'camera_optical_frame', 'camera_link' veya 'base_link'
        self.declare_parameter('tag_frame', 'tag36h11:0')
        self.declare_parameter('target_distance', 1.0)                  # İstenen hedef durma mesafesi (m)
        self.declare_parameter('max_transform_age_sec', 0.5)            # TF veri tazelik eşiği (sn)
        self.declare_parameter('max_linear_speed', 0.2)
        self.declare_parameter('max_angular_speed', 0.3)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        # 10 Hz kontrol döngüsü
        self.timer = self.create_timer(0.1, self.control_loop)

        target_frame = self.get_parameter('target_frame').value
        tag_frame = self.get_parameter('tag_frame').value
        self.get_logger().info(
            f'Tag Follower başladı. Referans Frame: {target_frame} -> Hedef Tag: {tag_frame}')

    def control_loop(self):
        target_frame = self.get_parameter('target_frame').value
        tag_frame = self.get_parameter('tag_frame').value
        max_age = self.get_parameter('max_transform_age_sec').value

        try:
            # En son mevcut TF dönüşümünü al
            transform = self.tf_buffer.lookup_transform(
                target_frame, tag_frame, Time())
        except TransformException as exc:
            # Tag görünmüyor veya TF zinciri henüz oluşmamış
            self.stop_robot()
            return

        # ⚠️ KRİTİK VERİ TAZELİĞİ (AGE) KONTROLÜ:
        # lookup_transform(..., Time()) son kaydedilen TF'i döndürür.
        # Tag görüş alanından çıksa bile son kayıt buffer'da kalır.
        # Bu yüzden dönüşümün zaman damgası (stamp) ile mevcut ROS zamanını kıyaslamalıyız.
        transform_time = Time.from_msg(transform.header.stamp)
        now = self.get_clock().now()
        age = (now - transform_time).nanoseconds * 1e-9

        # Zaman uyumsuzluğu teşhisi (Simülasyon vs Sistem Saati):
        if abs(age) > 1000.0:
            self.get_logger().error(
                f'ZAMAN SENKRONİZASYONU UYUŞMAZLIĞI! Mevcut ROS saati ile TF mesaj damgası arasında devasa fark ({age:.1f} sn) var. '
                f'Gazebo çalışırken node simülasyon saatini dinlemelidir.\n'
                f'Lütfen node\'u şu parametreyle çalıştırın: ros2 run tag_follower tag_follower --ros-args -p use_sim_time:=true',
                throttle_duration_sec=3.0)
            self.stop_robot()
            return

        if age > max_age:
            self.get_logger().warn(
                f'Tag verisi eski ({age:.2f} sn > {max_age:.2f} sn)! Tag kayboldu kabul edilip duruluyor.',
                throttle_duration_sec=2.0)
            self.stop_robot()
            return

        t = transform.transform.translation

        # ⚠️ FRAME KOORDİNAT SÖZLEŞMESİ:
        if target_frame == 'camera_optical_frame':
            # Kamera Optik Çerçevesi (Pinhole / REP-103 Optical):
            # Z = İleri (derinlik), X = Sağ (+), Y = Aşağı (+)
            forward_distance = t.z
            lateral_offset = t.x  # Pozitifse tag sağda, negatifse solda
            # Tag sağdaysa (lateral > 0), robotu sağa döndürmek gerekir.
            # ROS REP-103'te negatif angular.z = SAĞA dönüş, pozitif = SOLA dönüş.
            angular_error = -lateral_offset
        elif target_frame in ('base_link', 'camera_link'):
            # Robot Gövde / Kamera Montaj Çerçevesi (REP-103 Body):
            # X = İleri (+), Y = Sol (+), Z = Yukarı (+)
            forward_distance = t.x
            lateral_offset = t.y  # Pozitifse tag solda, negatifse sağda
            # Tag soldaysa (lateral > 0), robotu sola döndürmek gerekir (pozitif angular.z).
            angular_error = lateral_offset
        else:
            self.get_logger().error(f'Desteklenmeyen target_frame: {target_frame}')
            self.stop_robot()
            return

        target_dist = self.get_parameter('target_distance').value
        distance_error = forward_distance - target_dist

        twist = Twist()

        # Hedefe varış toleransı: ±5 cm mesafe, ±5 cm yanal hizalama
        if abs(distance_error) < 0.05 and abs(lateral_offset) < 0.05:
            self.get_logger().info(
                f'Hedefe ulaşıldı! İleri mesafe: {forward_distance:.2f}m, Yanal ofset: {lateral_offset:.2f}m',
                throttle_duration_sec=2.0)
            self.stop_robot()
            return
        else:
            max_lin = self.get_parameter('max_linear_speed').value
            max_ang = self.get_parameter('max_angular_speed').value

            # Oransal kontrol (Proportional Control)
            twist.linear.x = max(-max_lin, min(max_lin, distance_error * 0.4))
            twist.angular.z = max(-max_ang, min(max_ang, angular_error * 0.8))

            self.get_logger().info(
                f'Takip ediliyor -> İleri: {forward_distance:.2f}m (hata: {distance_error:+.2f}m), Ofset: {lateral_offset:+.2f}m | Hız cmd: vx={twist.linear.x:+.2f}, wz={twist.angular.z:+.2f}',
                throttle_duration_sec=1.0)

        self.publisher_.publish(twist)

    def stop_robot(self):
        """Robotu sıfır hızla durdurur."""
        self.publisher_.publish(Twist())

    def destroy_node(self):
        self.get_logger().info('Tag follower kapatılıyor, robot durduruluyor...')
        self.stop_robot()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = TagFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
