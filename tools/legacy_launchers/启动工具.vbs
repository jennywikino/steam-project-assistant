Option Explicit

Dim shell
Dim fso
Dim baseDir
Dim launcher
Dim url
Dim healthUrl
Dim http
Dim ready
Dim i

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
launcher = baseDir & "\启动后台服务.bat"
url = "http://localhost:8501"
healthUrl = url & "/_stcore/health"
ready = False

shell.CurrentDirectory = baseDir
shell.Run """" & launcher & """", 0, False

For i = 1 To 30
    On Error Resume Next
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", healthUrl, False
    http.Send
    If Err.Number = 0 Then
        If http.Status >= 200 And http.Status < 500 Then
            ready = True
            Exit For
        End If
    End If
    Err.Clear
    On Error GoTo 0
    WScript.Sleep 1000
Next

If ready Then
    shell.Run url, 1, False
Else
    WScript.Echo "Streamlit 服务未能在 30 秒内启动，请运行 调试启动.bat 查看错误。"
End If
