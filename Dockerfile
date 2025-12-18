# Use ROS2 Humble
FROM osrf/ros:humble-desktop-full

# Avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    xvfb \
    mesa-utils \
    cppcheck \
    ros-humble-gazebo-ros-pkgs \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip3 install flask flake8

# Create workspace
RUN mkdir -p /root/user_workspace/src
WORKDIR /workspace

# Setup ROS environment
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc