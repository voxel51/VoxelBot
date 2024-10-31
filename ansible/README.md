# Ansible Automation For Docker Compose Systems

In order to provide a GitOps
flow for docker compose, we wrote a suite of ansible tooling
to be triggered via GitHub actions.

This automation includes a few task sets:

1. A task set to perform any `git pull` / `git fetch` / `git checkout`
   actions for the fiftyone-teams-app-deploy repository.
   This includes:
      1. Cloning the repository
      1. Setting it a shared group repository
      1. Making it writeable to the `fiftyone` linux group
1. A task set to log in to GCP and internal docker registries
1. A task set to deploy our docker compose stacks. This includes:
      1. Ensuring there is a `.env` file either in google secrets manager
         or on disk for the stack to use.
      1. Ensuring there is a `license` file either in google secrets manager
         or on disk for the stack to use.
      1. Ensuring the ansible user is part of the `docker` linux group.
      1. Setting appropriate versions via override file
      1. Bringing up the docker compose stack
1. A task set to configure ingress. This includes:
      1. Using `certbot` to issue certificates
      1. Creating and testing `nginx` configurations based on whether this
         is a path-based or hostname-based routing system.
      1. Reloading `nginx` to make sure changes take effect.

## Variables

Host variables are documented and defaulted in [this](group_vars/all.yaml) file.

## Running

You can run locally via the `ansible-playbook` command.
You can set your hosts via the command line via the `ANSIBLE_HOST_OR_GROUP`
environment variable.

A list of environment variables:

* `ANSIBLE_HOST_OR_GROUP` - The ansbile host or group to target
* `GCP_LOCATION` - The GCP location to use for `gcloud` commands
* `GCP_PROJECT` - The GCP project to use for `gcloud` commands
* `GCP_SERVICE_ACCOUNT` - The GCP service account to use for `gcloud` commands
* `GCP_SA_KEY_JSON` - The GCP Service account key contents in JSON format

An example:

```shell
export ANSIBLE_HOST_OR_GROUP=docker-compose-new.dev.fiftyone.ai
export GCP_LOCATION=us-central1
export GCP_PROJECT=computer-vision-team
export GCP_SERVICE_ACCOUNT=github@computer-vision-team.iam.gserviceaccount.com
export GCP_SA_KEY_JSON='{.....}'
ansible-playbook -i inventory/hosts.yaml main.yml
```
