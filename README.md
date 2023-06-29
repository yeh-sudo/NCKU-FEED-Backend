# NCKU-FEED-Backend

Backend of NCKU FEED web app.

## About The Project

Project description.

## Getting Start

#### 1. Using docker

##### Prerequisites

Install docker. More information [here](https://docs.docker.com/get-docker/).

##### Installation and Run

* Step 1: Build the image

  ```
  docker build -f Dockerfile.dev -t USERNAME/flask-app .
  ```
* Step 2: Run the image in docker container

  1. Windows Powershell
     ```
     docker run -it -v ${pwd}:/flask-app -p 5000:5000 USERNAME/flask-app
     ```
  2. Windows cmd
     ```
     docker run -it -v %cd%:/flask-app -p 5000:5000 USERNAME/flask-app
     ```
  3. Linux and MacOS
     ```
     docker run -it -v $(pwd):/flask-app -p 5000:5000 USERNAME/flask-app
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
