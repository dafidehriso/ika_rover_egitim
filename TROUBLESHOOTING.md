# All Errors and Solutions — Quick Reference

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (HATALAR-VE-COZUMLERI.md)](HATALAR-VE-COZUMLERI.md)

This document provides a searchable, central index for all errors, edge cases, and pitfalls encountered across this curriculum. For detailed walkthroughs and root cause analyses, refer to the corresponding module's documentation.

| Symptom / Error | Diagnostic Check / Root Cause | Solution | Module |
|---|---|---|---|
| `Sorry, passwords do not match` | Characters are masked (invisible) when typing in Linux terminal | Type slowly; reset with `wsl -d Ubuntu-22.04 -u root` and `passwd` if needed | [01](./01-wsl-ros2-gazebo-kurulum/README_EN.md) |
| `.bashrc`: `syntax error near unexpected token` | Windows PATH directories containing spaces/parentheses were added unquoted | Always quote PATH exports: `export PATH="..."` | [01](./01-wsl-ros2-gazebo-kurulum/README_EN.md) |
| Edited `.bashrc` but commands not found | Modifications to `.bashrc` do not automatically take effect in existing shells | Run `source ~/.bashrc` or open a fresh terminal window | [01](./01-wsl-ros2-gazebo-kurulum/README_EN.md) |
| `colcon: command not found` | `python3-colcon-common-extensions` package not installed | Run `sudo apt install python3-colcon-common-extensions -y` | [01](./01-wsl-ros2-gazebo-kurulum/README_EN.md), [03](./03-engelden-kacma-algoritmasi/README_EN.md) |
| Model missing from Gazebo Insert menu | Gazebo only scans the model database upon startup | Close Gazebo completely and restart with a clean instance | [02](./02-kendi-robotunuzu-tasarlayin/README_EN.md) |
| `Service /spawn_entity unavailable` | Gazebo ROS factory plugin (`libgazebo_ros_factory.so`) not loaded | Start with `gazebo -s libgazebo_ros_init.so -s libgazebo_ros_factory.so` | [02](./02-kendi-robotunuzu-tasarlayin/README_EN.md) |
| `Error parsing XML ... Error document empty` | File created via PowerShell `>` was encoded as UTF-16LE | Verify with `file file.world`; ensure file is saved as UTF-8 | [02](./02-kendi-robotunuzu-tasarlayin/README_EN.md), [07](./07-cok-kamera-mimarisi-ve-parkur/README_EN.md), [11](./11-denge-ve-fizik-duzeltmeleri/README_EN.md) |
| Wheels rotate but robot does not move straight | Joint axis is evaluated in the rotated link's frame | Add `<use_parent_model_frame>1</use_parent_model_frame>` inside `<axis>` | [02](./02-kendi-robotunuzu-tasarlayin/README_EN.md) |
| Robot keeps driving after `Ctrl+C` | `diff_drive` plugin retains and executes the last velocity command indefinitely | Send a zero velocity Twist command during shutdown (`finally`/`destroy_node`) | [02](./02-kendi-robotunuzu-tasarlayin/README_EN.md), [03](./03-engelden-kacma-algoritmasi/README_EN.md) |
| Robot stops for obstacles behind it, not in front | In a $-\pi..\pi$ LiDAR scan, `ranges[0:15]` points backwards; front sector is in the center | Compute normalized angles using `angle_min + i * angle_increment` | [03](./03-engelden-kacma-algoritmasi/README_EN.md) |
| Camera view looks corrupted or identical to scene | Gazebo 3D camera is confused with robot's onboard sensor | Inspect the standalone borderless OpenCV window opened via `cv2.imshow` | [04](./04-opencv-goruntu-isleme/README_EN.md) |
| AprilTag PNG is only a few hundred bytes | **Not an error** — AprilTag raw patterns are genuinely low resolution ($10\times 10$ px) | Verify it is a valid PNG using the `file` command | [05](./05-apriltag-ile-konum-tespiti/README_EN.md) |
| Tag appears as a razor-thin line in camera view | Plate normal is $\pm Y$; camera looking along $+X$ sees the tag edge-on | Rotate tag $90^\circ$ around yaw axis (`yaw=1.5708` in pose) | [05](./05-apriltag-ile-konum-tespiti/README_EN.md) |
| AprilTag 3D distance has 25% error | `size` in YAML must define the inner $8\times 8$ black grid, not outer plate | For a 0.30 m physical plate, set `size: 0.24` | [05](./05-apriltag-ile-konum-tespiti/README_EN.md) |
| Robot keeps driving after tag leaves camera view | `lookup_transform(..., Time())` returns stale transforms from the buffer | Check transform stamp age (`now - stamp > 0.5s`) and stop the robot | [05](./05-apriltag-ile-konum-tespiti/README_EN.md) |
| `tag_follower`: `No executable found` | Missing console_scripts registration in package `setup.py` | Add `'tag_follower = tag_follower.tag_follower:main'` to `setup.py` | [05](./05-apriltag-ile-konum-tespiti/README_EN.md) |
| `tag_follower` sees tag but robot does not move | Node clock is using system time instead of simulation time `/clock` | Launch node with `--ros-args -p use_sim_time:=true` | [05](./05-apriltag-ile-konum-tespiti/README_EN.md) |
| TF lookup: `camera_optical_frame` not found | Basic SDF robot defines `camera_link`; optical frame TF is missing | Run static TF publisher: `0 0 0 -1.5708 0 -1.5708 camera_link camera_optical_frame` | [05](./05-apriltag-ile-konum-tespiti/README_EN.md) |
| `mavproxy.py: command not found` | `~/.local/bin` is not in shell PATH | Add `export PATH="$PATH:$HOME/.local/bin"` and reload `~/.bashrc` | [06](./06-mavros-ardupilot-entegrasyonu/README_EN.md) |
| ArduPilot veers North instead of forward after turning | Gazebo uses body FLU; MAVROS default is LOCAL_NED (map frame) | Run `ros2 param set /mavros/setpoint_velocity mav_frame BODY_NED` | [06](./06-mavros-ardupilot-entegrasyonu/README_EN.md) |
| Topics missing when launching `parkur.world` | Robot model is not defined or spawned in the world file | Include robot in `parkur.world` or spawn via `spawn_entity.py` | [07](./07-cok-kamera-mimarisi-ve-parkur/README_EN.md) |
| Gazebo/Rockwall texture not rendering | Material name assumed without checking `gazebo.material` script | Verify `texture_unit` in material scripts via `grep`/`awk` | [07](./07-cok-kamera-mimarisi-ve-parkur/README_EN.md) |
| Periodic texture (CeilingTiled) breaks stereo | Repeating tile patterns cause catastrophic stereo matching ambiguity | Use organic/irregular texture (such as `Gazebo/Grass`) | [07](./07-cok-kamera-mimarisi-ve-parkur/README_EN.md), [08](./08-stereo-derinlik-point-cloud/README_EN.md) |
| Mixed/corrupted frames in stereo sync | `ApproximateTimeSynchronizer` tolerance (`slop`) misconfigured | Set `slop=0.005` (5 ms) for 30 FPS camera streams | [08](./08-stereo-derinlik-point-cloud/README_EN.md) |
| Empty SLAM map, `Message Filter dropping message` | Missing URDF or sensor not linked in TF tree | Publish required sensor transforms with `static_transform_publisher` | [09](./09-2d-slam/README_EN.md) |
| TF valid but SLAM map remains blank | `slam_toolbox` defaults to `base_frame: base_footprint`, robot uses `base_link` | Configure `base_frame: base_link` in `slam_params.yaml` | [09](./09-2d-slam/README_EN.md) |
| `Package 'camera_vision' not found` or launch missing | Full package from repo not linked or built in `~/ika_ws/src` | Create symlink (`ln -s`) to repo package and run `colcon build` | [10](./10-3d-haritalama-octomap/README_EN.md) |
| OctoMap point cloud scattered or floating vertically | Optical frame rule (Z=depth) confused with ROS body rule (X=forward) | Publish optical rotation transform for `camera_optical_frame` | [10](./10-3d-haritalama-octomap/README_EN.md) |
| "Ghost walls" and voxel drift in OctoMap | OctoMap tracking 'map' frame which jumps on loop closure | Bind OctoMap sensor tracking to drift-free continuous 'odom' frame | [10](./10-3d-haritalama-octomap/README_EN.md) |
| FastDDS / ROS 2 message deadlocks on WSL2 | FastDDS low-level multicast routing lockup | Add environment variable `export FASTDDS_BUILTIN_TRANSPORTS=UDPv4` | [10](./10-3d-haritalama-octomap/README_EN.md) |
| Ramp acts like an invisible barrier to robot | Box rotated about center leaves bottom edge ~30 cm above ground | Recalculate box center and pitch so ramp entry touches $Z=0$ | [11](./11-denge-ve-fizik-duzeltmeleri/README_EN.md) |
| Robot pitches forward during acceleration | Single rear caster, zero front support (cantilever load) | Add 2 front caster wheels for stable 5-point ground contact | [11](./11-denge-ve-fizik-duzeltmeleri/README_EN.md) |

