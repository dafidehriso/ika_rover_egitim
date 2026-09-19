"""Keep measured obstacle surfaces while preserving the depth sensor frame for ray clearing."""

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2, PointField
from tf2_ros import Buffer, TransformException, TransformListener


class DepthCloudFilter(Node):
    def __init__(self):
        super().__init__('depth_cloud_filter')
        self.declare_parameter('min_height', 0.08)
        self.declare_parameter('max_height', 1.65)
        self.declare_parameter('max_range', 8.0)
        self.declare_parameter('voxel_size', 0.10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.pub = self.create_publisher(PointCloud2, '/ika_rover/depth/obstacles', 10)
        self.sub = self.create_subscription(
            PointCloud2, '/ika_rover/depth_camera/points', self.callback,
            qos_profile_sensor_data)
        self.frames = 0

    def callback(self, msg):
        if not msg.width or msg.row_step != msg.width * msg.point_step:
            return
        offsets = {}
        for field in msg.fields:
            if field.name in ('x', 'y', 'z') and field.datatype == PointField.FLOAT32:
                offsets[field.name] = field.offset
        if len(offsets) != 3:
            self.get_logger().error('Depth cloud needs float32 x/y/z fields')
            return
        try:
            # Only the height gate uses this transform. The output retains the
            # original stamp and frame, so OctoMap raycasts at the exact stamp.
            # Latest TF avoids dropping depth frames that arrive a few ms
            # before Gazebo's matching odom transform.
            transform = self.tf_buffer.lookup_transform(
                'odom', msg.header.frame_id, Time())
        except TransformException as exc:
            if self.frames % 50 == 0:
                self.get_logger().warn(f'Depth TF unavailable: {exc}')
            self.frames += 1
            return

        # The depth image has 76,800 samples. A regular 2x2 sample is dense
        # enough for 0.10 m OctoMap cells and keeps ray insertion responsive.
        rows = np.frombuffer(msg.data, dtype=np.uint8).reshape(
            msg.height, msg.width, msg.point_step)[::2, ::2].copy().reshape(
                -1, msg.point_step)
        xyz = []
        endian = '>f4' if msg.is_bigendian else '<f4'
        for axis in ('x', 'y', 'z'):
            data = rows[:, offsets[axis]:offsets[axis] + 4].copy()
            xyz.append(data.view(endian).reshape(-1).astype(np.float32))
        xyz = np.column_stack(xyz)
        q = transform.transform.rotation
        x, y, z, w = q.x, q.y, q.z, q.w
        rotation = np.array([
            [1 - 2*(y*y + z*z), 2*(x*y - z*w), 2*(x*z + y*w)],
            [2*(x*y + z*w), 1 - 2*(x*x + z*z), 2*(y*z - x*w)],
            [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x*x + y*y)],
        ], dtype=np.float32)
        translation = transform.transform.translation
        finite = np.isfinite(xyz).all(axis=1)
        xyz[~finite] = 0.0
        world = xyz @ rotation.T + np.array(
            [translation.x, translation.y, translation.z], dtype=np.float32)
        height = world[:, 2]
        distance = np.linalg.norm(xyz, axis=1)
        keep = finite
        keep &= (height >= self.get_parameter('min_height').value)
        keep &= (height <= self.get_parameter('max_height').value)
        keep &= (distance >= 0.25)
        keep &= (distance <= self.get_parameter('max_range').value)
        indices = np.flatnonzero(keep)
        if len(indices):
            size = self.get_parameter('voxel_size').value
            cells = np.floor(world[indices] / size).astype(np.int32)
            _, unique = np.unique(cells, axis=0, return_index=True)
            indices = indices[np.sort(unique)]
        selected = rows[indices].copy()
        output = PointCloud2(
            header=msg.header, height=1, width=len(indices), fields=msg.fields,
            is_bigendian=msg.is_bigendian, point_step=msg.point_step,
            row_step=len(indices) * msg.point_step, data=selected.tobytes(),
            is_dense=True)
        self.pub.publish(output)
        self.frames += 1
        if self.frames % 100 == 0:
            self.get_logger().info(
                f'Depth points: {len(xyz)} raw, {len(indices)} obstacles')


def main(args=None):
    rclpy.init(args=args)
    node = DepthCloudFilter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
