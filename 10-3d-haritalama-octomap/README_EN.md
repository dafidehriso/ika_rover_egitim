# Module 10: 3D Volumetric Mapping (OctoMap)

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## Status: COMPLETE (Quality and validation tuning ongoing)

## Prerequisites & Package Installation
```bash
sudo apt install ros-humble-octomap-server ros-humble-octomap-rviz-plugins ros-humble-slam-toolbox -y
```

## Module Files
- [`depth_cloud_filter.py`](./depth_cloud_filter.py): Node ingesting raw depth point clouds, filtering ground plane/ceiling artifacts, and downsampling via voxel grids.
- [`sensor_tf.launch.py`](./sensor_tf.launch.py): Launch file broadcasting chassis and optical TF frame transforms.
- [`ika_mapping.launch.py`](./ika_mapping.launch.py): Unified monolithic launch bringing up Gazebo, SLAM, point cloud filtering, OctoMap, and RViz in a single command.
- [`ika_mapping.rviz`](./ika_mapping.rviz): Preconfigured RViz visualization profile displaying 2D occupancy grids, 3D volumetric voxels, and sensor feeds.

---

## Conceptual Primer: What is OctoMap? (3D Mapping vs 3D SLAM)
- **2D SLAM (`slam_toolbox`):** Builds a 2D planar occupancy grid parallel to the ground plane from LiDAR range scans. It provides $(X, Y)$ obstacle existence, but lacks vertical elevation dimension ($Z$)—blind to overhangs, ceilings, ramps, or tables.
- **OctoMap (3D Volumetric Occupancy):** Discretizes 3D space hierarchically into an octree data structure composed of cubic cells (**voxels**, default $0.10\text{ m}$). It maintains probabilistic state updates ("occupied", "free", "unknown") for each voxel via 3D ray casting.
- **⚠️ Important Distinction:** OctoMap is **NOT a SLAM algorithm**. It does not perform pose estimation or scan matching; it requires an external pose source (wheel odometry or 2D/3D SLAM) to cast incoming 3D point cloud rays into a reference coordinate frame.

---

## THE CRITICAL CONCEPTUAL PITFALL: The "Optical Frame" Trap
When first streaming depth point clouds into OctoMap, the 3D map appeared completely corrupted: point clouds projected vertically straight into the sky above the robot instead of forward along the corridor!

### Root Cause: Conflicting Coordinate Conventions (REP-103 vs Pinhole Optics)
1. **ROS Robotics Convention (REP-103):** $+X$ = Forward, $+Y$ = Left, $+Z$ = Up.
2. **Computer Vision Pinhole Convention:** $+Z$ = Forward (Depth), $+X$ = Right, $+Y$ = Down.

The camera sensor generated 3D points in the standard pinhole optical frame (where $+Z$ represents distance forward). However, those points were stamped with `frame_id: 'camera_link'`. In the TF tree, `camera_link` was evaluated under the ROS body convention (where $+Z$ means straight UP).
Consequently, forward distance $(Z)$ was interpreted as vertical height, projecting entire horizontal hallways into the sky!

### Solution: The `camera_optical_frame` Rotation Bridge
Following standard industry practice (as used by Intel RealSense, stereolabs ZED, etc.), we define two distinct frames:
1. `camera_link`: Physical mounting offset relative to the chassis (`0.3m` forward, `0.2m` up).
2. `camera_optical_frame`: Pure orientation rotation converting ROS body axes into pinhole camera axes ($\text{roll} = -90^\circ, \text{yaw} = -90^\circ$):

```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 -1.5707963267948966 0 -1.5707963267948966 camera_link camera_optical_frame
```

All 3D point cloud messages are stamped with `header.frame_id = 'camera_optical_frame'`.

> **KEY LESSON:** When setting up sensor coordinate systems in robotics, the **physical mounting position** and the **mathematical coordinate convention of the sensor payload** are two separate entities. Never conflate them into a single frame identifier.

---

## Architectural Transition: From Stereo Disparity to Native Depth Cameras
Even after optical frame correction, stereoscopically computed point clouds retain noise on featureless textures (drywall, uniform grass).
- **New Node:** `depth_cloud_filter.py` ingests Gazebo's native simulated depth sensor (`/ika_rover/depth_camera/points`).
- **Filtering Pipeline:** Clamps ground floor reflections (filters out $Z < 0.08\text{ m}$), removes ceilings ($Z > 1.65\text{ m}$), enforces maximum range ($8.0\text{ m}$), and voxelizes at $0.10\text{ m}$ resolution to publish clean obstacle points (`/ika_rover/depth/obstacles`).
- *Note:* Module 8's `stereo_disparity.py` is intentionally retained as an educational reference.

---

## TF Frame Selection: Binding OctoMap to 'odom' vs 'map'
Initially, OctoMap was configured with `frame_id: map`.
- **The Issue:** When `slam_toolbox` closes a loop in the corridor circuit, it applies discrete non-rigid corrections to the `map -> odom` transform. When OctoMap was tracking `map`, these instantaneous pose jumps caused newly cast rays to misalign with historical voxels, baking "ghost walls" into the static octree.
- **Solution & Nuance:** OctoMap is bound to `frame_id: odom`.
  - `odom` is continuous and smooth (no discrete teleportation jumps); new obstacle rays integrate consistently with local history.
  - **⚠️ Technical Caveat:** Tracking `odom` is **not global loop-closure SLAM**. If wheel odometry drifts significantly, the map in `odom` will deform, and past voxels will not retroactively snap. In RViz, selecting `map` as the Fixed Frame transforms the overall `odom` octree under the latest global SLAM estimate.

---

## Odometry Source: Simulation Ground Truth vs Wheel Encoders
Inside the `diff_drive` plugin in `model.sdf`:
```xml
<odometry_source>1</odometry_source>
```
- **`1` (WORLD - Default):** Publishes perfect ground-truth pose from Gazebo's physics engine. Wheel slip does not corrupt odometry—ideal for verifying mapping pipelines.
- **`0` (ENCODER):** Integrates wheel encoder rotations; friction, wheel slip, and skidding induce realistic drift.

---

## Transferring and Building the `camera_vision` Package

```bash
# 1. Navigate to workspace source directory:
cd ~/ika_ws/src

# 2. Safely back up previous Module 4 work OUTSIDE the workspace:
mkdir -p ~/ika_backups
if [ -e camera_vision ] || [ -L camera_vision ]; then
    mv camera_vision ~/ika_backups/camera_vision_backup_$(date +%Y%m%d_%H%M%S)
fi

# 3. Symlink the full package into workspace:
ln -s ~/ika_rover_egitim/camera_vision ~/ika_ws/src/camera_vision

# 4. Build and source:
cd ~/ika_ws
colcon build --symlink-install --packages-select camera_vision
source install/setup.bash
```

---

## System Stability & Unified Launch

1. **DDS Deadlocks on WSL2:** Prevent multicast packet deadlocks on Ubuntu 22.04:
   ```bash
   export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
   ```
2. **Monolithic Mapping Pipeline:**
   ```bash
   ros2 launch camera_vision ika_mapping.launch.py
   ```
   This single command launches:
   - Gazebo simulation (`ika_rover.world` + 5-camera rover).
   - Sensor static TF tree (`sensor_tf.launch.py`).
   - 2D LiDAR SLAM engine (`slam_toolbox`).
   - Ground/ceiling point cloud filter (`depth_cloud_filter`).
   - 3D Voxel server (`octomap_server`).
   - Preconfigured RViz2 session.

---

## Next Up
[Module 11: Balance and Physics Corrections](../11-denge-ve-fizik-duzeltmeleri/README_EN.md)
