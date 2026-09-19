# Module 5: Relative Positioning with AprilTags

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## What is an AprilTag?

An AprilTag is a square fiducial marker featuring a 2D barcode payload (conceptually similar to a QR code, but optimized for rapid, robust computer vision detection under challenging angles and lighting). Because the camera driver and detection library already know the **exact physical dimensions** of the tag, the algorithm analyzes perspective foreshortening in the 2D image to geometrically extract the **full 6-DoF 3D position and orientation** of the target relative to the camera frame.

This technique is widely employed in robotics for GPS-denied indoor localization, precision docking (e.g. aligning with a wireless charging pad), and relative formation following.

---

## Step 1: Install the Package

```bash
sudo apt install ros-humble-apriltag-ros -y
```

---

## Step 2: Acquire a Genuine AprilTag Asset

**Important:** A hand-drawn or arbitrary black-and-white square will not work—the detector requires the exact bit layout of the tag dictionary.

```bash
mkdir -p ~/.gazebo/models/apriltag_0/materials/textures
wget https://raw.githubusercontent.com/AprilRobotics/apriltag-imgs/master/tag36h11/tag36_11_00000.png -O ~/.gazebo/models/apriltag_0/materials/textures/tag0.png
```

Verify the image: `file ~/.gazebo/models/apriltag_0/materials/textures/tag0.png` → outputs `PNG image data, 10 x 10`. **10x10 pixels is completely standard for an AprilTag bitmap**—low resolution is an intentional feature of the math, not a corrupted file.

---

## Step 3: Configure the Gazebo Model

Copy the files from this directory:
- [`apriltag_0.model.config`](./apriltag_0.model.config) → `~/.gazebo/models/apriltag_0/model.config`
- [`apriltag_model.sdf`](./apriltag_model.sdf) → `~/.gazebo/models/apriltag_0/model.sdf`
- [`apriltag.material`](./apriltag.material) → `~/.gazebo/models/apriltag_0/materials/scripts/apriltag.material`

The `filtering none` setting in `apriltag.material` is critical: it forces point sampling without bilinear blurring so the tag's sharp pixel borders are rendered cleanly.

Include the target in your world file:

```xml
<include>
  <uri>model://apriltag_0</uri>
  <name>apriltag_0</name>
  <pose>1.2 0 0.15 0 0 1.5708</pose>
</include>
```

### 🐛 Geometry Correction: Plate Normal & Orientation
In the model definition, the tag board is sized as `<size>0.3 0.01 0.3</size>` ($X=0.3\text{ m}$, $Y=0.01\text{ m}$ thickness, $Z=0.3\text{ m}$).
- **Surface Normal:** Because the thin edge lies along the $Y$ axis, the surface normal vector of the broad face points along **$\pm Y$**.
- **Camera Orientation:** Since the robot's front camera looks along $+X$, an unrotated (`yaw=0`) tag presents only its 1 cm razor-thin edge to the rover!
- **Solution:** Rotate the plate $90^\circ$ around the vertical $Z$ axis (`yaw=1.5708 rad`). The broad face then directly faces the robot camera.

### ⚠️ Critical Physical Scaling: The `size: 0.24` Reality
The `size` parameter in [`apriltag_config.yaml`](./apriltag_config.yaml):
- In `apriltag_ros`, `size` does **not** specify the outer board or white quiet zone; it defines the edge length of the detected black border.
- In a $10\times 10$ pixel `tag36h11` bitmap, subtracting the 1-pixel outer white margin leaves an $8\times 8$ black grid:
  $$\text{Effective Size} = \frac{8}{10} \times 0.30\text{ m} = 0.24\text{ m}$$
- If you configure `size: 0.3` in the YAML, estimated 3D distances will be inflated by ~25%! The mathematically correct value is `size: 0.24`.

---

## Step 4: Run the AprilTag Detector Node

Create `~/apriltag_config.yaml`:

```bash
printf 'apriltag:\n  ros__parameters:\n    image_transport: raw\n    family: 36h11\n    size: 0.24\n' > ~/apriltag_config.yaml
```

Launch the detector node:

```bash
ros2 run apriltag_ros apriltag_node --ros-args \
  -r image_rect:=/ika_rover/camera_sensor/image_raw \
  -r camera_info:=/ika_rover/camera_sensor/camera_info \
  --params-file ~/apriltag_config.yaml
```

