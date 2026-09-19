# Module 6: MAVROS + ArduPilot Integration

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## Why This Module?

In a real Pixhawk-powered autonomous ground vehicle (UGV), the robotics architecture is decoupled into two primary tiers:

- **Autopilot / Flight Controller (Pixhawk):** Runs real-time autopilot firmware (ArduPilot Rover). It directly controls low-level PWM lines, motor ESCs/drivers, internal IMU filtering, battery failsafes, and low-level closed-loop velocity PID.
- **Companion Computer:** An embedded single-board computer (such as a Raspberry Pi or NVIDIA Jetson) running ROS 2 on Linux. It ingests high-bandwidth sensors (LiDAR, stereo cameras), runs SLAM and navigation, and issues high-level velocity vectors ("drive at $v_x, \omega_z$").

These two computers communicate across a physical serial UART link using the lightweight binary **MAVLink** protocol. The bridge translating between ROS 2 topics and MAVLink packets is **MAVROS**. In this module, we simulate the Pixhawk without physical hardware via **SITL (Software-In-The-Loop)**, observing how our ROS 2 decision nodes stream setpoints into ArduPilot over MAVLink.

---

## ⚠️ Critical Architectural & Coordinate Frame Analysis

### 1. Scope of This Lab: "MAVLink Setpoint Stream Demonstration"
This setup demonstrates **MAVLink command forwarding and bridge verification**. It is an open-loop architectural bridge demonstration rather than a unified lockstep physics simulation:
- Gazebo and ArduPilot SITL run as **two independent processes**.
- The `avoider.py` node processes Gazebo LiDAR range scans, makes obstacle avoidance decisions, and publishes velocity commands simultaneously to Gazebo (`/cmd_vel`) and MAVROS.
- SITL receives the command stream from the companion computer via MAVLink and propagates its internal dead-reckoning state.

### 2. Coordinate Conventions (Body FLU vs Local NED/ENU)
- **Gazebo `/cmd_vel`:** Evaluated directly in the robot's local body frame (`base_link` - Forward, Left, Up / FLU). `linear.x = 1.0` always commands forward driving along the robot's heading.
- **MAVROS Velocity Setpoints (`/mavros/setpoint_velocity/cmd_vel_unstamped` or `cmd_vel`):**
  - In MAVROS ROS 2, `setpoint_velocity` runs as a component plugin node (`/mavros/setpoint_velocity`).
  - Its `mav_frame` parameter defaults to **`LOCAL_NED`** (North-East-Down), interpreting velocity components in the fixed map frame.
  - If the rover has yawed $90^\circ$ (e.g. facing East), commanding "forward" in the local map frame will cause the vehicle to drift North rather than following its nose!
  - ⚠️ **Source Code Fact:** The plugin callback does **not** inspect `header.frame_id`; coordinate frame transformation is strictly governed by the node's **`mav_frame`** parameter ([`setpoint_velocity.cpp`](https://github.com/mavlink/mavros/blob/ros2/mavros/src/plugins/setpoint_velocity.cpp)).
  - **Correct Configuration:** To ensure velocity commands track vehicle heading, set `mav_frame` to **`BODY_NED`** via `ros2 param set /mavros/setpoint_velocity mav_frame BODY_NED`.

---

## Step 1: Install ArduPilot Rover SITL

ArduPilot Rover provides mature differential-drive (skid-steer) kinematic support.

```bash
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git submodule update --init --recursive
Tools/environment_install/install-prereqs-ubuntu.sh -y
```

Launch SITL:

```bash
cd ~/ardupilot
sim_vehicle.py -v Rover --console --map
```

### 🐛 Troubleshooting: `sim_vehicle.py` or `mavproxy.py` Not Found
- The installer appends directories to `~/.bashrc`, but active shells require reloading: run `source ~/.bashrc`.
- If `mavproxy.py: command not found` occurs:
  ```bash
  pip3 install MAVProxy
  echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
  source ~/.bashrc
  ```

---

## Step 2: Install MAVROS and Establish Bridge

```bash
sudo apt install ros-humble-mavros ros-humble-mavros-extras -y
sudo bash /opt/ros/humble/lib/mavros/install_geographiclib_datasets.sh
```

With SITL running, launch MAVROS configured for APM:

```bash
ros2 launch mavros apm.launch fcu_url:=tcp://127.0.0.1:5762@
```

Verify the link state:

```bash
ros2 topic echo /mavros/state
```

Look for:
- **`connected: true`** — MAVROS is successfully receiving MAVLink heartbeat packets from SITL.

---

## Step 3: Switch to GUIDED Mode, Arm Motors, and Drive in BODY_NED

For safety, ArduPilot will only accept external companion computer setpoints when armed in **GUIDED** mode:

```bash
# 1. Switch mode to GUIDED
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'GUIDED'}"

# 2. Arm the vehicle motors (release safety interlock)
ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"

# 3. ⚠️ CRITICAL FRAME SETTING: Bind velocity setpoints to body frame (BODY_NED)
# First, verify the active plugin node name:
ros2 node list | grep setpoint_velocity
# Expected output: /mavros/setpoint_velocity

# Set mav_frame to BODY_NED:
ros2 param set /mavros/setpoint_velocity mav_frame BODY_NED

# Confirm setting:
ros2 param get /mavros/setpoint_velocity mav_frame
# Expected output: String value is: BODY_NED

# 4. Stream velocity commands (10 Hz periodic stream)
# Option A: Unstamped Twist (interpreted in BODY_NED relative to vehicle nose):
ros2 topic pub /mavros/setpoint_velocity/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" -r 10

# Option B (Alternative): TwistStamped stream:
# ros2 topic pub /mavros/setpoint_velocity/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}}" -r 10
```

In the MAVProxy map and console, observe vehicle groundspeed and position changing along the robot's heading.

---

## Co-Operating with Module 3's Avoidance Node

[`03-engelden-kacma-algoritmasi/avoider.py`](../03-engelden-kacma-algoritmasi/avoider.py) includes concurrent publishers for both Gazebo (`/cmd_vel`) and MAVROS (`/mavros/setpoint_velocity/cmd_vel_unstamped`).
When the rover detects an obstacle in Gazebo and commands a turn, the companion computer mirrors that steering intent into the Pixhawk autopilot over MAVLink in real time.

---

## Progress Milestone & Advanced Roadmap

Completing these first 6 modules establishes core competencies: Linux/WSL2 simulation setup, custom SDF modeling, planar LiDAR obstacle avoidance, OpenCV color processing, AprilTag relative localization, and the MAVLink flight controller bridge.

The remaining modules scale up perceptual and mapping autonomy:
- **Module 7:** Multi-camera optical array and loop-closure test world
- **Module 8:** Stereo disparity depth computation and 3D point cloud generation
- **Module 9:** 2D SLAM (`slam_toolbox`) with closed-loop mapping
- **Module 10:** 3D Volumetric Mapping (OctoMap) and REP-103 optical TF bridging
- **Module 11:** Multi-contact physics stabilization and ramp climbing geometry

---

## Next Up
[Module 7: Multi-Camera Architecture and Realistic Test Track](../07-cok-kamera-mimarisi-ve-parkur/README_EN.md)
