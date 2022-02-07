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

# The centos9-master-uc worker will:
# - Enable cron jobs for run-dlrn.sh
# - Not enable cron jobs for run-purge.sh
# - Mot enable dependency sync cron jobs
# - Create two symlinks: /var/www/html/centos9 and /var/www/html/centos9-master
# - Disable email sending
# - Enable mock tmpfs in its mock configuration
# - Not enable gerrit configuration
# - Enable public rsync, allowing access to a server named "dummy.example.com"
# - Use the centos9stream configuration for the mock template

def test_centos9_master_uc(host):
    cmd = host.run('crontab -l -u centos9-master-uc')
    assert 'run-dlrn.sh' in cmd.stdout
    assert 'run-purge.sh' not in cmd.stdout
    assert 'update-deps.sh' not in cmd.stdout

    inifile = host.file('/usr/local/share/dlrn/centos9-master-uc/projects.ini')
    assert inifile.exists
    assert b'smtpserver=localhost' not in inifile.content
    assert b'target=centos9-master-uc' in inifile.content

    link1 = host.file('/var/www/html/centos9-master')
    assert link1.exists
    assert link1.is_symlink
    assert link1.linked_to == '/home/centos9-master-uc/data/repos'

    mockfile = host.file('/home/centos9-master-uc/dlrn/scripts/centos9-master-uc.cfg')
    assert mockfile.exists
    assert b'config_opts[\'plugin_conf\'][\'tmpfs_enable\'] = True' in mockfile.content
    assert b'[baseos]' in mockfile.content

    rsyncfile = host.file('/etc/rsyncd.d/centos9-master-uc.conf')
    assert rsyncfile.exists
    assert b'hosts allow = dummy.example.com' in rsyncfile.content

    gitconfig = host.run('sudo -u centos9-master-uc git config --global -l') 
    assert 'user.name=rdo-trunk' not in gitconfig.stdout
    assert 'user.email=javier.pena@redhat.com' not in gitconfig.stdout
    assert 'gitreview.username=rdo-trunk' not in gitconfig.stdout
