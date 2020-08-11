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

def test_cronjob_missing(host):
    cmd = host.run('crontab -l -u centos8-train')
    cmd2  = host.run('crontab -l -u centos-stein')
    assert 'run-dlrn.sh' not in cmd.stdout
    # since this is a passive server, no cron jobs will be enabled
    assert 'run-dlrn.sh' not in cmd2.stdout
    assert 'run-purge.sh' not in cmd.stdout
    assert 'run-purge.sh' not in cmd2.stdout
    assert 'update-deps.sh' not in cmd.stdout
    assert 'update-deps.sh' not in cmd2.stdout

def test_smtp_missing(host):
    inifile = host.file('/usr/local/share/dlrn/centos8-train/projects.ini')
    inifile2 = host.file('/usr/local/share/dlrn/centos-stein/projects.ini')
    assert inifile.exists
    assert inifile2.exists
    # No mail configuration, regardless of whether it is enabled or not
    assert b'smtpserver=localhost' not in inifile.content
    assert b'smtpserver=localhost' not in inifile2.content
