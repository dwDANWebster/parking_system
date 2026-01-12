import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class Vehicle:
    def __init__(self, plate_number, vehicle_type, brand=None, model=None, color=None):
        self.id = None
        self.plate_number = plate_number
        self.vehicle_type = vehicle_type
        self.brand = brand
        self.model = model
        self.color = color
        self.entry_time = None
        self.exit_time = None
        self.parking_space_id = None
        self.status = "registered"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "plate_number": self.plate_number,
            "vehicle_type": self.vehicle_type,
            "brand": self.brand,
            "model": self.model,
            "color": self.color,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "parking_space_id": self.parking_space_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class LicensePlateRecognition:
    def __init__(self, database):
        self.database = database
    
    def recognize_plate(self, image_path):
        logger.info(f"识别车牌: {image_path}")
        # 模拟车牌识别，实际项目中可以集成OCR库
        # 这里返回一个随机生成的车牌作为模拟
        import random
        provinces = ['京', '津', '冀', '晋', '蒙', '辽', '吉', '黑', '沪', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '桂', '琼', '渝', '川', '黔', '滇', '藏', '陕', '甘', '青', '宁', '新']
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        
        province = random.choice(provinces)
        letter = random.choice(letters)
        number = ''.join(random.choices(digits, k=5))
        
        plate_number = f"{province}{letter}{number}"
        logger.info(f"识别结果: {plate_number}")
        return plate_number
    
    def verify_plate(self, plate_number):
        logger.info(f"验证车牌: {plate_number}")
        # 简单的车牌格式验证
        if len(plate_number) != 7:
            return False
        # 检查第一个字符是否为汉字（省份简称）
        provinces = ['京', '津', '冀', '晋', '蒙', '辽', '吉', '黑', '沪', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '桂', '琼', '渝', '川', '黔', '滇', '藏', '陕', '甘', '青', '宁', '新']
        if plate_number[0] not in provinces:
            return False
        # 检查第二个字符是否为字母
        if not plate_number[1].isalpha():
            return False
        # 检查后五个字符是否为字母或数字
        for char in plate_number[2:]:
            if not (char.isalpha() or char.isdigit()):
                return False
        return True