---

## Systematic Diagnostic Guide (Symptom → Check → Root Cause → Fix)

### 1. `Message Filter [target: ...] dropping message` Warning
This common ROS 2 warning can stem from several causes. Execute these 4 checks sequentially:
1. **Missing TF Transform:**
   - *Check:* Run `ros2 run tf2_tools view_frames` or `ros2 run tf2_ros tf2_echo odom <sensor_frame>`.
   - *Expected:* Continuous transform chain: `map -> odom -> base_link -> sensor_frame`.
   - *Fix:* Publish missing links via `static_transform_publisher` ([Module 9](./09-2d-slam/README_EN.md)).
2. **Simulation Time Mismatch (`use_sim_time`):**
   - *Check:* Inspect node and launch parameters for `use_sim_time`.
   - *Expected:* When running Gazebo, all nodes must synchronize against `/clock` (`use_sim_time:=true`). If one node uses wall clock and another uses simulation time, messages will be dropped as outdated.
3. **QoS (Quality of Service) Incompatibility:**
   - *Check:* `ros2 topic info /scan --verbose`.
   - *Root Cause:* If Gazebo publishes with `Best Effort` reliability and the receiving subscriber requires `Reliable`, the subscription will drop all incoming messages.
4. **Startup Race Condition:**
   - *Root Cause:* If sensor drivers start 1–2 seconds before TF publishers, initial messages drop. Ensure static transforms launch concurrently or prior to consumers ([Module 10](./10-3d-haritalama-octomap/README_EN.md)).

