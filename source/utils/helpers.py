import os
import shutil

def 

if not os.path.exists('tensorboard-final/'):
    os.makedirs('tensorboard-final/')


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
    closest_file = min(log_files, key=lambda x: abs(int(x.split('.')[3]) - int(time_now)))
    shutil.copy(os.path.join(tensorboard_path, closest_file), 'tensorboard-final/')
else:
    print("No log files found for the current hostname.")

print("Done!")

# Save the model
torch.save(model.state_dict(), "models/checkpoints/" + name + ".pth")
print("Saved PyTorch Model State to model.pth")