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

* `dlrn_server_type` (optional) can be `primary` or `backup`.  A primary server checks periodically
  for changes in repos and synchronizes every build to a passive server if rsync is enabled. A passive
  server receives builds from the primary and serves the repos. Some DLRN configuration will be
   different depending on the server type. Defaults to `primary`.
* `web_domain` (optional) defines the web url used to serve the repositories, without the initial
  `http://` part. Defaults to an empty string.
* `disk_for_builders` (optional), if set, specifies a disk to be used by the role for the workers. This
  disk will be initialized using LVM and mounted as /home.
* `sshd_port` (optional) defines an extra SSH port. The SSH daemon will be configured to use it,
  so you may reduce the number of automated attacks. Defaults to 22.
* `enable_https` (optional) allows us to specify if we want to set up HTTPS
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
* `api_authentication_drivers` (optional) is a list of the authentication drivers to use for incoming http requests.
  Defaults to DBAuthentication.
* `api_ipa_allowed_group` (required with KrbAuthentication driver) is the group allowed to consume the API. It would check if the given authenticated user is member of.
* `api_keytab_princ` (required with KrbAuthentication driver) it defines the keytab principal for retrieving a valid kerberos credential in order to connect IPA server.
* `api_keytab` (required with KrbAuthentication driver) it defines the keytab path for retrieving a valid kerberos credential in order to connect IPA server.
* `http_api_keytab` (optional) is the keytab path for decrypt the incoming kerberos token in order to authenticate the request's user.
  Defaults to api_keytab.
* `api_protected_read_endpoints` (optional) impose the authentication for those read-only endpoints.
* `force_python_version` (optional), if set, allows us to force a non-default Python version for
  the DLRN virtualenv. Set it to ``python3`` if you want to use python3 on a CentOS 7 system, for
  example. By default, it is undefined, meaning the default Python version will be used.
