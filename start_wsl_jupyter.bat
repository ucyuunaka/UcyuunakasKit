@echo off
REM ʹ�� UTF-8 ����ҳ
REM chcp 65001 > nul

echo ����׼������ WSL (Ubuntu-20.04) ���ڵ�ǰĿ¼�� WSL ӳ��·�������� Jupyter Notebook ������...
echo.

REM ��ȡ��ǰ .bat �ļ����ڵ� Windows Ŀ¼
set "SCRIPT_DIR=%~dp0"
REM ȥ��·��ĩβ�ķ�б�� (�������)
IF "%SCRIPT_DIR:~-1%"=="\" SET "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo Windows ��ǰ����Ŀ¼: "%SCRIPT_DIR%"
echo.

REM --- �ֶ����� WSL ·�� ---
echo �����ֶ����� WSL ·��...

REM ��ȡ�������� (���� D)
set "DRIVE_LETTER_RAW=%SCRIPT_DIR:~0,1%"

REM ����������תΪСд (d)
set "LOWER_CASE_DRIVE_LETTER=%DRIVE_LETTER_RAW%"
REM Basic lowercase conversion for A-Z
for %%L in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if /I "%%L"=="%DRIVE_LETTER_RAW%" set "LOWER_CASE_DRIVE_LETTER=%%L"
)
if "%LOWER_CASE_DRIVE_LETTER%" GEQ "A" if "%LOWER_CASE_DRIVE_LETTER%" LEQ "Z" (
    REM This is a trick: use a temp file with PowerShell to lowercase reliably if complex chars involved
    REM For simple A-Z, the loop above works for ASCII. Let's assume standard drive letters.
    REM For 'D' -> 'd', the loop should work by finding the lowercase match.
    REM Re-evaluating the loop for lowercase: it should be `set "LOWER_CASE_DRIVE_LETTER=%%l"` if %%l is the lowercase version
    REM Simpler: rely on WSL being okay with /mnt/D if direct lowercase is too complex in pure batch for all scenarios.
    REM For now, let's try direct lowercase for known letters.
    if /I "%DRIVE_LETTER_RAW%"=="A" set LOWER_CASE_DRIVE_LETTER=a
    if /I "%DRIVE_LETTER_RAW%"=="B" set LOWER_CASE_DRIVE_LETTER=b
    if /I "%DRIVE_LETTER_RAW%"=="C" set LOWER_CASE_DRIVE_LETTER=c
    if /I "%DRIVE_LETTER_RAW%"=="D" set LOWER_CASE_DRIVE_LETTER=d
    if /I "%DRIVE_LETTER_RAW%"=="E" set LOWER_CASE_DRIVE_LETTER=e
    if /I "%DRIVE_LETTER_RAW%"=="F" set LOWER_CASE_DRIVE_LETTER=f
    REM ... add for other common drive letters if needed
)

REM ��ȡ�������ź����·�� (���� \Users\linyu\Desktop\every)
set "PATH_AFTER_DRIVE=%SCRIPT_DIR:~2%"

REM ����б���滻Ϊ��б��
set "PATH_WITH_FORWARD_SLASHES=%PATH_AFTER_DRIVE:\=/%"

REM ��ϳ����յ� WSL ·�� (���� /mnt/d/Users/linyu/Desktop/every)
set "WSL_PATH=/mnt/%LOWER_CASE_DRIVE_LETTER%%PATH_WITH_FORWARD_SLASHES%"

echo �ֶ������ WSL ·��: "%WSL_PATH%"
echo.

REM --- ��� wslpath ���ߵ�������������ԶԱȣ� ---
REM FOR /F "usebackq delims=" %%P IN (`wsl wslpath -u "%SCRIPT_DIR%"`) DO SET "WSL_PATH_FROM_UTILITY=%%P"
REM echo �Աȣ�wslpath �������: "%WSL_PATH_FROM_UTILITY%"
REM echo.

IF NOT DEFINED WSL_PATH (
    echo ����δ�ܹ��� WSL ·����
    pause
    goto :eof
)

echo ������һ���µ� WSL �ն˴��ڡ�
echo ���ڸ��´����в����������µ� Jupyter ������ URL:
echo   http://localhost:8888/?token=xxxxxxxxxxxx
echo ��
echo   http://127.0.0.1:8888/?token=xxxxxxxxxxxx
echo.

start "WSL_Jupyter_Server" wsl -d Ubuntu-20.04 --cd "%WSL_PATH%" bash -lic "echo '--- Inside WSL Terminal ---'; echo 'Using WSL Path (from bat): %WSL_PATH%'; echo 'Current directory (pwd) after wsl --cd:'; pwd; echo 'Starting Jupyter Lab...'; jupyter lab --no-browser --ip=0.0.0.0 --notebook-dir=.; echo '--- Jupyter Lab has exited (or failed) ---'; echo 'Press any key to close this WSL window.'; read -n 1 -s -r -p ''"

echo.
echo Jupyter Lab ������Ӧ������һ���µ� WSL ������������
echo ����µ� WSL ����δ����ȷ���� Jupyter Lab�����鴰���еĴ�����Ϣ��
echo.
echo ��ǰ����ű����ڿ��Թرգ����߰�������ر�����
pause