# reportWriterDemo

This project is a demonstration of how the latex report writer library can be used. 

## Getting Started

To start, initialize this repo with `make firstRun`.
An example has been created under `src/modules/module1`. There are 2 functions: to create data, and to structure the data in the report.

## Prerequisites

You will need to have a valid Python installation on your system. This has been tested with Python 3.6. It does not assume a particulay version of python, however, it makes no assertions of proper working, either on this version of Python, or on another.

You will need to have LaTeX installed. 

## Installing

The folloiwing installations are for \*nix-like systems. This is currently tested in the following system: `Ubuntu 18.10`. 

For installation, first close this repository, and generate the virtual environment required for running the programs. 

This project framework uses [venv](https://docs.python.org/3/library/venv.html) for maintaining virtual environments. Please familiarize yourself with [venv](https://docs.python.org/3/library/venv.html) before working with this repository. You do not want to contaminate your system python while working with this repository.

A convenient script for doing this is present in the file [`bin/vEnv.sh`](../blob/master/bin/vEnv.sh). This is automatically do the following things:

1. Generate a virtual environment
2. activate this environment
3. install all required libraries
4. deactivate the virtual environment and return to the prompt. 

At this point you are ready to run programs. However, remember that you will need to activate the virtual environment any time you use the program.

For activating your virtual environment, type `source env/bin/activate` in the project folder in [bash](https://www.gnu.org/software/bash/) or `source env/bin/activate.fish` if you are using the [fish](https://fishshell.com/) shell.
For deactivating, just type deactivate in your shell

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

 - Python 3.6

## Contributing

Please send in a pull request.

## Authors

Geraldine Pang - Initial work (2019)

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details

## Acknowledgments

 - Hat tip to anyone who's code was used
 - Inspiration
 - etc.
 
