import sys,importlib,traceback,os
sys.path.insert(0, os.path.join(os.getcwd(),'python-tools'))
print('sys.path[0]=', sys.path[0])
try:
    importlib.import_module('api_server_v10')
    print('IMPORT_OK')
except Exception:
    traceback.print_exc()
    print('IMPORT_FAILED')
