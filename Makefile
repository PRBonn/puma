.PHONY: container check-env check-config
.DEFAULT_GOAL:= container

export USER_ID:=$(shell id -u)
export GROUP_ID:=$(shell id -g)

container: check-env check-config
	@echo Building apps container with user_id=${USER_ID} group_id=${GROUP_ID}...
	docker-compose build apps
	@echo You can run \"make run\" to test the docker installation now.

check-config:
	@echo Using the following docker configuration:
	@docker-compose config

run: check-env
	@docker-compose run --rm apps

clean:
	@echo Removing docker images...
	-docker image rm ignaciovizzo/puma:latest
	-docker image rm ignaciovizzo/puma_apps:latest

check-env:
ifndef DATASETS
	$(error Please specify where your datasets are located, export DATASETS=<path>)
else
	@echo Mounting\(read-only \) ${DATASETS} to /data.
	@echo Mounting\(read-write\) $(shell realpath apps/) to /apps/
	@echo uid=${USER_ID}, gid=${GROUP_ID}.
endif
