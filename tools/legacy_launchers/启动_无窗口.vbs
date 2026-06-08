Option Explicit

Dim shell
Dim fso
Dim baseDir
Dim launcher

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
launcher = baseDir & "\启动_后台服务.bat"

shell.CurrentDirectory = baseDir
shell.Run """" & launcher & """", 0, False
WScript.Sleep 3000
shell.Run "http://localhost:8501", 1, False
