# VoltPop Announce

A Flask based webhook target with Redis PubSub

## About:

The vp-announce service is a docker-containerized, easy-to-configure, easy-to-deploy pubsub solution with a Redis backend.

This solution (optionally) depends on the [Official Redis DocherHub image](https://hub.docker.com/\_/redis), to deploy a docker-compose managed instance. While not necessary, it  _is_ this architecture that was had in mind during the conception and development of this solution.

### Configuration

This solution currently leverages the `pipenv` mechanism to several ends:
* pipenv ENVVARS in the container environment are inherited by docker-compose via `.env`.
  * The file `service.cfg` is symbolically linked to `.env` in the root of the repository.

#### Required ENVVARS

Hard configurables (those pertaining to the physical server) are defined in `service.cfg`.

* VP_WEBHOST_PORT   // Webhost port 
* VP_REDIS_MAP_PORT // Local port, to which redis is mapped
* VP_REDIS_HOST     // Host to which announce.py will publish messages.

#### The announce.yml config file

The announce.yml file is a file containing web configurables including:
  * sqlite3 database file
  * announcer channel configuration 


Redis Channels are defined by adding additional entries to the channels list in the following format

```
announcer:
  channels:
    channelName:
      enabled: bool (required)
      queryable: bool (required)
      security: bool (optional)
      secure_token: <str> (optional)
```

### Deployment

The provided redis component is not neccary for the functioning of vp-announce.py. If it's not needed, skip the `docker-compose` step

#### Deploying the Redis Component
```
pipenv run docker-compose up -d
```

#### Starting the announcer service
```
pipenv run python3 announce.py
```

pipenv is ***REQUIRED*** due to the containerized configuration contained in `service.cfg`.


