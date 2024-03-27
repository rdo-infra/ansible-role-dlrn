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

def test_packages(host):
    assert host.package("fail2ban").is_installed
    assert host.package("fail2ban-systemd").is_installed

def test_fail2ban_sshd_config(host):
    cfg_file = host.file('/etc/fail2ban/jail.d/01-sshd.conf')
    assert cfg_file.exists
    assert b'port = 22,22' in cfg_file.content

def test_fail2ban_is_running(host):
     assert host.service("fail2ban").is_running is True

