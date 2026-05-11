@echo off
REM 停止并卸载后台服务（必须管理员）
cd /d %~dp0\..
python -m image_lock.service.lock_service stop
python -m image_lock.service.lock_service remove
