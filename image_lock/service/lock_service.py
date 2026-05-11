"""Windows service that periodically re-applies the locked image associations."""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
except ImportError:  # non-Windows dev — keep importable
    win32serviceutil = None  # type: ignore

from image_lock.core.config import load_config, get_locked_exts
from image_lock.core.locker import apply_rule, verify_rule

SERVICE_NAME = "ImageLockToolService"
SERVICE_DISPLAY_NAME = "图片查看锁定小工具 后台服务"
SERVICE_DESCRIPTION = "周期性地强制图片文件后缀关联到指定的查看程序"


if win32serviceutil is not None:

    class ImageLockService(win32serviceutil.ServiceFramework):
        _svc_name_ = SERVICE_NAME
        _svc_display_name_ = SERVICE_DISPLAY_NAME
        _svc_description_ = SERVICE_DESCRIPTION

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.running = False
            self.worker = None

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self.running = False
            win32event.SetEvent(self.hWaitStop)
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, ""),
            )

        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ""),
            )
            self.running = True
            self.worker = threading.Thread(target=self._loop, daemon=True)
            self.worker.start()
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

        def _loop(self):
            while self.running:
                try:
                    cfg = load_config()
                    if cfg.get("enabled", True):
                        app = cfg.get("app", "")
                        if app:
                            for ext in get_locked_exts(cfg):
                                if not verify_rule(ext, app):
                                    apply_rule(ext, app)
                    interval = int(cfg.get("checkInterval", 120))
                    for _ in range(max(1, interval)):
                        if not self.running:
                            break
                        time.sleep(1)
                except Exception:
                    time.sleep(30)


def install_service():
    if win32serviceutil is None:
        return False, "pywin32 not available"
    try:
        win32serviceutil.InstallService(
            sys.executable + f' "{os.path.abspath(__file__)}"',
            SERVICE_NAME,
            SERVICE_DISPLAY_NAME,
            startType=win32service.SERVICE_AUTO_START,
            description=SERVICE_DESCRIPTION,
        )
        return True, "服务已安装"
    except Exception as e:
        return False, str(e)


def remove_service():
    if win32serviceutil is None:
        return False, "pywin32 not available"
    try:
        win32serviceutil.RemoveService(SERVICE_NAME)
        return True, "服务已卸载"
    except Exception as e:
        return False, str(e)


def start_service():
    if win32serviceutil is None:
        return False, "pywin32 not available"
    try:
        win32serviceutil.StartService(SERVICE_NAME)
        return True, "服务已启动"
    except Exception as e:
        return False, str(e)


def stop_service():
    if win32serviceutil is None:
        return False, "pywin32 not available"
    try:
        win32serviceutil.StopService(SERVICE_NAME)
        return True, "服务已停止"
    except Exception as e:
        return False, str(e)


def query_service_status():
    if win32serviceutil is None:
        return False, "未安装"
    try:
        status = win32serviceutil.QueryServiceStatus(SERVICE_NAME)
        state_map = {
            win32service.SERVICE_STOPPED: "已停止",
            win32service.SERVICE_START_PENDING: "启动中",
            win32service.SERVICE_STOP_PENDING: "停止中",
            win32service.SERVICE_RUNNING: "运行中",
            win32service.SERVICE_CONTINUE_PENDING: "恢复中",
            win32service.SERVICE_PAUSE_PENDING: "暂停中",
            win32service.SERVICE_PAUSED: "已暂停",
        }
        return True, state_map.get(status[1], "未知")
    except Exception:
        return False, "未安装"


if __name__ == "__main__":
    if win32serviceutil is None:
        print("pywin32 is required to run as a Windows service.")
        sys.exit(1)
    win32serviceutil.HandleCommandLine(ImageLockService)
