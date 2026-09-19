# Module 2: Design Your Own Robot

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## Why Transition from a Pre-built Model (TurtleBot3) to a Custom Design?

While pre-built platforms like TurtleBot3 are great for initial sanity checks, building a genuine project requires designing your own robot from first principles. In this module, we construct a differential-drive robot model from scratch using **SDF (Simulation Description Format)**: rectangular chassis, 2 drive wheels, a passive caster balance sphere, IMU, planar 2D LiDAR, and camera sensors.

---

## What is SDF in a Nutshell?

SDF is the XML-based description format used by Gazebo to define worlds, robots, and physical objects. Key building blocks include:

- **`<link>`**: A rigid physical body (chassis, wheel, sensor casing) defining mass, inertia, collision geometries, and visual meshes.
- **`<joint>`**: A kinematic constraint connecting two links (revolute, continuous, fixed, prismatic).
- **`<sensor>`**: A hardware transducer attached to a link (camera, LiDAR, IMU).
- **`<plugin>`**: C++ bridge code linking Gazebo physics and simulated sensor outputs into ROS 2 topics.

---

## Model Architecture (`model.sdf`)

The [`model.sdf`](./model.sdf) in this directory includes:

- `base_link` — Main chassis box.
- `left_wheel` / `right_wheel` — Active drive wheels.
- `caster_wheel` — Low-friction passive caster sphere providing 3-point planar stability.
- `imu_link` — Inertial measurement unit (linear acceleration and angular velocity).
- `lidar_link` — 360° planar laser scanner publishing to `/scan`.
- `camera_link` — Front RGB sensor streaming to `/ika_rover/camera_sensor/image_raw`.
- `diff_drive` plugin — Standard Gazebo differential drive plugin subscribing to `/cmd_vel` and calculating wheel joint torques.

---

## 🐛 Bug #1: Model Missing from Gazebo Insert Menu

When placing model definitions (`model.config`, `model.sdf`) into `~/.gazebo/models/<name>/`, Gazebo occasionally fails to index them immediately.

**Solution:** Terminate Gazebo completely (check `ps aux | grep gz` to verify no background processes remain) and launch fresh. Gazebo typically indexes models only during startup.

---

## 🐛 Bug #2: Suffix Collision (`_0`) When Using Gazebo Insert

When dragging a model manually from the Gazebo "Insert" panel, Gazebo appends an instance suffix like `_0` (`ika_rover_0`). This breaks static topic mappings and plugin configurations that expect fixed node and frame names.

**Solution:** Rather than manually inserting models, embed the robot directly into the **simulation world file** so its entity name remains deterministic:

```bash
{
echo '<?xml version="1.0"?>'
echo '<sdf version="1.6">'
echo '  <world name="default">'
echo '    <include><uri>model://sun</uri></include>'
echo '    <include><uri>model://ground_plane</uri></include>'
sed -n '/<model /,/<\/model>/p' ~/.gazebo/models/ika_rover/model.sdf
echo '  </world>'
echo '</sdf>'
} > ~/ika_rover.world
```

---

## 🐛 Bug #3: Wheels Spin but Robot Won't Move Straight (Critical Lesson!)

To orient cylinder meshes horizontally as wheels, we rotated the link $90^\circ$ inside `<pose>`. However, we initially did not specify which coordinate frame the joint rotation axis (`<axis><xyz>0 1 0</xyz>`) should be evaluated in. By default, SDF evaluates this axis in the **rotated link's local frame**—causing the wheel to spin like a spinning top around the vertical axis rather than rolling along the floor!

**Solution:** Explicitly evaluate the joint rotation axis in the **parent model frame**:

```xml
<axis>
  <xyz>0 1 0</xyz>
  <use_parent_model_frame>1</use_parent_model_frame>
  <limit><lower>-1e+16</lower><upper>1e+16</upper></limit>
</axis>
```

This fix is already incorporated in [`model.sdf`](./model.sdf). **Whenever you add a joint to a rotated link in SDF, never forget `<use_parent_model_frame>1</use_parent_model_frame>`**—this is one of the most insidious bugs in Gazebo modeling because it outputs no console errors, producing only baffling physical behavior.

---

## Installation and Testing

```bash
mkdir -p ~/.gazebo/models/ika_rover
# Copy model.sdf and model.config into this directory (from this repo)

# Generate the world file (using the bash command above)

# Launch Gazebo with verbose console output
gazebo --verbose ~/ika_rover.world
```

In a second terminal, verify ROS 2 communication:

```bash
ros2 topic list
# You should see: /scan, /cmd_vel, /odom, /ika_rover/camera_sensor/image_raw
```

Test locomotion:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}}" -r 5
```

**Important:** The `-r 5` flag publishes commands at 5 Hz. Hitting `Ctrl+C` **does not stop the robot**—the `gazebo_ros_diff_drive` plugin continues applying the last received velocity until a new setpoint arrives. To halt the robot cleanly:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}" --once
```

---

## Next Up

[Module 3: Obstacle Avoidance Algorithm](../03-engelden-kacma-algoritmasi/README_EN.md) — We will process 2D LiDAR data and write our first autonomous reactive obstacle avoidance ROS 2 node.
