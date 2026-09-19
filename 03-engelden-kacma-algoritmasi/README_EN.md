# Module 3: Obstacle Avoidance Algorithm

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## Conceptual Primer: What is a ROS 2 Node?

A **node** in ROS 2 is an independent, modular process responsible for a single distinct function. Nodes communicate asynchronously via **topics**: a node **publishes** messages to a topic, while other nodes **subscribe** to that topic. The node we build in this module:

- **Subscribes** to `/scan` (receives 2D planar LiDAR range scans).
- **Publishes** to `/cmd_vel` (issues velocity vector setpoints).

In essence, this forms a reactive autonomous control loop: "Is there an obstacle ahead? If so, decide a heading, command wheel velocities, and avoid collisions."

---

## The Code: [`avoider.py`](./avoider.py)

**High-Level Logic:** The node monitors LiDAR rays within the frontal cone ($\pm 15^\circ$) using dynamically calculated ray angles. If the minimum measured obstacle distance within this front sector falls below `safe_distance` (default $0.5\text{ m}$), the robot halts and turns left; once clear, it resumes forward motion.

### ⚠️ CRITICAL PITFALL & HISTORICAL EVOLUTION: LiDAR Array Indexing Trap
In the initial naive implementation, the front sector was sliced like this:
```python
# FAULTY INITIAL IMPLEMENTATION:
front_ranges = msg.ranges[0:15] + msg.ranges[-15:]
```
- **Root Cause:** In the SDF sensor definition, the LiDAR spans from `min_angle = -3.14159` ($-\pi$) to `max_angle = +3.14159` ($+\pi$). Array index `0` corresponds to $-\pi$ (directly **BEHIND** the robot), while the final index corresponds to $+\pi$ (also directly **BEHIND** the robot)! Zero radians (straight forward) sits dead-center in the array (e.g. index 180 out of 360). Slicing the array ends caused the robot to check behind itself instead of in front!
- **Robust Solution:** Never assume hardcoded array indices (which also break when swapping between 360-ray and 720-ray LiDARs). Instead, compute each ray's true angle dynamically: `angle = angle_min + i * angle_increment`, normalize to $[-\pi, +\pi]$, and filter strictly for rays where `abs(beam_angle) <= math.radians(15.0)`.

---

### Angular Convention (REP-103) Standard
Under ROS conventions (REP-103), the $+Z$ axis points vertically upward. By the right-hand rule, **positive `angular.z` denotes counter-clockwise rotation, which means turning LEFT**. In our node, commanding `angular.z = +0.5 rad/s` swings the rover left.

---

### Sensor Data Policy (Handling NaN, Out-of-Range, and +Inf)
1. **`+Inf` (No Echo / Open Space):** The laser pulse traveled beyond the sensor's maximum range without intersecting an obstacle. This is **not an obstacle**; it indicates clear space ahead.
2. **`NaN` / Invalid Data:** Sensor dropouts or blind spots. Filtered out as non-measurable.
3. **Fail-Safe Policy:** If no valid distance readings can be retrieved across the frontal sector, the robot avoids driving blindly and halts immediately (`publish_stop()`).

---

### Watchdog Timer & Graceful Shutdown
- **Watchdog:** If the LiDAR node crashes or wireless telemetry drops, a software watchdog timer halts the rover if no fresh `/scan` message arrives within `scan_timeout_sec` ($0.5\text{ s}$).
- **Graceful Termination:** On `Ctrl+C`, the `finally` block and `destroy_node()` explicitly publish zero linear and angular velocities (`linear.x = 0`, `angular.z = 0`).
- *Architecture Note:* For hardware fail-safety against kernel panics or SIGKILL, low-level motor drivers should also feature hardware command timeouts.

---

### ⚠️ Command Multiplexing Warning
Publishing velocity commands to `/cmd_vel` from multiple concurrent sources (e.g. `teleop_twist_keyboard` and `avoider` simultaneously) produces rapid command oscillation and erratic motor jitter.
- Terminate keyboard teleop nodes before running `avoider`.
- In production architectures, use `twist_mux` to manage topic arbitration and command prioritization.

---

## Creating the ROS 2 Python Package

```bash
mkdir -p ~/ika_ws/src && cd ~/ika_ws/src
ros2 pkg create --build-type ament_python obstacle_avoidance --dependencies rclpy sensor_msgs geometry_msgs
```

Copy `avoider.py` to `~/ika_ws/src/obstacle_avoidance/obstacle_avoidance/avoider.py`.

Register the executable in `setup.py` under `entry_points`:

```python
entry_points={
    'console_scripts': [
        'avoider = obstacle_avoidance.avoider:main',
    ],
},
```

---

## Building and Running

```bash
cd ~/ika_ws
colcon build --packages-select obstacle_avoidance
source install/setup.bash
ros2 run obstacle_avoidance avoider
```

In Gazebo, observe your rover navigating autonomously: driving forward in open corridors, halting and yawing left when an obstacle encroaches within 0.5 m, and continuing once clear.

---

## Why Dual Publishing to Gazebo and MAVROS?

The node instantiates two separate publishers: one targeting Gazebo's direct controller (`/cmd_vel`) and another targeting ArduPilot via MAVROS (`/mavros/setpoint_velocity/cmd_vel_unstamped`). As detailed in [Module 6](../06-mavros-ardupilot-entegrasyonu/README_EN.md), real autonomous rovers employ a companion computer (running this node) to make high-level decisions while offloading low-level motor PID and RC safety to an autopilot (Pixhawk). If Module 6 is not yet configured, the MAVROS publisher simply runs passively with no connected subscriber.

---

## Next Up

[Module 4: OpenCV Image Processing](../04-opencv-goruntu-isleme/README_EN.md) — We will attach an onboard camera and implement color segmentation with HSV filtering and contour analysis.
