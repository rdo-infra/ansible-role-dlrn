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
    vhost_file = host.file('/etc/httpd/conf.d/25-trunk-server.rdoproject.org.conf')
    ssl_file = host.file('/etc/httpd/conf.d/25-ssl-trunk-server.rdoproject.org.conf')

    assert vhost_file.exists
    assert ssl_file.exists
    assert b'Redirect permanent / https://trunk-server.rdoproject.org/' in vhost_file.content
    assert b'<Location "/api-centos9-caracal">' in vhost_file.content
    assert b'WSGIDaemonProcess dlrn-centos9-caracal python-home=' in vhost_file.content
    assert b'Redirect /docs/ http://new.example.com/docs/' in vhost_file.content
    assert b'RedirectMatch ^/docs/(.*) http://new.example.com/docs/$1' in vhost_file.content
    assert b'Redirect /docs/ http://new.example.com/docs/' in ssl_file.content
    assert b'RedirectMatch ^/docs/(.*) http://new.example.com/docs/$1' in ssl_file.content

def test_rdo_files(host):
    logo_file = host.file('/var/www/html/images/rdo-logo-white.png')
    index_file = host.file('/var/www/html/index.html')
    assert logo_file.exists
    assert index_file.exists

def test_http_ports(host):
    assert host.socket("tcp://0.0.0.0:80").is_listening
    assert host.socket("tcp://0.0.0.0:443").is_listening

def test_packages(host):
    assert host.package("httpd").is_installed
    assert host.package("mod_ssl").is_installed
    assert host.package("python3-mod_wsgi").is_installed

def test_cron(host):
    cmd = host.run('crontab -l -u root')
    assert '/usr/local/bin/update-web-index.sh' not in cmd.stdout
