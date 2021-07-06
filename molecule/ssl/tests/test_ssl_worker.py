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

# The centos8-master-uc worker will:
# - Have an api-centos8-master-uc entry at /etc/httpd/conf.d/25-ssl-trunk.rdoproject.org.conf
# - Have a rewrite rule from api-centos8-master to api-centos8-master-uc in the same file
def test_centos8_master_uc(host):
    vhostfile = host.file('/etc/httpd/conf.d/25-ssl-trunk.rdoproject.org.conf')
    assert b'<Location "/api-centos8-master-uc">' in vhostfile.content
    assert b'RewriteRule ^/api-centos8-master/(.*) /api-centos8-master-uc/$1 [PT]' in vhostfile.content