---

### 2. Gazebo XML / SDF: `Error document empty`
- **Symptom:** `[gzserver] Error [parser.cc:403] Error parsing XML ... Error document empty.`
- **Check Command:**
  ```bash
  file <filename>
  ```
- **Expected Output:** `XML 1.0 document, Unicode text, UTF-8 text`
- **Faulty Output:** `XML 1.0 document, Unicode text, UTF-16, little-endian text`
- **Root Cause:** Windows PowerShell redirection (`cat ... > file.world`) creates UTF-16LE files by default. Gazebo's C++ XML parser (TinyXML) cannot parse UTF-16 and treats the document as empty.
- **Fix:** Save as UTF-8 or copy directly inside WSL bash (`cp source destination`).

---

### 3. LiDAR Array Indexing Pitfall (Front vs Rear Sector)
- **Symptom:** Robot fails to stop for obstacles 30 cm in front, but stops and avoids obstacles placed behind it.
- **Check Command:**
  ```bash
  ros2 topic echo /scan --field angle_min
  ros2 topic echo /scan --field angle_max
  ```
- **Expected Output:** `angle_min: -3.14159`, `angle_max: 3.14159`.
- **Root Cause:** Gazebo planar LiDAR scans from $-\pi$ to $+\pi$. Array index 0 and -1 represent the rear of the robot; the front sector sits in the middle of the array. Slicing `ranges[0:15]` checks behind the rover!
- **Fix:** Calculate angle dynamically: `angle = angle_min + i * angle_increment`. Only evaluate rays satisfying `abs(angle) <= math.radians(15.0)` ([Module 3](./03-engelden-kacma-algoritmasi/README_EN.md)).

---

### 4. AprilTag Size & 3D Depth Scaling (Quiet Zone Margin)
- **Symptom:** Robot commanded to stop at 1.0 m from an AprilTag actually stops at 1.25 m (25% distance error).
- **Check Command:** `cat apriltag_config.yaml | grep size`
- **Root Cause:** A $10\times 10$ pixel `tag36h11` pattern includes a 1-pixel outer white margin (quiet zone). The `size` parameter in AprilTag detectors specifies the physical edge length of the detected $8\times 8$ black grid, NOT the outer physical mounting board.
- **Fix:** For a 0.30 m outer board, set the active tag size to $(8/10) \times 0.30\text{ m} = 0.24\text{ m}$ ([Module 5](./05-apriltag-ile-konum-tespiti/README_EN.md)).

