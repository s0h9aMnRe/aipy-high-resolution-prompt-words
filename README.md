# aipy-high-resolution-prompt-words
添加了 windll.shcore.SetProcessDpiAwareness(1) 让程序感知高分屏<br>
设置了 tk.scaling 自动调整UI缩放<br>
使用"思源黑体"字体<br>
加大了字号和控件间距<br>
使用Frame和Canvas确保兼容性<br>
添加滚动条，防止控件溢出<br>
确保字段映射区域100%显示出来<br>

默认窗口放大到900x600，并设置最小尺寸800x500，确保打开就能看到所有控件<br>
响应式布局：控件会自动填满窗口空间，不会被压缩（比如输入框会横向扩展）<br>
字段映射区优化：<br>
增加控件间距（pady=8），避免拥挤<br>
选择框加宽到40字符，标签加粗<br>
滚动条自适应内容，字段再多也能看到<br>
禁止窗口过小：通过minsize防止用户把窗口拖到看不见控件<br>

使用Windows API SetProcessDpiAwareness(1) 设置系统级DPI感知<br>
参数值：1（系统DPI感知模式）<br>
作用：让应用程序正确识别系统的DPI设置，避免界面模糊或缩放不正确<br>

通过 tk.scaling 动态调整界面缩放比例<br>
参数值：根据系统DPI自动计算，例如：<br>
100% DPI → 1.0<br>
125% DPI → 1.25<br>
150% DPI → 1.5<br>
200% DPI → 2.0<br>
作用：确保界面元素在不同分辨率下保持合适大小<br>

字体大小：<br>
标签（Label）：10（例如：font=("微软雅黑",10)）<br>
按钮（Button）：10<br>
输入框（Entry）：10<br>
结果提示：11（加粗）<br>
作用：保证文字在高分辨率下清晰可读<br>

响应式布局：使用 grid_columnconfigure 设置列权重，例如 grid_columnconfigure(1, weight=1)<br>
控件间距：<br>
水平间距（padx）：5-10像素<br>
垂直间距（pady）：5-10像素<br>
进度条参数：thickness=20（确保进度条在高分辨率下清晰可见）<br>
作用：让界面元素自动适应窗口大小变化，保持布局合理性<br>
水平间距（padx）：5-10像素
垂直间距（pady）：5-10像素
进度条参数：thickness=20（确保进度条在高分辨率下清晰可见）
作用：让界面元素自动适应窗口大小变化，保持布局合理性
