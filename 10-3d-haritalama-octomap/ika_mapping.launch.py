"""Start the complete Gazebo, SLAM, stereo diagnostics and 3D map pipeline."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess,
                            IncludeLaunchDescription, SetEnvironmentVariable)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('camera_vision')
    slam_share = get_package_share_directory('slam_toolbox')
    world = PathJoinSubstitution([share, 'config', LaunchConfiguration('world')])
    slam_params = os.path.join(share, 'config', 'slam_params.yaml')
    rviz_config = os.path.join(share, 'rviz', 'ika_mapping.rviz')
    gui = LaunchConfiguration('gui')
    rviz = LaunchConfiguration('rviz')

    return LaunchDescription([
        SetEnvironmentVariable('FASTDDS_BUILTIN_TRANSPORTS', 'UDPv4'),
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', [
            os.path.join(share, 'models'), ':',
            EnvironmentVariable('GAZEBO_MODEL_PATH', default_value='')]),
        DeclareLaunchArgument('world', default_value='ika_rover.world',
                              description='World file from camera_vision/config'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true'),
        ExecuteProcess(cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', world], output='screen',
                       condition=IfCondition(gui)),
        ExecuteProcess(cmd=['gzserver', world, '--verbose', '-s', 'libgazebo_ros_init.so'], output='screen',
                       condition=UnlessCondition(gui)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
            os.path.join(share, 'launch', 'sensor_tf.launch.py'))),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
            os.path.join(slam_share, 'launch', 'online_async_launch.py')),
            launch_arguments={'slam_params_file': slam_params,
                              'use_sim_time': 'true'}.items()),
        Node(package='camera_vision', executable='stereo_disparity',
             name='stereo_disparity_node', output='screen',
             parameters=[{'use_sim_time': True}]),
        Node(package='camera_vision', executable='depth_cloud_filter',
             name='depth_cloud_filter', output='screen',
             parameters=[{'use_sim_time': True,
                          'min_height': 0.08, 'max_height': 1.65,
                          'max_range': 8.0, 'voxel_size': 0.10}]),
        Node(package='octomap_server', executable='octomap_server_node',
             name='octomap_server', output='screen',
             parameters=[{'use_sim_time': True, 'resolution': 0.10,
                          'frame_id': 'odom', 'base_frame_id': 'base_link',
                          'pointcloud_max_range': 8.0}],
             remappings=[('cloud_in', '/ika_rover/depth/obstacles')]),
        Node(package='rviz2', executable='rviz2', output='screen',
             arguments=['-d', rviz_config], parameters=[{'use_sim_time': True}],
             condition=IfCondition(rviz)),
    ])
