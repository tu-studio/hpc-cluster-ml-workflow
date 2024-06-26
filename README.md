# ml-training-pipeline

This repository provides a comprehensive template for the management of reproducible pipelines for machine learning training in the context of audio. The template is utilizing [DVC](https://dvc.org/) (data version control) and is adjusted for experiments on the Remote SLURM-Cluster [HPC cluster of the Technical University of Berlin](https://www.tu.berlin/campusmanagement/angebot/high-performance-computing-hpc).

## Features


## Install and Setup

```
git clone https://github.com/tu-studio/dataset-pipeline-template
```


Create and setup a virtual environment inside the repository. If you chose a different name than *myenv* make sure to add the directory name of your venv to the .gitignore.


```
cd ml-training-pipeline

python3 -m venv myenv

source myenv/bin/activate

pip install -r requirements.txt
```


Initiliase a dvc repository.

```
dvc init
```

Add a WebDAV server as remote storage to your dvc repository. 

```
dvc remote add -d myremote webdavs://tubcloud.tu-berlin.de/remote.php/dav/files/cf531c5e-2043-103b-8745-111da40a61ee/DVC
```

Add your username and password for server acces to a private config file (will be ignored by git).

```
dvc remote modify --local myremote user 'yourusername'

dvc remote modify --local myremote password 'yourpassword'

dvc remote modify myremote ask_password true
```

Add the raw data folder to the dvc repository.

```
dvc add data/raw
```


## Usage



## Contributors

- [Michael Witte](https://github.com/michaelwitte)
- [Fares Schulz](https://github.com/faressc)

## License

