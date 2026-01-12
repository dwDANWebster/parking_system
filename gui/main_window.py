#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI主窗口模块

该模块负责智能停车场管理系统的GUI界面设计和实现，包括登录窗口、主界面、各种功能表单等。
使用Tkinter库构建，支持多种功能模块的界面展示和交互。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class MainWindow:
    """
    主窗口类
    
    该类负责整个GUI应用的主窗口管理，包括登录窗口、主界面、菜单等组件的创建和管理。
    """
    
    def __init__(self, parking_system):
        """
        初始化主窗口对象
        
        参数：
            parking_system: 停车场系统主对象
        """
        self.parking_system = parking_system
        self.root = None
        self.notebook = None
        self.current_user = None
        self.frames = {}
    
    def run(self):
        """
        启动GUI应用
        
        该方法执行以下操作：
        1. 创建主窗口
        2. 设置窗口图标
        3. 创建菜单栏
        4. 创建主框架
        5. 显示登录窗口
        6. 启动主循环
        """
        logger.info("启动GUI界面")
        try:
            # 创建主窗口
            self.root = tk.Tk()
            self.root.title("智能停车场管理系统")
            self.root.geometry("1200x800")
            self.root.resizable(True, True)
            
            # 设置窗口图标（如果有）
            self._set_window_icon()
            
            # 创建菜单栏
            self._create_menu()
            
            # 创建主框架
            self._create_main_frame()
            
            # 创建登录窗口
            self._show_login_window()
            
            # 启动主循环
            self.root.mainloop()
        except Exception as e:
            logger.error(f"GUI启动失败: {e}")
            raise
    
    def stop(self):
        """
        停止GUI应用
        
        该方法安全地关闭主窗口，释放资源。
        """
        logger.info("停止GUI界面")
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def _set_window_icon(self):
        """
        设置窗口图标
        
        该方法尝试加载并设置窗口图标，如果图标文件不存在则跳过。
        """
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "../resources/icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"设置窗口图标失败: {e}")
    
    def _create_menu(self):
        """
        创建菜单栏
        
        该方法创建应用的菜单栏，包括文件、车辆管理、车位管理、用户管理、费用管理、报表统计、系统设置和帮助等菜单。
        """
        # 创建菜单栏
        menu_bar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="退出系统", command=self.stop)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 车辆管理菜单
        vehicle_menu = tk.Menu(menu_bar, tearoff=0)
        vehicle_menu.add_command(label="车辆登记", command=self._show_vehicle_registration)
        vehicle_menu.add_command(label="车辆进出记录", command=self._show_vehicle_records)
        vehicle_menu.add_command(label="车辆查询", command=self._show_vehicle_query)
        menu_bar.add_cascade(label="车辆管理", menu=vehicle_menu)
        
        # 车位管理菜单
        space_menu = tk.Menu(menu_bar, tearoff=0)
        space_menu.add_command(label="车位分配", command=self._show_space_allocation)
        space_menu.add_command(label="车位状态", command=self._show_space_status)
        space_menu.add_command(label="车位管理", command=self._show_space_management)
        menu_bar.add_cascade(label="车位管理", menu=space_menu)
        
        # 用户管理菜单
        user_menu = tk.Menu(menu_bar, tearoff=0)
        user_menu.add_command(label="用户添加", command=self._show_user_add)
        user_menu.add_command(label="用户管理", command=self._show_user_management)
        user_menu.add_command(label="修改密码", command=self._show_change_password)
        menu_bar.add_cascade(label="用户管理", menu=user_menu)
        
        # 费用管理菜单
        fee_menu = tk.Menu(menu_bar, tearoff=0)
        fee_menu.add_command(label="收费规则设置", command=self._show_fee_rules)
        fee_menu.add_command(label="费用查询", command=self._show_fee_query)
        menu_bar.add_cascade(label="费用管理", menu=fee_menu)
        
        # 报表统计菜单
        report_menu = tk.Menu(menu_bar, tearoff=0)
        report_menu.add_command(label="日报表", command=self._show_daily_report)
        report_menu.add_command(label="周报表", command=self._show_weekly_report)
        report_menu.add_command(label="月报表", command=self._show_monthly_report)
        report_menu.add_command(label="年报表", command=self._show_annual_report)
        menu_bar.add_cascade(label="报表统计", menu=report_menu)
        
        # 系统设置菜单
        system_menu = tk.Menu(menu_bar, tearoff=0)
        system_menu.add_command(label="系统配置", command=self._show_system_config)
        system_menu.add_command(label="数据库备份", command=self._show_database_backup)
        system_menu.add_command(label="系统日志", command=self._show_system_logs)
        menu_bar.add_cascade(label="系统设置", menu=system_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于系统", command=self._show_about)
        help_menu.add_command(label="使用帮助", command=self._show_help)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        # 将菜单栏添加到主窗口
        self.root.config(menu=menu_bar)
    
    def _create_main_frame(self):
        """
        创建主框架
        
        该方法创建应用的主框架，用于容纳各种功能模块的界面。
        """
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 隐藏主框架，直到登录成功
        self.main_frame.pack_forget()
    
    def _show_login_window(self):
        """
        显示登录窗口
        
        该方法创建并显示登录窗口，用于用户身份验证。
        """
        # 创建登录窗口
        login_window = tk.Toplevel(self.root)
        login_window.title("登录")
        login_window.geometry("400x300")
        login_window.resizable(False, False)
        login_window.transient(self.root)
        login_window.grab_set()
        
        # 创建登录框架
        login_frame = ttk.Frame(login_window, padding="20")
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(login_frame, text="智能停车场管理系统", font=("Arial", 16))
        title_label.pack(pady=20)
        
        # 用户名标签和输入框
        username_frame = ttk.Frame(login_frame)
        username_frame.pack(fill=tk.X, pady=10)
        
        username_label = ttk.Label(username_frame, text="用户名:", width=10)
        username_label.pack(side=tk.LEFT, padx=5)
        
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.username_entry.focus()
        
        # 密码标签和输入框
        password_frame = ttk.Frame(login_frame)
        password_frame.pack(fill=tk.X, pady=10)
        
        password_label = ttk.Label(password_frame, text="密码:", width=10)
        password_label.pack(side=tk.LEFT, padx=5)
        
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 登录按钮
        login_button = ttk.Button(login_frame, text="登录", command=lambda: self._login(login_window))
        login_button.pack(pady=20)
        
        # 绑定回车键登录
        self.username_entry.bind("<Return>", lambda event: self._login(login_window))
        self.password_entry.bind("<Return>", lambda event: self._login(login_window))
    
    def _login(self, login_window):
        """
        处理登录逻辑
        
        参数：
            login_window: 登录窗口对象
        """
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("登录失败", "用户名和密码不能为空")
            return
        
        # 调用用户管理器进行身份验证
        auth_result = self.parking_system.user_manager.authenticate_user(username, password)
        
        if auth_result:
            self.current_user = {
                "username": username,
                "user_id": auth_result["user_id"],
                "role": auth_result["role"]
            }
            
            logger.info(f"用户登录成功: {username}")
            messagebox.showinfo("登录成功", f"欢迎回来，{username}!")
            
            # 关闭登录窗口
            login_window.destroy()
            
            # 显示主框架
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 显示默认界面
            self._show_dashboard()
        else:
            logger.warning(f"用户登录失败: {username}")
            messagebox.showerror("登录失败", "用户名或密码错误")
    
    def _show_dashboard(self):
        """
        显示仪表盘界面
        
        该方法创建并显示系统仪表盘，展示系统状态、统计信息等。
        """
        # 检查是否已存在仪表盘选项卡
        if "dashboard" in self.frames:
            self.notebook.select(self.frames["dashboard"])
            return
        
        # 创建仪表盘框架
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="仪表盘")
        self.frames["dashboard"] = dashboard_frame
        
        # 创建欢迎标签
        welcome_label = ttk.Label(
            dashboard_frame, 
            text=f"欢迎使用智能停车场管理系统，{self.current_user['username']}!",
            font=("Arial", 14)
        )
        welcome_label.pack(pady=20)
        
        # 创建系统状态框架
        status_frame = ttk.LabelFrame(dashboard_frame, text="系统状态", padding="10")
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 获取系统状态
        system_status = self.parking_system.system_manager.get_system_status()
        
        # 创建状态标签
        status_info = f"""
        数据库状态: {system_status['database']}
        总车辆数: {system_status['total_vehicles']}
        停车中车辆数: {system_status['parking_vehicles']}
        总车位数: {system_status['total_spaces']}
        已占用车位数: {system_status['occupied_spaces']}
        可用车位数: {system_status['available_spaces']}
        车位使用率: {system_status['space_usage_rate']}%
        """
        status_label = ttk.Label(status_frame, text=status_info, justify=tk.LEFT)
        status_label.pack(anchor=tk.W)
        
        # 创建快速操作按钮框架
        quick_actions_frame = ttk.LabelFrame(dashboard_frame, text="快速操作", padding="10")
        quick_actions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 创建快速操作按钮
        button_frame = ttk.Frame(quick_actions_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="车辆登记", command=self._show_vehicle_registration).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(button_frame, text="车位分配", command=self._show_space_allocation).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(button_frame, text="费用查询", command=self._show_fee_query).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(button_frame, text="日报表", command=self._show_daily_report).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(button_frame, text="系统配置", command=self._show_system_config).pack(side=tk.LEFT, padx=10, pady=5)
    
    def _show_vehicle_registration(self):
        """
        显示车辆登记界面
        """
        logger.info("显示车辆登记界面")
        # 实现车辆登记界面
        pass
    
    def _show_vehicle_records(self):
        """
        显示车辆进出记录界面
        """
        logger.info("显示车辆进出记录界面")
        # 实现车辆进出记录界面
        pass
    
    def _show_vehicle_query(self):
        """
        显示车辆查询界面
        """
        logger.info("显示车辆查询界面")
        # 实现车辆查询界面
        pass
    
    def _show_space_allocation(self):
        """
        显示车位分配界面
        """
        logger.info("显示车位分配界面")
        # 实现车位分配界面
        pass
    
    def _show_space_status(self):
        """
        显示车位状态界面
        """
        logger.info("显示车位状态界面")
        # 实现车位状态界面
        pass
    
    def _show_space_management(self):
        """
        显示车位管理界面
        """
        logger.info("显示车位管理界面")
        # 实现车位管理界面
        pass
    
    def _show_user_add(self):
        """
        显示用户添加界面
        """
        logger.info("显示用户添加界面")
        # 实现用户添加界面
        pass
    
    def _show_user_management(self):
        """
        显示用户管理界面
        """
        logger.info("显示用户管理界面")
        # 实现用户管理界面
        pass
    
    def _show_change_password(self):
        """
        显示修改密码界面
        """
        logger.info("显示修改密码界面")
        # 实现修改密码界面
        pass
    
    def _show_fee_rules(self):
        """
        显示收费规则设置界面
        """
        logger.info("显示收费规则设置界面")
        # 实现收费规则设置界面
        pass
    
    def _show_fee_query(self):
        """
        显示费用查询界面
        """
        logger.info("显示费用查询界面")
        # 实现费用查询界面
        pass
    
    def _show_daily_report(self):
        """
        显示日报表界面
        """
        logger.info("显示日报表界面")
        # 实现日报表界面
        pass
    
    def _show_weekly_report(self):
        """
        显示周报表界面
        """
        logger.info("显示周报表界面")
        # 实现周报表界面
        pass
    
    def _show_monthly_report(self):
        """
        显示月报表界面
        """
        logger.info("显示月报表界面")
        # 实现月报表界面
        pass
    
    def _show_annual_report(self):
        """
        显示年报表界面
        """
        logger.info("显示年报表界面")
        # 实现年报表界面
        pass
    
    def _show_system_config(self):
        """
        显示系统配置界面
        """
        logger.info("显示系统配置界面")
        # 实现系统配置界面
        pass
    
    def _show_database_backup(self):
        """
        显示数据库备份界面
        """
        logger.info("显示数据库备份界面")
        # 实现数据库备份界面
        pass
    
    def _show_system_logs(self):
        """
        显示系统日志界面
        """
        logger.info("显示系统日志界面")
        # 实现系统日志界面
        pass
    
    def _show_about(self):
        """
        显示关于界面
        """
        logger.info("显示关于界面")
        about_info = """
智能停车场管理系统
版本: 1.0.0

该系统是一个功能完整的智能停车场管理解决方案，
支持车辆管理、车位管理、用户管理、费用管理、
报表统计等核心功能。
        """
        messagebox.showinfo("关于系统", about_info)
    
    def _show_help(self):
        """
        显示帮助界面
        """
        logger.info("显示帮助界面")
        help_info = """
使用帮助:

1. 车辆管理: 用于登记车辆、查看车辆进出记录、查询车辆信息
2. 车位管理: 用于分配车位、查看车位状态、管理车位信息
3. 用户管理: 用于添加用户、管理用户信息、修改密码
4. 费用管理: 用于设置收费规则、查询停车费用
5. 报表统计: 用于生成日报表、周报表、月报表、年报表
6. 系统设置: 用于配置系统参数、备份数据库、查看系统日志

如需更多帮助，请联系系统管理员。
        """
        messagebox.showinfo("使用帮助", help_info)
