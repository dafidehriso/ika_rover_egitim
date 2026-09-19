# Module 8: Stereo Depth & Point Clouds

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## Learning Objectives
1. Understand stereoscopic depth perception and disparity ($d$) between two monocular cameras.
2. Ingest camera intrinsic parameters (the $K$ matrix) dynamically from `camera_info`.
3. Compute dense disparity maps with OpenCV StereoSGBM and generate colored `PointCloud2` messages.
4. Diagnose and resolve low-texture matching failures in simulated physics engines.

## Module Files
- [`stereo_disparity.py`](./stereo_disparity.py): Synchronized stereo node computing disparity and streaming PointCloud2.

---

## Conceptual Primer: Two Eyes, One Depth Map
Similar to human binocular vision, the pixel displacement of a physical feature between the left and right rectified camera planes is called **disparity ($d$)**. Knowing the physical inter-camera separation (**baseline $B$**, which is $0.12\text{ m}$ in this rover model), depth ($Z$) along the optical axis is derived via similar triangles:

$$Z = \frac{B \cdot f_x}{d}$$

Corresponding 3D Cartesian coordinates ($X, Y, Z$) in metric space:
$$X = \frac{(u - c_x) \cdot Z}{f_x}, \quad Y = \frac{(v - c_y) \cdot Z}{f_y}$$

### The `camera_info` Topic & The K Matrix
Never hardcode camera intrinsics; ingest them dynamically from the driver's `camera_info` topic:
- $f_x, f_y$: Focal lengths in pixel units ($381.46\text{ px}$)
- $c_x, c_y$: Principal point optical center ($320.5, 240.5\text{ px}$)
- Image dimensions: $640 \times 480$

---

## StereoSGBM & Point Cloud Generation ([`stereo_disparity.py`](./stereo_disparity.py))

The `stereo_disparity.py` node:
1. Synchronizes incoming left (`/ika_rover/camera_sensor/image_raw`) and right (`/ika_rover/right_camera_sensor/image_raw`) image pairs using `message_filters.ApproximateTimeSynchronizer` with a **5 ms tolerance (`slop=0.005` s)**.
   - *Conceptual Precision (Simultaneous Capture vs Acceptance Window):* The 5 ms `slop` parameter **does not guarantee physical simultaneous shutter exposure**; it represents a software acceptance boundary between the header timestamps ($|t_{\text{left}} - t_{\text{right}}| \le 5\text{ ms}$).
   - *Why 5 ms?* At 30 FPS, the inter-frame interval is $\approx 33.3\text{ ms}$. A strict $5\text{ ms}$ window ensures frames from adjacent simulation cycles are never erroneously matched, while accommodating slight rendering jitter.
   - *Hardware vs Simulation:* In physical stereo rigs, true simultaneous exposure is enforced via hardware trigger lines (genlock / sync pins) and global-shutter sensors. In ROS, `ApproximateTimeSynchronizer` filters out non-synchronous message pairs.
2. Calculates dense disparity using `cv2.StereoSGBM` (`/ika_rover/stereo/disparity`).
3. Projects valid disparity pixels into $(X, Y, Z, RGB)$ tuples and serializes them into `sensor_msgs/PointCloud2` (`/ika_rover/stereo/points`).
4. Labels all points in the **`camera_optical_frame`** coordinate system (see Module 10 REP-103 convention).

---

## 🐛 Bug: Initial Disparity Map Was Completely Noisy
- **Root Cause:** Standard Gazebo walls, boxes, and ground planes use uniform, featureless textures. StereoSGBM relies on local intensity variance and gradient patterns to solve block-matching correspondence. On featureless surfaces, the matching cost is ambiguous, leading to random pixel matches and catastrophic noise.
- **Remediation:**
  1. Module 7 applied an organic, non-repeating `Gazebo/Grass` texture to the terrain.
  2. SGBM parameters were tuned for higher confidence:
     - `blockSize`: 7 → 11 (larger matching window).
     - `uniquenessRatio`: 10 → 15 (requires the best cost to decisively outperform the second-best candidate).
     - `speckleWindowSize`: 100 → 150 (cleans small noisy outlier clusters).
  3. A local variance filter (`cv2.boxFilter`) masks out regions whose intensity variance falls below 8 gray levels.

---

## Workspace Setup: Transitioning to the Full Package

To run the complete pipeline cleanly:

```bash
# 1. Back up any prior Module 4 work OUTSIDE the ROS workspace:
cd ~/ika_ws/src
mkdir -p ~/ika_backups
if [ -e camera_vision ] || [ -L camera_vision ]; then
    mv camera_vision ~/ika_backups/camera_vision_backup_$(date +%Y%m%d_%H%M%S)
fi

# 2. Symlink the full repository package into your workspace:
ln -s ~/ika_rover_egitim/camera_vision ~/ika_ws/src/camera_vision

# 3. Build and source:
cd ~/ika_ws
colcon build --symlink-install --packages-select camera_vision
source install/setup.bash
```

---

## Step-by-Step Execution & RViz Visualization

1. **Launch Simulation:**
   ```bash
   gazebo --verbose 07-cok-kamera-mimarisi-ve-parkur/parkur.world
   ```
2. **Launch Stereo Disparity Node:**
   ```bash
   ros2 run camera_vision stereo_disparity --ros-args -p use_sim_time:=true
   ```
3. **Inspect in RViz2:**
   ```bash
   rviz2
   ```
   - **Fixed Frame:** `camera_optical_frame`
   - **Add -> By topic -> `/ika_rover/stereo/points` (PointCloud2)**
   - **Color Transformer:** `RGB8`
   - **Style:** `Flat Squares`, Size: `0.03`

*Result:* A dense, photorealistic 3D point cloud will render in RViz, displaying the green grass, brown wooden ramps, and red brick walls.

---

## Architectural Note: Why Retain This Node?
For 3D volumetric mapping in Module 10, we transition to Gazebo's native `depth_camera` sensor (which provides direct depth without texture sensitivity). However, `stereo_disparity.py` is intentionally retained: it teaches the fundamental mathematics, operational limits, and practical workarounds of building stereoscopic vision systems using commodity dual-monocular cameras.

---

## Next Up
[Module 9: 2D SLAM (slam_toolbox)](../09-2d-slam/README_EN.md)
