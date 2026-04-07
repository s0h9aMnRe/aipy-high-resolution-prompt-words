# 高分辨率屏幕适配解决方案 - 优化版（含HDR截图支持）
# 优化内容：简化代码结构、移除冗余逻辑、添加HDR截图功能

import sys
import ctypes
from ctypes import windll, c_int
import tkinter as tk
from tkinter import ttk

# ============================================================
# 第一部分：DPI感知设置（优化版）
# ============================================================


def setup_dpi_awareness():
    """设置DPI感知，确保高分辨率屏幕显示正确"""
    if sys.platform != "win32":
        return

    try:
        # 优先使用Per-Monitor DPI Aware (级别2) - 现代Windows最佳实践
        windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            # 回退到系统级DPI感知 - 兼容旧版Windows
            windll.user32.SetProcessDPIAware()
        except:
            pass

    try:
        # 启用非客户区DPI缩放（窗口边框、标题栏）
        windll.user32.EnableNonClientDpiScaling(c_int(1))
    except:
        pass


# 执行DPI设置
setup_dpi_awareness()


# ============================================================
# 第二部分：安全字体选择（简化版）
# ============================================================


def get_safe_font():
    """获取跨平台安全字体"""
    fonts = {"win32": "Tahoma", "darwin": "Helvetica", "linux": "DejaVu Sans"}
    return fonts.get(sys.platform, "DejaVu Sans")


SAFE_FONT = get_safe_font()


# ============================================================
# 第三部分：HDR截图支持（新增功能）
# ============================================================


class HDRScreenshotHandler:
    """HDR截图处理器 - 防止HDR环境下截图过曝"""

    def __init__(self):
        self.hdr_enabled = False
        self.max_luminance = 80  # SDR标准亮度
        self._detect_hdr_status()

    def _detect_hdr_status(self):
        """检测系统HDR状态"""
        if sys.platform != "win32":
            return

        try:
            # 方法1：通过注册表检测HDR开关状态
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_READ
            )

            # 尝试读取HDR相关设置
            try:
                hdr_value, _ = winreg.QueryValueEx(key, "HDRContentSupported")
                self.hdr_enabled = bool(hdr_value)
            except:
                pass

            winreg.CloseKey(key)

            # 方法2：通过Windows API检测高级颜色支持
            try:
                # 获取显示器HDR能力
                self.hdr_enabled = self._check_display_hdr_capability()
            except:
                pass

        except Exception as e:
            print(f"HDR检测失败: {e}", file=sys.stderr)

    def _check_display_hdr_capability(self):
        """检查显示器HDR能力"""
        try:
            # 使用Windows.Graphics.HdrDetection API（需要Windows 10 1703+）
            # 这里使用简化的检测方法
            import subprocess

            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-WmiObject -Namespace root\\wmi -Class WmiMonitorBasicDisplayParams | Select-Object -First 1",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            # 如果命令执行成功，检查是否有HDR相关输出
            return "HDR" in result.stdout or "AdvancedColor" in result.stdout
        except:
            return False

    def capture_screenshot(self, region=None, apply_tone_mapping=True):
        """
        截图并应用HDR色调映射

        参数:
            region: 截图区域 (x, y, width, height)，None表示全屏
            apply_tone_mapping: 是否应用色调映射（HDR环境下自动启用）

        返回:
            PIL.Image对象
        """
        try:
            from PIL import Image, ImageGrab, ImageEnhance
            import numpy as np
        except ImportError:
            print("需要安装Pillow和numpy: pip install Pillow numpy", file=sys.stderr)
            return None

        # 截图
        if region:
            screenshot = ImageGrab.grab(bbox=region)
        else:
            screenshot = ImageGrab.grab()

        # 如果HDR启用且需要色调映射
        if self.hdr_enabled and apply_tone_mapping:
            screenshot = self._apply_hdr_tone_mapping(screenshot)

        return screenshot

    def _apply_hdr_tone_mapping(self, image):
        """
        应用HDR色调映射，防止过曝

        核心原理：
        1. 将HDR高动态范围压缩到SDR范围
        2. 保留暗部细节，压缩高光区域
        3. 应用Gamma校正
        """
        import numpy as np
        from PIL import ImageEnhance

        # 转换为numpy数组
        img_array = np.array(image, dtype=np.float32) / 255.0

        # 方法1：Reinhard色调映射
        # L = L / (1 + L) - 简单有效的高光压缩
        img_array = img_array / (1.0 + img_array)

        # 方法2：Gamma校正（修正整体亮度）
        gamma = 1.1  # 轻微提亮暗部
        img_array = np.power(img_array, 1.0 / gamma)

        # 方法3：限制最大值，防止过曝
        img_array = np.clip(img_array, 0, 1)

        # 转回PIL图像
        img_array = (img_array * 255).astype(np.uint8)
        result = Image.fromarray(img_array)

        # 方法4：调整对比度（可选）
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(0.95)  # 轻微降低对比度

        # 方法5：调整亮度（可选）
        brightness_enhancer = ImageEnhance.Brightness(result)
        result = brightness_enhancer.enhance(0.92)  # 轻微降低亮度

        return result

    def capture_with_sdr_fallback(self, region=None):
        """
        智能截图：HDR环境自动应用色调映射，SDR环境直接截图

        推荐使用此方法，自动适配HDR/SDR环境
        """
        return self.capture_screenshot(
            region=region, apply_tone_mapping=self.hdr_enabled
        )

    def save_screenshot(self, filename, region=None, format="PNG"):
        """
        截图并保存到文件

        参数:
            filename: 保存路径
            region: 截图区域
            format: 图片格式 (PNG/JPEG/BMP)
        """
        screenshot = self.capture_with_sdr_fallback(region)
        if screenshot:
            screenshot.save(filename, format=format)
            print(f"截图已保存: {filename}")
        return screenshot


