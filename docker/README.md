# Docker containers

The easiest way to try out our code without pulling all the dependencies is
by running our docker container. For that, you need to install `docker` and
`docker-compose`.

## `builder` container

To build this container, in case you need to modify the base image or
because you don't have access to the registry provided, just run this command
from the `puma` root directory:

```sh
docker-compose up --build builder
```

That will build the base image and tag it with the same tag that the `apps`
container is using it. Ideally, you should never do this unless you need to
change something from the dependencies.

If you plan to update the registry, you can do so by just running:

```sh
docker-compose push builder
```

## `apps` container

This container needs to be built locally since it will use the information of your
current user. This looks tricky and complicated but it's the easiest way to
share data between the container and the host-machine without needing to run
unnecessary long commands.

Additionally, an env variable called `$DATASETS` is also shared with the docker
container in case you have your data already somewhere else and you don't want
to duplicate it on the [data](../apps/data) directory.

Your user information is encoded in the [.env](../.env) file. If your user-id
and group id are not `1000` (defaults in debian-based system) then you need to
change this file.

Using this container is trivial, plus it also comes packaged with nice tools
such as zsh, vim, etc:

```sh
docker-compose run --rm apps
```

If the base image(`builder`) is not there it will pull it from the registry. If
you can't access it, as said above, then you need to build it by hand.

Be aware that this will only build the `apps` container the very first time.
**Only** if you need to re-build it then you need to run:

```sh
docker-compose up --build apps
```

This will build a docker container with all the pre-packaged dependencies. The
`apps/` directory is shared between host and container, so there are 2 specific
folder [data](./apps/data) and [results](./apps/results) in there where you can
put your data and inspect the results (from both, host and container).
