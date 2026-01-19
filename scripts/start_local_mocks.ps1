Write-Output 'Starting local mock services for tests on alternative ports (MOCK_BASE=15000)'
$env:MOCK_BASE = '15000'
python "python-tools\mocks\start_mocks.py"