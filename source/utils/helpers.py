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
        parts = f.split('.')
        # Erzeugt eine temporäre Liste ohne die ersten 3 Elemente und die letzten 2 Elemente
        # Annahme: Die ersten 3 Teile sind nicht Teil des Hostnamens und die letzten 2 Teile sind die ID und die Erweiterung
        temp_parts = parts[3:-2]
        # Wieder zusammensetzen und prüfen, ob der Hostname enthalten ist
        temp_hostname = '.'.join(temp_parts)
        if hostname in temp_hostname:
            log_files.append(f)
    # If there are log files for the current hostname, copy the log file with the closest timestamp to the current time
    if len(log_files) > 0:
        # Find the log file with the closest timestamp to the current time
        closest_file = min(log_files, key=lambda x: abs(int(x.split('.')[3]) - int(timestamp)))
        shutil.copy(os.path.join(tensorboard_path, closest_file), destination_path)
    else:
        print("No log files found for the current hostname.")