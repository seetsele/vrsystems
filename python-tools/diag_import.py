import sys, traceback
sys.path.insert(0, r'C:\Users\lawm\Desktop\verity-systems\python-tools')
try:
    import api_server_v10 as mod
    print('import ok')
except Exception:
    traceback.print_exc()
