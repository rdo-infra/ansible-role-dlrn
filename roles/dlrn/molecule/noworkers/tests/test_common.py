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


def test_rsyncd(host):
    config_file = host.file('/etc/rsyncd.conf')
    config_dir = host.file('/etc/rsyncd.d')
    assert b'&include /etc/rsyncd.d' in config_file.content
    assert host.service("rsyncd").is_running
    assert config_dir.exists
    assert config_dir.is_directory
