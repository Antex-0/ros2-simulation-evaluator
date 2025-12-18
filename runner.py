import subprocess
import time
import os
import signal
import sys

def run_sim(node_path):
    print('--- SIMULATION RUNNER STARTING ---')

    # 1. Setup Environment Variables
    # PYTHONUNBUFFERED=1 is crucial. It forces Python to print logs immediately
    # instead of holding them in memory (which causes empty log files).
    env = os.environ.copy()
    env['DISPLAY'] = ':99'
    env['PYTHONUNBUFFERED'] = '1'

    # 2. Start Virtual Monitor (Xvfb)
    print('1. Starting Xvfb (Virtual Monitor)...')
    xvfb = subprocess.Popen(
        ['Xvfb', ':99', '-screen', '0', '1024x768x24'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2) # Wait for it to initialize

    # 3. Start Gazebo
    print('2. Starting Gazebo...')
    # os.setsid creates a new process group so we can kill Gazebo cleanly later
    gz = subprocess.Popen(
        ['ros2', 'launch', 'gazebo_ros', 'gazebo.launch.py'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
        env=env
    )
    time.sleep(5) # Wait for Gazebo to load

    # 4. Run User Node (With Logging)
    print(f'3. Running User Node: {node_path}...')
    
    with open('simulation_log.txt', 'w') as log_file:
        # Write a header to verify file permissions work
        log_file.write(f'--- SIMULATION LOG START ---\n')
        log_file.write(f'Target Node: {node_path}\n')
        log_file.flush() # Force write to disk immediately

        user_process = None
        try:
            # Run the node using python3 -u (Unbuffered mode)
            user_process = subprocess.Popen(
                [sys.executable, '-u', node_path],
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setsid,
                env=env
            )

            # Let it run for 15 seconds
            print('   -> Simulation running for 15s...')
            time.sleep(15)

        except Exception as e:
            log_file.write(f'\nCRITICAL RUNNER ERROR: {str(e)}\n')
        finally:
            print('4. Stopping processes...')
            # Kill the user node group if it exists
            if user_process:
                try:
                    os.killpg(os.getpgid(user_process.pid), signal.SIGTERM)
                except:
                    pass

            # Kill the Gazebo group
            try:
                os.killpg(os.getpgid(gz.pid), signal.SIGTERM)
            except:
                pass

    # Kill Xvfb
    xvfb.terminate()
    print('--- SIMULATION COMPLETE ---')

if __name__ == '__main__':
    # Accept the node path as an argument (passed from app.py)
    # Default to 'my_node.py' if no argument provided
    target_node = sys.argv[1] if len(sys.argv) > 1 else 'my_node.py'
    
    if os.path.exists(target_node):
        run_sim(target_node)
    else:
        print(f"Error: Node file '{target_node}' not found.")
        # Create a dummy log so the website shows the error
        with open('simulation_log.txt', 'w') as f:
            f.write(f"Error: Could not run simulation.\nFile '{target_node}' does not exist.")