class VehicleManager:
    def __init__(self, database):
        self.database = database
        self.lpr = LicensePlateRecognition(database)
    
    def init(self):
        logger.info("初始化车辆管理模块")
        # 添加一些初始车辆类型配置
        self._add_initial_vehicle_types()
    
    def _add_initial_vehicle_types(self):
        logger.info("添加初始车辆类型")
        # 这里可以添加一些初始的车辆类型配置
        pass
    
    def register_vehicle(self, plate_number, vehicle_type, brand=None, model=None, color=None):
        logger.info(f"注册车辆: {plate_number}, {vehicle_type}")
        try:
            # 验证车牌格式
            if not self.lpr.verify_plate(plate_number):
                raise ValueError(f"无效的车牌格式: {plate_number}")
            
            # 检查车辆是否已存在
            existing = self.database.fetch_one(
                "SELECT * FROM vehicles WHERE plate_number = ?",
                (plate_number,)
            )
            if existing:
                raise ValueError(f"车辆已存在: {plate_number}")
            
            # 插入车辆记录
            vehicle_id = self.database.execute(
                "INSERT INTO vehicles (plate_number, vehicle_type, brand, model, color, status) VALUES (?, ?, ?, ?, ?, ?)",
                (plate_number, vehicle_type, brand, model, color, "registered")
            )
            
            logger.info(f"车辆注册成功: {plate_number}, ID: {vehicle_id}")
            return vehicle_id
        except Exception as e:
            logger.error(f"车辆注册失败: {e}")
            raise
    
    def get_vehicle_by_plate(self, plate_number):
        logger.info(f"根据车牌获取车辆: {plate_number}")
        try:
            result = self.database.fetch_one(
                "SELECT * FROM vehicles WHERE plate_number = ?",
                (plate_number,)
            )
            if result:
                vehicle = Vehicle(
                    result['plate_number'],
                    result['vehicle_type'],
                    result['brand'],
                    result['model'],
                    result['color']
                )
                vehicle.id = result['id']
                vehicle.entry_time = result['entry_time']
                vehicle.exit_time = result['exit_time']
                vehicle.parking_space_id = result['parking_space_id']
                vehicle.status = result['status']
                vehicle.created_at = result['created_at']
                vehicle.updated_at = result['updated_at']
                return vehicle
            return None
        except Exception as e:
            logger.error(f"获取车辆失败: {e}")
            raise
    
    def get_vehicle_by_id(self, vehicle_id):
        logger.info(f"根据ID获取车辆: {vehicle_id}")
        try:
            result = self.database.fetch_one(
                "SELECT * FROM vehicles WHERE id = ?",
                (vehicle_id,)
            )
            if result:
                vehicle = Vehicle(
                    result['plate_number'],
                    result['vehicle_type'],
                    result['brand'],
                    result['model'],
                    result['color']
                )
                vehicle.id = result['id']
                vehicle.entry_time = result['entry_time']
                vehicle.exit_time = result['exit_time']
                vehicle.parking_space_id = result['parking_space_id']
                vehicle.status = result['status']
                vehicle.created_at = result['created_at']
                vehicle.updated_at = result['updated_at']
                return vehicle
            return None
        except Exception as e:
            logger.error(f"获取车辆失败: {e}")
            raise
    
    def update_vehicle(self, vehicle_id, **kwargs):
        logger.info(f"更新车辆信息: {vehicle_id}, {kwargs}")
        try:
            # 构建更新语句
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key in ['plate_number', 'vehicle_type', 'brand', 'model', 'color', 'status', 'parking_space_id']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            update_values.append(datetime.now())
            update_fields.append("updated_at = ?")
            update_values.append(vehicle_id)
            
            update_query = f"UPDATE vehicles SET {', '.join(update_fields)} WHERE id = ?"
            
            self.database.execute(update_query, update_values)
            logger.info(f"车辆信息更新成功: {vehicle_id}")
            return True
        except Exception as e:
            logger.error(f"更新车辆信息失败: {e}")
            raise
    
    def delete_vehicle(self, vehicle_id):
        logger.info(f"删除车辆: {vehicle_id}")
        try:
            self.database.execute(
                "DELETE FROM vehicles WHERE id = ?",
                (vehicle_id,)
            )
            logger.info(f"车辆删除成功: {vehicle_id}")
            return True
        except Exception as e:
            logger.error(f"删除车辆失败: {e}")
            raise
    
    def record_entry(self, plate_number, parking_space_id):
        logger.info(f"记录车辆进场: {plate_number}, 车位: {parking_space_id}")
        try:
            now = datetime.now()
            
            # 获取或创建车辆
            vehicle = self.get_vehicle_by_plate(plate_number)
            if not vehicle:
                # 如果车辆不存在，默认创建为小型车
                vehicle_id = self.register_vehicle(plate_number, "小型车")
                vehicle = self.get_vehicle_by_id(vehicle_id)
            
            # 更新车辆信息
            self.database.execute(
                "UPDATE vehicles SET entry_time = ?, status = 'parking', parking_space_id = ? WHERE id = ?",
                (now, parking_space_id, vehicle.id)
            )
            
            # 创建停车记录
            record_id = self.database.execute(
                "INSERT INTO parking_records (vehicle_id, parking_space_id, entry_time, payment_status) VALUES (?, ?, ?, ?)",
                (vehicle.id, parking_space_id, now, "unpaid")
            )
            
            logger.info(f"车辆进场记录成功: {plate_number}, 记录ID: {record_id}")
            return record_id
        except Exception as e:
            logger.error(f"记录车辆进场失败: {e}")
            raise
    
    def record_exit(self, plate_number):
        logger.info(f"记录车辆出场: {plate_number}")
        try:
            now = datetime.now()
            
            # 获取车辆信息
            vehicle = self.get_vehicle_by_plate(plate_number)
            if not vehicle:
                raise ValueError(f"车辆不存在: {plate_number}")
            
            if vehicle.status != "parking":
                raise ValueError(f"车辆未在停车场内: {plate_number}")
            
            # 获取停车记录
            record = self.database.fetch_one(
                "SELECT * FROM parking_records WHERE vehicle_id = ? AND exit_time IS NULL",
                (vehicle.id,)
            )
            if not record:
                raise ValueError(f"未找到有效的停车记录: {plate_number}")
            
            # 计算停车时长（分钟）
            entry_time = datetime.strptime(record['entry_time'], '%Y-%m-%d %H:%M:%S')
            duration = int((now - entry_time).total_seconds() / 60)
            
            # 更新车辆信息
            self.database.execute(
                "UPDATE vehicles SET exit_time = ?, status = 'registered', parking_space_id = NULL WHERE id = ?",
                (now, vehicle.id)
            )
            
            # 更新停车记录
            self.database.execute(
                "UPDATE parking_records SET exit_time = ?, duration = ? WHERE id = ?",
                (now, duration, record['id'])
            )
            
            logger.info(f"车辆出场记录成功: {plate_number}, 停车时长: {duration}分钟")
            return record['id']
        except Exception as e:
            logger.error(f"记录车辆出场失败: {e}")
            raise
    
    def get_all_vehicles(self, status=None):
        logger.info(f"获取所有车辆, 状态: {status}")
        try:
            query = "SELECT * FROM vehicles"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            query += " ORDER BY updated_at DESC"
            
            results = self.database.fetch_all(query, params)
            
            vehicles = []
            for result in results:
                vehicle = Vehicle(
                    result['plate_number'],
                    result['vehicle_type'],
                    result['brand'],
                    result['model'],
                    result['color']
                )
                vehicle.id = result['id']
                vehicle.entry_time = result['entry_time']
                vehicle.exit_time = result['exit_time']
                vehicle.parking_space_id = result['parking_space_id']
                vehicle.status = result['status']
                vehicle.created_at = result['created_at']
                vehicle.updated_at = result['updated_at']
                vehicles.append(vehicle)
            
            return vehicles
        except Exception as e:
            logger.error(f"获取所有车辆失败: {e}")
            raise
    
    def get_parking_vehicles(self):
        logger.info("获取当前停车车辆")
        return self.get_all_vehicles("parking")
    
    def get_vehicle_statistics(self, start_date, end_date):
        logger.info(f"获取车辆统计数据: {start_date} 到 {end_date}")
        try:
            # 统计这段时间内的车辆进出情况
            entry_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE entry_time BETWEEN ? AND ?",
                (start_date, end_date)
            )['count']
            
            exit_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE exit_time BETWEEN ? AND ?",
                (start_date, end_date)
            )['count']
            
            parking_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM vehicles WHERE status = 'parking'"
            )['count']
            
            total_vehicles = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM vehicles"
            )['count']
            
            return {
                'entry_count': entry_count,
                'exit_count': exit_count,
                'parking_count': parking_count,
                'total_vehicles': total_vehicles
            }
        except Exception as e:
            logger.error(f"获取车辆统计数据失败: {e}")
            raise
    
    def export_vehicle_data(self, file_path, start_date=None, end_date=None):
        logger.info(f"导出车辆数据到: {file_path}")
        try:
            import csv
            
            # 查询数据
            query = "SELECT * FROM vehicles"
            params = []
            
            if start_date and end_date:
                query += " WHERE created_at BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
            results = self.database.fetch_all(query, params)
            
            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(['ID', '车牌号码', '车辆类型', '品牌', '型号', '颜色', '进场时间', '出场时间', '车位ID', '状态', '创建时间', '更新时间'])
                
                # 写入数据
                for result in results:
                    writer.writerow([
                        result['id'],
                        result['plate_number'],
                        result['vehicle_type'],
                        result['brand'],
                        result['model'],
                        result['color'],
                        result['entry_time'],
                        result['exit_time'],
                        result['parking_space_id'],
                        result['status'],
                        result['created_at'],
                        result['updated_at']
                    ])
            
            logger.info(f"车辆数据导出成功: {file_path}, 共 {len(results)} 条记录")
            return len(results)
        except Exception as e:
            logger.error(f"导出车辆数据失败: {e}")
            raise