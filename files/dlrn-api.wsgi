import os
import sys

def application(environ, start_response):
    dlrn_debug = environ.get('DLRN_DEBUG', False)
    if dlrn_debug:
        os.environ['DLRN_DEBUG'] = dlrn_debug

    dlrn_log_file = environ.get('DLRN_LOG_FILE', False)
    if dlrn_log_file:
        os.environ['DLRN_LOG_FILE'] = dlrn_log_file

    api_auth_debug = environ.get('API_AUTH_DEBUG', False)
    if api_auth_debug:
        os.environ['API_AUTH_DEBUG'] = api_auth_debug

    api_auth_log_file = environ.get('API_AUTH_LOG_FILE', False)
    if api_auth_log_file:
        os.environ['API_AUTH_LOG_FILE'] = api_auth_log_file

    authentication_drivers = environ.get('AUTHENTICATION_DRIVERS', False)
    if authentication_drivers:
        os.environ['AUTHENTICATION_DRIVERS'] = authentication_drivers

    keytab_path = environ.get('KEYTAB_PATH', False)
    if keytab_path:
        os.environ['KEYTAB_PATH'] = keytab_path

    keytab_princ = environ.get('KEYTAB_PRINC', False)
    if keytab_princ:
        os.environ['KEYTAB_PRINC'] = keytab_princ

    api_read_write_roles = environ.get('API_READ_WRITE_ROLES', False)
    if api_read_write_roles:
        os.environ['API_READ_WRITE_ROLES'] = api_read_write_roles

    api_read_only_roles = environ.get('API_READ_ONLY_ROLES', False)
    if api_read_only_roles:
        os.environ['API_READ_ONLY_ROLES'] = api_read_only_roles

    http_keytab_path = environ.get('HTTP_KEYTAB_PATH', False)
    if http_keytab_path:
        os.environ['HTTP_KEYTAB_PATH'] = http_keytab_path

    protected_endpoints = environ.get('PROTECT_READ_ENDPOINTS', False)
    if protected_endpoints:
        os.environ['PROTECT_READ_ENDPOINTS'] = protected_endpoints

    os.environ['CONFIG_FILE'] = environ['CONFIG_FILE']
    from dlrn.api import app
    return app(environ, start_response)
