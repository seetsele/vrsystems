import importlib,traceback

try:
    importlib.import_module('api_server_v10')
    print('IMPORT_OK')
except Exception:
    traceback.print_exc()
    print('IMPORT_FAILED')
