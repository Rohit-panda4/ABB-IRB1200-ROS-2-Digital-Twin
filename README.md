# ABB IRB1200 ROS 2 Digital Twin

## Introduction

### Project Introduction

We are building a ROS 2 Humble digital twin of an ABB IRB1200 palletizing cell with a Robotiq 2F-140 gripper, using MoveIt 2, RViz, and fake hardware inside an Ubuntu VirtualBox setup. So far, the workspace is built successfully, the ABB robot model and gripper are integrated and visible in RViz, the pallet/table/box environment is being published, and arm planning works correctly. We also fixed the OMPL planning configuration so Motion Planning loads properly, but we are still debugging the gripper motion because its open/close behavior can overlap or fail under some planning states.

## Prerequisites

**Ubuntu 22.04**  
This is the base operating system for the whole project. ROS 2 Humble is best supported on Ubuntu 22.04, so using this version avoids package and compatibility issues.

**ROS 2 Humble**  
This is the core robotics middleware. It provides node communication, topics, services, actions, parameters, and the whole framework that your ABB robot, MoveIt, and scene publisher use to talk to each other.

**RViz2**  
This is the 3D visualization tool. You use it to see the ABB robot model, the gripper, the palletizing scene, interactive markers, and motion plans.

**MoveIt 2**  
This is the motion planning framework. It calculates safe robot trajectories, checks collisions, and lets you plan and execute arm and gripper motions.

**Colcon**  
This is the build tool for ROS 2 workspaces. It compiles your packages and creates the install/ space that ROS uses when you source the workspace.

**Git**  
This is used for version control and for pushing your project to GitHub.

**Terminator**  
This is your terminal manager. You use it because your workflow needs multiple terminals at the same time:
- one for robot control
- one for MoveIt + RViz
- one for scene objects
- one for controller verification

**Python 3 and ROS Python packages**  
These are needed for your custom scene publisher node and for ROS 2 Python-based scripts.

**ABB-related packages**  
Robot description, support files, MoveIt config, controller setup, and launch files for the IRB1200: `abb_libegm`, `abb_librws`, `abb_rapid_msgs`, `abb_egm_msgs`, `abb_egm_rws_managers`, `abb_robot_msgs`, `abb_rapid_sm_addin_msgs`, `abb_resources`, `abb_hardware_interface`, `abb_ros2`, `abb_bringup`, `abb_rws_client`, `abb_cell_setup`, `abb_irb1200_support`, `abb_irb1200_5_90_moveit_config`, `abb_irb4600_support`.

**Robotiq gripper packages**  
Gripper model, control interface, and integration with the ABB wrist: `robotiq_description`, `robotiq_driver`, `robotiq_controllers`, `robotiq_hardware_tests`.

## Installation and Setup Guide

### 1. Clone Your GitHub Repo

On the new PC, create your workspace folder and clone the repository.

```bash
mkdir -p ~/abb_ws/src
cd ~/abb_ws/src
git clone https://github.com/Rohit-panda4/ABB-IRB1200-ROS-2-Digital-Twin.git
```

This downloads your project from GitHub to the new machine.

### 2. Build the Workspace

After cloning, go to the workspace root and build it.

```bash
cd ~/abb_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-skip robotiq_driver robotiq_controllers robotiq_hardware_tests
```

This resolves dependencies and compiles all packages in the workspace.

### 3. Source the Workspace

After every new terminal or after every build, source ROS and your workspace.

```bash
source /opt/ros/humble/setup.bash
source ~/abb_ws/install/setup.bash
```

This makes the ROS 2 packages and your custom workspace available in the terminal.

## Running the Simulation

### Running the Project Using Four Terminal Panes

Launch the project using four separate terminal panes in Terminator. It is strongly recommended to follow the execution order exactly as described below, since each terminal is responsible for a specific subsystem of the digital twin environment.

![Four Terminal Panes Setup](ROS%20screen%20Shots/Image%201.png)

**The startup sequence is important because:**

- Terminal 1 initializes the robot controllers and hardware interface.
- Terminal 2 launches MoveIt 2 and RViz for planning and visualization.
- Terminal 3 publishes the workspace objects and updates the planning scene.
- Terminal 4 is used to verify that all controllers are running correctly.

### Terminal 1 — Robot Control Stack

This terminal initializes the ABB robot control layer and starts the required controllers.

```bash
source /opt/ros/humble/setup.bash
source ~/abb_ws/install/setup.bash
ros2 launch abb_bringup abb_control.launch.py \
  description_package:=abb_irb1200_support \
  description_file:=irb1200_5_90.xacro \
  launch_rviz:=false \
  moveit_config_package:=abb_irb1200_5_90_moveit_config \
  use_fake_hardware:=true
```

**Purpose**

This launch process performs the following tasks:

- Starts the ROS 2 controller manager
- Loads the ABB arm controller
- Loads the gripper controller
- Initializes the fake hardware interface
- Publishes robot joint states

**Why This Terminal Is Required**

Without the control stack running, MoveIt 2 cannot communicate with or command the robot model.

### Terminal 2 — MoveIt 2 and RViz Visualization

This terminal launches the motion planning and visualization environment.

```bash
source /opt/ros/humble/setup.bash
source ~/abb_ws/install/setup.bash

ros2 launch abb_bringup abb_moveit.launch.py \
  robot_xacro_file:=irb1200_5_90.xacro \
  support_package:=abb_irb1200_support \
  moveit_config_package:=abb_irb1200_5_90_moveit_config \
  moveit_config_file:=abb_irb1200_5_90.srdf.xacro
```

