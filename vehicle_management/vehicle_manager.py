#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车辆管理模块

该模块负责智能停车场的车辆管理，包括车辆信息维护、车牌识别模拟、车辆进出记录等功能。
实现了基于车牌的车辆识别和管理，支持多种车辆类型。
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class Vehicle:
    """
    车辆信息类
    
    该类封装了车辆的基本信息，包括车牌号码、车辆类型、品牌、型号、颜色等属性。
    
    属性：
        id: 车辆ID，数据库自动生成
        plate_number: 车牌号码，唯一标识
        vehicle_type: 车辆类型，如'小型车'、'大型车'、'残疾人专用'等
        brand: 车辆品牌
        model: 车辆型号
        color: 车辆颜色
        entry_time: 进场时间
        exit_time: 出场时间
        parking_space_id: 分配的车位ID
        status: 车辆状态，如'registered'（已注册）、'parking'（停车中）、'left'（已离开）等
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    def __init__(self, plate_number, vehicle_type, brand=None, model=None, color=None):
        """
        初始化车辆对象
        
        参数：
            plate_number: 车牌号码
            vehicle_type: 车辆类型
            brand: 车辆品牌，可选
            model: 车辆型号，可选
            color: 车辆颜色，可选
        """
        self.id = None
        self.plate_number = plate_number
        self.vehicle_type = vehicle_type
        self.brand = brand
        self.model = model
        self.color = color
        self.entry_time = None
        self.exit_time = None
        self.parking_space_id = None
        self.status = "registered"  # 默认状态为已注册
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """
        将车辆对象转换为字典格式
        
        返回：
            包含车辆所有属性的字典
        """
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
    """
    车牌识别类
    
    该类模拟了车牌识别功能，实际项目中可以集成OCR库或摄像头硬件来实现真实的车牌识别。
    
    属性：
        database: 数据库连接对象
    """
    
    def __init__(self, database):
        """
        初始化车牌识别对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
    
    def recognize_plate(self, image_path):
        """
        识别车牌号码
        
        该方法模拟了车牌识别功能，返回一个随机生成的车牌号码。
        实际项目中，这里可以集成OCR库或调用硬件接口来实现真实的车牌识别。
        
        参数：
            image_path: 包含车牌的图片路径
        
        返回：
            识别到的车牌号码
        """
        logger.info(f"识别车牌: {image_path}")
        # 模拟车牌识别，实际项目中可以集成OCR库
        # 这里返回一个随机生成的车牌作为模拟
        import random
        provinces = ['京', '津', '冀', '晋', '蒙', '辽', '吉', '黑', '沪', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '桂', '琼', '渝', '川', '黔', '滇', '藏', '陕', '甘', '青', '宁', '新']
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        
        province = random.choice(provinces)
        letter = random.choice(letters)
        number_part = ''.join(random.choices(digits, k=5))
        
        recognized_plate = f"{province}{letter}{number_part}"
        logger.info(f"识别结果: {recognized_plate}")
        return recognized_plate


