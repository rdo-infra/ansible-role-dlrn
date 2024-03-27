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


# The centos9-caracal worker will:
# - Enable cron jobs for run-dlrn.sh
# - Enable cron jobs for run-purge.sh
# - Enable dependency sync cron jobs
# - Create symlink: /var/www/html/centos9-caracal
# - Disable email sending
# - Not enable mock tmpfs in its mock configuration
# - Not enable gerrit configuration
# - Not enable public rsync
# - Use commits.sqliteabc in the db_connection string in alembic.ini
# - Have custom keys for rdoinfo_driver in projects.ini

def test_centos9_caracal(host):
    cmd = host.run('crontab -l -u centos9-caracal')
    assert 'run-dlrn.sh' not in cmd.stdout
    assert 'run-purge.sh' not in cmd.stdout
    assert 'update-deps.sh' not in cmd.stdout

    inifile = host.file('/usr/local/share/dlrn/centos9-caracal/projects.ini')
    assert inifile.exists
    assert b'smtpserver=localhost' not in inifile.content
    assert b'repo=http://github.com/redhat-openstack/rdoinfo' in inifile.content
    assert b'info_files=test.yml' in inifile.content
    assert b'cache_dir' not in inifile.content
    assert b'target=centos9-caracal' in inifile.content

    link1 = host.file('/var/www/html/centos9-caracal')
    assert link1.exists
    assert link1.is_symlink
    assert link1.linked_to == '/home/centos9-caracal/data/repos'

    mockfile = host.file('/home/centos9-caracal/dlrn/scripts/centos9stream.cfg')
    assert mockfile.exists
    assert b'config_opts[\'plugin_conf\'][\'tmpfs_enable\'] = True' in mockfile.content

    gitconfig = host.run('sudo -u centos9-caracal git config --global -l') 
    assert 'user.name=rdo-trunk' not in gitconfig.stdout
    assert 'user.email=javier.pena@redhat.com' not in gitconfig.stdout
    assert 'gitreview.username=rdo-trunk' not in gitconfig.stdout

    alembic = host.file('/home/centos9-caracal/dlrn/alembic.ini')
    assert alembic.exists
    assert b'sqlalchemy.url = sqlite:///commits.sqliteabc' in alembic.content

