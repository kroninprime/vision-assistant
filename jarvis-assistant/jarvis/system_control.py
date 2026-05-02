"""Enhanced system control module for app launching and system management."""
import logging
import subprocess
import os
import sys
from typing import Dict, List, Optional

logger = logging.getLogger("jarvis.system_control")


class SystemControl:
    """
    Control system and applications.
    
    Handles:
    - App launching/closing
    - System settings
    - Process management
    - Command execution
    """

    def __init__(self):
        self.is_windows = sys.platform == "win32"
        self.running_processes: Dict[str, int] = {}

    def open_application(self, app_name: str, args: List[str] = None) -> str:
        """
        Open an application.
        
        Examples:
            - "chrome" -> Opens Chrome
            - "notepad" -> Opens Notepad
            - "calculator" -> Opens Calculator
        """
        try:
            args = args or []
            cmd = [app_name] + args

            if self.is_windows:
                # Try common Windows app names
                app_map = {
                    "chrome": "chrome.exe",
                    "firefox": "firefox.exe",
                    "edge": "msedge.exe",
                    "notepad": "notepad.exe",
                    "calculator": "calc.exe",
                    "paint": "mspaint.exe",
                    "word": "winword.exe",
                    "excel": "excel.exe",
                    "powershell": "powershell.exe",
                }
                actual_app = app_map.get(app_name.lower(), f"{app_name}.exe")
                cmd[0] = actual_app

            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.running_processes[app_name] = process.pid

            logger.info(f"Opened application: {app_name} (PID: {process.pid})")
            return f"✓ Opened {app_name}"

        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return f"✗ Failed to open {app_name}: {e}"

    def close_application(self, app_name: str) -> str:
        """Close running application by name."""
        try:
            if self.is_windows:
                # Use taskkill on Windows
                app_filename = f"{app_name}.exe" if not app_name.endswith(".exe") else app_name
                subprocess.run(
                    ["taskkill", "/IM", app_filename, "/F"],
                    check=True,
                    capture_output=True,
                )
            else:
                # Use killall on Unix/Linux/Mac
                subprocess.run(["killall", app_name], check=True, capture_output=True)

            logger.info(f"Closed application: {app_name}")
            return f"✓ Closed {app_name}"

        except Exception as e:
            logger.warning(f"Failed to close {app_name}: {e}")
            return f"✗ Could not close {app_name}"

    def set_volume(self, level: int) -> str:
        """Set system volume (0-100)."""
        try:
            level = max(0, min(100, level))

            if self.is_windows:
                # Use nircmd or similar for Windows
                try:
                    subprocess.run(
                        ["nircmd", "setsysvolume", str(int(level * 655))],
                        check=False,
                    )
                    return f"✓ Volume set to {level}%"
                except:
                    return "Volume control requires nircmd utility"
            else:
                return "Volume control not yet implemented for this OS"

        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return f"✗ Could not set volume"

    def set_brightness(self, level: int) -> str:
        """Set screen brightness (0-100)."""
        try:
            level = max(0, min(100, level))

            if self.is_windows:
                try:
                    # Try using WMI
                    os.system(
                        f'powershell -Command "Get-CimInstance -N root\\cimv2 -CN WmiMonitorBrightnessMethods | Invoke-CimMethod -MethodName WmiSetBrightness -Arguments @{{Brightness={level}}}"'
                    )
                    return f"✓ Brightness set to {level}%"
                except:
                    return "Brightness control requires admin rights"
            else:
                return "Brightness control not yet implemented for this OS"

        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
            return f"✗ Could not set brightness"

    def execute_command(self, command: str, check: bool = False) -> str:
        """
        Execute system command.
        
        Security note: Only execute trusted commands.
        """
        try:
            logger.info(f"Executing command: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check,
            )
            return result.stdout or "Command executed successfully"

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            return f"Command error: {e.stderr}"
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return f"✗ Execution failed: {e}"

    def get_system_info(self) -> str:
        """Get system information."""
        try:
            info = {
                "platform": sys.platform,
                "python_version": sys.version,
            }

            if self.is_windows:
                # Get Windows version
                import platform
                info["os_version"] = platform.platform()

            return str(info)
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return "Could not retrieve system info"

    def list_running_processes(self) -> List[str]:
        """Get list of running processes."""
        return list(self.running_processes.keys())

    def get_process_status(self, app_name: str) -> bool:
        """Check if application is running."""
        return app_name in self.running_processes