# ============================================================
# 第四部分：应用程序主类（优化版）
# ============================================================


class WishlistCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("标题11111")

        # 窗口尺寸设置（优化：更合理的默认值）
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # 初始化HDR截图处理器
        self.hdr_handler = HDRScreenshotHandler()

        # 设置窗口图标
        self._setup_window_icon()

        # 设置DPI自适应样式
        self._setup_dpi_styles()

        # 创建UI
        self._create_ui()

    def _setup_window_icon(self):
        """设置窗口图标"""
        try:
            # 尝试加载图标
            icon_path = "icon.ico"  # 简化路径处理
            self.root.iconbitmap(icon_path)

            # Windows任务栏图标
            if sys.platform == "win32":
                windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "SteamWishlistChecker"
                )
        except Exception as e:
            print(f"图标加载失败: {e}", file=sys.stderr)

    def _setup_dpi_styles(self):
        """设置DPI自适应样式（简化版）"""
        style = ttk.Style()

        # 获取DPI缩放因子
        scale_factor = self._get_dpi_scale()

        # 计算缩放后的字体大小
        base_size = 10
        scaled_size = int(base_size * scale_factor)
        row_height = int(30 * scale_factor)

        # 统一设置样式
        style.configure(".", font=(SAFE_FONT, scaled_size))
        style.configure("Treeview", rowheight=row_height, font=(SAFE_FONT, scaled_size))
        style.configure("Treeview.Heading", font=(SAFE_FONT, scaled_size, "bold"))

    def _get_dpi_scale(self):
        """获取DPI缩放因子"""
        try:
            if sys.platform == "win32":
                dpi = windll.user32.GetDpiForWindow(self.root.winfo_id())
                return dpi / 96.0
        except:
            pass
        return 1.0

    def _create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 配置网格权重（响应式布局）
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 示例控件
        row = 0

        # 输入框
        ttk.Label(main_frame, text="输入内容:").grid(
            row=row, column=0, sticky="w", pady=5
        )
        self.entry = ttk.Entry(main_frame, width=50)
        self.entry.grid(row=row, column=1, sticky="ew", pady=5, padx=5)

        row += 1

        # 截图按钮（新增HDR支持）
        ttk.Button(
            main_frame, text="截图（HDR优化）", command=self._take_screenshot
        ).grid(row=row, column=0, columnspan=2, pady=10)

        row += 1

        # HDR状态显示
        hdr_status = "HDR已启用" if self.hdr_handler.hdr_enabled else "SDR模式"
        ttk.Label(
            main_frame, text=f"当前显示模式: {hdr_status}", font=(SAFE_FONT, 10, "bold")
        ).grid(row=row, column=0, columnspan=2, pady=5)

    def _take_screenshot(self):
        """截图并保存（HDR优化）"""
        from datetime import datetime

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"

        # 使用HDR处理器截图
        screenshot = self.hdr_handler.save_screenshot(filename)

        if screenshot:
            # 显示成功提示
            from tkinter import messagebox

            messagebox.showinfo(
                "截图成功",
                f"截图已保存到: {filename}\n"
                f"HDR色调映射: {'已应用' if self.hdr_handler.hdr_enabled else '未启用'}",
            )


# ============================================================
# 第五部分：主程序入口
# ============================================================


def main():
    """主函数"""
    root = tk.Tk()
    app = WishlistCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
