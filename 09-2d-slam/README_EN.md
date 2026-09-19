# Module 9: 2D SLAM (`slam_toolbox`)

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## Learning Objectives
1. Understand Simultaneous Localization and Mapping (SLAM) and graph-based loop closure.
2. Diagnose missing TF frames in pure SDF models and resolve them using `static_transform_publisher`.
3. Configure `slam_toolbox` for custom base frame names (`base_frame: base_link`, `use_sim_time: true`).
4. Navigate an enclosed circuit to generate a 2D occupancy grid and pose graph in RViz.

## Module Files
- [`slam_params.yaml`](./slam_params.yaml): Base frames and operational range configurations for `slam_toolbox`.

---

## Conceptual Primer: The Chicken-or-Egg Dilemma of SLAM
**SLAM = Simultaneous Localization And Mapping**
- To construct an accurate spatial map, the robot must know its exact pose in world coordinates.
- To determine its exact pose, the robot requires a prior map to localize against.

SLAM resolves this cyclical dependency by correlating consecutive laser scans (scan matching) and fusing them with dead-reckoning wheel odometry inside a pose-graph optimization back-end.

### Why Loop Closure Matters
Wheel odometry drifts monotonically over time, and scan matching accumulates small rotational errors. When the robot returns to an area visited earlier (closing the loop), the optimizer detects matching spatial features between historical submaps and the current scan. It adds a loop-closure constraint into the graph, retroactively correcting the entire trajectory and snapping accumulated drift back to zero. This is why our test track in Module 7 was deliberately built as an **ENCLOSED CIRCUIT**.

---

## 🐛 Bug #1: Blank Map — "Message Filter dropping message" Warning
- **Symptom:** Selecting `/map` in RViz displays nothing; console logs stream `Message Filter [target: odom] dropping message: frame 'lidar_link' does not exist`.
- **Root Cause:** The robot was defined purely in Gazebo SDF without a URDF or `robot_state_publisher`. While Gazebo published `/scan` messages with `header.frame_id = 'lidar_link'`, ROS 2 had no transform connecting `lidar_link` to `base_link`.
- **Solution:** Publish the static TF mounting offset matching the SDF position (`0.2, 0, 0.3`):
  ```bash
  ros2 run tf2_ros static_transform_publisher 0.2 0 0.3 0 0 0 base_link lidar_link
  ```

---

## 🐛 Bug #2: TF Resolved but Map Still Blank (`base_frame` Mismatch)
- **Symptom:** TF warnings disappear, but `/map` still does not generate.
- **Root Cause:** By default, `slam_toolbox` searches for `base_frame: base_footprint`. Our robot model does not define `base_footprint`; its root chassis link is `base_link`.
- **Solution:** Create a custom [`slam_params.yaml`](./slam_params.yaml) setting `base_frame: base_link` alongside `use_sim_time: true`:

```yaml
slam_toolbox:
  ros__parameters:
    odom_frame: odom
    map_frame: map
    base_frame: base_link
    scan_topic: /scan
    use_sim_time: true
    min_laser_range: 0.12
    max_laser_range: 10.0
```

---

## Step-by-Step Lab Execution

### 1. Install Dependencies:
```bash
sudo apt install ros-humble-slam-toolbox -y
```

### 2. Terminal 1: Launch the World & Robot
```bash
gazebo --verbose 07-cok-kamera-mimarisi-ve-parkur/parkur.world
```

### 3. Terminal 2: Publish LiDAR Static Transform
```bash
ros2 run tf2_ros static_transform_publisher 0.2 0 0.3 0 0 0 base_link lidar_link
```

### 4. Terminal 3: Launch SLAM Toolbox with Configuration
```bash
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=09-2d-slam/slam_params.yaml use_sim_time:=true
```

### 5. Terminal 4: Visualize in RViz2
```bash
rviz2
```
- **Fixed Frame:** `map`
- **Add -> By topic -> `/map` (Map)**
- **Add -> By topic -> `/scan` (LaserScan)**

### 6. Terminal 5: Drive and Close the Loop
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
Drive through all four corridor legs. As the rover re-enters the starting hallway, observe RViz snapping the pose graph into place, creating a crisp, orthogonal rectangular map.

---

## Next Up
[Module 10: 3D Volumetric Mapping (OctoMap)](../10-3d-haritalama-octomap/README_EN.md)