---

### 5. AprilTag / TF Transform Staleness (Stale Transform)
- **Symptom:** When the AprilTag leaves the camera field of view, the robot keeps driving or turning indefinitely.
- **Check Command:** Compare `transform.header.stamp` with `node.get_clock().now()`.
- **Root Cause:** Calling `lookup_transform(..., Time())` without explicit time checks returns the last recorded transform in the TF buffer.
- **Fix:** Calculate age: `age = now - stamp`. If `age > 0.5s`, treat the tag as lost and command zero velocity ([Module 5](./05-apriltag-ile-konum-tespiti/README_EN.md)).

---

### 6. Simulation Clock (`use_sim_time`) vs Wall Clock Mismatch
- **Symptom:** `tag_follower` runs, camera sees the tag clearly, `/tf` messages publish, but robot refuses to drive, logging "Transform data stale".
- **Check Command:** Verify if the node was started with `--ros-args -p use_sim_time:=true`.
- **Root Cause:** Gazebo starts its clock at 0.0 seconds. If a ROS 2 node runs without `use_sim_time`, `get_clock().now()` queries the Linux system wall clock (epoch ~1.7 billion seconds). The resulting delta $(now - stamp)$ is astronomical, triggering watchdog timeouts.
- **Fix:** Pass `--ros-args -p use_sim_time:=true` to all nodes running against simulation ([Module 5](./05-apriltag-ile-konum-tespiti/README_EN.md), [Module 8](./08-stereo-derinlik-point-cloud/README_EN.md)).

---

### 7. Missing Package `entry_points` (`No executable found`)
- **Symptom:** `ros2 run <package_name> <script_name>` fails with `No executable found`.
- **Check Command:** `cat ~/ika_ws/src/<package_name>/setup.py | grep entry_points -A 5`
- **Root Cause:** `ros2 pkg create --build-type ament_python` creates an empty `entry_points` dictionary. Merely creating a `.py` file inside the package folder is not enough; it must be registered under `console_scripts`.
- **Fix:** Add `'<script_name> = <package_name>.<script_name>:main'` to `entry_points` in `setup.py` and run `colcon build` ([Module 5](./05-apriltag-ile-konum-tespiti/README_EN.md)).

---

### 8. `camera_vision` Workspace Transition & Clean Backup
- **Symptom:** Running `ros2 launch camera_vision ika_mapping.launch.py` in Module 10 produces `Package 'camera_vision' not found`.
- **Check Command:** Inspect `ros2 pkg prefix camera_vision`.
- **Root Cause:** Module 4 created an initial, basic `camera_vision` package. The complete repository package contains full launch files, RViz configs, multi-camera SDF models, and stereo/depth processing nodes.
- **Fix:** Move previous Module 4 work to an isolated backup directory outside the workspace (`~/ika_backups/...`), symlink the full repository package (`ln -s ~/ika_rover_egitim/camera_vision ~/ika_ws/src/camera_vision`), and build with `colcon build --packages-select camera_vision` ([Module 10](./10-3d-haritalama-octomap/README_EN.md)).

---

### 9. MAVROS Velocity Coordinate Frame (`LOCAL_NED` vs `BODY_NED`)
- **Symptom:** When commanding forward velocity after turning the rover, it drifts North instead of following its nose.
- **Check Command:** Check the node name with `ros2 node list | grep setpoint_velocity`, then inspect `ros2 param get /mavros/setpoint_velocity mav_frame`.
- **Root Cause:** MAVROS defaults to `LOCAL_NED` (map North-East-Down). To drive relative to the vehicle heading, velocities must be interpreted in `BODY_NED`. The plugin callback does not inspect `header.frame_id`; coordinate frame conversion is strictly controlled by the node's `mav_frame` parameter.
- **Fix:** Set the parameter on the plugin node: `ros2 param set /mavros/setpoint_velocity mav_frame BODY_NED` ([Module 6](./06-mavros-ardupilot-entegrasyonu/README_EN.md)).
