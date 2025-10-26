# 高分辨率屏幕适配解决方案 - 增强版
if sys.platform == "win32":
    try:
        # 导入Windows系统API
        from ctypes import windll, c_int
        
        # 关键DPI设置：启用DPI感知（解决模糊问题）
        # 使用更全面的DPI感知设置方案
        # 尝试设置Per-Monitor DPI Aware (级别2)
        try:
            # 现代Windows系统的最佳实践
            windll.shcore.SetProcessDpiAwareness(2)
        except:
            # 兼容旧版Windows系统（Windows 8.1及更早版本）
            windll.user32.SetProcessDPIAware()
        
        # 添加：为所有窗口启用非客户区DPI缩放
        # 这确保窗口边框和标题栏也能正确缩放
        windll.user32.EnableNonClientDpiScaling(c_int(1))
    except Exception as e:
        print(f"DPI设置出错: {e}", file=sys.stderr)
        # 忽略可能的兼容性问题，不影响主要功能

# 安全字体选择方案 - 使用跨平台通用字体
# 避免使用微软雅黑等有版权风险的字体
# 使用系统默认字体 + 安全备用方案
def get_safe_font():
    """获取安全、无版权风险的字体"""
    # 首选系统默认字体
    if sys.platform.startswith("win"):
        # Windows系统 - 使用Tahoma字体（Windows自带，无版权问题）
        return "Tahoma"
    elif sys.platform.startswith("darwin"):
        # macOS系统 - 使用Helvetica字体（macOS自带）
        return "Helvetica"
    else:
        # Linux及其他系统 - 使用DejaVu Sans字体（开源免费）
        return "DejaVu Sans"

# 在全局范围内定义字体
safe_font = get_safe_font()

class WishlistCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("标题11111")
        
        # 核心修复：增大默认窗口尺寸 + 设置最小尺寸
        # 确保在高分辨率屏幕上控件布局正常
        self.root.geometry("1200x800")  # 默认窗口放大到1200x800（原1000x700）
        self.root.minsize(1000, 700)   # 禁止窗口小于1000x700，防止控件被压缩
        
        # 添加：设置窗口图标缩放
        # 确保图标在高DPI屏幕上清晰显示
        try:
            # 使用资源路径获取图标
            icon_path = resource_path("icon.ico")
            # 设置窗口图标
            self.root.iconbitmap(icon_path)
            # 添加任务栏图标
            if sys.platform.startswith("win"):
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SteamWishlistChecker")
        except Exception as e:
            print(f"图标加载失败: {e}", file=sys.stderr)
        
        # 添加：字体大小自适应
        # 根据DPI缩放调整字体大小
        try:
            # 获取系统DPI缩放
            dpi = ctypes.windll.user32.GetDpiForWindow(root.winfo_id())
            scale_factor = dpi / 96.0
            
            # 设置基础字体大小
            base_font_size = 10
            scaled_font_size = int(base_font_size * scale_factor)
            
            # 创建样式对象
            style = ttk.Style()
            
            # 设置默认字体 - 使用安全字体
            style.configure(".", font=(safe_font, scaled_font_size))
            
            # 设置Treeview字体
            style.configure("Treeview", 
                           rowheight=int(30 * scale_factor),
                           font=(safe_font, scaled_font_size))
            
            # 设置表头字体
            style.configure("Treeview.Heading", 
                           font=(safe_font, scaled_font_size, "bold"))
        except:
            # 如果DPI获取失败，使用默认字体大小
            style = ttk.Style()
            style.configure(".", font=(safe_font, 10))
            style.configure("Treeview", 
                           rowheight=30,
                           font=(safe_font, 10))
            style.configure("Treeview.Heading", 
                           font=(safe_font, 10, "bold"))
        
        # 其余初始化代码保持不变...
