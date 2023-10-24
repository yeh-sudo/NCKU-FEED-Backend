# NCKU-FEED-Backend

Backend of NCKU FEED web app.

## About The Project

Project description.

## Getting Start

* Prerequisites

  Install docker. More information [here](https://docs.docker.com/get-docker/).

* Using docker compose to build image and run

  ```
  docker-compose -f ./Dockerfiles/Docker-compose.yaml up --build
  ```

## Test
  1. Check with Pylint
      ```
      pip install pylint && pylint ./app
      ```
  2. Unit tests and integration tests
      ```
      docker-compose -f ./Dockerfiles/Docker-compose-test.yaml up --build --exit-code-from server-test
      ```