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

def test_selinux_enforcing(host):
    selinux = host.file('/etc/sysconfig/selinux')
    assert selinux.exists
    assert b'SELINUX=enforcing' in selinux.content

def test_packages(host):
    assert host.package("epel-release").is_installed
    assert host.package("mock").is_installed

def test_sshd(host):
    sshd_config = host.file('/etc/ssh/sshd_config')
    assert b'Port 22' in sshd_config.content
    assert host.service("sshd").is_running

def test_firewalld(host):
    rule_file = host.file('/etc/firewalld/zones/public.xml')
    assert host.service("firewalld").is_running
    assert b'service name="ssh"' in rule_file.content
    assert b'service name="http"' in rule_file.content
    assert b'service name="https"' not in rule_file.content
    assert b'port port="22" protocol="tcp"' in rule_file.content

def test_mock(host):
    assert host.group('mock').exists

def test_local_share_dlrn(host):
    dlrn_dir = host.file('/usr/local/share/dlrn')
    assert dlrn_dir.exists
    assert dlrn_dir.is_directory

def test_scripts(host):
    for script in ['run-dlrn.sh', 'run-purge.sh', 'update-deps.sh',
                   'purge-deps.sh']:
        assert host.file('/usr/local/bin/%s' % script).exists

def test_yum_timeout(host):
    yum_cfg = host.file('/etc/yum.conf')
    assert b'timeout = 120' in yum_cfg.content
