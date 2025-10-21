"""
DPI缩放模块 - 跨平台DPI检测和缩放支持
"""
import sys
import os
import platform
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple


class DPIHelper:
    """Cross-platform DPI detection and scaling helper class"""

    # 标准DPI基准
    STANDARD_DPI = 96.0

    @staticmethod
    def get_system_dpi() -> Tuple[float, float]:
        """
        Get system DPI setting based on platform

        Returns:
            Tuple[float, float]: System DPI values (dpi_x, dpi_y)
        """
        system = platform.system()

        if system == "Windows":
            return DPIHelper._get_windows_dpi()
        elif system == "Linux":
            return DPIHelper._get_linux_dpi()
        elif system == "Darwin":  # macOS
            return DPIHelper._get_macos_dpi()
        else:
            # 未知平台默认使用标准DPI
            return (DPIHelper.STANDARD_DPI, DPIHelper.STANDARD_DPI)

    @staticmethod
    def get_scaling_factor() -> float:
        """
        Calculate scaling factor relative to 96 DPI

        Returns:
            float: Scaling factor (e.g., 1.25 for 120 DPI, 1.5 for 144 DPI)
        """
        dpi_x, dpi_y = DPIHelper.get_system_dpi()
        # 使用X和Y DPI的平均值
        dpi = (dpi_x + dpi_y) / 2
        return dpi / DPIHelper.STANDARD_DPI

    @staticmethod
    def set_dpi_awareness() -> None:
        """
        Set application DPI awareness level (Windows only)
        """
        if platform.system() == "Windows":
            DPIHelper._set_windows_dpi_awareness()

    @staticmethod
    def _get_windows_dpi() -> Tuple[float, float]:
        """
        Get Windows system DPI using Windows API

        Returns:
            Tuple[float, float]: Windows system DPI (dpi_x, dpi_y)
        """
        try:
            # 尝试使用GetDpiForSystem (Windows 10+)
            try:
                user32 = ctypes.windll.user32
                user32.GetDpiForSystem.restype = wintypes.UINT
                dpi = user32.GetDpiForSystem()
                return (float(dpi), float(dpi))
            except AttributeError:
                # 旧版本Windows的降级方案
                # Get DPI from the window device context
                gdi32 = ctypes.windll.gdi32
                user32 = ctypes.windll.user32

                # Get desktop window
                hwnd = user32.GetDesktopWindow()

                # Get device context
                hdc = user32.GetDC(hwnd)

                # Get DPI
                dpi_x = gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                dpi_y = gdi32.GetDeviceCaps(hdc, 90)  # LOGPIXELSY

                # Release device context
                user32.ReleaseDC(hwnd, hdc)

                # Return X and Y DPI
                return (float(dpi_x), float(dpi_y))

        except Exception:
            # Fallback to standard DPI on error
            return (DPIHelper.STANDARD_DPI, DPIHelper.STANDARD_DPI)

    @staticmethod
    def _get_linux_dpi() -> Tuple[float, float]:
        """
        Get Linux system DPI using environment variables and system commands

        Returns:
            Tuple[float, float]: Linux system DPI (dpi_x, dpi_y)
        """
        try:
            # Check GDK_SCALE environment variable (GNOME/GTK)
            gdk_scale = os.environ.get('GDK_SCALE')
            if gdk_scale:
                dpi = DPIHelper.STANDARD_DPI * float(gdk_scale)
                return (dpi, dpi)

            # Check QT_SCALE_FACTOR (KDE/Qt)
            qt_scale = os.environ.get('QT_SCALE_FACTOR')
            if qt_scale:
                dpi = DPIHelper.STANDARD_DPI * float(qt_scale)
                return (dpi, dpi)

            # Try to get DPI from X server
            try:
                import subprocess
                result = subprocess.run(['xrdb', '-query'],
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Xft.dpi' in line:
                            dpi = float(line.split(':')[1].strip())
                            return (dpi, dpi)
            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                pass

            # Default to standard DPI
            return (DPIHelper.STANDARD_DPI, DPIHelper.STANDARD_DPI)

        except Exception:
            return (DPIHelper.STANDARD_DPI, DPIHelper.STANDARD_DPI)

    @staticmethod
    def _get_macos_dpi() -> Tuple[float, float]:
        """
        Get macOS system DPI using tk scaling

        Returns:
            Tuple[float, float]: macOS system DPI (dpi_x, dpi_y)
        """
        try:
            # On macOS, we'll use the tk scaling factor
            # This will be set when the first tk window is created
            # For now, return standard DPI and let the app adjust
            return (DPIHelper.STANDARD_DPI, DPIHelper.STANDARD_DPI)

        except Exception:
            return (DPIHelper.STANDARD_DPI, DPIHelper.STANDARD_DPI)

    @staticmethod
    def _set_windows_dpi_awareness() -> None:
        """
        Set Windows DPI awareness level
        """
        try:
            # Try to set per-monitor DPI awareness (Windows 10+)
            try:
                shcore = ctypes.windll.shcore
                # PROCESS_PER_MONITOR_DPI_AWARE = 2
                shcore.SetProcessDpiAwareness(2)
                return
            except (AttributeError, OSError):
                pass

            # Try system DPI awareness (Windows 8.1+)
            try:
                shcore = ctypes.windll.shcore
                # PROCESS_SYSTEM_DPI_AWARE = 1
                shcore.SetProcessDpiAwareness(1)
                return
            except (AttributeError, OSError):
                pass

            # Fallback to SetProcessDPIAware (Windows Vista+)
            try:
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
            except AttributeError:
                pass

        except Exception:
            # Ignore any errors and continue
            pass

    @staticmethod
    def scale_value(value: float, scaling_factor: Optional[float] = None) -> int:
        """
        Scale a value based on DPI scaling factor

        Args:
            value: Base value to scale
            scaling_factor: Optional scaling factor (uses system if not provided)

        Returns:
            int: Scaled value (rounded to nearest integer)
        """
        if scaling_factor is None:
            scaling_factor = DPIHelper.get_scaling_factor()

        return int(round(value * scaling_factor))

    @staticmethod
    def scale_font_size(base_size: int, scaling_factor: Optional[float] = None,
                       min_size: int = 8, max_size: int = 24) -> int:
        """
        Scale font size with min/max limits

        Args:
            base_size: Base font size
            scaling_factor: Optional scaling factor
            min_size: Minimum font size
            max_size: Maximum font size

        Returns:
            int: Scaled font size (clamped to min/max)
        """
        scaled_size = DPIHelper.scale_value(base_size, scaling_factor)
        return max(min_size, min(max_size, scaled_size))


# Module-level singleton instance
_dpi_helper_instance: Optional[DPIHelper] = None


def get_dpi_helper() -> DPIHelper:
    """
    Get or create the singleton DPIHelper instance
    
    Returns:
        DPIHelper: Singleton DPIHelper instance
    """
    global _dpi_helper_instance
    if _dpi_helper_instance is None:
        _dpi_helper_instance = DPIHelper()
    return _dpi_helper_instance


def set_dpi_awareness() -> bool:
    """
    Set DPI awareness for the application
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        DPIHelper.set_dpi_awareness()
        return True
    except Exception:
        return False