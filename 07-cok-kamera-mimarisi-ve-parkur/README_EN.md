# Module 7: Multi-Camera Architecture & Realistic Test Track

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## Learning Objectives
1. Expand the single-camera robot model into a 5-camera situational awareness array (front stereo pair + lateral/rear monocular cameras).
2. Construct an enclosed 4-leg corridor circuit in Gazebo suitable for SLAM loop-closure validation.
3. Learn how to verify Gazebo material and texture dependencies before using them in world models.
4. Drive the robot manually using `teleop_twist_keyboard`.

## Module Files
- [`model.sdf`](./model.sdf): 5-camera UGV Rover SDF model.
- [`model.config`](./model.config): Model metadata manifest.
- [`parkur.world`](./parkur.world): Enclosed 4-corridor test circuit.

---

## The Anatomy of a Simulated Camera Sensor
In Gazebo, a camera sensor consists of 4 elements:
1. `<joint>` — Fixed kinematic attachment to `base_link` (`type="fixed"`).
2. `<link>` — Physical spatial mounting pose (`pose: x y z roll pitch yaw`).
3. `<sensor type="camera">` — Optical parameters: horizontal field of view (HFOV), pixel resolution, update rate.
4. `<plugin libgazebo_ros_camera.so>` — C++ bridge publishing image frames and `CameraInfo` onto ROS 2 topics.

**ROS Heading Conventions (REP-103):**
- $+X$ = Forward, $+Y$ = Left, $+Z$ = Up
- $yaw = -1.5708\text{ rad } (-90^\circ)$ points Right
- $yaw = +1.5708\text{ rad } (+90^\circ)$ points Left
- $yaw = 3.14159\text{ rad } (180^\circ)$ points Rearward

---

## 5-Camera Situational Awareness Array
Extending the single-camera model from [Module 2](../02-kendi-robotunuzu-tasarlayin/README_EN.md) to 5 cameras ([`model.sdf`](./model.sdf)):
- `camera_link` (0.3, 0, 0.2): Front-left primary camera.
- `right_camera_link` (0.3, -0.12, 0.2): Front-right camera (12 cm right of the left camera, forming a **STEREO PAIR** with $0.12\text{ m}$ baseline; used in Module 8).
- `side_right_camera_link` (0, -0.25, 0.2, yaw=-1.5708): Right-facing monocular camera.
- `side_left_camera_link` (0, 0.25, 0.2, yaw=1.5708): Left-facing monocular camera.
- `rear_camera_link` (-0.3, 0, 0.2, yaw=3.14159): Rear-facing monocular camera.

All streams are published cleanly under the `/ika_rover/...` namespace.

---

## Realistic Test Track ([`parkur.world`](./parkur.world))
Rather than a flat infinite plane, an enclosed, rectangular 4-leg corridor circuit was built:
- **Purpose:** Testing SLAM loop closure requires driving around an enclosed loop and returning to a previously visited area—impossible on an open featureless plain.
- **Materials Used:** `Gazebo/Grass` (ground), `Gazebo/Bricks`, `Gazebo/PaintedWall`, `Gazebo/Wood`.

### 🐛 Bug: `Gazebo/Rockwall` Texture Failed to Render
- **Cause:** The material name was referenced assuming standard installation, but the underlying texture file was missing from the standard Gazebo package.
- **Solution:** Verify `texture_unit` definitions in the system `gazebo.material` script before writing world files:
  ```bash
  awk '/^material Gazebo\// {name=$0} /texture (wood|bricks|grass)\.(jpg|png)/ {print name, "->", $0}' /usr/share/gazebo-11/media/materials/scripts/gazebo.material
  ```

### 🐛 Bug: Periodic Tiles (CeilingTiled) Break Stereo Vision
Repeating square grid textures cause severe multi-hypothesis matching ambiguities in StereoSGBM (Module 8). Always select organic, non-repeating textures like `Gazebo/Grass` for stereo testing surfaces.

---

## Manual Teleoperation (`teleop_twist_keyboard`)

```bash
sudo apt install ros-humble-teleop-twist-keyboard -y
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### ⌨️ Keybindings:
- **Motion:**
  - `i` : Drive straight forward
  - `,` : Drive straight backward
  - `j` : Yaw left in place
  - `l` : Yaw right in place
  - `u` / `o` : Forward left / Forward right arc
  - `m` / `.` : Backward left / Backward right arc
  - `k` or `Space` : Emergency stop
- **Velocity Adjustment:**
  - `w` / `x` : Increase / decrease linear velocity by 10%
  - `e` / `c` : Increase / decrease angular velocity by 10%

---

## Launch and Verification

### 1. Launch Track and Robot
[`parkur.world`](./parkur.world) contains the enclosed circuit and embeds the 5-camera UGV Rover directly at origin `(0, 0, 0.15)`:

```bash
gazebo --verbose 07-cok-kamera-mimarisi-ve-parkur/parkur.world
```

### 2. Verify Active Sensor Topics
Inspect active camera topics (5 cameras $\times$ 2 topics = 10 streams):

```bash
ros2 topic list | grep camera
```

Expected output:
- `/ika_rover/camera_sensor/image_raw` & `camera_info` (Front-left)
- `/ika_rover/right_camera_sensor/image_raw` & `camera_info` (Front-right stereo)
- `/ika_rover/side_right_camera_sensor/image_raw` & `camera_info` (Right mono)
- `/ika_rover/side_left_camera_sensor/image_raw` & `camera_info` (Left mono)
- `/ika_rover/rear_camera_sensor/image_raw` & `camera_info` (Rear mono)

Verify LiDAR (`/scan`) and Odometry (`/odom`):
```bash
ros2 topic echo /odom --once
```

### 3. Drive the Circuit via Teleop
In a separate terminal, launch keyboard teleop and steer the rover through the corridor circuit:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

---

## Next Up
[Module 8: Stereo Depth and Point Clouds](../08-stereo-derinlik-point-cloud/README_EN.md)
