#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统管理模块

该模块负责智能停车场的系统管理功能，包括系统配置管理、日志管理、系统状态监控等。
实现了灵活的配置管理和全面的系统日志记录功能。
"""

import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SystemConfig:
    """
    系统配置类
    
    该类负责系统配置的加载、保存和管理。
    """
    
    def __init__(self, database):
        """
        初始化系统配置对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
        self.configs = {}
        self._load_configs()
    
    def _load_configs(self):
        """
        从数据库加载系统配置
        """
        logger.info("加载系统配置")
        try:
            configs = self.database.fetchall("SELECT * FROM system_configs")
            for config in configs:
                self.configs[config["config_key"]] = {
                    "value": config["config_value"],
                    "type": config["config_type"],
                    "description": config["description"]
                }
            logger.info(f"成功加载{len(self.configs)}项系统配置")
        except Exception as e:
            logger.error(f"加载系统配置失败: {e}")
    
    def get_config(self, key, default=None):
        """
        获取配置项
        
        参数：
            key: 配置项键名
            default: 默认值，可选
        
        返回：
            配置项值
        """
        if key in self.configs:
            config = self.configs[key]
            value = config["value"]
            # 根据配置类型转换值
            if config["type"] == "int":
                return int(value)
            elif config["type"] == "float":
                return float(value)
            elif config["type"] == "bool":
                return value.lower() == "true"
            return value
        return default
    
    def set_config(self, key, value, config_type="string", description=""):
        """
        设置配置项
        
        参数：
            key: 配置项键名
            value: 配置项值
            config_type: 配置项类型，可选值：string, int, float, bool
            description: 配置项描述
        """
        logger.info(f"设置配置项: {key} = {value}, 类型: {config_type}")
        try:
            # 转换值为字符串
            str_value = str(value)
            
            # 更新内存中的配置
            self.configs[key] = {
                "value": str_value,
                "type": config_type,
                "description": description
            }
            
            # 更新数据库中的配置
            # 检查配置项是否已存在
            existing_config = self.database.fetchone(
                "SELECT * FROM system_configs WHERE config_key = ?",
                [key]
            )
            
            if existing_config:
                # 更新现有配置
                self.database.update(
                    "system_configs",
                    {
                        "config_value": str_value,
                        "config_type": config_type,
                        "description": description,
                        "updated_at": datetime.now()
                    },
                    "config_key = ?",
                    [key]
                )
            else:
                # 插入新配置
                self.database.insert(
                    "system_configs",
                    {
                        "config_key": key,
                        "config_value": str_value,
                        "config_type": config_type,
                        "description": description,
                        "updated_at": datetime.now()
                    }
                )
            logger.info(f"配置项设置成功: {key}")
            return True
        except Exception as e:
            logger.error(f"设置配置项失败: {e}")
            return False
    
    def get_all_configs(self):
        """
        获取所有配置项
        
        返回：
            包含所有配置项的字典
        """
        return self.configs


