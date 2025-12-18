# ROS 2 Code Checker & Simulation Runner

## Overview
This tool allows developers to upload ROS 2 (Python) packages, validates their structure and code safety, and runs them in a headless Gazebo simulation environment.

## Features
- **Static Analysis:** Checks for `package.xml`, `setup.py`, and syntax errors (Flake8).
- **Safety Checks:** Detects infinite loops without sleep commands.
- **Simulation:** Runs the node in a Dockerized Gazebo environment and captures logs.
- **Web Interface:** Simple UI for uploading and viewing results.

## Project Structure
- `app.py`: Flask backend handling file uploads and execution.
- `checker.py`: Script that validates the ROS package structure and syntax.
- `runner.py`: Script that launches Xvfb, Gazebo, and the user node.
- `Dockerfile`: Defines the ROS 2 Humble environment.
- `docs/`: Sphinx documentation.

## Setup Instructions

### Prerequisites
- Docker Desktop installed and running.

### Installation
1. Clone this repository:
   ```bash
   git clone <YOUR_GITHUB_REPO_URL>