---

## Step 5: Verify Detection

```bash
ros2 topic echo /detections
```

Healthy detection output will report:
- **`hamming: 0`** — Zero bit errors.
- **`decision_margin`** — High confidence score.

---

## Step 6: TF Conventions & Optical Frame Bridge

`apriltag_ros` broadcasts tag poses relative to the camera optical frame:

```bash
ros2 run tf2_ros tf2_echo camera_optical_frame tag36h11:0
```

- **In `camera_optical_frame` (Pinhole Camera Convention):**
  - **Z = Forward distance (depth)**
  - **X = Lateral offset** (positive = right, negative = left)
  - **Y = Vertical offset** (positive = down)
- **In `base_link` or `camera_link` (Robot Body Convention REP-103):**
  - **X = Forward distance**
  - **Y = Lateral offset** (positive = left, negative = right)
  - **Z = Vertical height**

### ⚠️ Bridging `camera_link` and `camera_optical_frame`
The basic SDF model sets the camera frame name to `camera_link` (body-aligned: $+X$ forward, $+Z$ up). Computer vision algorithms, however, assume the pinhole optical convention (`camera_optical_frame`: $+Z$ forward, $+X$ right, $+Y$ down).

Publish static transforms in a separate terminal:

```bash
# 1. Optical rotation from camera_link to camera_optical_frame (roll=-90°, yaw=-90°):
ros2 run tf2_ros static_transform_publisher 0 0 0 -1.5708 0 -1.5708 camera_link camera_optical_frame

# 2. Physical mounting offset from base_link to camera_link (0.3 m forward, 0.2 m up):
ros2 run tf2_ros static_transform_publisher 0.3 0 0.2 0 0 0 base_link camera_link
```

This completes the unbroken transform chain: `base_link -> camera_link -> camera_optical_frame -> tag36h11:0`.

---

## Step 7: Autonomous Tag Follower Node ([`tag_follower.py`](./tag_follower.py))

[`tag_follower.py`](./tag_follower.py) subscribes to `/tf`, computes relative spatial error, and drives the rover to settle precisely 1.0 m in front of the target.

### ⚠️ Key Operational Details:
1. **Transform Staleness Watchdog:** Calling `lookup_transform(..., Time())` retrieves the last buffered transform. If the tag leaves the camera FOV, old transforms persist! `tag_follower.py` validates the transform timestamp (`transform.header.stamp`); if older than 0.5 s, it treats the target as lost and executes `stop_robot()`.
2. **Simulation Clock (`use_sim_time`):** Nodes running against Gazebo must synchronize against `/clock`. Note that ROS 2 Humble natively declares this parameter; do not call `declare_parameter('use_sim_time', ...)` inside node classes.
3. **Mounting Offsets:** The physical camera is mounted 0.3 m ahead of `base_link`. Setting `target_frame: camera_optical_frame` measures distance from the camera lens; setting `target_frame: base_link` measures from the chassis rotational center.
4. **Shutdown Safety:** Explicit zero velocities are commanded during node termination.

### 🛠️ Creating the Package and Running:

```bash
# 1. Create the package
cd ~/ika_ws/src
ros2 pkg create --build-type ament_python tag_follower --dependencies rclpy geometry_msgs tf2_ros

# 2. Copy the node script
cp ~/ika_rover_egitim/05-apriltag-ile-konum-tespiti/tag_follower.py ~/ika_ws/src/tag_follower/tag_follower/
```

**Register in `setup.py` under `entry_points`:**
```python
    entry_points={
        'console_scripts': [
            'tag_follower = tag_follower.tag_follower:main',
        ],
    },
```

```bash
# 3. Build and source
cd ~/ika_ws
colcon build --packages-select tag_follower
source install/setup.bash

# 4. Run with simulation time enabled:
ros2 run tag_follower tag_follower --ros-args -p use_sim_time:=true
```

---

## Next Up

[Module 6: MAVROS + ArduPilot Integration](../06-mavros-ardupilot-entegrasyonu/README_EN.md) — Bridging companion computer setpoints into a Pixhawk autopilot simulation via MAVLink.
