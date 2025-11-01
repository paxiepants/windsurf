# PowerShell script to run ollama_chat.py with proper terminal
# Right-click and select "Run with PowerShell" to use this

# Ensure we're running in an interactive console
if ($Host.Name -ne 'ConsoleHost') {
    Write-Host "Please run this script from PowerShell, not ISE or other hosts" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Ollama Chat Interactive Menu" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure Ollama is running in another window!" -ForegroundColor Yellow
Write-Host "If not, open a new terminal and run: ollama serve" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Enter to continue..." -ForegroundColor Green
Read-Host

# Change to the script directory
Set-Location $PSScriptRoot

# Run the Python script with unbuffered output
$env:PYTHONUNBUFFERED = "1"
python -u ollama_chat.py

# Keep window open
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
if ($LASTEXITCODE -eq 0) {
    Write-Host "Session ended. Press any key to close..." -ForegroundColor Green
} else {
    Write-Host "An error occurred. Press any key to close..." -ForegroundColor Red
}
Write-Host "============================================================" -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
