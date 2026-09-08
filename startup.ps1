# PhoWhisper Auto-Startup Script
# Run this script to manually start PM2 services
# Or add to Windows Task Scheduler to auto-start on boot

Set-Location 'D:\App\PhoWhisper'

Write-Host "Starting PhoWhisper services with PM2..."
Write-Host "Time: $(Get-Date)" -ForegroundColor Green

# Start PM2 with saved config
pm2 start ecosystem.config.js --force

Write-Host ""
Write-Host "Services started. Monitor with: pm2 monit" -ForegroundColor Green
