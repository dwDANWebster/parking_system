import logging
from datetime import datetime
from typing import List, Dict, Optional
import os
import json

logger = logging.getLogger(__name__)

class SystemManager:
    def __init__(self, database):
        self.database = database
    
    def init(self):
        logger.info("初始化系统管理模块")
        # 添加初始系统配置
        self._add_initial_configs()
        # 添加初始设备
        self._add_initial_devices()
    
    def _add_initial_configs(self):
        logger.info("添加初始系统配置")
        try:
            # 定义初始配置项
            configs = [
                ("system_name", "智能停车场管理系统", "系统名称"),
                ("version", "1.0.0", "系统版本"),
                ("max_parking_time", "1440", "最大停车时间（分钟）"),
                ("default_vehicle_type", "小型车", "默认车辆类型"),
                ("entry_timeout", "30", "入场超时时间（秒）"),
                ("exit_timeout", "30", "出场超时时间（秒）"),
                ("reservation_validity", "60", "预订有效期（分钟）"),
                ("fee_update_interval", "5", "费用更新间隔（秒）"),
                ("log_level", "INFO", "日志级别"),
                ("backup_path", "./backups", "备份路径"),
                ("auto_backup", "true", "是否自动备份")
            ]
            
            for config_key, config_value, description in configs:
                # 检查配置项是否已存在
                existing = self.database.fetch_one(
                    "SELECT * FROM system_configs WHERE config_key = ?",
                    (config_key,)
                )
                if not existing:
                    self.database.execute(
                        "INSERT INTO system_configs (config_key, config_value, description) VALUES (?, ?, ?)",
                        (config_key, config_value, description)
                    )
            
            logger.info("初始系统配置添加完成")
        except Exception as e:
            logger.error(f"添加初始系统配置失败: {e}")
            raise
    
    def _add_initial_devices(self):
        logger.info("添加初始设备")
        try:
            # 定义初始设备
            devices = [
                ("入口摄像头1", "camera", "192.168.1.100", 8080, "online"),
                ("入口摄像头2", "camera", "192.168.1.101", 8080, "online"),
                ("出口摄像头1", "camera", "192.168.1.102", 8080, "online"),
                ("出口摄像头2", "camera", "192.168.1.103", 8080, "online"),
                ("入口道闸", "barrier", "192.168.1.200", 8000, "online"),
                ("出口道闸", "barrier", "192.168.1.201", 8000, "online"),
                ("车位检测器1", "sensor", "192.168.1.300", 9000, "online"),
                ("车位检测器2", "sensor", "192.168.1.301", 9000, "online")
            ]
            
            for device_name, device_type, ip_address, port, status in devices:
                # 检查设备是否已存在
                existing = self.database.fetch_one(
                    "SELECT * FROM devices WHERE device_name = ?",
                    (device_name,)
                )
                if not existing:
                    self.database.execute(
                        "INSERT INTO devices (device_name, device_type, ip_address, port, status, last_online) VALUES (?, ?, ?, ?, ?, ?)",
                        (device_name, device_type, ip_address, port, status, datetime.now())
                    )
            
            logger.info("初始设备添加完成")
        except Exception as e:
            logger.error(f"添加初始设备失败: {e}")
            raise
    
    def get_config(self, config_key):
        logger.info(f"获取系统配置: {config_key}")
        try:
            result = self.database.fetch_one(
                "SELECT * FROM system_configs WHERE config_key = ?",
                (config_key,)
            )
            if result:
                return result['config_value']
            return None
        except Exception as e:
            logger.error(f"获取系统配置失败: {e}")
            raise
    
    def get_all_configs(self):
        logger.info("获取所有系统配置")
        try:
            results = self.database.fetch_all(
                "SELECT * FROM system_configs ORDER BY config_key"
            )
            
            configs = {}
            for result in results:
                configs[result['config_key']] = result['config_value']
            
            return configs
        except Exception as e:
            logger.error(f"获取所有系统配置失败: {e}")
            raise
    
    def update_config(self, config_key, config_value, description=None):
        logger.info(f"更新系统配置: {config_key} = {config_value}")
        try:
            # 检查配置项是否存在
            existing = self.database.fetch_one(
                "SELECT * FROM system_configs WHERE config_key = ?",
                (config_key,)
            )
            
            if existing:
                # 更新配置
                if description:
                    self.database.execute(
                        "UPDATE system_configs SET config_value = ?, description = ?, updated_at = ? WHERE config_key = ?",
                        (config_value, description, datetime.now(), config_key)
                    )
                else:
                    self.database.execute(
                        "UPDATE system_configs SET config_value = ?, updated_at = ? WHERE config_key = ?",
                        (config_value, datetime.now(), config_key)
                    )
            else:
                # 添加新配置
                self.database.execute(
                    "INSERT INTO system_configs (config_key, config_value, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (config_key, config_value, description, datetime.now(), datetime.now())
                )
            
            logger.info(f"系统配置更新成功: {config_key} = {config_value}")
            return True
        except Exception as e:
            logger.error(f"更新系统配置失败: {e}")
            raise
    
    def delete_config(self, config_key):
        logger.info(f"删除系统配置: {config_key}")
        try:
            self.database.execute(
                "DELETE FROM system_configs WHERE config_key = ?",
                (config_key,)
            )
            logger.info(f"系统配置删除成功: {config_key}")
            return True
        except Exception as e:
            logger.error(f"删除系统配置失败: {e}")
            raise
    
    def log_system_event(self, module, message, details=None):
        logger.info(f"记录系统事件: {module} - {message}")
        try:
            self.database.execute(
                "INSERT INTO logs (log_level, module, message, details) VALUES (?, ?, ?, ?)",
                ("INFO", module, message, details)
            )
            return True
        except Exception as e:
            logger.error(f"记录系统事件失败: {e}")
            raise
    
    def log_error_event(self, module, message, details=None):
        logger.error(f"记录错误事件: {module} - {message}")
        try:
            self.database.execute(
                "INSERT INTO logs (log_level, module, message, details) VALUES (?, ?, ?, ?)",
                ("ERROR", module, message, details)
            )
            return True
        except Exception as e:
            logger.error(f"记录错误事件失败: {e}")
            raise
    
    def get_logs(self, log_level=None, module=None, start_date=None, end_date=None, limit=100):
        logger.info(f"获取系统日志: 级别 {log_level}, 模块 {module}, 开始日期 {start_date}, 结束日期 {end_date}, 限制 {limit}")
        try:
            query = "SELECT * FROM logs"
            params = []
            conditions = []
            
            if log_level:
                conditions.append("log_level = ?")
                params.append(log_level)
            
            if module:
                conditions.append("module = ?")
                params.append(module)
            
            if start_date:
                conditions.append("log_time >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("log_time <= ?")
                params.append(end_date)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY log_time DESC LIMIT ?"
            params.append(limit)
            
            results = self.database.fetch_all(query, params)
            
            logs = []
            for result in results:
                logs.append({
                    "id": result['id'],
                    "log_time": result['log_time'],
                    "log_level": result['log_level'],
                    "module": result['module'],
                    "message": result['message'],
                    "details": result['details']
                })
            
            return logs
        except Exception as e:
            logger.error(f"获取系统日志失败: {e}")
            raise
    
    def export_logs(self, file_path, log_level=None, module=None, start_date=None, end_date=None):
        logger.info(f"导出系统日志到: {file_path}")
        try:
            import csv
            
            # 获取日志数据
            logs = self.get_logs(log_level, module, start_date, end_date, limit=10000)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(['ID', '时间', '级别', '模块', '消息', '详情'])
                
                # 写入数据
                for log in logs:
                    writer.writerow([
                        log['id'],
                        log['log_time'],
                        log['log_level'],
                        log['module'],
                        log['message'],
                        log['details']
                    ])
            
            logger.info(f"系统日志导出成功: {file_path}, 共 {len(logs)} 条记录")
            return len(logs)
        except Exception as e:
            logger.error(f"导出系统日志失败: {e}")
            raise
    
    def add_device(self, device_name, device_type, ip_address, port, status="online"):
        logger.info(f"添加设备: {device_name}, 类型: {device_type}")
        try:
            # 检查设备是否已存在
            existing = self.database.fetch_one(
                "SELECT * FROM devices WHERE device_name = ?",
                (device_name,)
            )
            if existing:
                raise ValueError(f"设备已存在: {device_name}")
            
            # 插入设备记录
            device_id = self.database.execute(
                "INSERT INTO devices (device_name, device_type, ip_address, port, status, last_online) VALUES (?, ?, ?, ?, ?, ?)",
                (device_name, device_type, ip_address, port, status, datetime.now())
            )
            
            logger.info(f"设备添加成功: {device_name}, ID: {device_id}")
            return device_id
        except Exception as e:
            logger.error(f"添加设备失败: {e}")
            raise
    
    def get_device(self, device_id):
        logger.info(f"获取设备: {device_id}")
        try:
            result = self.database.fetch_one(
                "SELECT * FROM devices WHERE id = ?",
                (device_id,)
            )
            if result:
                return {
                    "id": result['id'],
                    "device_name": result['device_name'],
                    "device_type": result['device_type'],
                    "ip_address": result['ip_address'],
                    "port": result['port'],
                    "status": result['status'],
                    "last_online": result['last_online'],
                    "created_at": result['created_at'],
                    "updated_at": result['updated_at']
                }
            return None
        except Exception as e:
            logger.error(f"获取设备失败: {e}")
            raise
    
    def get_all_devices(self, device_type=None, status=None):
        logger.info(f"获取所有设备, 类型: {device_type}, 状态: {status}")
        try:
            query = "SELECT * FROM devices"
            params = []
            conditions = []
            
            if device_type:
                conditions.append("device_type = ?")
                params.append(device_type)
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY updated_at DESC"
            
            results = self.database.fetch_all(query, params)
            
            devices = []
            for result in results:
                devices.append({
                    "id": result['id'],
                    "device_name": result['device_name'],
                    "device_type": result['device_type'],
                    "ip_address": result['ip_address'],
                    "port": result['port'],
                    "status": result['status'],
                    "last_online": result['last_online'],
                    "created_at": result['created_at'],
                    "updated_at": result['updated_at']
                })
            
            return devices
        except Exception as e:
            logger.error(f"获取所有设备失败: {e}")
            raise
    
    def update_device(self, device_id, **kwargs):
        logger.info(f"更新设备信息: {device_id}, {kwargs}")
        try:
            # 构建更新语句
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key in ['device_name', 'device_type', 'ip_address', 'port', 'status', 'last_online']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            update_values.append(datetime.now())
            update_fields.append("updated_at = ?")
            update_values.append(device_id)
            
            update_query = f"UPDATE devices SET {', '.join(update_fields)} WHERE id = ?"
            
            self.database.execute(update_query, update_values)
            logger.info(f"设备信息更新成功: {device_id}")
            return True
        except Exception as e:
            logger.error(f"更新设备信息失败: {e}")
            raise
    
    def delete_device(self, device_id):
        logger.info(f"删除设备: {device_id}")
        try:
            self.database.execute(
                "DELETE FROM devices WHERE id = ?",
                (device_id,)
            )
            logger.info(f"设备删除成功: {device_id}")
            return True
        except Exception as e:
            logger.error(f"删除设备失败: {e}")
            raise
    
    def backup_database(self, backup_path=None):
        logger.info(f"备份数据库: {backup_path}")
        try:
            # 获取备份路径
            if not backup_path:
                backup_path = self.get_config("backup_path") or "./backups"
            
            # 创建备份目录
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
            
            # 生成备份文件名
            backup_filename = f"parking_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_filepath = os.path.join(backup_path, backup_filename)
            
            # 执行备份
            import shutil
            shutil.copy2("parking_system.db", backup_filepath)
            
            logger.info(f"数据库备份成功: {backup_filepath}")
            return backup_filepath
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            raise
    
    def restore_database(self, backup_filepath):
        logger.info(f"恢复数据库: {backup_filepath}")
        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_filepath):
                raise ValueError(f"备份文件不存在: {backup_filepath}")
            
            # 执行恢复
            import shutil
            shutil.copy2(backup_filepath, "parking_system.db")
            
            logger.info(f"数据库恢复成功: {backup_filepath}")
            return True
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}")
            raise
    
    def get_system_status(self):
        logger.info("获取系统状态")
        try:
            # 获取系统基本信息
            system_info = {
                "system_name": self.get_config("system_name"),
                "version": self.get_config("version"),
                "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "python_version": self._get_python_version()
            }
            
            # 获取系统资源使用情况
            resource_info = self._get_resource_usage()
            
            # 获取数据库状态
            db_info = self._get_database_status()
            
            # 获取设备状态统计
            device_stats = self._get_device_stats()
            
            # 获取系统配置摘要
            config_summary = {
                "log_level": self.get_config("log_level"),
                "auto_backup": self.get_config("auto_backup"),
                "backup_path": self.get_config("backup_path")
            }
            
            return {
                "system_info": system_info,
                "resource_info": resource_info,
                "db_info": db_info,
                "device_stats": device_stats,
                "config_summary": config_summary
            }
        except Exception as e:
            logger.error(f"获取系统状态失败: {e}")
            raise
    
    def _get_python_version(self):
        import sys
        return f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_resource_usage(self):
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_total": round(memory.total / (1024 * 1024 * 1024), 2),
                "memory_used": round(memory.used / (1024 * 1024 * 1024), 2),
                "memory_percent": memory.percent,
                "disk_total": round(disk.total / (1024 * 1024 * 1024), 2),
                "disk_used": round(disk.used / (1024 * 1024 * 1024), 2),
                "disk_percent": disk.percent
            }
        except Exception as e:
            logger.warning(f"获取系统资源使用情况失败: {e}")
            return {}
    
    def _get_database_status(self):
        try:
            # 获取数据库连接数
            # 这里简化处理，实际项目中可以根据数据库类型获取
            
            # 获取数据库表统计
            tables = ['vehicles', 'parking_spaces', 'users', 'parking_records', 'payments', 'logs']
            table_stats = {}
            for table in tables:
                count = self.database.fetch_one(
                    f"SELECT COUNT(*) as count FROM {table}"
                )['count']
                table_stats[table] = count
            
            return table_stats
        except Exception as e:
            logger.error(f"获取数据库状态失败: {e}")
            return {}
    
    def _get_device_stats(self):
        try:
            # 统计设备状态
            online_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM devices WHERE status = ?",
                ("online",)
            )['count']
            
            offline_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM devices WHERE status = ?",
                ("offline",)
            )['count']
            
            # 统计设备类型
            device_type_stats = self.database.fetch_all(
                "SELECT device_type, COUNT(*) as count FROM devices GROUP BY device_type"
            )
            
            type_stats = {}
            for stat in device_type_stats:
                type_stats[stat['device_type']] = stat['count']
            
            return {
                "total": online_count + offline_count,
                "online": online_count,
                "offline": offline_count,
                "type_stats": type_stats
            }
        except Exception as e:
            logger.error(f"获取设备状态统计失败: {e}")
            return {}
    
    def export_system_data(self, export_path):
        logger.info(f"导出系统数据到: {export_path}")
        try:
            # 创建导出目录
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            
            # 导出系统配置
            configs = self.get_all_configs()
            config_file = os.path.join(export_path, "system_configs.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
            
            # 导出设备信息
            devices = self.get_all_devices()
            devices_file = os.path.join(export_path, "devices.json")
            with open(devices_file, 'w', encoding='utf-8') as f:
                json.dump(devices, f, ensure_ascii=False, indent=2, default=str)
            
            # 导出日志（最近1000条）
            logs = self.get_logs(limit=1000)
            logs_file = os.path.join(export_path, "recent_logs.json")
            with open(logs_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"系统数据导出成功: {export_path}")
            return {
                "config_file": config_file,
                "devices_file": devices_file,
                "logs_file": logs_file
            }
        except Exception as e:
            logger.error(f"导出系统数据失败: {e}")
            raise
    
    def import_system_data(self, import_path):
        logger.info(f"导入系统数据从: {import_path}")
        try:
            # 导入系统配置
            config_file = os.path.join(import_path, "system_configs.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    configs = json.load(f)
                    for key, value in configs.items():
                        self.update_config(key, value)
            
            # 导入设备信息（仅添加新设备）
            devices_file = os.path.join(import_path, "devices.json")
            if os.path.exists(devices_file):
                with open(devices_file, 'r', encoding='utf-8') as f:
                    devices = json.load(f)
                    for device in devices:
                        # 检查设备是否已存在
                        existing = self.database.fetch_one(
                            "SELECT * FROM devices WHERE device_name = ?",
                            (device['device_name'],)
                        )
                        if not existing:
                            self.add_device(
                                device['device_name'],
                                device['device_type'],
                                device['ip_address'],
                                device['port'],
                                device['status']
                            )
            
            logger.info(f"系统数据导入成功: {import_path}")
            return True
        except Exception as e:
            logger.error(f"导入系统数据失败: {e}")
            raise
    
    def generate_system_report(self, report_type="summary"):
        logger.info(f"生成系统报告: {report_type}")
        try:
            # 获取系统状态
            system_status = self.get_system_status()
            
            # 根据报告类型生成不同内容
            if report_type == "detailed":
                # 详细报告，包含所有系统信息
                return system_status
            else:
                # 摘要报告，仅包含关键信息
                return {
                    "system_name": system_status["system_info"]["system_name"],
                    "version": system_status["system_info"]["version"],
                    "current_time": system_status["system_info"]["current_time"],
                    "resource_usage": {
                        "cpu_percent": system_status["resource_info"]["cpu_percent"],
                        "memory_percent": system_status["resource_info"]["memory_percent"],
                        "disk_percent": system_status["resource_info"]["disk_percent"]
                    },
                    "device_stats": system_status["device_stats"],
                    "db_table_counts": {
                        "vehicles": system_status["db_info"]["vehicles"] if "vehicles" in system_status["db_info"] else 0,
                        "parking_spaces": system_status["db_info"]["parking_spaces"] if "parking_spaces" in system_status["db_info"] else 0,
                        "users": system_status["db_info"]["users"] if "users" in system_status["db_info"] else 0,
                        "parking_records": system_status["db_info"]["parking_records"] if "parking_records" in system_status["db_info"] else 0,
                        "payments": system_status["db_info"]["payments"] if "payments" in system_status["db_info"] else 0,
                        "logs": system_status["db_info"]["logs"] if "logs" in system_status["db_info"] else 0
                    },
                    "config_summary": system_status["config_summary"]
                }
        except Exception as e:
            logger.error(f"生成系统报告失败: {e}")
            raise