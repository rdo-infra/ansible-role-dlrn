# Copyright 2020 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import testinfra

testinfra_hosts = ['all']


# The centos8-train worker will:
# - Not enable cron jobs for run-dlrn.sh
# - Enable cron jobs for run-purge.sh
# - Enable dependency sync cron jobs
# - Create two symlinks: /var/www/html/centos8-train and /var/www/html/train/centos8
# - Disable email sending
# - Enable mock tmpfs in its mock configuration
# - Enable gerrit configuration
# - Not enable public rsync

def test_centos8_train(host):
    cmd = host.run('crontab -l -u centos8-train')
    assert 'run-dlrn.sh' not in cmd.stdout
    assert 'run-purge.sh' in cmd.stdout
    assert 'update-deps.sh' in cmd.stdout

    inifile = host.file('/usr/local/share/dlrn/centos8-train/projects.ini')
    assert inifile.exists
    assert b'smtpserver=localhost' not in inifile.content

    link1 = host.file('/var/www/html/centos8-train')
    assert link1.exists
    assert link1.is_symlink
    assert link1.linked_to == '/home/centos8-train/data/repos'

    link2 = host.file('/var/www/html/train/centos8')
    assert link2.exists
    assert link2.is_symlink
    assert link2.linked_to == '/home/centos8-train/data/repos'

    mockfile = host.file('/home/centos8-train/dlrn/scripts/centos8-train.cfg')
    assert mockfile.exists
    assert b'config_opts[\'plugin_conf\'][\'tmpfs_enable\'] = True' in mockfile.content

    rsyncfile = host.file('/etc/rsyncd.d/centos8-train.conf')
    assert not rsyncfile.exists

    gitconfig = host.run('sudo -u centos8-train git config --global -l') 
    assert 'user.name=rdo-trunk' in gitconfig.stdout
    assert 'user.email=javier.pena@redhat.com' in gitconfig.stdout
    assert 'gitreview.username=rdo-trunk' in gitconfig.stdout

# The rhel8-master worker will:
# - Enable cron jobs for run-dlrn.sh
# - Not enable cron jobs for run-purge.sh
# - Mot enable dependency sync cron jobs
# - Create two symlinks: /var/www/html/rhel8-master and /var/www/html/redhat8-master
# - Disable email sending
# - Not enable mock tmpfs in its mock configuration
# - Not enable gerrit configuration
# - Not enable public rsync
# - Use commits.sqliteabc in the db_connection string in alembic.ini
# - Have custom keys for rdoinfo_driver in projects.ini

def test_rhel8_master(host):
    cmd = host.run('crontab -l -u rhel8-master')
    assert 'run-dlrn.sh' in cmd.stdout
    assert 'run-purge.sh' not in cmd.stdout
    assert 'update-deps.sh' not in cmd.stdout

    inifile = host.file('/usr/local/share/dlrn/rhel8-master/projects.ini')
    assert inifile.exists
    assert b'smtpserver=localhost' not in inifile.content
    assert b'repo=http://github.com/redhat-openstack/rdoinfo' in inifile.content
    assert b'info_files=test.yml' in inifile.content
    assert b'cache_dir' not in inifile.content

    link1 = host.file('/var/www/html/rhel8-master')
    assert link1.exists
    assert link1.is_symlink
    assert link1.linked_to == '/home/rhel8-master/data/repos'

    link2 = host.file('/var/www/html/redhat8-master')
    assert link2.exists
    assert link2.is_symlink
    assert link2.linked_to == '/home/rhel8-master/data/repos'

    mockfile = host.file('/home/rhel8-master/dlrn/scripts/rhel8.cfg')
    assert mockfile.exists
    assert b'config_opts[\'plugin_conf\'][\'tmpfs_enable\'] = False' in mockfile.content

    rsyncfile = host.file('/etc/rsyncd.d/rhel8-master.conf')
    assert not rsyncfile.exists

    gitconfig = host.run('sudo -u rhel8-master git config --global -l') 
    assert 'user.name=rdo-trunk' not in gitconfig.stdout
    assert 'user.email=javier.pena@redhat.com' not in gitconfig.stdout
    assert 'gitreview.username=rdo-trunk' not in gitconfig.stdout

    alembic = host.file('/home/rhel8-master/dlrn/alembic.ini')
    assert alembic.exists
    assert b'sqlalchemy.url = sqlite:///commits.sqliteabc' in alembic.content

