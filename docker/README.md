# Docker containers

After trying multiple scenarios of the [docker multistage
builds](https://docs.docker.com/develop/develop-images/multistage-build) and
tired because nothing worked. I've decided to split the containers into 2
separate ones. One will be mainly used to build the package(`builder`) and the
other one is the one you will most likely run locally, and thus you need to
build it by your own(`apps`).

## `builder` container

To actually build this container, in case you need to modify the base image or
because you don't have access to the registry provided, just run this command
from the `puma` root directory:

```sh
docker-compose up --build builder
```

That will build the base image and tag it with the same tag that the `apps`
container is using it. Ideally you should never do this unless you need to
change something from the dependencies.

If you plan to update the registry, you can do so by just running:

```sh
docker-compose push builder
```

## `apps` container

This container needs to be built locally since it will use information of your
current user. This looks tricky and complicated but it's the easiest way to
share data between the container and the host-machine without needing to run
unnecessary long commands.

Your user information is encoded in the [.env](../.env) file. If your user id
and group id are not `1000` (defaults in debian-based sytem) then you need to
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
docker-compose up --build apss
```
