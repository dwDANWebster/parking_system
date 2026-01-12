#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能停车场管理系统主入口

该模块是智能停车场管理系统的核心入口点，负责初始化所有系统模块、建立数据库连接、
启动GUI界面，并协调整个系统的运行。
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到Python路径，确保模块导入正常
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vehicle_management.vehicle_manager import VehicleManager
from parking_space_management.space_manager import SpaceManager
from user_management.user_manager import UserManager
from fee_management.fee_manager import FeeManager
from report_statistics.report_manager import ReportManager
from system_management.system_manager import SystemManager
from gui.main_window import MainWindow
from utils.database import Database

# 配置日志系统，记录系统运行状态和错误信息
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parking_system.log'),  # 将日志保存到文件
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger(__name__)


class ParkingSystem:
    """
    智能停车场管理系统主类
    
    该类负责协调整个停车场管理系统的各个模块，包括：
    - 车辆管理
    - 车位管理
    - 用户管理
    - 费用管理
    - 报表统计
    - 系统管理
    - GUI界面
    
    属性：
        database: 数据库连接对象
        vehicle_manager: 车辆管理模块
        space_manager: 车位管理模块
        user_manager: 用户管理模块
        fee_manager: 费用管理模块
        report_manager: 报表管理模块
        system_manager: 系统管理模块
        gui: GUI界面对象
        is_running: 系统运行状态标志
    """
    
    def __init__(self):
        """初始化智能停车场管理系统"""
        logger.info("初始化智能停车场管理系统")
        self.database = Database()  # 数据库连接对象
        self.vehicle_manager = VehicleManager(self.database)  # 车辆管理模块
        self.space_manager = SpaceManager(self.database)  # 车位管理模块
        self.user_manager = UserManager(self.database)  # 用户管理模块
        self.fee_manager = FeeManager(self.database)  # 费用管理模块
        self.report_manager = ReportManager(self.database)  # 报表管理模块
        self.system_manager = SystemManager(self.database)  # 系统管理模块
        self.gui = None  # GUI界面对象
        self.is_running = False  # 系统运行状态标志
    
    def start(self):
        """
        启动智能停车场管理系统
        
        该方法执行以下操作：
        1. 建立数据库连接
        2. 初始化各个功能模块
        3. 启动GUI界面
        """
        logger.info("启动智能停车场管理系统")
        try:
            # 初始化数据库连接
            self.database.connect()
            
            # 初始化各个模块
            self.vehicle_manager.init()
            self.space_manager.init()
            self.user_manager.init()
            self.fee_manager.init()
            self.report_manager.init()
            self.system_manager.init()
            
            # 创建并启动GUI界面
            self.gui = MainWindow(self)
            self.is_running = True
            self.gui.run()
        except Exception as e:
            logger.error(f"系统启动失败: {e}")
            self.stop()
            raise
    
    def stop(self):
        """
        停止智能停车场管理系统
        
        该方法执行以下操作：
        1. 停止GUI界面
        2. 关闭数据库连接
        3. 清理系统资源
        """
        logger.info("停止智能停车场管理系统")
        try:
            if self.gui:
                self.gui.stop()
            
            if self.database:
                self.database.disconnect()
            
            self.is_running = False
            logger.info("系统已成功停止")
        except Exception as e:
            logger.error(f"系统停止过程中发生错误: {e}")
    
    def get_module(self, module_name):
        """
        获取指定名称的系统模块
        
        参数：
            module_name: 模块名称，可选值包括：
                - vehicle_manager
                - space_manager
                - user_manager
                - fee_manager
                - report_manager
                - system_manager
        
        返回：
            对应的模块对象，若模块名称无效则返回None
        """
        module_map = {
            'vehicle_manager': self.vehicle_manager,
            'space_manager': self.space_manager,
            'user_manager': self.user_manager,
            'fee_manager': self.fee_manager,
            'report_manager': self.report_manager,
            'system_manager': self.system_manager
        }
        return module_map.get(module_name)


def main():
    """
    系统主函数
    
    该函数创建ParkingSystem实例并启动系统，处理系统启动和停止的异常情况。
    """
    logger.info("=== 智能停车场管理系统启动 ===")
    parking_system = ParkingSystem()
    
    try:
        parking_system.start()
    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号，停止系统")
        parking_system.stop()
    except Exception as e:
        logger.error(f"系统运行过程中发生严重错误: {e}")
        parking_system.stop()
        sys.exit(1)
    finally:
        logger.info("=== 智能停车场管理系统停止 ===")


if __name__ == "__main__":
    # 直接运行该脚本时，启动系统
    main()