class VehicleManager:
    """
    车辆管理器类
    
    该类封装了车辆管理的核心功能，包括车辆的添加、删除、查询、进出记录等操作。
    
    属性：
        database: 数据库连接对象
        license_plate_recognition: 车牌识别对象
    """
    
    def __init__(self, database):
        """
        初始化车辆管理器对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
        self.license_plate_recognition = LicensePlateRecognition(database)
    
    def init(self):
        """
        初始化车辆管理器
        
        该方法执行以下操作：
        1. 检查是否需要初始化车辆数据
        2. 如果没有车辆数据，则创建初始车辆
        """
        logger.info("初始化车辆管理器")
        try:
            # 检查是否已有车辆数据
            vehicle_count = self.database.fetchone("SELECT COUNT(*) as count FROM vehicles")["count"]
            
            # 如果没有车辆数据，则创建初始车辆
            if vehicle_count == 0:
                logger.info("没有车辆数据，创建初始车辆")
                self._create_initial_vehicles()
        except Exception as e:
            logger.error(f"车辆管理器初始化失败: {e}")
            raise
    
    def _create_initial_vehicles(self):
        """
        创建初始车辆数据
        
        该方法创建一些示例车辆数据，用于系统测试和演示。
        """
        initial_vehicles = [
            {
                "plate_number": "京A12345",
                "vehicle_type": "小型车",
                "brand": "大众",
                "model": "帕萨特",
                "color": "黑色",
                "status": "registered",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "plate_number": "沪B67890",
                "vehicle_type": "小型车",
                "brand": "丰田",
                "model": "凯美瑞",
                "color": "白色",
                "status": "registered",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "plate_number": "粤C54321",
                "vehicle_type": "大型车",
                "brand": "解放",
                "model": "J6P",
                "color": "红色",
                "status": "registered",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "plate_number": "苏D98765",
                "vehicle_type": "小型车",
                "brand": "本田",
                "model": "CR-V",
                "color": "银色",
                "status": "registered",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        # 插入初始车辆数据
        for vehicle in initial_vehicles:
            self.database.insert("vehicles", vehicle)
        
        logger.info(f"成功创建{len(initial_vehicles)}个初始车辆")
    
    def add_vehicle(self, plate_number, vehicle_type, brand=None, model=None, color=None):
        """
        添加新车辆
        
        参数：
            plate_number: 车牌号码
            vehicle_type: 车辆类型
            brand: 车辆品牌，可选
            model: 车辆型号，可选
            color: 车辆颜色，可选
        
        返回：
            新添加的车辆ID
        """
        logger.info(f"添加新车辆: {plate_number}, 类型: {vehicle_type}")
        try:
            # 检查车牌号码是否已存在
            existing_vehicle = self.database.fetchone(
                "SELECT * FROM vehicles WHERE plate_number = ?",
                [plate_number]
            )
            
            if existing_vehicle:
                logger.warning(f"车牌号码已存在: {plate_number}")
                return None
            
            # 创建新车辆
            new_vehicle = {
                "plate_number": plate_number,
                "vehicle_type": vehicle_type,
                "brand": brand,
                "model": model,
                "color": color,
                "status": "registered",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 插入新车辆数据
            vehicle_id = self.database.insert("vehicles", new_vehicle)
            logger.info(f"成功添加新车辆: {vehicle_id}")
            return vehicle_id
        except Exception as e:
            logger.error(f"添加车辆失败: {e}")
            return None
    
    def delete_vehicle(self, vehicle_id):
        """
        删除车辆
        
        参数：
            vehicle_id: 要删除的车辆ID
        
        返回：
            布尔值，表示删除是否成功
        """
        logger.info(f"删除车辆: {vehicle_id}")
        try:
            # 检查车辆是否存在
            existing_vehicle = self.database.fetchone(
                "SELECT * FROM vehicles WHERE id = ?",
                [vehicle_id]
            )
            
            if not existing_vehicle:
                logger.warning(f"车辆不存在: {vehicle_id}")
                return False
            
            # 检查车辆是否正在停车
            if existing_vehicle["status"] == "parking":
                logger.warning(f"车辆正在停车中，无法删除: {vehicle_id}")
                return False
            
            # 删除车辆
            rows_affected = self.database.delete("vehicles", "id = ?", [vehicle_id])
            
            if rows_affected > 0:
                logger.info(f"成功删除车辆: {vehicle_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"删除车辆失败: {e}")
            return False
    
    def get_vehicle(self, vehicle_id):
        """
        获取车辆信息
        
        参数：
            vehicle_id: 车辆ID
        
        返回：
            车辆信息字典，若车辆不存在则返回None
        """
        try:
            vehicle = self.database.fetchone(
                "SELECT * FROM vehicles WHERE id = ?",
                [vehicle_id]
            )
            
            if vehicle:
                return dict(vehicle)
            return None
        except Exception as e:
            logger.error(f"获取车辆信息失败: {e}")
            return None
    
    def get_vehicle_by_plate(self, plate_number):
        """
        根据车牌号码获取车辆信息
        
        参数：
            plate_number: 车牌号码
        
        返回：
            车辆信息字典，若车辆不存在则返回None
        """
        try:
            vehicle = self.database.fetchone(
                "SELECT * FROM vehicles WHERE plate_number = ?",
                [plate_number]
            )
            
            if vehicle:
                return dict(vehicle)
            return None
        except Exception as e:
            logger.error(f"根据车牌获取车辆信息失败: {e}")
            return None
    
    def get_all_vehicles(self):
        """
        获取所有车辆信息
        
        返回：
            所有车辆信息的列表
        """
        try:
            vehicles = self.database.fetchall("SELECT * FROM vehicles ORDER BY created_at DESC")
            return [dict(vehicle) for vehicle in vehicles]
        except Exception as e:
            logger.error(f"获取所有车辆信息失败: {e}")
            return []
    
    def get_parking_vehicles(self):
        """
        获取正在停车的车辆信息
        
        返回：
            正在停车的车辆信息列表
        """
        try:
            vehicles = self.database.fetchall(
                "SELECT * FROM vehicles WHERE status = 'parking' ORDER BY entry_time DESC"
            )
            return [dict(vehicle) for vehicle in vehicles]
        except Exception as e:
            logger.error(f"获取正在停车的车辆信息失败: {e}")
            return []
    
    def register_vehicle_entry(self, plate_number, vehicle_type=None, preferred_floor=None):
        """
        登记车辆进场
        
        该方法执行以下操作：
        1. 检查车辆是否已注册
        2. 如果未注册，则创建新车辆
        3. 更新车辆状态为停车中
        4. 记录进场时间
        5. 分配车位
        
        参数：
            plate_number: 车牌号码
            vehicle_type: 车辆类型，可选，若车辆未注册则必填
            preferred_floor: 用户偏好楼层，可选
        
        返回：
            包含车辆ID和分配到的车位ID的字典，若失败则返回None
        """
        logger.info(f"登记车辆进场: {plate_number}, 类型: {vehicle_type}, 偏好楼层: {preferred_floor}")
        try:
            # 检查车辆是否已注册
            existing_vehicle = self.get_vehicle_by_plate(plate_number)
            vehicle_id = None
            
            # 如果车辆未注册，则创建新车辆
            if not existing_vehicle:
                if not vehicle_type:
                    logger.error(f"车辆未注册且未提供车辆类型: {plate_number}")
                    return None
                
                vehicle_id = self.add_vehicle(plate_number, vehicle_type)
                if not vehicle_id:
                    return None
            else:
                vehicle_id = existing_vehicle["id"]
                vehicle_type = existing_vehicle["vehicle_type"]
            
            # 从车位管理器中分配车位
            from parking_space_management.space_manager import SpaceManager
            space_manager = SpaceManager(self.database)
            parking_space_id = space_manager.allocate_parking_space(vehicle_type, preferred_floor)
            
            if not parking_space_id:
                logger.warning(f"无法分配车位: {plate_number}")
                return None
            
            # 更新车辆信息
            self.database.update(
                "vehicles",
                {
                    "status": "parking",
                    "entry_time": datetime.now(),
                    "parking_space_id": parking_space_id,
                    "updated_at": datetime.now()
                },
                "id = ?",
                [vehicle_id]
            )
            
            logger.info(f"车辆进场成功: {plate_number}, 车位: {parking_space_id}")
            return {
                "vehicle_id": vehicle_id,
                "parking_space_id": parking_space_id
            }
        except Exception as e:
            logger.error(f"登记车辆进场失败: {e}")
            return None
    
    def register_vehicle_exit(self, plate_number):
        """
        登记车辆出场
        
        该方法执行以下操作：
        1. 检查车辆是否正在停车
        2. 记录出场时间
        3. 释放车位
        4. 计算停车费用
        5. 更新车辆状态为已离开
        
        参数：
            plate_number: 车牌号码
        
        返回：
            包含车辆ID、停车时长和费用的字典，若失败则返回None
        """
        logger.info(f"登记车辆出场: {plate_number}")
        try:
            # 获取车辆信息
            vehicle = self.get_vehicle_by_plate(plate_number)
            if not vehicle:
                logger.warning(f"车辆不存在: {plate_number}")
                return None
            
            if vehicle["status"] != "parking":
                logger.warning(f"车辆未在停车中: {plate_number}")
                return None
            
            # 获取车位ID
            parking_space_id = vehicle["parking_space_id"]
            if not parking_space_id:
                logger.error(f"车辆没有分配车位: {plate_number}")
                return None
            
            # 计算停车时长
            entry_time = vehicle["entry_time"]
            exit_time = datetime.now()
            duration = int((exit_time - entry_time).total_seconds() / 60)  # 停车时长（分钟）
            
            # 计算停车费用
            from fee_management.fee_manager import FeeManager
            fee_manager = FeeManager(self.database)
            fee = fee_manager.calculate_fee(vehicle["vehicle_type"], duration)
            
            # 释放车位
            from parking_space_management.space_manager import SpaceManager
            space_manager = SpaceManager(self.database)
            space_manager.release_parking_space(parking_space_id)
            
            # 更新车辆信息
            self.database.update(
                "vehicles",
                {
                    "status": "left",
                    "exit_time": exit_time,
                    "parking_space_id": None,
                    "updated_at": datetime.now()
                },
                "id = ?",
                [vehicle["id"]]
            )
            
            # 创建停车交易记录
            transaction_data = {
                "vehicle_id": vehicle["id"],
                "parking_space_id": parking_space_id,
                "entry_time": entry_time,
                "exit_time": exit_time,
                "duration": duration,
                "fee": fee,
                "payment_status": "unpaid",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            self.database.insert("parking_transactions", transaction_data)
            
            logger.info(f"车辆出场成功: {plate_number}, 时长: {duration}分钟, 费用: {fee}元")
            return {
                "vehicle_id": vehicle["id"],
                "duration": duration,
                "fee": fee
            }
        except Exception as e:
            logger.error(f"登记车辆出场失败: {e}")
            return None
    
    def update_vehicle_info(self, vehicle_id, update_data):
        """
        更新车辆信息
        
        参数：
            vehicle_id: 车辆ID
            update_data: 要更新的车辆信息字典
        
        返回：
            布尔值，表示更新是否成功
        """
        logger.info(f"更新车辆信息: {vehicle_id}, 数据: {update_data}")
        try:
            # 检查车辆是否存在
            existing_vehicle = self.get_vehicle(vehicle_id)
            if not existing_vehicle:
                logger.warning(f"车辆不存在: {vehicle_id}")
                return False
            
            # 更新车辆信息
            update_data["updated_at"] = datetime.now()
            rows_affected = self.database.update(
                "vehicles",
                update_data,
                "id = ?",
                [vehicle_id]
            )
            
            if rows_affected > 0:
                logger.info(f"成功更新车辆信息: {vehicle_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"更新车辆信息失败: {e}")
            return False
    
    def get_vehicle_statistics(self):
        """
        获取车辆统计信息
        
        返回：
            包含车辆统计信息的字典，包括：
                - total: 总车辆数
                - registered: 已注册车辆数
                - parking: 正在停车的车辆数
                - by_type: 按类型统计的车辆数
        """
        try:
            # 获取总车辆数
            total = self.database.fetchone("SELECT COUNT(*) as count FROM vehicles")["count"]
            
            # 获取已注册车辆数
            registered = self.database.fetchone(
                "SELECT COUNT(*) as count FROM vehicles WHERE status = 'registered'"
            )["count"]
            
            # 获取正在停车的车辆数
            parking = self.database.fetchone(
                "SELECT COUNT(*) as count FROM vehicles WHERE status = 'parking'"
            )["count"]
            
            # 获取按类型统计的车辆数
            by_type = {}
            type_stats = self.database.fetchall(
                "SELECT vehicle_type, COUNT(*) as count FROM vehicles GROUP BY vehicle_type"
            )
            
            for stat in type_stats:
                by_type[stat["vehicle_type"]] = stat["count"]
            
            return {
                "total": total,
                "registered": registered,
                "parking": parking,
                "by_type": by_type
            }
        except Exception as e:
            logger.error(f"获取车辆统计信息失败: {e}")
            return None
