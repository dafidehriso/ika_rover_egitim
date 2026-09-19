# Module 4: OpenCV Image Processing

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## What is OpenCV, in a Nutshell?

OpenCV (Open Source Computer Vision) is the industry-standard computer vision library. In Python, an image is fundamentally a **multidimensional numerical array (NumPy array)** where each element represents pixel color channels (Blue, Green, Red). OpenCV provides optimized primitives for color space conversions, spatial filtering, edge detection, and morphological transformations.

---

## Why We Need a Colored Simulation World

In an untextured, monochrome world, computer vision algorithms have little contrast to operate on. For this module, we introduce static RGB target boxes into `ika_rover.world` (extending the world created in [Module 2](../02-kendi-robotunuzu-tasarlayin/README_EN.md)):

```xml
<model name="red_box">
  <static>true</static>
  <pose>2 1 0.25 0 0 0</pose>
  <link name="link">
    <collision name="collision">
      <geometry><box><size>0.5 0.5 0.5</size></box></geometry>
    </collision>
    <visual name="visual">
      <geometry><box><size>0.5 0.5 0.5</size></box></geometry>
      <material>
        <ambient>1 0 0 1</ambient>
        <diffuse>1 0 0 1</diffuse>
      </material>
    </visual>
  </link>
</model>
```
(Use `0 1 0 1` for green and `0 0 1 1` for blue, placing them at varying coordinates.)

---

## Installation & Package Setup

```bash
sudo apt install ros-humble-cv-bridge python3-opencv -y
cd ~/ika_ws/src
ros2 pkg create --build-type ament_python camera_vision --dependencies rclpy sensor_msgs cv_bridge
```

`cv_bridge` is the official middleware bridge that transforms ROS image messages (`sensor_msgs/Image`) into native NumPy arrays suitable for OpenCV, and vice-versa.

Place `camera_viewer.py` inside `~/ika_ws/src/camera_vision/camera_vision/` and register it in `setup.py`:

```python
'camera_viewer = camera_vision.camera_viewer:main',
```

---

## Step-by-Step Algorithm Logic

1. **BGR to HSV Conversion:** Camera streams arrive in BGR format. However, segmentation is far more robust in the **HSV** (Hue, Saturation, Value) color space, where chromaticity (Hue) is decoupled from illumination and shadow intensity (Value).
2. **`cv2.inRange` Masking:** Binary thresholding isolating pixels falling within the predefined lower and upper Hue bounds (handling red's wraparound at 0° and 180°).
3. **`cv2.findContours`:** Extracts boundary contours of connected white components from the binary mask.
4. **`cv2.boundingRect`:** Calculates the minimal upright bounding box around the largest detected component and overlays it onto the video feed.

---

## Building and Execution

```bash
cd ~/ika_ws && colcon build --packages-select camera_vision
source install/setup.bash
ros2 run camera_vision camera_viewer
```

Two visual windows will appear:
- **Raw Stream:** Original RGB view with green tracking bounding boxes drawn around detected targets.
- **Binary Mask:** Segmented output where red targets appear solid white against an all-black background.

---

## 🐛 Common Pitfall: Inspecting the Wrong Display Window

Gazebo's 3D perspective viewport (with gridlines and scene navigation) is completely separate from the **robot's onboard optical perspective** displayed via `cv2.imshow`. Always inspect the OpenCV window titled "ika_rover kamerasi" to evaluate what the rover's computer vision algorithm actually sees.

> **💡 Architectural Note (Package Roadmap):**
> The minimal `camera_vision` package initialized in this lesson will be expanded in later modules ([Module 8](../08-stereo-derinlik-point-cloud/README_EN.md) for stereo disparity and [Module 10](../10-3d-haritalama-octomap/README_EN.md) for 3D OctoMap pipelines) into the full multi-node package located in the repository root.

---

## Next Up

[Module 5: Relative Positioning with AprilTags](../05-apriltag-ile-konum-tespiti/README_EN.md) — We will estimate exact 6-DoF 3D spatial poses of fiducial markers and implement closed-loop visual tracking.
