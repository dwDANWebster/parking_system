import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vehicle_management.vehicle_manager import VehicleManager
from parking_space_management.space_manager import SpaceManager
from user_management.user_manager import UserManager
from fee_management.fee_manager import FeeManager
from report_statistics.report_manager import ReportManager
from system_management.system_manager import SystemManager
from gui.main_window import MainWindow
from utils.database import Database

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parking_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ParkingSystem:
    def __init__(self):
        logger.info("初始化智能停车场管理系统")
        self.database = Database()
        self.vehicle_manager = VehicleManager(self.database)
        self.space_manager = SpaceManager(self.database)
        self.user_manager = UserManager(self.database)
        self.fee_manager = FeeManager(self.database)
        self.report_manager = ReportManager(self.database)
        self.system_manager = SystemManager(self.database)
        self.gui = None
        self.is_running = False
    
    def start(self):
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
            
            # 启动GUI界面
            self.gui = MainWindow(self)
            self.is_running = True
            self.gui.run()
            
        except Exception as e:
            logger.error(f"系统启动失败: {e}")
            raise
    
    def stop(self):
        logger.info("停止智能停车场管理系统")
        if self.is_running:
            try:
                # 关闭GUI界面
                if self.gui:
                    self.gui.stop()
                
                # 关闭数据库连接
                self.database.disconnect()
                
                self.is_running = False
            except Exception as e:
                logger.error(f"系统停止失败: {e}")
                raise
    
    def get_vehicle_manager(self):
        return self.vehicle_manager
    
    def get_space_manager(self):
        return self.space_manager
    
    def get_user_manager(self):
        return self.user_manager
    
    def get_fee_manager(self):
        return self.fee_manager
    
    def get_report_manager(self):
        return self.report_manager
    
    def get_system_manager(self):
        return self.system_manager

if __name__ == "__main__":
    logger.info("=== 智能停车场管理系统启动 ===")
    system = ParkingSystem()
    try:
        system.start()
    except KeyboardInterrupt:
        logger.info("用户中断系统")
    except Exception as e:
        logger.error(f"系统运行出错: {e}")
    finally:
        system.stop()
    logger.info("=== 智能停车场管理系统关闭 ===")