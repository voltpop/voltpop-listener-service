# VoltPop Announce

A flask based webhook target with PubSub

## Development
`pipenv shell` will start an interactive shell for development.

## Running
adjust / start the redis container using `docker-compose up` in the root of the directory.
from there `pipenv run python3 vp-announcer.py` will run the announcer webhook service.
