# 1. Download Cloudflared (if not already present)
if (-not (Test-Path "cloudflared.exe")) {
    Write-Host "Downloading cloudflared..."
    Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
    Write-Host "Download complete!"
}

# 2. Start Flask app in a new terminal
Write-Host "Starting Flask server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py"
Start-Sleep -Seconds 5  # Give Flask time to start

# 3. Start Cloudflare Tunnel
Write-Host "Starting Cloudflare Tunnel..."
.\cloudflared.exe tunnel --url http://localhost:5000

# 4. Cleanup instructions
Write-Host "`nPress CTRL+C in BOTH terminals to stop everything when done."