class SystemLogger:
    """
    系统日志类
    
    该类负责系统日志的记录和管理。
    """
    
    def __init__(self, database):
        """
        初始化系统日志对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
    
    def log(self, level, message, module="", user_id=None):
        """
        记录系统日志
        
        参数：
            level: 日志级别，可选值：debug, info, warning, error, critical
            message: 日志消息
            module: 模块名称
            user_id: 用户ID，可选
        """
        try:
            self.database.insert(
                "logs",
                {
                    "level": level,
                    "message": message,
                    "module": module,
                    "user_id": user_id,
                    "created_at": datetime.now()
                }
            )
        except Exception as e:
            # 如果数据库日志记录失败，回退到文件日志
            logger.error(f"记录日志到数据库失败: {e}, 消息: {message}")
    
    def get_logs(self, level=None, start_time=None, end_time=None, module=None, limit=100):
        """
        获取系统日志
        
        参数：
            level: 日志级别，可选
            start_time: 开始时间，可选
            end_time: 结束时间，可选
            module: 模块名称，可选
            limit: 返回日志数量限制，默认100
        
        返回：
            日志列表
        """
        logger.info(f"获取系统日志: 级别: {level}, 开始时间: {start_time}, 结束时间: {end_time}, 模块: {module}")
        try:
            # 构建查询条件
            query = "SELECT * FROM logs WHERE 1=1"
            params = []
            
            if level:
                query += " AND level = ?"
                params.append(level)
            
            if start_time:
                query += " AND created_at >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND created_at <= ?"
                params.append(end_time)
            
            if module:
                query += " AND module = ?"
                params.append(module)
            
            # 按时间倒序排列，限制返回数量
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            logs = self.database.fetchall(query, params)
            return [dict(log) for log in logs]
        except Exception as e:
            logger.error(f"获取系统日志失败: {e}")
            return []


class SystemManager:
    """
    系统管理器类
    
    该类负责系统的整体管理，包括配置管理、日志管理、系统状态监控等。
    """
    
    def __init__(self, database):
        """
        初始化系统管理器
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
        self.config = SystemConfig(database)
        self.logger = SystemLogger(database)
        self._init_default_configs()
    
    def init(self):
        """
        初始化系统管理器
        """
        logger.info("初始化系统管理器")
    
    def _init_default_configs(self):
        """
        初始化默认配置项
        """
        logger.info("初始化默认配置项")
        # 停车费用相关配置
        self.config.set_config(
            "parking.fee.small_car.hourly_rate",
            5.0,
            "float",
            "小型车每小时停车费"
        )
        
        self.config.set_config(
            "parking.fee.large_car.hourly_rate",
            10.0,
            "float",
            "大型车每小时停车费"
        )
        
        self.config.set_config(
            "parking.fee.free_duration",
            30,
            "int",
            "免费停车时长（分钟）"
        )
        
        self.config.set_config(
            "parking.fee.daily_max",
            50.0,
            "float",
            "每日最大停车费"
        )
        
        # 系统相关配置
        self.config.set_config(
            "system.name",
            "智能停车场管理系统",
            "string",
            "系统名称"
        )
        
        self.config.set_config(
            "system.version",
            "1.0.0",
            "string",
            "系统版本"
        )
        
        self.config.set_config(
            "system.log_level",
            "info",
            "string",
            "系统日志级别"
        )
    
    def get_system_info(self):
        """
        获取系统信息
        
        返回：
            包含系统信息的字典
        """
        logger.info("获取系统信息")
        return {
            "name": self.config.get_config("system.name"),
            "version": self.config.get_config("system.version"),
            "log_level": self.config.get_config("system.log_level"),
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_system_status(self):
        """
        获取系统状态
        
        返回：
            包含系统状态的字典
        """
        logger.info("获取系统状态")
        try:
            # 获取数据库连接状态
            db_status = "connected" if self.database.conn else "disconnected"
            
            # 获取车辆数量统计
            total_vehicles = self.database.fetchone(
                "SELECT COUNT(*) as count FROM vehicles" 
            )["count"]
            
            parking_vehicles = self.database.fetchone(
                "SELECT COUNT(*) as count FROM vehicles WHERE status = 'parking'"
            )["count"]
            
            # 获取车位数量统计
            total_spaces = self.database.fetchone(
                "SELECT COUNT(*) as count FROM parking_spaces"
            )["count"]
            
            occupied_spaces = self.database.fetchone(
                "SELECT COUNT(*) as count FROM parking_spaces WHERE status = 'occupied'"
            )["count"]
            
            return {
                "database": db_status,
                "total_vehicles": total_vehicles,
                "parking_vehicles": parking_vehicles,
                "total_spaces": total_spaces,
                "occupied_spaces": occupied_spaces,
                "available_spaces": total_spaces - occupied_spaces,
                "space_usage_rate": round(occupied_spaces / total_spaces * 100, 2) if total_spaces > 0 else 0
            }
        except Exception as e:
            logger.error(f"获取系统状态失败: {e}")
            return {
                "database": "error",
                "error": str(e)
            }
    
    def backup_database(self, backup_path=None):
        """
        备份数据库
        
        参数：
            backup_path: 备份文件路径，可选
        
        返回：
            备份文件路径
        """
        logger.info("备份数据库")
        try:
            if not backup_path:
                # 默认备份路径
                backup_dir = "backups"
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(backup_dir, f"parking_system_backup_{timestamp}.db")
            
            # 执行备份
            # 对于SQLite，可以直接复制数据库文件
            import shutil
            shutil.copy2("parking_system.db", backup_path)
            
            logger.info(f"数据库备份成功: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return None
    
    def restore_database(self, backup_path):
        """
        恢复数据库
        
        参数：
            backup_path: 备份文件路径
        
        返回：
            布尔值，表示恢复是否成功
        """
        logger.info(f"恢复数据库: {backup_path}")
        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_path):
                logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            # 关闭数据库连接
            self.database.disconnect()
            
            # 复制备份文件到数据库路径
            import shutil
            shutil.copy2(backup_path, "parking_system.db")
            
            # 重新连接数据库
            self.database.connect()
            
            logger.info("数据库恢复成功")
            return True
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}")
            # 尝试重新连接数据库
            try:
                self.database.connect()
            except:
                pass
            return False
    
    def clean_old_logs(self, days=30):
        """
        清理旧日志
        
        参数：
            days: 保留最近多少天的日志
        
        返回：
            布尔值，表示清理是否成功
        """
        logger.info(f"清理{days}天前的旧日志")
        try:
            # 计算清理日期
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # 删除指定日期之前的日志
            deleted_count = self.database.delete(
                "logs",
                "created_at < ?",
                [cutoff_str]
            )
            
            logger.info(f"成功清理{deleted_count}条旧日志")
            return True
        except Exception as e:
            logger.error(f"清理旧日志失败: {e}")
            return False
