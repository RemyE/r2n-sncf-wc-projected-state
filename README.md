# r2n-sncf-wc-projected-state
The purpose of this project is to estimate the water consumption needs of toilet sets for the [TER](https://en.wikipedia.org/wiki/Transport_express_r%C3%A9gional) [Regio 2N](https://en.wikipedia.org/wiki/Regio_2N) [SNCF](https://en.wikipedia.org/wiki/SNCF) fleet on a set of missions carried out by these trains.

Knowing the water needs, we can forecast refueling needs more accurately and limit the immobilization of the trains due to lack of water.

## Libraries install
You must install the pandas, progress and pyarrow libraries
```
pip install pandas progress pyarrow
```

## Setup
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

## Tips
Launch the software from a terminal to ensure the visualization of data processing progress bars, via
```
python main.py
```
