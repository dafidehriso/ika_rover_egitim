import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo, PointCloud2, PointField
from std_msgs.msg import Header
import message_filters
from cv_bridge import CvBridge
import cv2
import numpy as np

class StereoDisparityNode(Node):
    def __init__(self):
        super().__init__('stereo_disparity_node')
        self.declare_parameter('use_sim_time', False)
        self.bridge = CvBridge()

        # Kamera intrinsics - camera_info gelene kadar None, ilk mesajda doldurulacak
        self.fx = None
        self.fy = None
        self.cx = None
        self.cy = None
        self.baseline = 0.12  # metre - model.sdf'teki iki kamera arası mesafe
        self.ground_y_limit = 0.12  # 0.20 m kamera yüksekliği: 0.08 m altındaki zemin yansımalarını filtrele
        self.last_stamp = None
        self.right_fx = None
        self.right_width = None

        self.info_sub = self.create_subscription(
            CameraInfo, '/ika_rover/camera_sensor/camera_info', self.info_callback, 10)
        self.right_info_sub = self.create_subscription(
            CameraInfo, '/ika_rover/right_camera_sensor/camera_info',
            self.right_info_callback, 10)

        self.pc_pub = self.create_publisher(PointCloud2, '/ika_rover/stereo/points', 10)
        self.disp_pub = self.create_publisher(Image, '/ika_rover/stereo/disparity', 10)
        self.disp_view_pub = self.create_publisher(
            Image, '/ika_rover/stereo/disparity_visual', 10)

        left_sub = message_filters.Subscriber(self, Image, '/ika_rover/camera_sensor/image_raw')
        right_sub = message_filters.Subscriber(self, Image, '/ika_rover/right_camera_sensor/image_raw')

        # 5 milisaniye (0.005 sn) tolerans: 30 FPS'de (33.3 ms periyot) aynı render anına ait
        # sol ve sağ kareleri eşleştirir, ardışık karelerin yanlış eşleşmesini engeller.
        ts = message_filters.ApproximateTimeSynchronizer(
            [left_sub, right_sub], queue_size=10, slop=0.005)
        ts.registerCallback(self.callback)

        # StereoSGBM parametreleri - dokusuz yüzey gürültüsünü azaltacak şekilde ayarlanmış
        self.stereo = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=16*6,   # 16'nın katı olmalı (96)
            blockSize=11,
            P1=8*3*11**2,
            P2=32*3*11**2,
            disp12MaxDiff=1,
            uniquenessRatio=15,
            speckleWindowSize=150,
            speckleRange=32
        )
        self.right_stereo = cv2.StereoSGBM_create(
            minDisparity=-96, numDisparities=96, blockSize=11,
            P1=8*3*11**2, P2=32*3*11**2, disp12MaxDiff=1,
            uniquenessRatio=15, speckleWindowSize=150, speckleRange=32)

        self.get_logger().info('Stereo disparity node başlatıldı, sol/sağ görüntü bekleniyor...')

    def info_callback(self, msg):
        if self.fx is None:
            self.fx = msg.k[0]
            self.fy = msg.k[4]
            self.cx = msg.k[2]
            self.cy = msg.k[5]
            self.get_logger().info(
                f'Kamera intrinsics alındı: fx={self.fx:.2f} fy={self.fy:.2f} cx={self.cx:.2f} cy={self.cy:.2f}')

    def right_info_callback(self, msg):
        self.right_fx = msg.k[0]
        self.right_width = msg.width

    def callback(self, left_msg, right_msg):
        if self.fx is None or self.right_fx is None:
            return

        stamp = left_msg.header.stamp.sec + left_msg.header.stamp.nanosec * 1e-9
        if self.last_stamp is not None and stamp - self.last_stamp < 0.19:
            return
        self.last_stamp = stamp

        if left_msg.width != right_msg.width or left_msg.height != right_msg.height:
            self.get_logger().error('Stereo görüntü boyutları uyuşmuyor')
            return
        if left_msg.width != self.right_width or abs(self.fx - self.right_fx) > 1.0:
            self.get_logger().error('Stereo kamera kalibrasyonu eşleşmiyor')
            return

        left_img = self.bridge.imgmsg_to_cv2(left_msg, desired_encoding='bgr8')
        right_img = self.bridge.imgmsg_to_cv2(right_msg, desired_encoding='bgr8')

        left_gray = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)

        disparity = self.stereo.compute(left_gray, right_gray).astype(np.float32) / 16.0
        right_disparity = self.right_stereo.compute(
            right_gray, left_gray).astype(np.float32) / 16.0

        # Düz/tek renkli yüzeylerde yanlış eşleşmeyi önleme: yerel varyans kontrolü
        gray = left_gray.astype(np.float32)
        mean = cv2.boxFilter(gray, -1, (11, 11))
        variance = cv2.boxFilter(gray * gray, -1, (11, 11)) - mean * mean
        textured = variance >= 64.0  # yerel standart sapma >= 8 gri ton seviyesi

        disp_msg = self.bridge.cv2_to_imgmsg(disparity, encoding='32FC1')
        disp_msg.header = left_msg.header
        self.disp_pub.publish(disp_msg)

        display = np.clip(disparity * (255.0 / 96.0), 0, 255).astype(np.uint8)
        display[disparity <= 0] = 0
        view_msg = self.bridge.cv2_to_imgmsg(display, encoding='mono8')
        view_msg.header = left_msg.header
        self.disp_view_pub.publish(view_msg)

        self.publish_pointcloud(disparity, right_disparity, textured,
                                left_img, left_msg.header)

    def publish_pointcloud(self, disparity, right_disparity, textured,
                           color_img, header):
        step = 5  # her 5 pikselde bir örnekle (performans ve temiz bulut için)
        sampled = disparity[::step, ::step]
        valid = np.isfinite(sampled) & (sampled > 0.5) & (sampled < 94.5)
        valid &= textured[::step, ::step]
        rows, cols = np.nonzero(valid)
        d = sampled[rows, cols]
        u = cols * step
        v = rows * step
        right_u = np.rint(u - d).astype(np.int32)
        inside = (right_u >= 0) & (right_u < disparity.shape[1])
        consistent = np.zeros(len(d), dtype=bool)
        consistent[inside] = np.abs(
            d[inside] + right_disparity[v[inside], right_u[inside]]) <= 1.5
        d, u, v = d[consistent], u[consistent], v[consistent]

        # Pinhole stereo projeksiyon formülleri (Kamera Optik Çerçevesi kuralı: Z=derinlik, X=sağ, Y=aşağı)
        z = (self.baseline * self.fx / d).astype(np.float32)
        y = ((v - self.cy) * z / self.fy).astype(np.float32)
        keep = (z >= 0.4) & (z <= 8.0)
        keep &= (y <= self.ground_y_limit) & (y >= -1.45)
        u, v, z, y = u[keep], v[keep], z[keep], y[keep]
        x = ((u - self.cx) * z / self.fx).astype(np.float32)

        bgr = color_img[v, u].astype(np.uint32)
        rgb = (bgr[:, 2] << 16) | (bgr[:, 1] << 8) | bgr[:, 0]

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='rgb', offset=12, datatype=PointField.UINT32, count=1),
        ]

        cloud_header = Header()
        cloud_header.stamp = header.stamp
        # Optik eksen standardı: optik rotasyona sahip camera_optical_frame'e bağlanır
        cloud_header.frame_id = 'camera_optical_frame'

        points = np.empty(len(z), dtype=[
            ('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('rgb', '<u4')])
        points['x'], points['y'], points['z'], points['rgb'] = x, y, z, rgb
        cloud_msg = PointCloud2(
            header=cloud_header, height=1, width=len(points), fields=fields,
            is_bigendian=False, point_step=16, row_step=16 * len(points),
            data=points.tobytes(), is_dense=True)
        self.pc_pub.publish(cloud_msg)

def main(args=None):
    rclpy.init(args=args)
    node = StereoDisparityNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()

if __name__ == '__main__':
    main()
