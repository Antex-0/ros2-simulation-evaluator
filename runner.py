import subprocess
import time
import os
import signal
import sys

def run_simulation(user_node_path, duration=15):
    """
    Launches Gazebo and the user's ROS2 node in a headless environment.

    1. Starts Xvfb (Virtual Monitor).
    2. Launches Gazebo.
    3. Runs the user's Python script.
    4. Cleans up processes after the duration ends.

    :param user_node_path: Path to the python script to run.
    :param duration: How long (in seconds) to run the simulation.
    """
    # ... existing code ...
    print("Starting simulation...")
    # Setup the Virtual Environment
    display_port = ":99"
    os.environ['DISPLAY'] = display_port
    
    print(f"1. Starting Virtual Display on {display_port}...")
    xvfb_process = subprocess.Popen(['Xvfb', display_port, '-screen', '0', '1024x768x24'], stdout = subprocess.PIPE, stderr = subprocess.DEVNULL)
    time.sleep(2)  # Give some time for Xvfb to start
    
    # 2. Launch Gazebo Simulator
    print("2. Launching Gazebo Simulator...")
    gazebo_cmd =['ros2', 'launch', 'gazebo_ros', 'gazebo.launch.py']
    gazebo_process = subprocess.Popen(gazebo_cmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, preexec_fn = os.setsid)
    time.sleep(5)  # Give some time for Gazebo to start
    
    # 3. Launch User Node
    print(f"3. Launching User Node from {user_node_path}...")
    log_file = open('simulation_log.txt', 'w')
    
    # Assuming user_node_path is a Python script for ROS2 node
    user_process = subprocess.Popen([ sys.executable, user_node_path], stdout = log_file, stderr = log_file, preexec_fn=os.setsid)
    
    # 4. Run for specified duration
    print(f"4. Running simulation for {duration} seconds...")
    time.sleep(duration)
    
    # 5. Cleanup
    print("5. Cleaning up...")
    os.killpg(os.getpgid(user_process.pid), signal.SIGTERM) # Terminate user process group
    os.killpg(os.getpgid(gazebo_process.pid), signal.SIGTERM)  # Terminate gazebo process group

    xvfb_process.terminate()  # Terminate Xvfb process
    log_file.close()
    
    print("Simulation ended. Logs are saved in simulation_log.txt")
    
if __name__ == "__main__":
    # Example usage
    test_node = "my_node.py"  # Replace with actual user node script path
    
    # Check if the user node script exists
    if not os.path.isfile(test_node):
        print(f"Error: The specified user node script '{test_node}' does not exist.")
    else:
        run_simulation(test_node, duration = 15)