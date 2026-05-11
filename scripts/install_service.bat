@echo off
REM 安装并启动后台服务（必须管理员）
cd /d %~dp0\..
python -m image_lock.service.lock_service install
python -m image_lock.service.lock_service start