* `rdoinfo_shell` (optional). With this we select the shell to use for the user rdoinfo.
* `promoter_shell` (optional). With this we select the shell to use for the user promoter.
* `dlrn_workers` (optional). This dictionary contains the definition of all workers to be deployed
  by the role. Each dictionary entry can contain the following entries:

  - `distro` (required): Distro for worker (centos7, centos8...).
  - `target` (required): Mock target (centos, rhel8-osp16, centos8-ussuri...).
  - `distgit_branch` (optional): Branch for dist-git. Defaults to rpm-master.
  - `distro_branch` (optional): Branch for upstream git. Defaults to master.
  - `disable_email` (optional): Disable e-mail notifications. Defaults to true.
  - `mock_tmpfs_enable` (optional): Enable the mock tmpfs plugin. Note this requires a lot of RAM.
    Defaults to false.
  - `mock_config` (optional): If defined, a custom mock configuration file will be used for this
    worker, and this variable defines the name of the file template (e.g. mockfile.cfg.j2). If
    undefined (the default), the file template will be derived from the worker name, being the
    name part before the first '-' sign (e.g. centos8.cfg.j2 for centos8-master, fedora.cfg.j2
    for fedora-ussuri, etc.). Undefined by default.
  - `enable_cron` (optional): Enable cron jobs to run DLRN on the worker. Defaults to false.
  - `cron_env` (optional): Environment variables for DLRN cron command (run-dlrn.sh).
    Defaults to empty string.
  - `cron_hour` (optional): If enable_cron is set to true, set the hour for the cron job.
    Defaults to '*'.
  - `cron_minute` (optional): If enable_cron=true, set the minute for the cron job.
    Defaults to '*/5' (every 5 minutes).
  - `shell` (optional): With this we select the shell to use for the given user.
  - `enable_purge` (optional): Enable a cron job to periodically purge old commits from the
    DLRN db and file system, reducing space requirements. Defaults to false.
  - `purge_hour` (optional): If enable_purge is set to true, set the hour for the cron job.
    Defaults to '1'.
  - `purge_minute` (optional): If enable_purge is set to true, set the minute for the cron job.
    Defaults to '7'.
  - `purge_custom_args` (optional): If enable_purge is set to true, and this option is set,
    it will define the custom arguments passed to the `run-purge.sh` script instead of the
    default ones. Undefined by default.
  - `symlinks` (optional): List of directories to be symlinked under to the repo directory.
    Example: ['/var/www/html/centos8', '/var/www/html/centos8-master'].
    If not specified (default), no symlinks will be created.
  - `release` (optional): Release this worker will be using (all lowercase.
    Example: 'train'.
    Defaults to 'rocky'.
  - `baseurl` (optional): Base URL for the exported repositories.
    Example: 'https://trunk.rdoproject.org/centos7-train'.
    Defaults to 'http://localhost'.
  - `gerrit_user` (optional): User to run Gerrit reviews after build failures. If not defined
    (this is the default),  do not enable Gerrit reviews.
    Example: 'rdo-trunk'.
  - `gerrit_email` (optional): E-mail for gerrit_user.
    Example: 'rdo-trunk@rdoproject.org'
    Not defined by default.
  - `gerrit_topic` (optional): Gerrit topic to use when opening a review. Only used it gerrit_user
    is defined.
    Example: 'rdo-FTBFS-train'.
    Defaults to 'rdo-FTBFS'.
  - `rsyncdest` (optional): destination where builtdir and reports are replicated when build is ok.
    format: <user>@<ip or hostname>:<destdir>
    Example: 'centos-master@backupserver.example.com:/home/centos-master/data/repos'.
    Not defined by default.
  - `rsyncport` (optional): port number for ssh in server where builtdir and reports are copied
    after built is successful.
    Example: '22'.
    Defaults to '22'.
  - `enable_public_rsync` (optional): Enable a public rsyncd module for the worker repos.
    Defaults to false.
  - `public_rsync_hosts_allow` (optional) if enable_public_rsync is set to true, this variable defines
    a list of hosts/networks which will be allowed to sync from this module.
    Not defined by default (meaning noone can sync).
  - `worker_processes` (optional): Number of worker processes to use during build.
    Defaults to 1.
  - `use_components` (optional): If set to true, tell DLRN to use a component-based structure for
    its repositories.
    Defaults to false.
  - `project_name` (optional): If set, specify the project name that will be displayed as part
    of the HTML reports.
    Defaults to 'RDO'.
  - `db_connection`(optional) Specify a database connection string, using the SQLAlchemy syntax.
    Defaults to 'sqlite:///commits.sqlite'.
  - `fallback_to_master` (optional): If set to true, DLRN will fall back to the master branch
    for source repositories if the configured branch cannot be found, and rpm-master for distgit
    repositories. If set to false, it will fail in case the configured branch cannot be found.
    Defaults to true.
  - `nonfallback_branches` (optional): Defines a list of regular expressions of branches for
    source and distgit repositories that should never fall back to other branches, even if not
    present in the repository.
    Defaults to '^master$,^rpm-master$'.
  - `include_srpm_in_repo` (optional): If set to false, DLRN will exclude source RPMs from the
    generated repositories.
    Defaults to true.
  - `pkginfo_driver` (optional): DLRN driver to use to manage the distgit repositories.
    The current available options are 'dlrn.drivers.rdoinfo.RdoInfoDriver',
    'dlrn.drivers.gitrepo.GitRepoDriver' and 'dlrn.drivers.downstream.DownstreamInfoDriver'.
    Defaults to 'dlrn.drivers.rdoinfo.RdoInfoDriver'.
  - `build_driver` (optional): DLRN driver used to build packages. The current available
    options are 'dlrn.drivers.mockdriver.MockBuildDriver', 'dlrn.drivers.kojidriver.KojiBuildDriver'
    and 'dlrn.drivers.coprdriver.CoprBuildDriver'.
    Defaults to 'dlrn.drivers.mockdriver.MockBuildDriver'.
  - `release_numbering` (optional)_ Define the algorithm used by DLRN to assign release numbers to
    packages. The release number is created from the current date and the source repository git hash,
    and can use two algorithms:

    - '0.date.hash' if the old method is used: 0.<date>.<hash>
    - '0.1.date.hash' if the new method is used: 0.1.<date>.<hash>. This
      method provides better compatibility with the Fedora packaging guidelines.
    - 'minor.date.hash' allows you to specify the minor version to be used, which
      can be different from 0. If this release numbering schema is used, the value
      of 'minor' will be determined by 'release_minor'.
      Defaults to '0.date.hash'.
  - `release_minor` (optional): If 'release_numbering` is set to 'minor.date.hash', this parameter
    will specify the value of 'minor'.
    Defaults to '0'.
  - `enable_deps_sync` (optional): Enable a cron job to periodically synchronize dependencies repo
    with cloud{centos-release}-openstack-<release>-testing CBS tag.
    Defaults to false.
  - `enable_brs_sync` (optional): Enable a cron job to periodically synchronize build requirements
    repo with cloud{centos-release}-openstack-<release>-el{centos-release}-build CBS tag.
    Defaults to false.
  - `allow_force_rechecks` (optional): If set to true, allow force rechecks of successfully built
    commits. Please note that this is not advisable if you rely on the DLRN-generated
    repositories, since it will remove packages that other hashed repositories may have symlinked.
    Defaults to false.
  - `custom_preprocess` (optional): If set, defines a comma-separated list of custom programs or
    scripts to be called as part of the pre-process step. The custom programs will be executed
    sequentially.
    Not defined by default.
  - `keep_changelog` (optional): If set to true, DLRN will not clean the %changelog section from
    spec files when building the source RPM. When set to the default value of false, DLRN will
    remove all changelog content from specs.
    Defaults to false.
  - `rdoinfo_repo` (optional): If pkginfo_driver is 'dlrn.drivers.gitrepo.RdoInfoDriver', this
    option will define the Git repo to use as a source for the information.
    Not defined by default, so DLRN will use its internally default value.
  - `rdoinfo_info_files` (optional): If pkginfo_driver is 'dlrn.drivers.gitrepo.RdoInfoDriver', this
    option will define the base YAML file(s) to be used by distroinfo to fetch the information
    from the repository.
    Not defined by default, so DLRN will use its internally default value.
  - `rdoinfo_cache_dir` (optional): If pkginfo_driver is 'dlrn.drivers.gitrepo.RdoInfoDriver', this
    option will define the directory used by distroinfo as a cache for the repository.
    Not defined by default, so DLRN will use its internally default value.
  - `gitrepo_repo` (optional): If pkginfo_driver is 'dlrn.drivers.gitrepo.GitRepoDriver', this
    option must be specified, and is the Git repo to use as a source.
    Defaults to 'http://github.com/openstack/rpm-packaging'
  - `gitrepo_dir` (optional): If pkginfo_driver is 'dlrn.drivers.gitrepo.GitRepoDriver', this
    option must be specified, and it is the directory inside gitrepo_repo where the spec files are
    located.
    Defaults to '/openstack'.
  - `gitrepo_skip` (optional): If pkginfo_driver is 'dlrn.drivers.gitrepo.GitRepoDriver', this
    option must be specified, and it is a list of directories inside gitrepo_dir to be skipped by the
    gitrepo driver, when finding packages to be built.
    Defaults to ['openstack-macros'].
  - `gitrepo_use_version_from_spec` (optional): If pkginfo_driver is 'dlrn.drivers.gitrepo.GitRepoDriver',
    this option specifies whether the gitrepo driver will parse the spec file and use the version
    from it as source-branch or not.
    Defaults to true.
  - `downstream_distroinfo_repo` (optional): If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option specifies the distroinfo repository
    to get package information from.
    Not defined by default.
  - `downstream_info_files` (optional) If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option specifies the info file (or a list
    of info files) to get package information from, within the distroinfo repo.
    Not defined by default.
  - `downstream_versions_url` (optional) If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option specifies the URL of a versions.csv
    file generated by another DLRN instance. distro_hash and commit_hash will be reused from supplied
    versions.csv and only packages present in the file are processed.
    Not defined by default.
  - `downstream_distro_branch` (optional): If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option specifies the branch to use when
    cloning the downstream distgit, since it may be different from the upstream distgit branch.
    Not defined by default.
  - `downstream_tag` (optional): If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option will filter the 'packages' section of
    the packaging metadata (from 'repo/info_files') to only contain packages with the 'downstream_tag'
    tag. This tag will be filtered in addition to the one set in the 'DEFAULT/tags' section.
    Not defined by default.
  - `downstream_distgit_key` (optional): If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option will specify the key used to find the
    downstream distgit in the 'packages' section of packaging metadata (from 'repo/info_files').
    Not defined by default.
  - `use_upstream_spec` (optional): If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option defines if the upstream distgit
    contents (spec file and additional files) should be copied over the downstream distgit after cloning.
    Defaults to false.
  - `downstream_spec_replace_list` (optional): If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option will perform some sed-like edits
    in the spec file after copying it from the upstream to the downstream distgit. This is specially
    useful when the downstream DLRN instance has special requirements, such as building without
    documentation.
    Not defined by default.
  - `downstream_source_git_key` (optional): If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option will specify the key used to find the
    downstream source git in the 'packages' section of packaging metadata (from 'repo/info_files').
    Not defined by default.
  - `downstream_source_git_branch` (optional): If pkginfo_driver is
    'dlrn.drivers.downstream.DownstreamInfoDriver', this option specifies the branch to use when
    cloning the downstream source git, since it may be different from the upstream git branch.
    Not defined by default.
  - `koji_exe` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver',
    this option defines the executable to use. Some Koji instances create their own client
    packages to add their default configuration, such as CBS or Brew.
    Defaults to 'koji'.
  - `koji_krb_principal` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver',
    this option defines the Kerberos principal to use for the Koji builds. If not defined, DLRN will
    assume that authentication is performed using SSL certificates.
    Not defined by default.
  - `koji_krb_keytab` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver',
    this is the full path to a Kerberos keytab file, which contains the Kerberos credentials for the
    principal defined in the koji_krb_principal option.
    Not defined by default.
  - `koji_scratch_builds` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver',
    this option defines if a scratch build should be used.
    Defaults to true.
  - `koji_build_target` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver',
    this option defines the build target to use. This defines the buildroot and base repositories
    to be used for the build.
    Not defined by default.
  - `koji_arch` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver',
    this option defines an override to the default architecture (x86_64) in some cases
    (e.g retrieving mock configuration from Koji instance).
    Defaults to 'x86_64'.
  - `koji_fetch_mock_config` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver',
    when this option is set to true, DLRN will download the mock configuration for the build target
    from Koji, and use it when building the source RPM. If set to 'false', DLRN will use its
    internally defined mock configuration, based on the ``DEFAULT/target`` configuration option.
    Defaults to false.
  - `koji_use_rhpkg` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver',
    when this option is set to true, 'rhpkg' will be used by DLRN as the build tool in combination
    with 'koji_exe'.
    Defaults to false.
  - `koji_mock_base_packages` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver'
    and 'fetch_mock_config' is set to true, this option will define the set of base packages that
    will be installed in the mock configuration when creating the source RPM. This list of packages
    will override the one fetched in the mock configuration, if set. If not set, no overriding will
    be done.
    Not defined by default.
  - `koji_mock_package_manager` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver'
    and 'fetch_mock_config' is set to true, this option will  will override the
    config_ops['package_manager'] option from the fetched mock configuration. This allows us to have
    different package managers if we are building for different operating system releases,
    such as CentOS 7 (yum) and CentOS 8 (dnf).
    Not defined by default.
  - `additional_koji_tags` (optional): If build_driver is 'dlrn.drivers.kojidriver.KojiBuildDriver'
    this option defines a list of additional tags to be applied to the build, once it is finished.
    Not defined by default.
  - `enable_api_login_logs` (optional): If true, the API will log every authentication and authorization process for protected endpoints and regular logs to the files defined with environment variable API_AUTH_LOG_FILE and DLRN_LOG_FILE respectively. If one/all of them is missing, then It'll be written in the WSGI logs defined in its configuration file.

# Migration notes

If you are migrating a server deployed using [puppet-dlrn](https://github.com/rdo-infra/puppet-dlrn),
please take into account the following details:

* Cron jobs for workers should not be duplicated, however you will have duplicate comments from Puppet
  and Ansible in each crontab. Just make sure the old Puppet comments are removed.
* The `httpd` service may fail to restart on the first deployment. If that is the case, please check if
  there are duplicate files under /etc/httpd/conf.d with different numbers (e.g. 10-trunk-primary.rdoproject.org.conf
  and 25-trunk-primary.rdoproject.org.conf). If that is the case, please remove the file with an older
  timestamp and restart the httpd service.
* The YAML configuration file from the puppet-dlrn instance can be almost completely reused for the
  Ansible role. However, the `cron_hour` and `cron_minute` parameters, which accepted a list in
  puppet-dlrn, now require a string in the same format as required by crontab. For example,
  'cron_minute: [1,31]' would now be 'cron_minute: "1,31'.
* The SSH key generated for each worker may be changed, if it was not created with the default size
  of 2048 bits for RSA keys (CentOS 7 and 8).

# Limitations

The module has only been tested on CentOS/RHEL 7 and 8.

SELinux is set to `enforcing`, and the required SELinux booleans and file contexts
are set. However, there is one limitation with this setup:

* Remote import operations are not working.

# Contributing

The project uses the Gerrit infrastructure at https://review.rdoproject.org.

Contributions are most welcome, plase use **git-review** to propose a change. Setup your ssh keys after sign in at https://review.rdoproject.org/auth/login .
