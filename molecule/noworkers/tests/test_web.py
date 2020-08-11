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


def test_httpd_is_running(host):
     assert host.service("httpd").is_running

def test_vhost_files(host):
    vhost_file = host.file('/etc/httpd/conf.d/25-trunk.rdoproject.org.conf')
    ssl_file = host.file('/etc/httpd/conf.d/25-ssl-trunk.rdoproject.org.conf')

    assert vhost_file.exists
    assert not ssl_file.exists
    assert b'Redirect' not in vhost_file.content
    assert b'WSGIDaemonProcess' not in vhost_file.content
