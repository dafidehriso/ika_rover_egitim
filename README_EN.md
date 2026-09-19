# UGV Course: Autonomous Unmanned Ground Vehicle Simulation with ROS 2 + Gazebo on Windows from Scratch

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

This repository is a comprehensive, step-by-step tutorial series designed for anyone—even with zero prior Linux or ROS experience—to build their own **autonomous mobile robot (UGV) simulation** on **Windows 11 + WSL2**, complete with detailed explanations of real-world bugs and their practical solutions.

Unlike tutorials that claim "everything worked perfectly on the first try", this repository is an authentic record of real robotic software engineering: trial-and-error, diagnosing failures, understanding root causes, and implementing robust fixes. You will encounter the exact problems real roboticists face—and learn how to systematically solve them.

---

## Who Is This For?

- Anyone needing to build a robotics project (university, internship, competition, or personal) who has never used ROS 2 or Gazebo before.
- Windows users who want to avoid dual-booting Linux (WSL2 solves this completely).
- Engineers and students who want to understand **why** commands are run, rather than blindly copy-pasting terminal lines.
- University Rover Challenge (URC) / European Rover Challenge (ERC) and robotics competition teams looking for a battle-tested reference architecture.

---

## Course Curriculum

Each directory represents a standalone yet progressive module—follow them in order, as each one builds directly upon the previous:

| # | Module | What You Learn |
|---|--------|----------------|
| [01](./01-wsl-ros2-gazebo-kurulum/README_EN.md) | WSL2 + ROS 2 + Gazebo Installation | Setting up a Linux robotics environment on Windows, fixing `.bashrc`/PATH issues, WSLg GUI configuration |
| [02](./02-kendi-robotunuzu-tasarlayin/README_EN.md) | Design Your Own Robot | Creating an SDF robot model from scratch (chassis, wheels, sensors), resolving joint & physics discrepancies |
| [03](./03-engelden-kacma-algoritmasi/README_EN.md) | Obstacle Avoidance Algorithm | Processing 2D LiDAR data, writing a Python ROS 2 node, reactive obstacle avoidance with watchdog protection |
| [04](./04-opencv-goruntu-isleme/README_EN.md) | OpenCV Image Processing | Integrating simulated cameras, `cv_bridge` image conversion, HSV color space segmentation, contour detection |
| [05](./05-apriltag-ile-konum-tespiti/README_EN.md) | AprilTag Relative Localization | Extracting 3D target poses, `tf2` transforms, transform staleness checks, closed-loop autonomous visual tracking |
| [06](./06-mavros-ardupilot-entegrasyonu/README_EN.md) | MAVROS + ArduPilot Integration | SITL simulation, companion computer ↔ flight controller bridge, body frames vs local frames (`BODY_NED`), parameter handling |
| [07](./07-cok-kamera-mimarisi-ve-parkur/README_EN.md) | Multi-Camera Architecture & Track | 5-camera SDF design, ground textures for computer vision, closed-loop corridor test world, keyboard teleop |
| [08](./08-stereo-derinlik-point-cloud/README_EN.md) | Stereo Depth & Point Clouds | Disparity maps via StereoSGBM, camera intrinsics, PointCloud2 generation, timestamp sync (`slop`), RViz display |
| [09](./09-2d-slam/README_EN.md) | 2D SLAM (`slam_toolbox`) | Building the TF tree, base_frame tuning, closed-loop loop closure, generating 2D occupancy grids |
| [10](./10-3d-haritalama-octomap/README_EN.md) | 3D Volumetric Mapping (OctoMap) | REP-103 optical frames, native depth sensors, point cloud filtering, unified launch pipeline |
| [11](./11-denge-ve-fizik-duzeltmeleri/README_EN.md) | Balance & Physics Corrections | Center-of-mass tuning, caster wheel friction, ramp climbing physics & tipping limit calculations |

---

## Tested System Environment

The code, launch files, and simulation worlds in this curriculum were tested and verified under:

- **Host OS:** Windows 11 Pro + WSL2 (Ubuntu 22.04 LTS)
- **ROS Distribution:** ROS 2 Humble Hawksbill (`ros-humble-desktop`)
- **Simulator:** Gazebo Classic 11.10.2 (`gazebo11`)
- **Important Note on Gazebo Classic EOL:** Gazebo Classic (Gazebo 11) reached its official End-of-Life (EOL) in January 2025. While it remains widely used and rock-solid with ROS 2 Humble, migrating to Modern Gazebo (Gazebo Sim / Harmonic) is recommended for newer distributions like ROS 2 Jazzy or Rolling. This repository is built on Gazebo Classic 11; a migration guide for modern Gazebo Sim is planned for future updates.

---

## High-Level System Architecture

By the end of this curriculum, you will possess a complete autonomous robotics stack:

```
Gazebo Simulation (Physics + Sensors)
   ├── 2D LiDAR → Obstacle Avoidance Node → /cmd_vel
   ├── Front Camera → OpenCV Color Segmentation
   ├── Front Camera → AprilTag Detection → TF Pose → Tag Follower Node → /cmd_vel
   ├── 5-Camera Array (Front Stereo Pair + Left/Right/Rear Monoculars) → 360° Vision
   ├── Front Stereo Pair → Stereo Disparity Node → PointCloud2 (Visual inspection)
   ├── Native Depth Camera → Depth Cloud Filter Node → Filtered PointCloud2 → OctoMap (3D Voxels in odom frame)
   ├── 2D LiDAR → slam_toolbox → 2D Occupancy Grid Map (map frame, loop closure)
   └── /cmd_vel ──┬──> Gazebo diff_drive plugin (Direct visual & physical movement)
                  └──> MAVROS → ArduPilot Rover SITL (Autonomous companion computer setpoint stream)
```

---

## Why Follow in This Order?

Each module requires a **functioning and tested** foundation from the previous one. For example, AprilTag tracking requires that camera streams and TF frames are already broadcasting properly. Skipping ahead risks encountering errors whose root causes were diagnosed and solved in earlier lessons.

---

## Quick Troubleshooting Guide

Stuck on a specific error? Refer to [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) for a comprehensive error diagnosis matrix featuring quick one-line solutions and direct links to the relevant modules.

---

## General Lessons Learned (Universal Patterns)

Keep these recurring patterns in mind throughout your robotics journey:

1. **Terminal Copy-Paste Issues:** When pasting multi-line snippets into the terminal, lines can sometimes get concatenated. Commands in this repository are formatted with `heredoc` or `printf` where possible to minimize this.
2. **Environment Changes (`.bashrc` / PATH):** When adding new environment variables, either run `source ~/.bashrc` or open a new terminal session.
3. **WSL2 Startup Latency:** Gazebo and initial compilation jobs can take longer on first launch; give the system a moment before assuming a hang.
4. **Always Verify with ROS 2 CLI Tools First:** When something seems unresponsive, diagnose before guessing: use `ros2 topic list`, `ros2 topic echo`, and `ros2 node list` to inspect active publishers and subscribers.

---

## License & Usage

This educational content is freely available for educational use, adaptation, and sharing. If you utilize it in a university course, internship, or competition rover project, attribution is appreciated!