# The centos8-master-uc worker will:
# - Enable cron jobs for run-dlrn.sh
# - Not enable cron jobs for run-purge.sh
# - Mot enable dependency sync cron jobs
# - Create two symlinks: /var/www/html/centos8 and /var/www/html/centos8-master
# - Disable email sending
# - Enable mock tmpfs in its mock configuration
# - Not enable gerrit configuration
# - Enable public rsync, allowing access to a server named "dummy.example.com"

def test_centos8_master_uc(host):
    cmd = host.run('crontab -l -u centos8-master-uc')
    assert 'run-dlrn.sh' in cmd.stdout
    assert 'run-purge.sh' not in cmd.stdout
    assert 'update-deps.sh' not in cmd.stdout

    inifile = host.file('/usr/local/share/dlrn/centos8-master-uc/projects.ini')
    assert inifile.exists
    assert b'smtpserver=localhost' not in inifile.content

    link1 = host.file('/var/www/html/centos8')
    assert link1.exists
    assert link1.is_symlink
    assert link1.linked_to == '/home/centos8-master-uc/data/repos'

    link2 = host.file('/var/www/html/centos8-master')
    assert link2.exists
    assert link2.is_symlink
    assert link2.linked_to == '/home/centos8-master-uc/data/repos'

    mockfile = host.file('/home/centos8-master-uc/dlrn/scripts/centos8-master-uc.cfg')
    assert mockfile.exists
    assert b'config_opts[\'plugin_conf\'][\'tmpfs_enable\'] = True' in mockfile.content

    rsyncfile = host.file('/etc/rsyncd.d/centos8-master-uc.conf')
    assert rsyncfile.exists
    assert b'hosts allow = dummy.example.com' in rsyncfile.content

    gitconfig = host.run('sudo -u centos8-master-uc git config --global -l') 
    assert 'user.name=rdo-trunk' not in gitconfig.stdout
    assert 'user.email=javier.pena@redhat.com' not in gitconfig.stdout
    assert 'gitreview.username=rdo-trunk' not in gitconfig.stdout

# The centos-stein worker will:
# - Enable cron jobs for run-dlrn.sh
# - Not enable cron jobs for run-purge.sh
# - Enable dependency sync cron jobs
# - Create two symlinks: /var/www/html/centos7-stein and /var/www/html/stein/centos7
# - Enable email sending
# - Enable mock tmpfs in its mock configuration
# - Not enable gerrit configuration
# - Enable public rsync, allowing access to a server named "dummy.example.com"
# - Set release_numbering to "minor.date.hash" and release_minor to '5'

def test_centos_stein(host):
    cmd = host.run('crontab -l -u centos-stein')
    assert 'run-dlrn.sh' in cmd.stdout
    assert 'run-purge.sh' not in cmd.stdout
    assert 'update-deps.sh' in cmd.stdout

    inifile = host.file('/usr/local/share/dlrn/centos-stein/projects.ini')
    assert inifile.exists
    assert b'smtpserver=localhost' in inifile.content
    assert b'release_numbering=minor.date.hash' in inifile.content
    assert b'release_minor=5' in inifile.content

    link1 = host.file('/var/www/html/centos7-stein')
    assert link1.exists
    assert link1.is_symlink
    assert link1.linked_to == '/home/centos-stein/data/repos'

    link2 = host.file('/var/www/html/stein/centos7')
    assert link2.exists
    assert link2.is_symlink
    assert link2.linked_to == '/home/centos-stein/data/repos'

    mockfile = host.file('/home/centos-stein/dlrn/scripts/centos-stein.cfg')
    assert mockfile.exists
    assert b'config_opts[\'plugin_conf\'][\'tmpfs_enable\'] = True' in mockfile.content

    rsyncfile = host.file('/etc/rsyncd.d/centos-stein.conf')
    assert rsyncfile.exists
    assert b'hosts allow = dummy.example.com' in rsyncfile.content

    gitconfig = host.run('sudo -u centos-stein git config --global -l') 
    assert 'user.name=rdo-trunk' not in gitconfig.stdout
    assert 'user.email=javier.pena@redhat.com' not in gitconfig.stdout
    assert 'gitreview.username=rdo-trunk' not in gitconfig.stdout
