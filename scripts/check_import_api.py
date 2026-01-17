import importlib, traceback

try:
    importlib.import_module('api_server_v10')
    print('import ok')
except Exception:
    traceback.print_exc()