**Purpose**

This process:

- Launches the move_group planning node
- Opens RViz 2
- Loads the ABB IRB1200 robot model
- Enables the Motion Planning interface
- Connects MoveIt 2 with the active controllers

**Why This Terminal Is Required**

This environment is used to:

- Visualize the robot
- Plan trajectories
- Execute robot motions
- Interact with the digital twin system

![RViz and Scene Publisher](ROS%20screen%20Shots/Image%202.png)

### Terminal 3 — Environment and Scene Objects

This terminal publishes the workspace objects into the planning scene.

```bash
source /opt/ros/humble/setup.bash
source ~/abb_ws/install/setup.bash

ros2 run abb_cell_setup scene_objects
```

**Purpose**

This node publishes the environment elements, including:

- Pallet structures
- Tables
- Boxes and obstacles
- Additional planning scene objects

**Why This Terminal Is Required**

Without the environment objects, the robot would plan trajectories in an empty workspace, making collision-aware planning impossible. This terminal enables realistic palletizing and workspace interaction inside RViz.

![Scene Objects Published](ROS%20screen%20Shots/Image%203.png)

### Terminal 4 — Controller Verification and Diagnostics

This terminal is used to verify the operational state of the controllers.

```bash
source /opt/ros/humble/setup.bash
source ~/abb_ws/install/setup.bash

ros2 control list_controllers
```

**Purpose**

This command:

- Lists all active ROS 2 controllers
- Displays controller states
- Confirms successful controller initialization

**Why This Terminal Is Required**

This acts as a quick system health check before motion execution. You should verify that:

- The arm controller is active
- The gripper controller is active
- No controller remains in an unconfigured or inactive state

## Project Structure and Workflow

### Project structure

Your repository is built around one ROS 2 workspace that contains the ABB robot, the MoveIt configuration, the gripper, and your custom scene publisher. The core idea is: the robot model defines the digital twin, MoveIt handles planning, `ros2_control` handles execution, and your scene node adds the palletizing environment.

### Main folders and what they do

`abb_ros2/` — Main ABB robot package set. Contains the robot description, support files, controller integration, launch files, and MoveIt-related config for the IRB1200. This is the heart of the digital twin for the arm.

`abb_irb1200_support/` — Holds the URDF/Xacro robot model and supporting links/joints. Includes the robot geometry, joint definitions, and gripper attachment points. This is what RViz uses to draw the robot.

`abb_irb1200_5_90_moveit_config/` — Holds MoveIt 2 configuration. Includes SRDF, OMPL planning config, controller config, and planning scene setup. This is what lets the arm and gripper plan motion.

`abb_bringup/` — Contains launch files. One launch file starts the robot control stack. Another starts MoveIt and RViz.

`abb_cell_setup/` — Your custom package. Publishes the pallet, table, and boxes into the planning scene. This is what makes the project look like a real palletizing cell.

`ros2_robotiq_gripper/` — Contains the Robotiq gripper model and control integration. Provides the gripper URDF, `ros2_control` definitions, and mimic joint setup.

`build/`, `install/`, `log/` — Auto-generated by `colcon`. `build/` stores build files, `install/` stores runnable ROS package outputs, and `log/` stores build logs.

### Main nodes used

- `ros2_control_node` — Starts the controller manager; loads and activates the robot and gripper controllers. In this project it manages both the ABB arm and the Robotiq gripper.
- `robot_state_publisher` — Reads the robot description and publishes TF transforms so links appear correctly in RViz and update based on joint states.
- `joint_state_broadcaster` — Publishes the current joint states of the robot so MoveIt and RViz know the robot pose.
- `joint_trajectory_controller` — Receives planned arm trajectories and sends them to the (fake) hardware interface.
- `gripper_controller` — Controls the Robotiq finger joint(s) for open/close commands.
- `move_group` — The main MoveIt planning node; handles planning, collision checking, planning requests, and trajectory generation.
- `rviz2` — The visualization node for interacting with the robot, planning UI, and executing trajectories.
- `scene_objects` — Your custom node from `abb_cell_setup` that publishes the palletizing environment (table, pallet, boxes) into the planning scene.
- `static_transform_publisher` — Publishes fixed transforms such as `world -> base_link` to provide a fixed reference frame.

![Scene and TF Example](ROS%20screen%20Shots/Image%205.png)

### How the nodes work together

The flow is basically:

1. `robot_state_publisher` publishes robot link transforms.
2. `ros2_control_node` manages controllers and hardware interface.
3. `joint_state_broadcaster` publishes joint states produced by controllers.
4. `move_group` reads joint states and computes motion plans (using MoveIt / OMPL).
5. `rviz2` lets the user visualize and request plans via the Motion Planning UI.
6. `scene_objects` adds the table, pallet, and boxes to the planning scene so planning is collision-aware.
7. `joint_trajectory_controller` and `gripper_controller` execute the planned arm and gripper commands on the (fake) hardware interface.

So the system behaves like a digital twin: the robot is visualized, planned, and driven through software without needing physical hardware.

## Outcomes

![Outcomes](ROS%20screen%20Shots/Image%204.png)

We’ve achieved a solid working digital twin foundation for the ABB IRB1200 project. The workspace builds successfully, the robot model loads in RViz, arm planning works correctly, the Robotiq gripper is integrated and visible, and the palletizing scene with table, pallet, and boxes is being published. We also fixed the major OMPL planning configuration issue, so MoveIt now starts and plans properly for the arm.
