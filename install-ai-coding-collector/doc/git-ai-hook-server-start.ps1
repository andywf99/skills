$taskName = "GitAiHookServer"
$hooksDir = "$env:USERPROFILE\.claude\hooks"
$script   = "$hooksDir\git-ai-hook-server.js"
$vbs      = "$hooksDir\start-git-ai-hook-server.vbs"

# 1) 生成隐藏启动 VBS（0=隐藏窗口，False=异步后台）
$vbsContent = @'
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "node ""%USERPROFILE%\.claude\hooks\git-ai-hook-server.js""", 0, False
'@
New-Item -ItemType Directory -Force -Path $hooksDir | Out-Null
Set-Content -Path $vbs -Value $vbsContent -Encoding ASCII -Force

# 2) 任务动作改为 wscript 调 VBS
$action   = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$vbs`""
$trigger1 = New-ScheduledTaskTrigger -AtStartup
$trigger2 = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
  -RestartCount 999 `
  -RestartInterval (New-TimeSpan -Minutes 1) `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable

# 3) 注册（覆盖旧任务）并启动
Register-ScheduledTask `
  -TaskName $taskName `
  -Action $action `
  -Trigger @($trigger1,$trigger2) `
  -Settings $settings `
  -Description "Run git-ai hook server hidden in background" `
  -Force

Start-ScheduledTask -TaskName $taskName