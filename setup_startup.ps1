# Setup Myra Voice Assistant to Start on Windows Login
# Run this script as Administrator for best results

Write-Host "🤖 Setting up Myra Voice Assistant for Startup" -ForegroundColor Green
Write-Host "=" * 50

$scriptPath = "D:\Pys\start_myra_at_login.bat"
$startupFolder = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupFolder "Myra Voice Assistant.lnk"

try {
    # Check if the startup script exists
    if (!(Test-Path $scriptPath)) {
        Write-Host "❌ Startup script not found at: $scriptPath" -ForegroundColor Red
        Write-Host "Please ensure start_myra_at_login.bat exists in D:\Pys\" -ForegroundColor Yellow
        exit 1
    }

    # Create shortcut in startup folder
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $scriptPath
    $Shortcut.WorkingDirectory = "D:\Pys"
    $Shortcut.Description = "Myra Voice Assistant - AI Helper"
    $Shortcut.Save()

    Write-Host "✅ Myra shortcut created in startup folder" -ForegroundColor Green
    Write-Host "📍 Location: $shortcutPath" -ForegroundColor Cyan

    # Optional: Create a scheduled task for more reliable startup (requires admin)
    try {
        $taskName = "MyraVoiceAssistant"
        
        # Check if task already exists
        $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Write-Host "⚠️  Scheduled task already exists. Updating..." -ForegroundColor Yellow
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        }

        # Create new scheduled task
        $action = New-ScheduledTaskAction -Execute $scriptPath
        $trigger = New-ScheduledTaskTrigger -AtLogOn
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
        
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Myra Voice Assistant Auto-Start" | Out-Null
        
        Write-Host "✅ Scheduled task created successfully" -ForegroundColor Green
        Write-Host "🔧 Task Name: $taskName" -ForegroundColor Cyan
        
    } catch {
        Write-Host "⚠️  Could not create scheduled task (may need admin rights)" -ForegroundColor Yellow
        Write-Host "   Startup shortcut will still work" -ForegroundColor White
    }

    Write-Host "`n🎉 Setup Complete!" -ForegroundColor Magenta
    Write-Host "📋 What happens next:" -ForegroundColor Yellow
    Write-Host "   1. Myra will start automatically when you log in" -ForegroundColor White
    Write-Host "   2. She'll greet you personally with your username" -ForegroundColor White
    Write-Host "   3. She'll ask if you need anything right away" -ForegroundColor White
    Write-Host "   4. Then she'll sleep quietly until you say 'Hello Myra'" -ForegroundColor White

    Write-Host "`n🔧 Management Commands:" -ForegroundColor Blue
    Write-Host "   To disable: Delete shortcut from startup folder or disable scheduled task" -ForegroundColor Gray
    Write-Host "   Startup folder: $startupFolder" -ForegroundColor Gray

} catch {
    Write-Host "❌ Error setting up startup: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Try running as Administrator" -ForegroundColor Yellow
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
