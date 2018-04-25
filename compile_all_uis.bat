@ECHO OFF

set OSGEO4W_ROOT=C:\Trapps_Software\QGIS3

set PATH=%OSGEO4W_ROOT%\bin;%PATH%
set PATH=%PATH%;%OSGEO4W_ROOT%\apps\qgis\bin

@echo off
call "%OSGEO4W_ROOT%\bin\o4w_env.bat"
call "%OSGEO4W_ROOT%\bin\qt5_env.bat"
call "%OSGEO4W_ROOT%\bin\py3_env.bat"
@echo off
path %OSGEO4W_ROOT%\apps\qgis-dev\bin;%OSGEO4W_ROOT%\apps\grass\grass-7.2.2\lib;%OSGEO4W_ROOT%\apps\grass\grass-7.2.2\bin;%PATH%

cd /d %~dp0

@ECHO ON
::Ui Compilation
call pyuic5 Tachy2GIS_dialog_base.ui -o Tachy2GIS_dialog_base.py          
call pyuic5 AnchorUpdateDialog.ui -o AnchorUpdateDialog_base.py
call pyuic5 FieldDialog.ui -o FieldDialog_base.py


@ECHO OFF
GOTO END

:ERROR
   echo "Failed!"
   set ERRORLEVEL=%ERRORLEVEL%
   pause

:END
@ECHO ON