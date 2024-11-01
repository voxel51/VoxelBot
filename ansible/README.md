# Ansible Automation For Docker Compose Systems

In order to provide a GitOps
flow for docker compose, we wrote a suite of ansible tooling
to be triggered via GitHub actions.

This automation includes a few task sets:

1. A task set to log in to GCP and internal docker registries
1. A task set to deploy our docker compose stacks. This includes:
      1. Ensuring there is a `.env` file either in google secrets manager
         or on disk for the stack to use.
      1. Ensuring the ansible user is part of the `docker` linux group.
      1. Bringing up the docker compose stack

## Variables

Host variables are documented and defaulted in [this](group_vars/all.yaml) file.

## Running

You can run locally via the `ansible-playbook` command.
You can set your hosts via the command line via the `ANSIBLE_HOST_OR_GROUP`
environment variable.

A list of environment variables:

* `DOCKER_REGISTRY` - The registry to pull images from
* `GCP_COMPUTE_SERVER_NAME` - The ansbile host or group to deploy to
* `GCP_SM_KEY` - The GCP secret with .env file contents
* `TAG` - The image tag to deploy

An example:

```shell
export DOCKER_REGISTRY="us.gcr.io/.../..."
export GCP_COMPUTE_SERVER_NAME=some-server-name
export GCP_SM_KEY="some-key-name"
export TAG="abc123"
ansible-playbook main.yml
```
