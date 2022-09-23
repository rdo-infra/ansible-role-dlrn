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

    os.environ['CONFIG_FILE'] = environ['CONFIG_FILE']
    from dlrn.api import app
    return app(environ, start_response)
