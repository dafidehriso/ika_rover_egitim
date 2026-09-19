from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Gazebo diff_drive publishes odom -> base_link at the model origin (ground).
    # Use model-relative sensor heights from the SDF for these TF transforms.
    transforms = [
        ('base_link', 'imu_link', 0.0, 0.0, 0.25, 0.0),
        ('base_link', 'lidar_link', 0.2, 0.0, 0.30, 0.0),
        ('base_link', 'camera_link', 0.3, 0.0, 0.20, 0.0),
        ('base_link', 'right_camera_link', 0.3, -0.12, 0.20, 0.0),
        ('base_link', 'side_right_camera_link', 0.0, -0.25, 0.20, -1.5708),
        ('base_link', 'side_left_camera_link', 0.0, 0.25, 0.20, 1.5708),
        ('base_link', 'rear_camera_link', -0.3, 0.0, 0.20, 3.14159),
    ]
    optical_frames = [
        ('camera_link', 'camera_optical_frame'),
        ('right_camera_link', 'right_camera_optical_frame'),
        ('side_right_camera_link', 'side_right_camera_optical_frame'),
        ('side_left_camera_link', 'side_left_camera_optical_frame'),
        ('rear_camera_link', 'rear_camera_optical_frame'),
    ]
    nodes = []
    for parent, child, x, y, z, yaw in transforms:
        nodes.append(Node(
            package='tf2_ros', executable='static_transform_publisher',
            arguments=['--x', str(x), '--y', str(y), '--z', str(z),
                       '--yaw', str(yaw), '--frame-id', parent,
                       '--child-frame-id', child],
        ))
    for parent, child in optical_frames:
        nodes.append(Node(
            package='tf2_ros', executable='static_transform_publisher',
            arguments=['--roll', str(-1.5707963267948966),
                       '--yaw', str(-1.5707963267948966),
                       '--frame-id', parent, '--child-frame-id', child],
        ))
    return LaunchDescription(nodes)
