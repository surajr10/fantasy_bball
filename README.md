# fantasy_bball

### Setup
1. ```conda create -n fantasy -f environment.yml``` should create a conda env with the necessary dependencies.
    2. Once already installed, ```mamba env update -n fantasy -f environment.yml``` to stay up-to-date 
        * [mamba ](https://github.com/mamba-org/mamba) is a faster dependency resolver for conda, updating/installing conda packages in an existing env is excruciatingly slow otherwise.
2. ```league.py``` is main entry point for ESPN League data currently, but requires a config.json with the necessary cookies to work correctly (hmu)