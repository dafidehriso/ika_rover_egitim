# Module 1: WSL2 + ROS 2 + Gazebo Setup

> 🌐 **Language / Dil:** **English** | [Türkçe Sürüm (README.md)](README.md)

## Why WSL2 and Not Docker?

A 3D robotics simulator like Gazebo requires a **graphical user interface (GUI)**. Because standard Docker containers lack a display server out of the box, rendering GUIs usually requires setting up third-party X servers (such as VcXsrv) alongside fragile network and display configuration.

On Windows 11, there is a much cleaner, native solution: **WSL2 + WSLg**. WSLg is built directly into Windows 11, allowing Linux GUI applications to render seamlessly as native desktop windows without extra configuration or manual display forwarding.

---

## Step 1: Installing WSL2 + Ubuntu 22.04

Open PowerShell **as Administrator** and run:

```powershell
wsl --install -d Ubuntu-22.04
```

**Why Ubuntu 22.04 (Jammy)?** ROS 2 Humble officially targets Ubuntu 22.04 LTS. Using any other Ubuntu version will lead to obscure dependency conflicts and missing precompiled binaries down the road.

### 🐛 Issue: "Sorry, passwords do not match"

When typing passwords in Linux terminals, **characters are not echoed to the screen** (not even asterisks). This is standard UNIX security behavior, but it makes typing errors easy.

**Solution:** Type slowly and deliberately. If you get locked out or mistype repeatedly, launch WSL as root from Windows PowerShell to reset your user password:

```powershell
wsl -d Ubuntu-22.04 -u root
```

Inside the root shell, execute: `passwd <your_username>`

### 🐛 Issue: Syntax Error in `.bashrc`

When appending directories to your `PATH` variable, you may run into an error like:

```
-bash: /home/user/.bashrc: line 123: syntax error near unexpected token `('
```

**Why does this happen?** WSL automatically inherits the host Windows `PATH`. Windows paths frequently include spaces and parentheses (e.g. `C:\Program Files (x86)\...`). When appended unquoted, bash interprets the parenthesis as command syntax.

**Solution:** Always enclose PATH exports in double quotes:

```bash
export PATH="$PATH:$HOME/ardupilot/Tools/autotest:$HOME/.local/bin"
```

---

## Step 2: Installing ROS 2 Humble

```bash
# 1. Configure UTF-8 Locale (ROS 2 requires UTF-8)
sudo apt update && sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

# 2. Enable the Ubuntu Universe repository
sudo apt install software-properties-common -y
sudo add-apt-repository universe

# 3. Add the ROS 2 official GPG key
sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# 4. Add the ROS 2 apt repository to sources list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 5. Install ROS 2 Desktop
sudo apt update && sudo apt install ros-humble-desktop -y

# 6. Automatically source ROS 2 setup in new shells
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Verification

```bash
printenv ROS_DISTRO   # Must output: humble
```

Verify communication using the classic publisher/subscriber demo across two terminal tabs:

```bash
# Terminal 1: Publisher
ros2 run demo_nodes_cpp talker

# Terminal 2: Subscriber
ros2 run demo_nodes_py listener
```

If messages published by the talker appear in the listener, your ROS 2 middleware and networking layer are functioning properly.

---

## Step 3: Installing Gazebo Classic

```bash
sudo apt install ros-humble-gazebo-ros-pkgs -y
gazebo
```

Thanks to WSLg, the Gazebo GUI will launch directly as a native Windows application window.

### 🐛 Issue: `colcon: command not found`

The `colcon` build tool used for compiling ROS 2 workspace packages is not bundled with `ros-humble-desktop`.

**Solution:**

```bash
sudo apt install python3-colcon-common-extensions -y
```

### ⚠️ Simulator Version & Gazebo Classic EOL Notice
This curriculum uses **Gazebo Classic 11.10.2** (`gazebo_ros_pkgs`).
- Gazebo Classic officially reached End-of-Life (EOL) in January 2025.
- However, across universities, competition teams (e.g. URC/ERC), and industrial codebases, Gazebo Classic SDF models remain dominant and reliable on Ubuntu 22.04 + ROS 2 Humble. This course provides a rock-solid, fully tested baseline on this stack.
- For new long-term commercial deployments, transitioning to Modern Gazebo (Gazebo Sim / Harmonic) is recommended; a migration guide is planned for future iterations.

---

## Key Lessons from This Module

- **`.bashrc` changes do not automatically update running shells:** Always run `source ~/.bashrc` or open a new terminal after editing environment variables.
- Keystrokes are sent exclusively to the **active terminal window**—always verify which terminal has focus.
- Initial startups in WSL2 (particularly 3D rendering engines like Gazebo) may take a few moments on the first run.

---

## Next Up

[Module 2: Design Your Own Robot](../02-kendi-robotunuzu-tasarlayin/README_EN.md) — After testing standard models, we will build a custom differential-drive robot model from scratch using the SDF format.
