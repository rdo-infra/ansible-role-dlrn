Ansible-role-dlrn
=================


# Overview
This is an Ansible role aimed at setting up a new DLRN instance from scratch.

# Description

[DLRN](https://github.com/softwarefactory-project/DLRN) builds and maintains yum repositories following commit streams, usually from OpenStack projects.

The DLRN infrastructure on an instance contains the following components:

- A number of `workers`. A worker is basically a local user, with a local DLRN checkout from the git repo, and some associated configuration.
- An `rdoinfo` user. This user simply hosts a local checkout of the [rdoinfo repository](https://github.com/redhat-openstack/rdoinfo), which is refreshed periodically using a crontab entry.
- A web server to host the generated repos.

You can find more information on the DLRN instance architecture [here](https://github.com/redhat-openstack/delorean-instance/blob/master/docs/delorean-instance.md).

This role can configure the basic parameters required by a DLRN instace, plus all the workers.

# Variables

The role will use the following variables, defined in the inventory:

* `dlrn_server_type` (required) can be `primary` or `backup`. Some DLRN configuration will be
   different depending on the server type. Defaults to `primary`.
* `web_domain` (required) defines the web url used to serve the repositories, without the initial
  `http://` part. Defaults to an empty string.
* `disk_for_builders` (optional), if set, specifies a disk to be used by the role for the workers. This
  disk will be initialized using LVM and mounted as /home.
* `sshd_port` (required) defines an extra SSH port. The SSH daemon will be configured to use it,
  so you may reduce the number of automated attacks. Defaults to 22.
* `enable_https` (required) allows us to specify if we want to set up HTTPS
  for the web component. If set to `true`, the required Apache vhost entries will be created. Defaults
  to `false`.
* `dlrn_manage_letsencrypt` (optional), when `enable_https` is set to `true`, tells the role to take care
  of requesting and renewing the HTTPS certificates using LetsEncrypt. If set to `false`, you will be
  responsible of deploying the SSL certificates to the following locations:

  - /etc/letsencrypt/live/`web_domain`/cert.pem: SSL certificate
  - /etc/letsencrypt/live/`web_domain`/privkey.pem: SSL certificate private key
  - /etc/letsencrypt/live/`web_domain`/fullchain.pem: full SSL certificate chain

  Defaults to `false`.
* `cert_mail` (optional), when `dlrn_manage_letsencrypt` is set to `true`, specifies the email address
  used for the LetsEncrypt certificate. Defaults to `test@example.com`.
* `api_workers` (optional) is a list of the workers where the DLRN API will be enabled.
  Defaults to an empty list.

# Limitations

The module has only been tested on CentOS 7 and 8.

# Contributing

The project uses the Gerrit infrastructure at https://review.rdoproject.org.

Contributions are most welcome, plase use **git-review** to propose a change. Setup your ssh keys after sign in at https://review.rdoproject.org/auth/login .
