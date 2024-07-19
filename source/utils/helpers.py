import os
import shutil

def copy_tensorboard_log(tensorboard_path, hostname, timestamp) -> None:

    experiment_name = os.environ.get('DVC_EXP_NAME')
    if experiment_name is None:
        raise EnvironmentError(r"The environment variable 'DVC_EXP_NAME' is not set.")

    destination_path = os.path.join('exp-logs/tensorboard', experiment_name)

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # Check if there are log files for the current hostname and append them to a list
    log_files = []
    for f in os.listdir(tensorboard_path):
        if f.startswith('events.out.tfevents'):
            parts = f.split('.')
            temp_parts = parts[3:-2]
            temp_hostname = '.'.join(temp_parts)
            if hostname in temp_hostname:
                log_files.append(f)
    # If there are log files for the current hostname, copy the log file with the closest timestamp to the current time
    if len(log_files) > 0:
        # Find the log file with the closest timestamp to the current time, timestamp before SummaryWriter creation
        closest_file = min(log_files, key=lambda x: int(x.split('.')[3]) - int(timestamp))
        shutil.copy(os.path.join(tensorboard_path, closest_file), destination_path)
    else:
        print("No log files found for the current hostname.")

    print(f"Tensorboard log {closest_file} copied to {destination_path}")