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
    vhost_file = host.file('/etc/httpd/conf.d/10-trunk.rdoproject.org.conf')
    ssl_file = host.file('/etc/httpd/conf.d/10-ssl-trunk.rdoproject.org.conf')
    
    assert vhost_file.exists
    assert not ssl_file.exists
    assert b'Redirect' not in vhost_file.content
    assert b'<Location "/api-rhel8-master">' in vhost_file.content
    assert b'<Location "/api-redhat-master">' in vhost_file.content
    assert b'<Location "/api-centos8-train">' in vhost_file.content
    assert b'WSGIDaemonProcess dlrn-centos-stein python-home=' in vhost_file.content

def test_rdo_files(host):
    logo_file = host.file('/var/www/html/images/rdo-logo-white.png')
    index_file = host.file('/var/www/html/index.html')   
    assert logo_file.exists
    assert index_file.exists

def test_http_ports(host):
    assert host.socket("tcp://0.0.0.0:80").is_listening
    assert not host.socket("tcp://0.0.0.0:443").is_listening

def test_packages(host):
    assert host.package("httpd").is_installed
    assert not host.package("mod_ssl").is_installed
    assert host.package("python3-mod_wsgi").is_installed

def test_cron(host):
    cmd = host.run('crontab -l -u root')
    assert '/usr/local/bin/update-web-index.sh' in cmd.stdout
