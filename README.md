# NCKU-FEED-Backend

Backend of NCKU FEED web app.

## About The Project

Project description.

## Getting Start

#### 1. Using docker

##### Prerequisites

Install docker. More information [here](https://docs.docker.com/get-docker/).

##### Using docker compose to build image and run

```
docker compose -f Docker-compose.dev.yaml up --build
```

#### 2. Using venv

##### Prerequisites

Install python 3.8. More information [here](https://www.python.org/downloads/).

##### Installation and Run

* Step 1: Install virtualenv
  ```
  pip install virtualenv
  ```
* Step 2: Create a virtual environment
  ```
  python -m venv env
  ```
* Step 3: Activate virtual environment
  1. Windows Powershell
     ```
     ./env/Scripts/Activate.ps1
     ```
  2. Windows cmd
     ```
     .\env\Scripts\activate.bat
     ```
  3. Linux and MacOS
     ```
     source env/bin/activate
     ```
* Step 4: Install packages
  ```
  pip install -r requirements.txt
  ```
* Step 5: Run the program
  1. Set the environment variables
     * FLASK_APP=run.py
     * FLASK_ENV=development
  2. Run flask
     ```
     flask --debug run --host 0.0.0.0
     ```
