# VoltPop Announce

A Flask based webhook target with Redis PubSub

## About:

The vp-announce service is a containerized, easy-to-configure, easy-to-deploy pubsub solution.

This solution optionally depends on the [Official Redis DocherHub image](https://hub.docker.com/\_/redis), to deploy a docker-compose managed instance.

### Configuration

This solution currently leverages the `pipenv` mechanism to set ENVVARS in the container environment. The file `announce.cfg` is symbolically linked to `.env` in the root of the repository. This exports the configuration details into the container environment for `vp-announce`.

Currently, vp-announce requires three configured items:
* VP_WEBHOST_PORT   // Webhost port 
* VP_REDIS_MAP_PORT // Local port, to which redis is mapped
* VP_REDIS_HOST     // Host to which announce.py will publish messages.

### Deployment

The provided redis component is not neccary for the functioning of vp-announce.py. If it's not needed, skip the `docker-compose` step

#### Deploying the Redis Component
```
pipenv run docker-compose up --detach;
```

#### Starting the announcer service
```
pipenv run python3 announce.py
```


pipenv is ***REQUIRED*** due to the containerized configuration contained in `announce.cfg`.


