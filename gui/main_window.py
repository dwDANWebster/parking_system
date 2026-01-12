import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class MainWindow:
    def __init__(self, parking_system):
        self.parking_system = parking_system
        self.root = None
        self.notebook = None
        self.current_user = None
        self.frames = {}
    
    def run(self):
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
        logger.info("停止GUI界面")
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def _set_window_icon(self):
        # 设置窗口图标（如果有）
        pass
    
    def _create_menu(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="退出系统", command=self.stop)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 系统菜单
        system_menu = tk.Menu(menubar, tearoff=0)
        system_menu.add_command(label="系统配置", command=self._show_system_config_window)
        system_menu.add_command(label="数据库备份", command=self._show_database_backup_window)
        system_menu.add_command(label="系统状态", command=self._show_system_status_window)
        menubar.add_cascade(label="系统", menu=system_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about_window)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _create_main_frame(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个功能标签页
        self._create_vehicle_management_tab()
        self._create_parking_space_tab()
        self._create_user_management_tab()
        self._create_fee_management_tab()
        self._create_report_tab()
        self._create_log_tab()
        
        # 默认隐藏所有标签页，登录后显示
        self.notebook.pack_forget()
    
    def _show_login_window(self):
        # 创建登录窗口
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("用户登录")
        self.login_window.geometry("400x300")
        self.login_window.resizable(False, False)
        
        # 登录窗口居中
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        
        # 创建登录表单
        login_frame = ttk.Frame(self.login_window, padding="20")
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(login_frame, text="智能停车场管理系统", font=("Arial", 16))
        title_label.pack(pady=20)
        
        # 用户名
        username_frame = ttk.Frame(login_frame)
        username_frame.pack(fill=tk.X, pady=10)
        
        username_label = ttk.Label(username_frame, text="用户名:", width=10)
        username_label.pack(side=tk.LEFT, padx=5)
        
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.username_entry.focus()
        
        # 密码
        password_frame = ttk.Frame(login_frame)
        password_frame.pack(fill=tk.X, pady=10)
        
        password_label = ttk.Label(password_frame, text="密码:", width=10)
        password_label.pack(side=tk.LEFT, padx=5)
        
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 登录按钮
        login_button = ttk.Button(login_frame, text="登录", command=self._handle_login)
        login_button.pack(pady=20, fill=tk.X)
        
        # 绑定回车键登录
        self.login_window.bind('<Return>', lambda event: self._handle_login())
    
    def _handle_login(self):
        # 处理登录
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("警告", "请输入用户名和密码")
            return
        
        try:
            # 调用用户管理器进行登录验证
            self.current_user = self.parking_system.user_manager.login(username, password)
            
            # 登录成功
            self.login_window.destroy()
            messagebox.showinfo("成功", f"欢迎回来，{username}！")
            
            # 显示主标签页
            self.notebook.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("错误", f"登录失败: {e}")
    
    def _create_vehicle_management_tab(self):
        # 创建车辆管理标签页
        vehicle_frame = ttk.Frame(self.notebook)
        self.notebook.add(vehicle_frame, text="车辆管理")
        
        # 顶部工具栏
        toolbar = ttk.Frame(vehicle_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 车辆进场按钮
        entry_button = ttk.Button(toolbar, text="车辆进场", command=self._show_vehicle_entry_window)
        entry_button.pack(side=tk.LEFT, padx=5)
        
        # 车辆出场按钮
        exit_button = ttk.Button(toolbar, text="车辆出场", command=self._show_vehicle_exit_window)
        exit_button.pack(side=tk.LEFT, padx=5)
        
        # 车辆注册按钮
        register_button = ttk.Button(toolbar, text="车辆注册", command=self._show_vehicle_register_window)
        register_button.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_button = ttk.Button(toolbar, text="刷新", command=self._refresh_vehicle_table)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        search_label = ttk.Label(search_frame, text="搜索:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.vehicle_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.vehicle_search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_button = ttk.Button(search_frame, text="搜索", command=self._search_vehicles)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # 表格框架
        table_frame = ttk.Frame(vehicle_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ("id", "车牌号码", "车辆类型", "品牌", "型号", "颜色", "状态", "入场时间", "出场时间", "车位ID")
        self.vehicle_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # 设置列宽
        for col in columns:
            self.vehicle_tree.heading(col, text=col)
            self.vehicle_tree.column(col, width=100)
        
        # 设置滚动条
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.vehicle_tree.yview)
        self.vehicle_tree.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.vehicle_tree.xview)
        self.vehicle_tree.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.vehicle_tree.pack(fill=tk.BOTH, expand=True)
        
        # 右键菜单
        self.vehicle_tree.bind("<Button-3>", self._show_vehicle_context_menu)
        self.vehicle_context_menu = tk.Menu(self.vehicle_tree, tearoff=0)
        self.vehicle_context_menu.add_command(label="查看详情", command=self._show_vehicle_detail)
        self.vehicle_context_menu.add_command(label="编辑车辆", command=self._edit_vehicle)
        self.vehicle_context_menu.add_command(label="删除车辆", command=self._delete_vehicle)
    
    def _refresh_vehicle_table(self):
        # 刷新车辆表格
        # 清空表格
        for item in self.vehicle_tree.get_children():
            self.vehicle_tree.delete(item)
        
        # 获取所有车辆
        vehicles = self.parking_system.vehicle_manager.get_all_vehicles()
        
        # 插入数据
        for vehicle in vehicles:
            self.vehicle_tree.insert("", tk.END, values=(
                vehicle.id,
                vehicle.plate_number,
                vehicle.vehicle_type,
                vehicle.brand or "",
                vehicle.model or "",
                vehicle.color or "",
                vehicle.status,
                vehicle.entry_time or "",
                vehicle.exit_time or "",
                vehicle.parking_space_id or ""
            ))
    
    def _search_vehicles(self):
        # 搜索车辆
        search_text = self.vehicle_search_var.get().strip()
        if not search_text:
            self._refresh_vehicle_table()
            return
        
        # 清空表格
        for item in self.vehicle_tree.get_children():
            self.vehicle_tree.delete(item)
        
        # 获取所有车辆
        vehicles = self.parking_system.vehicle_manager.get_all_vehicles()
        
        # 过滤车辆
        filtered_vehicles = []
        for vehicle in vehicles:
            if search_text in str(vehicle.plate_number) or search_text in str(vehicle.vehicle_type):
                filtered_vehicles.append(vehicle)
        
        # 插入数据
        for vehicle in filtered_vehicles:
            self.vehicle_tree.insert("", tk.END, values=(
                vehicle.id,
                vehicle.plate_number,
                vehicle.vehicle_type,
                vehicle.brand or "",
                vehicle.model or "",
                vehicle.color or "",
                vehicle.status,
                vehicle.entry_time or "",
                vehicle.exit_time or "",
                vehicle.parking_space_id or ""
            ))
    
    def _show_vehicle_context_menu(self, event):
        # 显示车辆右键菜单
        item = self.vehicle_tree.identify_row(event.y)
        if item:
            self.vehicle_tree.selection_set(item)
            self.vehicle_context_menu.post(event.x_root, event.y_root)
    
    def _show_vehicle_detail(self):
        # 查看车辆详情
        selected_items = self.vehicle_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一辆车")
            return
        
        item = selected_items[0]
        values = self.vehicle_tree.item(item, "values")
        vehicle_id = values[0]
        
        # 获取车辆详情
        vehicle = self.parking_system.vehicle_manager.get_vehicle_by_id(vehicle_id)
        
        # 显示详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"车辆详情 - {vehicle.plate_number}")
        detail_window.geometry("400x300")
        
        # 创建详情表单
        detail_frame = ttk.Frame(detail_window, padding="20")
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # 显示车辆信息
        info_text = f"ID: {vehicle.id}\n"
        info_text += f"车牌号码: {vehicle.plate_number}\n"
        info_text += f"车辆类型: {vehicle.vehicle_type}\n"
        info_text += f"品牌: {vehicle.brand or '无'}\n"
        info_text += f"型号: {vehicle.model or '无'}\n"
        info_text += f"颜色: {vehicle.color or '无'}\n"
        info_text += f"状态: {vehicle.status}\n"
        info_text += f"入场时间: {vehicle.entry_time or '无'}\n"
        info_text += f"出场时间: {vehicle.exit_time or '无'}\n"
        info_text += f"车位ID: {vehicle.parking_space_id or '无'}\n"
        info_text += f"创建时间: {vehicle.created_at}\n"
        info_text += f"更新时间: {vehicle.updated_at}\n"
        
        info_label = ttk.Label(detail_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(fill=tk.BOTH, expand=True)
    
    def _edit_vehicle(self):
        # 编辑车辆信息
        selected_items = self.vehicle_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一辆车")
            return
        
        item = selected_items[0]
        values = self.vehicle_tree.item(item, "values")
        vehicle_id = values[0]
        
        # 获取车辆详情
        vehicle = self.parking_system.vehicle_manager.get_vehicle_by_id(vehicle_id)
        
        # 显示编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑车辆 - {vehicle.plate_number}")
        edit_window.geometry("400x300")
        
        # 创建编辑表单
        edit_frame = ttk.Frame(edit_window, padding="20")
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # 车牌号码（只读）
        plate_frame = ttk.Frame(edit_frame)
        plate_frame.pack(fill=tk.X, pady=5)
        
        plate_label = ttk.Label(plate_frame, text="车牌号码:", width=10)
        plate_label.pack(side=tk.LEFT, padx=5)
        
        plate_entry = ttk.Entry(plate_frame)
        plate_entry.insert(0, vehicle.plate_number)
        plate_entry.config(state=tk.DISABLED)
        plate_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 车辆类型
        type_frame = ttk.Frame(edit_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        type_label = ttk.Label(type_frame, text="车辆类型:", width=10)
        type_label.pack(side=tk.LEFT, padx=5)
        
        type_var = tk.StringVar(value=vehicle.vehicle_type)
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=["小型车", "大型车", "新能源汽车"])
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 品牌
        brand_frame = ttk.Frame(edit_frame)
        brand_frame.pack(fill=tk.X, pady=5)
        
        brand_label = ttk.Label(brand_frame, text="品牌:", width=10)
        brand_label.pack(side=tk.LEFT, padx=5)
        
        brand_entry = ttk.Entry(brand_frame)
        brand_entry.insert(0, vehicle.brand or "")
        brand_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 型号
        model_frame = ttk.Frame(edit_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        model_label = ttk.Label(model_frame, text="型号:", width=10)
        model_label.pack(side=tk.LEFT, padx=5)
        
        model_entry = ttk.Entry(model_frame)
        model_entry.insert(0, vehicle.model or "")
        model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 颜色
        color_frame = ttk.Frame(edit_frame)
        color_frame.pack(fill=tk.X, pady=5)
        
        color_label = ttk.Label(color_frame, text="颜色:", width=10)
        color_label.pack(side=tk.LEFT, padx=5)
        
        color_entry = ttk.Entry(color_frame)
        color_entry.insert(0, vehicle.color or "")
        color_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_button = ttk.Button(button_frame, text="保存", command=lambda: self._save_vehicle_edit(edit_window, vehicle_id, type_var.get(), brand_entry.get(), model_entry.get(), color_entry.get()))
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=edit_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _save_vehicle_edit(self, window, vehicle_id, vehicle_type, brand, model, color):
        # 保存车辆编辑
        try:
            self.parking_system.vehicle_manager.update_vehicle(
                vehicle_id,
                vehicle_type=vehicle_type,
                brand=brand,
                model=model,
                color=color
            )
            messagebox.showinfo("成功", "车辆信息更新成功")
            window.destroy()
            self._refresh_vehicle_table()
        except Exception as e:
            messagebox.showerror("错误", f"更新失败: {e}")
    
    def _delete_vehicle(self):
        # 删除车辆
        selected_items = self.vehicle_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一辆车")
            return
        
        item = selected_items[0]
        values = self.vehicle_tree.item(item, "values")
        vehicle_id = values[0]
        plate_number = values[1]
        
        # 确认删除
        if messagebox.askyesno("确认", f"确定要删除车辆 {plate_number} 吗？"):
            try:
                self.parking_system.vehicle_manager.delete_vehicle(vehicle_id)
                messagebox.showinfo("成功", "车辆删除成功")
                self._refresh_vehicle_table()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")
    
    def _show_vehicle_entry_window(self):
        # 显示车辆进场窗口
        entry_window = tk.Toplevel(self.root)
        entry_window.title("车辆进场")
        entry_window.geometry("400x200")
        
        # 创建进场表单
        entry_frame = ttk.Frame(entry_window, padding="20")
        entry_frame.pack(fill=tk.BOTH, expand=True)
        
        # 车牌号码
        plate_frame = ttk.Frame(entry_frame)
        plate_frame.pack(fill=tk.X, pady=10)
        
        plate_label = ttk.Label(plate_frame, text="车牌号码:", width=10)
        plate_label.pack(side=tk.LEFT, padx=5)
        
        plate_entry = ttk.Entry(plate_frame)
        plate_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        plate_entry.focus()
        
        # 底部按钮
        button_frame = ttk.Frame(entry_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        confirm_button = ttk.Button(button_frame, text="确认进场", command=lambda: self._handle_vehicle_entry(entry_window, plate_entry.get()))
        confirm_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=entry_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _handle_vehicle_entry(self, window, plate_number):
        # 处理车辆进场
        plate_number = plate_number.strip()
        if not plate_number:
            messagebox.showwarning("警告", "请输入车牌号码")
            return
        
        try:
            # 分配车位
            space_id = self.parking_system.space_manager.allocation_algorithm.allocate_space("小型车")
            if not space_id:
                messagebox.showerror("错误", "没有可用车位")
                return
            
            # 记录车辆进场
            self.parking_system.vehicle_manager.record_entry(plate_number, space_id)
            
            # 更新车位状态
            self.parking_system.space_manager.occupy_space(space_id)
            
            messagebox.showinfo("成功", f"车辆 {plate_number} 进场成功，分配车位 ID: {space_id}")
            window.destroy()
            
            # 刷新车辆表格和车位表格
            self._refresh_vehicle_table()
            self._refresh_parking_space_table()
            
        except Exception as e:
            messagebox.showerror("错误", f"车辆进场失败: {e}")
    
    def _show_vehicle_exit_window(self):
        # 显示车辆出场窗口
        exit_window = tk.Toplevel(self.root)
        exit_window.title("车辆出场")
        exit_window.geometry("400x200")
        
        # 创建出场表单
        exit_frame = ttk.Frame(exit_window, padding="20")
        exit_frame.pack(fill=tk.BOTH, expand=True)
        
        # 车牌号码
        plate_frame = ttk.Frame(exit_frame)
        plate_frame.pack(fill=tk.X, pady=10)
        
        plate_label = ttk.Label(plate_frame, text="车牌号码:", width=10)
        plate_label.pack(side=tk.LEFT, padx=5)
        
        plate_entry = ttk.Entry(plate_frame)
        plate_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        plate_entry.focus()
        
        # 底部按钮
        button_frame = ttk.Frame(exit_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        confirm_button = ttk.Button(button_frame, text="确认出场", command=lambda: self._handle_vehicle_exit(exit_window, plate_entry.get()))
        confirm_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=exit_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _handle_vehicle_exit(self, window, plate_number):
        # 处理车辆出场
        plate_number = plate_number.strip()
        if not plate_number:
            messagebox.showwarning("警告", "请输入车牌号码")
            return
        
        try:
            # 记录车辆出场
            record_id = self.parking_system.vehicle_manager.record_exit(plate_number)
            
            # 获取车辆信息
            vehicle = self.parking_system.vehicle_manager.get_vehicle_by_plate(plate_number)
            
            # 处理支付
            payment_result = self.parking_system.fee_manager.process_exit_payment(plate_number, "cash")
            
            # 释放车位
            self.parking_system.space_manager.release_space(vehicle.parking_space_id)
            
            messagebox.showinfo("成功", f"车辆 {plate_number} 出场成功，费用: {payment_result['fee']}元")
            window.destroy()
            
            # 刷新车辆表格和车位表格
            self._refresh_vehicle_table()
            self._refresh_parking_space_table()
            
        except Exception as e:
            messagebox.showerror("错误", f"车辆出场失败: {e}")
    
    def _show_vehicle_register_window(self):
        # 显示车辆注册窗口
        register_window = tk.Toplevel(self.root)
        register_window.title("车辆注册")
        register_window.geometry("400x300")
        
        # 创建注册表单
        register_frame = ttk.Frame(register_window, padding="20")
        register_frame.pack(fill=tk.BOTH, expand=True)
        
        # 车牌号码
        plate_frame = ttk.Frame(register_frame)
        plate_frame.pack(fill=tk.X, pady=5)
        
        plate_label = ttk.Label(plate_frame, text="车牌号码:", width=10)
        plate_label.pack(side=tk.LEFT, padx=5)
        
        plate_entry = ttk.Entry(plate_frame)
        plate_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        plate_entry.focus()
        
        # 车辆类型
        type_frame = ttk.Frame(register_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        type_label = ttk.Label(type_frame, text="车辆类型:", width=10)
        type_label.pack(side=tk.LEFT, padx=5)
        
        type_var = tk.StringVar(value="小型车")
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=["小型车", "大型车", "新能源汽车"])
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 品牌
        brand_frame = ttk.Frame(register_frame)
        brand_frame.pack(fill=tk.X, pady=5)
        
        brand_label = ttk.Label(brand_frame, text="品牌:", width=10)
        brand_label.pack(side=tk.LEFT, padx=5)
        
        brand_entry = ttk.Entry(brand_frame)
        brand_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 型号
        model_frame = ttk.Frame(register_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        model_label = ttk.Label(model_frame, text="型号:", width=10)
        model_label.pack(side=tk.LEFT, padx=5)
        
        model_entry = ttk.Entry(model_frame)
        model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 颜色
        color_frame = ttk.Frame(register_frame)
        color_frame.pack(fill=tk.X, pady=5)
        
        color_label = ttk.Label(color_frame, text="颜色:", width=10)
        color_label.pack(side=tk.LEFT, padx=5)
        
        color_entry = ttk.Entry(color_frame)
        color_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(register_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        register_button = ttk.Button(button_frame, text="注册", command=lambda: self._handle_vehicle_register(register_window, plate_entry.get(), type_var.get(), brand_entry.get(), model_entry.get(), color_entry.get()))
        register_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=register_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _handle_vehicle_register(self, window, plate_number, vehicle_type, brand, model, color):
        # 处理车辆注册
        plate_number = plate_number.strip()
        if not plate_number:
            messagebox.showwarning("警告", "请输入车牌号码")
            return
        
        try:
            # 注册车辆
            self.parking_system.vehicle_manager.register_vehicle(plate_number, vehicle_type, brand, model, color)
            
            messagebox.showinfo("成功", f"车辆 {plate_number} 注册成功")
            window.destroy()
            
            # 刷新车辆表格
            self._refresh_vehicle_table()
            
        except Exception as e:
            messagebox.showerror("错误", f"车辆注册失败: {e}")
    
    def _create_parking_space_tab(self):
        # 创建车位管理标签页
        space_frame = ttk.Frame(self.notebook)
        self.notebook.add(space_frame, text="车位管理")
        
        # 顶部工具栏
        toolbar = ttk.Frame(space_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加车位按钮
        add_button = ttk.Button(toolbar, text="添加车位", command=self._show_add_parking_space_window)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_button = ttk.Button(toolbar, text="刷新", command=self._refresh_parking_space_table)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        search_label = ttk.Label(search_frame, text="搜索:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.space_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.space_search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_button = ttk.Button(search_frame, text="搜索", command=self._search_parking_spaces)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # 表格框架
        table_frame = ttk.Frame(space_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ("id", "车位号", "楼层", "车位类型", "状态", "是否预订", "预订用户ID")
        self.space_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # 设置列宽
        for col in columns:
            self.space_tree.heading(col, text=col)
            self.space_tree.column(col, width=100)
        
        # 设置滚动条
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.space_tree.yview)
        self.space_tree.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.space_tree.xview)
        self.space_tree.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.space_tree.pack(fill=tk.BOTH, expand=True)
        
        # 右键菜单
        self.space_tree.bind("<Button-3>", self._show_space_context_menu)
        self.space_context_menu = tk.Menu(self.space_tree, tearoff=0)
        self.space_context_menu.add_command(label="查看详情", command=self._show_space_detail)
        self.space_context_menu.add_command(label="编辑车位", command=self._edit_space)
        self.space_context_menu.add_command(label="删除车位", command=self._delete_space)
        self.space_context_menu.add_separator()
        self.space_context_menu.add_command(label="释放车位", command=self._release_space)
    
    def _refresh_parking_space_table(self):
        # 刷新车位表格
        # 清空表格
        for item in self.space_tree.get_children():
            self.space_tree.delete(item)
        
        # 获取所有车位
        spaces = self.parking_system.space_manager.get_all_spaces()
        
        # 插入数据
        for space in spaces:
            self.space_tree.insert("", tk.END, values=(
                space.id,
                space.space_number,
                space.floor,
                space.space_type,
                space.status,
                "是" if space.is_reserved else "否",
                space.reserved_user_id or ""
            ))
    
    def _search_parking_spaces(self):
        # 搜索车位
        search_text = self.space_search_var.get().strip()
        if not search_text:
            self._refresh_parking_space_table()
            return
        
        # 清空表格
        for item in self.space_tree.get_children():
            self.space_tree.delete(item)
        
        # 获取所有车位
        spaces = self.parking_system.space_manager.get_all_spaces()
        
        # 过滤车位
        filtered_spaces = []
        for space in spaces:
            if search_text in str(space.space_number) or search_text in str(space.space_type) or search_text in str(space.floor):
                filtered_spaces.append(space)
        
        # 插入数据
        for space in filtered_spaces:
            self.space_tree.insert("", tk.END, values=(
                space.id,
                space.space_number,
                space.floor,
                space.space_type,
                space.status,
                "是" if space.is_reserved else "否",
                space.reserved_user_id or ""
            ))
    
    def _show_space_context_menu(self, event):
        # 显示车位右键菜单
        item = self.space_tree.identify_row(event.y)
        if item:
            self.space_tree.selection_set(item)
            self.space_context_menu.post(event.x_root, event.y_root)
    
    def _show_space_detail(self):
        # 查看车位详情
        selected_items = self.space_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个车位")
            return
        
        item = selected_items[0]
        values = self.space_tree.item(item, "values")
        space_id = values[0]
        
        # 获取车位详情
        space = self.parking_system.space_manager.get_space_by_id(space_id)
        
        # 显示详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"车位详情 - {space.space_number}")
        detail_window.geometry("400x300")
        
        # 创建详情表单
        detail_frame = ttk.Frame(detail_window, padding="20")
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # 显示车位信息
        info_text = f"ID: {space.id}\n"
        info_text += f"车位号: {space.space_number}\n"
        info_text += f"楼层: {space.floor}\n"
        info_text += f"车位类型: {space.space_type}\n"
        info_text += f"状态: {space.status}\n"
        info_text += f"是否预订: {'是' if space.is_reserved else '否'}\n"
        info_text += f"预订用户ID: {space.reserved_user_id or '无'}\n"
        info_text += f"创建时间: {space.created_at}\n"
        info_text += f"更新时间: {space.updated_at}\n"
        
        info_label = ttk.Label(detail_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(fill=tk.BOTH, expand=True)
    
    def _edit_space(self):
        # 编辑车位信息
        selected_items = self.space_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个车位")
            return
        
        item = selected_items[0]
        values = self.space_tree.item(item, "values")
        space_id = values[0]
        
        # 获取车位详情
        space = self.parking_system.space_manager.get_space_by_id(space_id)
        
        # 显示编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑车位 - {space.space_number}")
        edit_window.geometry("400x300")
        
        # 创建编辑表单
        edit_frame = ttk.Frame(edit_window, padding="20")
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # 车位号
        number_frame = ttk.Frame(edit_frame)
        number_frame.pack(fill=tk.X, pady=5)
        
        number_label = ttk.Label(number_frame, text="车位号:", width=10)
        number_label.pack(side=tk.LEFT, padx=5)
        
        number_entry = ttk.Entry(edit_frame)
        number_entry.insert(0, space.space_number)
        number_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 楼层
        floor_frame = ttk.Frame(edit_frame)
        floor_frame.pack(fill=tk.X, pady=5)
        
        floor_label = ttk.Label(floor_frame, text="楼层:", width=10)
        floor_label.pack(side=tk.LEFT, padx=5)
        
        floor_entry = ttk.Entry(edit_frame)
        floor_entry.insert(0, space.floor)
        floor_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 车位类型
        type_frame = ttk.Frame(edit_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        type_label = ttk.Label(type_frame, text="车位类型:", width=10)
        type_label.pack(side=tk.LEFT, padx=5)
        
        type_var = tk.StringVar(value=space.space_type)
        type_combo = ttk.Combobox(edit_frame, textvariable=type_var, values=["小型车", "大型车", "新能源汽车"])
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 状态
        status_frame = ttk.Frame(edit_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        status_label = ttk.Label(status_frame, text="状态:", width=10)
        status_label.pack(side=tk.LEFT, padx=5)
        
        status_var = tk.StringVar(value=space.status)
        status_combo = ttk.Combobox(edit_frame, textvariable=status_var, values=["available", "occupied", "reserved"])
        status_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_button = ttk.Button(button_frame, text="保存", command=lambda: self._save_space_edit(edit_window, space_id, number_entry.get(), floor_entry.get(), type_var.get(), status_var.get()))
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=edit_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _save_space_edit(self, window, space_id, space_number, floor, space_type, status):
        # 保存车位编辑
        try:
            self.parking_system.space_manager.update_vehicle(
                space_id,
                space_number=space_number,
                floor=int(floor),
                space_type=space_type,
                status=status
            )
            messagebox.showinfo("成功", "车位信息更新成功")
            window.destroy()
            self._refresh_parking_space_table()
        except Exception as e:
            messagebox.showerror("错误", f"更新失败: {e}")
    
    def _delete_space(self):
        # 删除车位
        selected_items = self.space_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个车位")
            return
        
        item = selected_items[0]
        values = self.space_tree.item(item, "values")
        space_id = values[0]
        space_number = values[1]
        
        # 确认删除
        if messagebox.askyesno("确认", f"确定要删除车位 {space_number} 吗？"):
            try:
                self.parking_system.space_manager.delete_space(space_id)
                messagebox.showinfo("成功", "车位删除成功")
                self._refresh_parking_space_table()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")
    
    def _release_space(self):
        # 释放车位
        selected_items = self.space_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个车位")
            return
        
        item = selected_items[0]
        values = self.space_tree.item(item, "values")
        space_id = values[0]
        space_number = values[1]
        
        # 确认释放
        if messagebox.askyesno("确认", f"确定要释放车位 {space_number} 吗？"):
            try:
                self.parking_system.space_manager.release_space(space_id)
                messagebox.showinfo("成功", "车位释放成功")
                self._refresh_parking_space_table()
            except Exception as e:
                messagebox.showerror("错误", f"释放失败: {e}")
    
    def _show_add_parking_space_window(self):
        # 显示添加车位窗口
        add_window = tk.Toplevel(self.root)
        add_window.title("添加车位")
        add_window.geometry("400x300")
        
        # 创建添加表单
        add_frame = ttk.Frame(add_window, padding="20")
        add_frame.pack(fill=tk.BOTH, expand=True)
        
        # 车位号
        number_frame = ttk.Frame(add_frame)
        number_frame.pack(fill=tk.X, pady=5)
        
        number_label = ttk.Label(number_frame, text="车位号:", width=10)
        number_label.pack(side=tk.LEFT, padx=5)
        
        number_entry = ttk.Entry(number_frame)
        number_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        number_entry.focus()
        
        # 楼层
        floor_frame = ttk.Frame(add_frame)
        floor_frame.pack(fill=tk.X, pady=5)
        
        floor_label = ttk.Label(floor_frame, text="楼层:", width=10)
        floor_label.pack(side=tk.LEFT, padx=5)
        
        floor_entry = ttk.Entry(floor_frame)
        floor_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 车位类型
        type_frame = ttk.Frame(add_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        type_label = ttk.Label(type_frame, text="车位类型:", width=10)
        type_label.pack(side=tk.LEFT, padx=5)
        
        type_var = tk.StringVar(value="小型车")
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=["小型车", "大型车", "新能源汽车"])
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(add_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        add_button = ttk.Button(button_frame, text="添加", command=lambda: self._handle_add_parking_space(add_window, number_entry.get(), floor_entry.get(), type_var.get()))
        add_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=add_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _handle_add_parking_space(self, window, space_number, floor, space_type):
        # 处理添加车位
        space_number = space_number.strip()
        floor = floor.strip()
        
        if not space_number or not floor:
            messagebox.showwarning("警告", "请输入车位号和楼层")
            return
        
        try:
            floor = int(floor)
            
            # 添加车位
            self.parking_system.space_manager.add_space(space_number, floor, space_type)
            
            messagebox.showinfo("成功", f"车位 {space_number} 添加成功")
            window.destroy()
            
            # 刷新车位表格
            self._refresh_parking_space_table()
            
        except ValueError as e:
            messagebox.showerror("错误", f"无效的输入: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"添加车位失败: {e}")
    
    def _create_user_management_tab(self):
        # 创建用户管理标签页
        user_frame = ttk.Frame(self.notebook)
        self.notebook.add(user_frame, text="用户管理")
        
        # 顶部工具栏
        toolbar = ttk.Frame(user_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加用户按钮
        add_button = ttk.Button(toolbar, text="添加用户", command=self._show_add_user_window)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_button = ttk.Button(toolbar, text="刷新", command=self._refresh_user_table)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        search_label = ttk.Label(search_frame, text="搜索:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.user_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.user_search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_button = ttk.Button(search_frame, text="搜索", command=self._search_users)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # 表格框架
        table_frame = ttk.Frame(user_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ("id", "用户名", "角色", "真实姓名", "电话", "邮箱", "车牌号码", "是否会员", "会员等级", "余额")
        self.user_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # 设置列宽
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=100)
        
        # 设置滚动条
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.user_tree.xview)
        self.user_tree.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.user_tree.pack(fill=tk.BOTH, expand=True)
        
        # 右键菜单
        self.user_tree.bind("<Button-3>", self._show_user_context_menu)
        self.user_context_menu = tk.Menu(self.user_tree, tearoff=0)
        self.user_context_menu.add_command(label="查看详情", command=self._show_user_detail)
        self.user_context_menu.add_command(label="编辑用户", command=self._edit_user)
        self.user_context_menu.add_command(label="删除用户", command=self._delete_user)
        self.user_context_menu.add_separator()
        self.user_context_menu.add_command(label="修改密码", command=self._change_user_password)
        self.user_context_menu.add_separator()
        self.user_context_menu.add_command(label="添加会员", command=self._add_user_member)
        self.user_context_menu.add_command(label="取消会员", command=self._cancel_user_member)
    
    def _refresh_user_table(self):
        # 刷新用户表格
        # 清空表格
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # 获取所有用户
        users = self.parking_system.user_manager.get_all_users()
        
        # 插入数据
        for user in users:
            self.user_tree.insert("", tk.END, values=(
                user.id,
                user.username,
                user.role,
                user.real_name or "",
                user.phone or "",
                user.email or "",
                user.vehicle_plate or "",
                "是" if user.is_member else "否",
                user.member_level or "",
                user.balance
            ))
    
    def _search_users(self):
        # 搜索用户
        search_text = self.user_search_var.get().strip()
        if not search_text:
            self._refresh_user_table()
            return
        
        # 清空表格
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # 获取所有用户
        users = self.parking_system.user_manager.get_all_users()
        
        # 过滤用户
        filtered_users = []
        for user in users:
            if search_text in str(user.username) or search_text in str(user.real_name) or search_text in str(user.phone):
                filtered_users.append(user)
        
        # 插入数据
        for user in filtered_users:
            self.user_tree.insert("", tk.END, values=(
                user.id,
                user.username,
                user.role,
                user.real_name or "",
                user.phone or "",
                user.email or "",
                user.vehicle_plate or "",
                "是" if user.is_member else "否",
                user.member_level or "",
                user.balance
            ))
    
    def _show_user_context_menu(self, event):
        # 显示用户右键菜单
        item = self.user_tree.identify_row(event.y)
        if item:
            self.user_tree.selection_set(item)
            self.user_context_menu.post(event.x_root, event.y_root)
    
    def _show_user_detail(self):
        # 查看用户详情
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个用户")
            return
        
        item = selected_items[0]
        values = self.user_tree.item(item, "values")
        user_id = values[0]
        
        # 获取用户详情
        user = self.parking_system.user_manager.get_user_by_id(user_id)
        
        # 显示详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"用户详情 - {user.username}")
        detail_window.geometry("400x300")
        
        # 创建详情表单
        detail_frame = ttk.Frame(detail_window, padding="20")
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # 显示用户信息
        info_text = f"ID: {user.id}\n"
        info_text += f"用户名: {user.username}\n"
        info_text += f"角色: {user.role}\n"
        info_text += f"真实姓名: {user.real_name or '无'}\n"
        info_text += f"电话: {user.phone or '无'}\n"
        info_text += f"邮箱: {user.email or '无'}\n"
        info_text += f"车牌号码: {user.vehicle_plate or '无'}\n"
        info_text += f"是否会员: {'是' if user.is_member else '否'}\n"
        info_text += f"会员等级: {user.member_level or '无'}\n"
        info_text += f"会员到期时间: {user.member_expiry or '无'}\n"
        info_text += f"余额: {user.balance}元\n"
        info_text += f"创建时间: {user.created_at}\n"
        info_text += f"更新时间: {user.updated_at}\n"
        
        info_label = ttk.Label(detail_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(fill=tk.BOTH, expand=True)
    
    def _edit_user(self):
        # 编辑用户信息
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个用户")
            return
        
        item = selected_items[0]
        values = self.user_tree.item(item, "values")
        user_id = values[0]
        
        # 获取用户详情
        user = self.parking_system.user_manager.get_user_by_id(user_id)
        
        # 显示编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑用户 - {user.username}")
        edit_window.geometry("400x300")
        
        # 创建编辑表单
        edit_frame = ttk.Frame(edit_window, padding="20")
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # 用户名（只读）
        username_frame = ttk.Frame(edit_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        username_label = ttk.Label(username_frame, text="用户名:", width=10)
        username_label.pack(side=tk.LEFT, padx=5)
        
        username_entry = ttk.Entry(username_frame)
        username_entry.insert(0, user.username)
        username_entry.config(state=tk.DISABLED)
        username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 角色
        role_frame = ttk.Frame(edit_frame)
        role_frame.pack(fill=tk.X, pady=5)
        
        role_label = ttk.Label(role_frame, text="角色:", width=10)
        role_label.pack(side=tk.LEFT, padx=5)
        
        role_var = tk.StringVar(value=user.role)
        role_combo = ttk.Combobox(role_frame, textvariable=role_var, values=["admin", "user"])
        role_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 真实姓名
        real_name_frame = ttk.Frame(edit_frame)
        real_name_frame.pack(fill=tk.X, pady=5)
        
        real_name_label = ttk.Label(real_name_frame, text="真实姓名:", width=10)
        real_name_label.pack(side=tk.LEFT, padx=5)
        
        real_name_entry = ttk.Entry(real_name_frame)
        real_name_entry.insert(0, user.real_name or "")
        real_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 电话
        phone_frame = ttk.Frame(edit_frame)
        phone_frame.pack(fill=tk.X, pady=5)
        
        phone_label = ttk.Label(phone_frame, text="电话:", width=10)
        phone_label.pack(side=tk.LEFT, padx=5)
        
        phone_entry = ttk.Entry(phone_frame)
        phone_entry.insert(0, user.phone or "")
        phone_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 邮箱
        email_frame = ttk.Frame(edit_frame)
        email_frame.pack(fill=tk.X, pady=5)
        
        email_label = ttk.Label(email_frame, text="邮箱:", width=10)
        email_label.pack(side=tk.LEFT, padx=5)
        
        email_entry = ttk.Entry(email_frame)
        email_entry.insert(0, user.email or "")
        email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 车牌号码
        plate_frame = ttk.Frame(edit_frame)
        plate_frame.pack(fill=tk.X, pady=5)
        
        plate_label = ttk.Label(plate_frame, text="车牌号码:", width=10)
        plate_label.pack(side=tk.LEFT, padx=5)
        
        plate_entry = ttk.Entry(plate_frame)
        plate_entry.insert(0, user.vehicle_plate or "")
        plate_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_button = ttk.Button(button_frame, text="保存", command=lambda: self._save_user_edit(edit_window, user_id, role_var.get(), real_name_entry.get(), phone_entry.get(), email_entry.get(), plate_entry.get()))
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=edit_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _save_user_edit(self, window, user_id, role, real_name, phone, email, vehicle_plate):
        # 保存用户编辑
        try:
            self.parking_system.user_manager.update_vehicle(
                user_id,
                role=role,
                real_name=real_name,
                phone=phone,
                email=email,
                vehicle_plate=vehicle_plate
            )
            messagebox.showinfo("成功", "用户信息更新成功")
            window.destroy()
            self._refresh_user_table()
        except Exception as e:
            messagebox.showerror("错误", f"更新失败: {e}")
    
    def _delete_user(self):
        # 删除用户
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个用户")
            return
        
        item = selected_items[0]
        values = self.user_tree.item(item, "values")
        user_id = values[0]
        username = values[1]
        
        # 确认删除
        if messagebox.askyesno("确认", f"确定要删除用户 {username} 吗？"):
            try:
                self.parking_system.user_manager.delete_user(user_id)
                messagebox.showinfo("成功", "用户删除成功")
                self._refresh_user_table()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")
    
    def _change_user_password(self):
        # 修改用户密码
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个用户")
            return
        
        item = selected_items[0]
        values = self.user_tree.item(item, "values")
        user_id = values[0]
        username = values[1]
        
        # 显示修改密码窗口
        password_window = tk.Toplevel(self.root)
        password_window.title(f"修改密码 - {username}")
        password_window.geometry("400x250")
        
        # 创建密码修改表单
        password_frame = ttk.Frame(password_window, padding="20")
        password_frame.pack(fill=tk.BOTH, expand=True)
        
        # 旧密码
        old_frame = ttk.Frame(password_frame)
        old_frame.pack(fill=tk.X, pady=5)
        
        old_label = ttk.Label(old_frame, text="旧密码:", width=10)
        old_label.pack(side=tk.LEFT, padx=5)
        
        old_entry = ttk.Entry(old_frame, show="*")
        old_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 新密码
        new_frame = ttk.Frame(password_frame)
        new_frame.pack(fill=tk.X, pady=5)
        
        new_label = ttk.Label(new_frame, text="新密码:", width=10)
        new_label.pack(side=tk.LEFT, padx=5)
        
        new_entry = ttk.Entry(new_frame, show="*")
        new_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 确认新密码
        confirm_frame = ttk.Frame(password_frame)
        confirm_frame.pack(fill=tk.X, pady=5)
        
        confirm_label = ttk.Label(confirm_frame, text="确认新密码:", width=10)
        confirm_label.pack(side=tk.LEFT, padx=5)
        
        confirm_entry = ttk.Entry(confirm_frame, show="*")
        confirm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(password_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_button = ttk.Button(button_frame, text="保存", command=lambda: self._save_user_password(password_window, user_id, old_entry.get(), new_entry.get(), confirm_entry.get()))
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=password_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _save_user_password(self, window, user_id, old_password, new_password, confirm_password):
        # 保存用户密码
        if not old_password or not new_password or not confirm_password:
            messagebox.showwarning("警告", "请输入所有密码字段")
            return
        
        if new_password != confirm_password:
            messagebox.showwarning("警告", "两次输入的密码不一致")
            return
        
        try:
            self.parking_system.user_manager.change_password(user_id, old_password, new_password)
            messagebox.showinfo("成功", "密码修改成功")
            window.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"密码修改失败: {e}")
    
    def _add_user_member(self):
        # 添加会员
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个用户")
            return
        
        item = selected_items[0]
        values = self.user_tree.item(item, "values")
        user_id = values[0]
        username = values[1]
        
        # 显示添加会员窗口
        member_window = tk.Toplevel(self.root)
        member_window.title(f"添加会员 - {username}")
        member_window.geometry("400x250")
        
        # 创建会员表单
        member_frame = ttk.Frame(member_window, padding="20")
        member_frame.pack(fill=tk.BOTH, expand=True)
        
        # 会员等级
        level_frame = ttk.Frame(member_frame)
        level_frame.pack(fill=tk.X, pady=10)
        
        level_label = ttk.Label(level_frame, text="会员等级:", width=10)
        level_label.pack(side=tk.LEFT, padx=5)
        
        # 获取会员等级列表
        member_levels = self.parking_system.user_manager.get_member_levels()
        level_names = [level['level_name'] for level in member_levels]
        
        level_var = tk.StringVar(value=level_names[0] if level_names else "")
        level_combo = ttk.Combobox(level_frame, textvariable=level_var, values=level_names)
        level_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 会员时长（月）
        duration_frame = ttk.Frame(member_frame)
        duration_frame.pack(fill=tk.X, pady=10)
        
        duration_label = ttk.Label(duration_frame, text="时长(月):", width=10)
        duration_label.pack(side=tk.LEFT, padx=5)
        
        duration_var = tk.IntVar(value=1)
        duration_spin = ttk.Spinbox(duration_frame, from_=1, to=24, textvariable=duration_var)
        duration_spin.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(member_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        add_button = ttk.Button(button_frame, text="添加会员", command=lambda: self._save_user_member(member_window, user_id, level_var.get(), duration_var.get()))
        add_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=member_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _save_user_member(self, window, user_id, member_level, duration):
        # 保存会员信息
        try:
            self.parking_system.user_manager.add_member(user_id, member_level, duration)
            messagebox.showinfo("成功", "会员添加成功")
            window.destroy()
            self._refresh_user_table()
        except Exception as e:
            messagebox.showerror("错误", f"添加会员失败: {e}")
    
    def _cancel_user_member(self):
        # 取消会员
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一个用户")
            return
        
        item = selected_items[0]
        values = self.user_tree.item(item, "values")
        user_id = values[0]
        username = values[1]
        
        # 确认取消
        if messagebox.askyesno("确认", f"确定要取消 {username} 的会员资格吗？"):
            try:
                self.parking_system.user_manager.cancel_member(user_id)
                messagebox.showinfo("成功", "会员资格已取消")
                self._refresh_user_table()
            except Exception as e:
                messagebox.showerror("错误", f"取消会员失败: {e}")
    
    def _show_add_user_window(self):
        # 显示添加用户窗口
        add_window = tk.Toplevel(self.root)
        add_window.title("添加用户")
        add_window.geometry("400x350")
        
        # 创建添加表单
        add_frame = ttk.Frame(add_window, padding="20")
        add_frame.pack(fill=tk.BOTH, expand=True)
        
        # 用户名
        username_frame = ttk.Frame(add_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        username_label = ttk.Label(username_frame, text="用户名:", width=10)
        username_label.pack(side=tk.LEFT, padx=5)
        
        username_entry = ttk.Entry(username_frame)
        username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        username_entry.focus()
        
        # 密码
        password_frame = ttk.Frame(add_frame)
        password_frame.pack(fill=tk.X, pady=5)
        
        password_label = ttk.Label(password_frame, text="密码:", width=10)
        password_label.pack(side=tk.LEFT, padx=5)
        
        password_entry = ttk.Entry(password_frame, show="*")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 角色
        role_frame = ttk.Frame(add_frame)
        role_frame.pack(fill=tk.X, pady=5)
        
        role_label = ttk.Label(role_frame, text="角色:", width=10)
        role_label.pack(side=tk.LEFT, padx=5)
        
        role_var = tk.StringVar(value="user")
        role_combo = ttk.Combobox(role_frame, textvariable=role_var, values=["admin", "user"])
        role_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 真实姓名
        real_name_frame = ttk.Frame(add_frame)
        real_name_frame.pack(fill=tk.X, pady=5)
        
        real_name_label = ttk.Label(real_name_frame, text="真实姓名:", width=10)
        real_name_label.pack(side=tk.LEFT, padx=5)
        
        real_name_entry = ttk.Entry(real_name_frame)
        real_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 电话
        phone_frame = ttk.Frame(add_frame)
        phone_frame.pack(fill=tk.X, pady=5)
        
        phone_label = ttk.Label(phone_frame, text="电话:", width=10)
        phone_label.pack(side=tk.LEFT, padx=5)
        
        phone_entry = ttk.Entry(phone_frame)
        phone_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 邮箱
        email_frame = ttk.Frame(add_frame)
        email_frame.pack(fill=tk.X, pady=5)
        
        email_label = ttk.Label(email_frame, text="邮箱:", width=10)
        email_label.pack(side=tk.LEFT, padx=5)
        
        email_entry = ttk.Entry(email_frame)
        email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(add_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        add_button = ttk.Button(button_frame, text="添加", command=lambda: self._handle_add_user(add_window, username_entry.get(), password_entry.get(), role_var.get(), real_name_entry.get(), phone_entry.get(), email_entry.get()))
        add_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=add_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _handle_add_user(self, window, username, password, role, real_name, phone, email):
        # 处理添加用户
        username = username.strip()
        password = password.strip()
        
        if not username or not password:
            messagebox.showwarning("警告", "请输入用户名和密码")
            return
        
        try:
            # 添加用户
            self.parking_system.user_manager.register_user(username, password, role, real_name, phone, email)
            
            messagebox.showinfo("成功", f"用户 {username} 添加成功")
            window.destroy()
            
            # 刷新用户表格
            self._refresh_user_table()
            
        except Exception as e:
            messagebox.showerror("错误", f"添加用户失败: {e}")
    
    def _create_fee_management_tab(self):
        # 创建收费管理标签页
        fee_frame = ttk.Frame(self.notebook)
        self.notebook.add(fee_frame, text="收费管理")
        
        # 顶部工具栏
        toolbar = ttk.Frame(fee_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加收费规则按钮
        add_rule_button = ttk.Button(toolbar, text="添加收费规则", command=self._show_add_fee_rule_window)
        add_rule_button.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_button = ttk.Button(toolbar, text="刷新", command=self._refresh_fee_rule_table)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 表格框架
        table_frame = ttk.Frame(fee_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ("id", "规则名称", "车辆类型", "时间单位", "单价", "免费时长", "每日最高费用", "状态")
        self.fee_rule_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # 设置列宽
        for col in columns:
            self.fee_rule_tree.heading(col, text=col)
            self.fee_rule_tree.column(col, width=100)
        
        # 设置滚动条
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.fee_rule_tree.yview)
        self.fee_rule_tree.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.fee_rule_tree.xview)
        self.fee_rule_tree.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.fee_rule_tree.pack(fill=tk.BOTH, expand=True)
        
        # 右键菜单
        self.fee_rule_tree.bind("<Button-3>", self._show_fee_rule_context_menu)
        self.fee_rule_context_menu = tk.Menu(self.fee_rule_tree, tearoff=0)
        self.fee_rule_context_menu.add_command(label="编辑规则", command=self._edit_fee_rule)
        self.fee_rule_context_menu.add_command(label="删除规则", command=self._delete_fee_rule)
        self.fee_rule_context_menu.add_command(label="启用/禁用规则", command=self._toggle_fee_rule_status)
    
    def _refresh_fee_rule_table(self):
        # 刷新收费规则表格
        # 清空表格
        for item in self.fee_rule_tree.get_children():
            self.fee_rule_tree.delete(item)
        
        # 获取所有收费规则
        rules = self.parking_system.fee_manager.get_all_fee_rules()
        
        # 插入数据
        for rule in rules:
            self.fee_rule_tree.insert("", tk.END, values=(
                rule.id,
                rule.rule_name,
                rule.vehicle_type,
                rule.time_unit,
                rule.unit_price,
                rule.free_duration,
                rule.max_daily_fee or "无",
                "启用" if rule.is_active else "禁用"
            ))
    
    def _show_fee_rule_context_menu(self, event):
        # 显示收费规则右键菜单
        item = self.fee_rule_tree.identify_row(event.y)
        if item:
            self.fee_rule_tree.selection_set(item)
            self.fee_rule_context_menu.post(event.x_root, event.y_root)
    
    def _show_add_fee_rule_window(self):
        # 显示添加收费规则窗口
        rule_window = tk.Toplevel(self.root)
        rule_window.title("添加收费规则")
        rule_window.geometry("400x350")
        
        # 创建添加表单
        rule_frame = ttk.Frame(rule_window, padding="20")
        rule_frame.pack(fill=tk.BOTH, expand=True)
        
        # 规则名称
        name_frame = ttk.Frame(rule_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        name_label = ttk.Label(name_frame, text="规则名称:", width=10)
        name_label.pack(side=tk.LEFT, padx=5)
        
        name_entry = ttk.Entry(name_frame)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        name_entry.focus()
        
        # 车辆类型
        type_frame = ttk.Frame(rule_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        type_label = ttk.Label(type_frame, text="车辆类型:", width=10)
        type_label.pack(side=tk.LEFT, padx=5)
        
        type_var = tk.StringVar(value="小型车")
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=["小型车", "大型车", "新能源汽车"])
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 时间单位
        unit_frame = ttk.Frame(rule_frame)
        unit_frame.pack(fill=tk.X, pady=5)
        
        unit_label = ttk.Label(unit_frame, text="时间单位:", width=10)
        unit_label.pack(side=tk.LEFT, padx=5)
        
        unit_var = tk.StringVar(value="hour")
        unit_combo = ttk.Combobox(unit_frame, textvariable=unit_var, values=["minute", "half_hour", "hour"])
        unit_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 单价
        price_frame = ttk.Frame(rule_frame)
        price_frame.pack(fill=tk.X, pady=5)
        
        price_label = ttk.Label(price_frame, text="单价(元):", width=10)
        price_label.pack(side=tk.LEFT, padx=5)
        
        price_entry = ttk.Entry(price_frame)
        price_entry.insert(0, "5.0")
        price_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 免费时长
        free_frame = ttk.Frame(rule_frame)
        free_frame.pack(fill=tk.X, pady=5)
        
        free_label = ttk.Label(free_frame, text="免费时长(分钟):", width=10)
        free_label.pack(side=tk.LEFT, padx=5)
        
        free_entry = ttk.Entry(free_frame)
        free_entry.insert(0, "30")
        free_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 每日最高费用
        max_frame = ttk.Frame(rule_frame)
        max_frame.pack(fill=tk.X, pady=5)
        
        max_label = ttk.Label(max_frame, text="每日最高费用(元):", width=15)
        max_label.pack(side=tk.LEFT, padx=5)
        
        max_entry = ttk.Entry(max_frame)
        max_entry.insert(0, "50.0")
        max_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(rule_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        add_button = ttk.Button(button_frame, text="添加", command=lambda: self._handle_add_fee_rule(rule_window, name_entry.get(), type_var.get(), unit_var.get(), float(price_entry.get()), int(free_entry.get()), float(max_entry.get()) if max_entry.get() else None))
        add_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=rule_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _handle_add_fee_rule(self, window, rule_name, vehicle_type, time_unit, unit_price, free_duration, max_daily_fee):
        # 处理添加收费规则
        rule_name = rule_name.strip()
        
        if not rule_name:
            messagebox.showwarning("警告", "请输入规则名称")
            return
        
        try:
            # 添加收费规则
            self.parking_system.fee_manager.add_fee_rule(rule_name, vehicle_type, time_unit, unit_price, free_duration, max_daily_fee)
            
            messagebox.showinfo("成功", f"收费规则 {rule_name} 添加成功")
            window.destroy()
            
            # 刷新收费规则表格
            self._refresh_fee_rule_table()
            
        except Exception as e:
            messagebox.showerror("错误", f"添加收费规则失败: {e}")
    
    def _edit_fee_rule(self):
        # 编辑收费规则
        selected_items = self.fee_rule_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一条规则")
            return
        
        item = selected_items[0]
        values = self.fee_rule_tree.item(item, "values")
        rule_id = values[0]
        
        # 获取规则详情
        rule = self.parking_system.fee_manager.get_fee_rule_by_id(rule_id)
        
        # 显示编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑收费规则 - {rule.rule_name}")
        edit_window.geometry("400x350")
        
        # 创建编辑表单
        edit_frame = ttk.Frame(edit_window, padding="20")
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # 规则名称
        name_frame = ttk.Frame(edit_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        name_label = ttk.Label(name_frame, text="规则名称:", width=10)
        name_label.pack(side=tk.LEFT, padx=5)
        
        name_entry = ttk.Entry(name_frame)
        name_entry.insert(0, rule.rule_name)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 车辆类型
        type_frame = ttk.Frame(edit_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        type_label = ttk.Label(type_frame, text="车辆类型:", width=10)
        type_label.pack(side=tk.LEFT, padx=5)
        
        type_var = tk.StringVar(value=rule.vehicle_type)
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, values=["小型车", "大型车", "新能源汽车"])
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 时间单位
        unit_frame = ttk.Frame(edit_frame)
        unit_frame.pack(fill=tk.X, pady=5)
        
        unit_label = ttk.Label(unit_frame, text="时间单位:", width=10)
        unit_label.pack(side=tk.LEFT, padx=5)
        
        unit_var = tk.StringVar(value=rule.time_unit)
        unit_combo = ttk.Combobox(unit_frame, textvariable=unit_var, values=["minute", "half_hour", "hour"])
        unit_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 单价
        price_frame = ttk.Frame(edit_frame)
        price_frame.pack(fill=tk.X, pady=5)
        
        price_label = ttk.Label(price_frame, text="单价(元):", width=10)
        price_label.pack(side=tk.LEFT, padx=5)
        
        price_entry = ttk.Entry(price_frame)
        price_entry.insert(0, str(rule.unit_price))
        price_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 免费时长
        free_frame = ttk.Frame(edit_frame)
        free_frame.pack(fill=tk.X, pady=5)
        
        free_label = ttk.Label(free_frame, text="免费时长(分钟):", width=10)
        free_label.pack(side=tk.LEFT, padx=5)
        
        free_entry = ttk.Entry(free_frame)
        free_entry.insert(0, str(rule.free_duration))
        free_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 每日最高费用
        max_frame = ttk.Frame(edit_frame)
        max_frame.pack(fill=tk.X, pady=5)
        
        max_label = ttk.Label(max_frame, text="每日最高费用(元):", width=15)
        max_label.pack(side=tk.LEFT, padx=5)
        
        max_entry = ttk.Entry(max_frame)
        max_entry.insert(0, str(rule.max_daily_fee) if rule.max_daily_fee else "")
        max_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_button = ttk.Button(button_frame, text="保存", command=lambda: self._save_fee_rule_edit(edit_window, rule_id, name_entry.get(), type_var.get(), unit_var.get(), float(price_entry.get()), int(free_entry.get()), float(max_entry.get()) if max_entry.get() else None))
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=edit_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _save_fee_rule_edit(self, window, rule_id, rule_name, vehicle_type, time_unit, unit_price, free_duration, max_daily_fee):
        # 保存收费规则编辑
        try:
            self.parking_system.fee_manager.update_fee_rule(
                rule_id,
                rule_name=rule_name,
                vehicle_type=vehicle_type,
                time_unit=time_unit,
                unit_price=unit_price,
                free_duration=free_duration,
                max_daily_fee=max_daily_fee
            )
            messagebox.showinfo("成功", "收费规则更新成功")
            window.destroy()
            self._refresh_fee_rule_table()
        except Exception as e:
            messagebox.showerror("错误", f"更新收费规则失败: {e}")
    
    def _delete_fee_rule(self):
        # 删除收费规则
        selected_items = self.fee_rule_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一条规则")
            return
        
        item = selected_items[0]
        values = self.fee_rule_tree.item(item, "values")
        rule_id = values[0]
        rule_name = values[1]
        
        # 确认删除
        if messagebox.askyesno("确认", f"确定要删除收费规则 {rule_name} 吗？"):
            try:
                self.parking_system.fee_manager.delete_fee_rule(rule_id)
                messagebox.showinfo("成功", "收费规则删除成功")
                self._refresh_fee_rule_table()
            except Exception as e:
                messagebox.showerror("错误", f"删除收费规则失败: {e}")
    
    def _toggle_fee_rule_status(self):
        # 启用/禁用收费规则
        selected_items = self.fee_rule_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择一条规则")
            return
        
        item = selected_items[0]
        values = self.fee_rule_tree.item(item, "values")
        rule_id = values[0]
        
        # 获取规则详情
        rule = self.parking_system.fee_manager.get_fee_rule_by_id(rule_id)
        
        # 切换状态
        new_status = not rule.is_active
        
        try:
            self.parking_system.fee_manager.update_fee_rule(rule_id, is_active=new_status)
            messagebox.showinfo("成功", f"收费规则已{'启用' if new_status else '禁用'}")
            self._refresh_fee_rule_table()
        except Exception as e:
            messagebox.showerror("错误", f"切换规则状态失败: {e}")
    
    def _create_report_tab(self):
        # 创建报表统计标签页
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="报表统计")
        
        # 顶部工具栏
        toolbar = ttk.Frame(report_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 报表类型
        type_frame = ttk.Frame(toolbar)
        type_frame.pack(side=tk.LEFT, padx=5)
        
        type_label = ttk.Label(type_frame, text="报表类型:")
        type_label.pack(side=tk.LEFT, padx=5)
        
        report_type_var = tk.StringVar(value="daily")
        type_combo = ttk.Combobox(type_frame, textvariable=report_type_var, values=["daily", "weekly", "monthly", "annual"])
        type_combo.pack(side=tk.LEFT, padx=5)
        
        # 生成报表按钮
        generate_button = ttk.Button(toolbar, text="生成报表", command=lambda: self._generate_report(report_type_var.get()))
        generate_button.pack(side=tk.LEFT, padx=5)
        
        # 导出报表按钮
        export_button = ttk.Button(toolbar, text="导出报表", command=lambda: self._export_report(report_type_var.get()))
        export_button.pack(side=tk.LEFT, padx=5)
        
        # 报表内容区域
        content_frame = ttk.Frame(report_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建报表文本框
        self.report_text = tk.Text(content_frame, wrap=tk.WORD, height=20, width=80)
        self.report_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(content_frame, command=self.report_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.configure(yscrollcommand=scrollbar.set)
    
    def _generate_report(self, report_type):
        # 生成报表
        try:
            if report_type == "daily":
                report = self.parking_system.report_manager.generate_daily_report()
            elif report_type == "weekly":
                report = self.parking_system.report_manager.generate_weekly_report()
            elif report_type == "monthly":
                report = self.parking_system.report_manager.generate_monthly_report()
            elif report_type == "annual":
                report = self.parking_system.report_manager.generate_annual_report()
            else:
                messagebox.showwarning("警告", "无效的报表类型")
                return
            
            # 显示报表内容
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, f"=== {report_type} 报表 ===\n\n")
            
            if 'date' in report:
                self.report_text.insert(tk.END, f"日期: {report['date']}\n\n")
            elif 'start_date' in report and 'end_date' in report:
                self.report_text.insert(tk.END, f"开始日期: {report['start_date']}\n")
                self.report_text.insert(tk.END, f"结束日期: {report['end_date']}\n\n")
            elif 'year' in report:
                self.report_text.insert(tk.END, f"年份: {report['year']}\n\n")
            
            # 基本统计
            self.report_text.insert(tk.END, "=== 基本统计 ===\n")
            self.report_text.insert(tk.END, f"入场车辆数: {report['basic_stats']['entry_count']}\n")
            self.report_text.insert(tk.END, f"出场车辆数: {report['basic_stats']['exit_count']}\n")
            self.report_text.insert(tk.END, f"总收入(元): {report['basic_stats']['total_fee']}\n")
            self.report_text.insert(tk.END, f"平均停留时间(分钟): {report['basic_stats']['avg_stay_time']}\n")
            self.report_text.insert(tk.END, f"车位使用率(%): {report['basic_stats']['occupancy_rate']}\n")
            self.report_text.insert(tk.END, f"高峰期最大占用数: {report['basic_stats']['max_occupied']}\n\n")
            
            # 车辆类型分布
            self.report_text.insert(tk.END, "=== 车辆类型分布 ===\n")
            for stat in report['vehicle_type_stats']:
                self.report_text.insert(tk.END, f"{stat['vehicle_type']}: {stat['count']} 辆\n")
            self.report_text.insert(tk.END, "\n")
            
            # 收入统计
            self.report_text.insert(tk.END, "=== 收入统计 ===\n")
            if 'daily_fee_stats' in report:
                for stat in report['daily_fee_stats']:
                    self.report_text.insert(tk.END, f"{stat['date']}: {stat['fee']} 元\n")
            elif 'monthly_fee_stats' in report:
                for stat in report['monthly_fee_stats']:
                    self.report_text.insert(tk.END, f"第{stat['month']}月: {stat['fee']} 元\n")
            self.report_text.insert(tk.END, "\n")
            
            messagebox.showinfo("成功", "报表生成成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成报表失败: {e}")
    
    def _export_report(self, report_type):
        # 导出报表
        try:
            if report_type == "daily":
                report = self.parking_system.report_manager.generate_daily_report()
            elif report_type == "weekly":
                report = self.parking_system.report_manager.generate_weekly_report()
            elif report_type == "monthly":
                report = self.parking_system.report_manager.generate_monthly_report()
            elif report_type == "annual":
                report = self.parking_system.report_manager.generate_annual_report()
            else:
                messagebox.showwarning("警告", "无效的报表类型")
                return
            
            # 生成导出文件名
            export_path = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # 导出报表
            self.parking_system.report_manager.export_report_to_csv(report, export_path)
            
            messagebox.showinfo("成功", f"报表导出成功: {export_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出报表失败: {e}")
    
    def _create_log_tab(self):
        # 创建日志标签页
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="系统日志")
        
        # 顶部工具栏
        toolbar = ttk.Frame(log_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 日志级别过滤
        level_frame = ttk.Frame(toolbar)
        level_frame.pack(side=tk.LEFT, padx=5)
        
        level_label = ttk.Label(level_frame, text="日志级别:")
        level_label.pack(side=tk.LEFT, padx=5)
        
        log_level_var = tk.StringVar(value="ALL")
        level_combo = ttk.Combobox(level_frame, textvariable=log_level_var, values=["ALL", "INFO", "ERROR"])
        level_combo.pack(side=tk.LEFT, padx=5)
        
        # 刷新日志按钮
        refresh_button = ttk.Button(toolbar, text="刷新日志", command=lambda: self._refresh_logs(log_level_var.get()))
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 清空日志按钮
        clear_button = ttk.Button(toolbar, text="清空日志", command=self._clear_logs)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 导出日志按钮
        export_button = ttk.Button(toolbar, text="导出日志", command=lambda: self._export_logs(log_level_var.get()))
        export_button.pack(side=tk.LEFT, padx=5)
        
        # 日志内容区域
        content_frame = ttk.Frame(log_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建日志文本框
        self.log_text = tk.Text(content_frame, wrap=tk.WORD, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(content_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # 初始刷新日志
        self._refresh_logs("ALL")
    
    def _refresh_logs(self, log_level):
        # 刷新日志
        try:
            level = None if log_level == "ALL" else log_level
            logs = self.parking_system.system_manager.get_logs(log_level=level, limit=200)
            
            # 显示日志内容
            self.log_text.delete(1.0, tk.END)
            for log in logs:
                self.log_text.insert(tk.END, f"[{log['log_time']}] [{log['log_level']}] [{log['module']}] {log['message']}\n")
                if log['details']:
                    self.log_text.insert(tk.END, f"  详情: {log['details']}\n")
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新日志失败: {e}")
    
    def _clear_logs(self):
        # 清空日志显示
        self.log_text.delete(1.0, tk.END)
    
    def _export_logs(self, log_level):
        # 导出日志
        try:
            level = None if log_level == "ALL" else log_level
            logs = self.parking_system.system_manager.get_logs(log_level=level, limit=1000)
            
            # 生成导出文件名
            export_path = f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # 写入日志文件
            with open(export_path, 'w', encoding='utf-8') as f:
                for log in logs:
                    f.write(f"[{log['log_time']}] [{log['log_level']}] [{log['module']}] {log['message']}\n")
                    if log['details']:
                        f.write(f"  详情: {log['details']}\n")
            
            messagebox.showinfo("成功", f"日志导出成功: {export_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出日志失败: {e}")
    
    def _show_system_config_window(self):
        # 显示系统配置窗口
        config_window = tk.Toplevel(self.root)
        config_window.title("系统配置")
        config_window.geometry("600x400")
        
        # 创建配置框架
        config_frame = ttk.Frame(config_window, padding="20")
        config_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建配置列表
        self.config_tree = ttk.Treeview(config_frame, columns=("key", "value", "description"), show="headings")
        self.config_tree.heading("key", text="配置项")
        self.config_tree.heading("value", text="配置值")
        self.config_tree.heading("description", text="描述")
        self.config_tree.column("key", width=150)
        self.config_tree.column("value", width=200)
        self.config_tree.column("description", width=250)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(config_frame, orient=tk.VERTICAL, command=self.config_tree.yview)
        self.config_tree.configure(yscroll=scrollbar.set)
        
        self.config_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 底部按钮
        button_frame = ttk.Frame(config_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        save_button = ttk.Button(button_frame, text="保存配置", command=self._save_system_config)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=config_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # 加载配置
        self._load_system_config()
    
    def _load_system_config(self):
        # 加载系统配置
        configs = self.parking_system.system_manager.get_all_configs()
        
        # 清空配置树
        for item in self.config_tree.get_children():
            self.config_tree.delete(item)
        
        # 插入配置项
        for key, value in configs.items():
            # 获取配置描述
            description = self.parking_system.system_manager.get_config_description(key) or ""
            self.config_tree.insert("", tk.END, values=(key, value, description))
    
    def _save_system_config(self):
        # 保存系统配置
        try:
            for item in self.config_tree.get_children():
                values = self.config_tree.item(item, "values")
                key = values[0]
                value = values[1]
                self.parking_system.system_manager.update_config(key, value)
            
            messagebox.showinfo("成功", "系统配置保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存系统配置失败: {e}")
    
    def _show_database_backup_window(self):
        # 显示数据库备份窗口
        backup_window = tk.Toplevel(self.root)
        backup_window.title("数据库备份")
        backup_window.geometry("400x250")
        
        # 创建备份框架
        backup_frame = ttk.Frame(backup_window, padding="20")
        backup_frame.pack(fill=tk.BOTH, expand=True)
        
        # 备份路径
        path_frame = ttk.Frame(backup_frame)
        path_frame.pack(fill=tk.X, pady=10)
        
        path_label = ttk.Label(path_frame, text="备份路径:", width=10)
        path_label.pack(side=tk.LEFT, padx=5)
        
        path_entry = ttk.Entry(path_frame)
        path_entry.insert(0, self.parking_system.system_manager.get_config("backup_path") or "./backups")
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 底部按钮
        button_frame = ttk.Frame(backup_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        backup_button = ttk.Button(button_frame, text="立即备份", command=lambda: self._perform_database_backup(backup_window, path_entry.get()))
        backup_button.pack(side=tk.RIGHT, padx=5)
        
        restore_button = ttk.Button(button_frame, text="恢复备份", command=lambda: self._perform_database_restore(backup_window))
        restore_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=backup_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _perform_database_backup(self, window, backup_path):
        # 执行数据库备份
        try:
            backup_file = self.parking_system.system_manager.backup_database(backup_path)
            messagebox.showinfo("成功", f"数据库备份成功: {backup_file}")
        except Exception as e:
            messagebox.showerror("错误", f"数据库备份失败: {e}")
    
    def _perform_database_restore(self, window):
        # 执行数据库恢复
        try:
            # 这里简化处理，实际项目中应该提供文件选择对话框
            backup_file = "parking_system_backup.db"
            self.parking_system.system_manager.restore_database(backup_file)
            messagebox.showinfo("成功", "数据库恢复成功")
        except Exception as e:
            messagebox.showerror("错误", f"数据库恢复失败: {e}")
    
    def _show_system_status_window(self):
        # 显示系统状态窗口
        status_window = tk.Toplevel(self.root)
        status_window.title("系统状态")
        status_window.geometry("600x400")
        
        # 创建状态框架
        status_frame = ttk.Frame(status_window, padding="20")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # 获取系统状态
        status = self.parking_system.system_manager.get_system_status()
        
        # 系统基本信息
        info_frame = ttk.LabelFrame(status_frame, text="系统基本信息", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = f"系统名称: {status['system_info']['system_name']}\n"
        info_text += f"版本: {status['system_info']['version']}\n"
        info_text += f"当前时间: {status['system_info']['current_time']}\n"
        info_text += f"Python版本: {status['system_info']['python_version']}\n"
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(fill=tk.X)
        
        # 资源使用情况
        resource_frame = ttk.LabelFrame(status_frame, text="系统资源使用情况", padding="10")
        resource_frame.pack(fill=tk.X, pady=10)
        
        resource_text = f"CPU使用率: {status['resource_info'].get('cpu_percent', 'N/A')}%\n"
        resource_text += f"内存使用率: {status['resource_info'].get('memory_percent', 'N/A')}%\n"
        resource_text += f"磁盘使用率: {status['resource_info'].get('disk_percent', 'N/A')}%\n"
        
        resource_label = ttk.Label(resource_frame, text=resource_text, justify=tk.LEFT)
        resource_label.pack(fill=tk.X)
        
        # 数据库状态
        db_frame = ttk.LabelFrame(status_frame, text="数据库状态", padding="10")
        db_frame.pack(fill=tk.X, pady=10)
        
        db_text = "数据库表统计:\n"
        for table, count in status['db_info'].items():
            db_text += f"  {table}: {count} 条记录\n"
        
        db_label = ttk.Label(db_frame, text=db_text, justify=tk.LEFT)
        db_label.pack(fill=tk.X)
        
        # 设备状态
        device_frame = ttk.LabelFrame(status_frame, text="设备状态", padding="10")
        device_frame.pack(fill=tk.X, pady=10)
        
        device_text = f"设备总数: {status['device_stats']['total']}\n"
        device_text += f"在线设备: {status['device_stats']['online']}\n"
        device_text += f"离线设备: {status['device_stats']['offline']}\n"
        device_text += "设备类型分布:\n"
        for device_type, count in status['device_stats']['type_stats'].items():
            device_text += f"  {device_type}: {count} 台\n"
        
        device_label = ttk.Label(device_frame, text=device_text, justify=tk.LEFT)
        device_label.pack(fill=tk.X)
    
    def _show_about_window(self):
        # 显示关于窗口
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x250")
        
        # 创建关于框架
        about_frame = ttk.Frame(about_window, padding="20")
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # 关于信息
        about_text = "智能停车场管理系统\n"
        about_text += "版本: 1.0.0\n\n"
        about_text += "这是一个基于Python开发的智能停车场管理系统，\n"
        about_text += "提供车辆管理、车位管理、用户管理、收费管理、\n"
        about_text += "报表统计和系统管理等功能。\n\n"
        about_text += "版权所有 © 2026\n"
        
        about_label = ttk.Label(about_frame, text=about_text, justify=tk.CENTER, font=("Arial", 12))
        about_label.pack(fill=tk.BOTH, expand=True)
        
        # 确定按钮
        ok_button = ttk.Button(about_frame, text="确定", command=about_window.destroy)
        ok_button.pack(side=tk.BOTTOM, pady=10)
