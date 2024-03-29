# r2n-sncf-wc-projected-state
The purpose of this project is to estimate the water consumption needs of toilet sets for the [TER](https://en.wikipedia.org/wiki/Transport_express_r%C3%A9gional) [Regio 2N](https://en.wikipedia.org/wiki/Regio_2N) [SNCF](https://en.wikipedia.org/wiki/SNCF) fleet on a set of missions carried out by these trains.

Knowing the water needs, we can forecast refueling needs more accurately and limit the immobilization of the trains due to lack of water.

## Libraries install
You must install the numpy, pandas, progress, pyarrow, python-dateutil, pytz, six, PySide6, snappy, spherogram, psycopg2, matplotlib and seaborn libraries.
```
python -m pip install numpy>=1.23.4 pandas>=1.5.1 progress>=1.6 pyarrow>=10.0.0 python-dateutil>=2.8.2 pytz>=2022.6 six>=1.16.0 PySide6~=6.4.2 snappy>=3.0.3 spherogram>=2.1 psycopg2>=2.9.6 matplotlib>=3.7.1 seaborn>=0.12.2
```

## Setup
The project has been tested with [Python 3.10.9](https://www.python.org/downloads/release/python-3109/).
You have to:
1. Git clones the project
2. Fill in the path to which you want to create the software workspace in the file `./src/ProjectRootPath.py`, variable  `self.__project_path` (referenced as `project_root` below)
> **Warning** The directory must have backslash separators, for example `C:\Users\Bernard\Documents\WC_R2N_TER`
3. Launch the software to allow the creation of folders
4. Place data folders in `project_root\Data\Parquet\Source`
> **Note** data folders should be named as follow: 
```
<train_id[z55xxxxx]>_<date[yyyymmdd]>_<time[hhmmss]>_<data_folder_id(from 0 to n)>`, eg: `z5500503_20221107_131914_0`
```
5. Launch the software and see for merged folders (only feature available at the moment) in `project_root\Data\Parquet\Edited`
6. You will see an error like `Constants.USER = line.split(": ")[1].strip()` in your console. This error is normal. You need to configure the conenction informations of the postgreSQL database. To do that:
   - Find the repository of the `r2n-sncf-wc-projected-state` project and go to his parent folder
   - You will find a text file named `Configuration postgreSQL`. Open it and fill in the informations. Then save it
   - Relaunch the software
     - If one ore more information is incorrect you will see an error with the `cursor`. See logs for details

## Tips
Launch the software from a terminal to ensure the visualization of data processing progress bars, via
```
python main.py
```
