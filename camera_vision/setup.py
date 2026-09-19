from setuptools import find_packages, setup
from glob import glob

package_name = 'camera_vision'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
        ('share/' + package_name + '/models/ika_rover',
            glob('models/ika_rover/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='İKA Kursu',
    maintainer_email='kurs@example.com',
    description='İKA Rover Eğitim Serisi Kamera Görme, Stereo ve Haritalama Paketi',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'camera_viewer = camera_vision.camera_viewer:main',
            'stereo_disparity = camera_vision.stereo_disparity:main',
            'depth_cloud_filter = camera_vision.depth_cloud_filter:main',
        ],
    },
)
