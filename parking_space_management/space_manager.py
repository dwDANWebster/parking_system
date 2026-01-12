#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车位管理模块

该模块负责智能停车场的车位管理，包括车位信息维护、智能分配算法、车位状态监控等功能。
实现了基于车辆类型和用户偏好的智能车位分配，以及实时的车位状态更新。
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ParkingSpace:
    """
    车位信息类
    
    该类封装了车位的基本信息，包括车位编号、楼层、类型、状态等属性。
    
    属性：
        id: 车位ID，数据库自动生成
        space_number: 车位编号，唯一标识
        floor: 楼层号
        space_type: 车位类型，如'小型车'、'大型车'、'残疾人专用'等
        status: 车位状态，如'available'（可用）、'occupied'（已占用）、'reserved'（已预约）等
        is_reserved: 是否被预约
        reserved_user_id: 预约用户ID
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    def __init__(self, space_number, floor, space_type):
        """
        初始化车位对象
        
        参数：
            space_number: 车位编号
            floor: 楼层号
            space_type: 车位类型
        """
        self.id = None
        self.space_number = space_number
        self.floor = floor
        self.space_type = space_type
        self.status = "available"  # 默认状态为可用
        self.is_reserved = False  # 默认未被预约
        self.reserved_user_id = None  # 默认无预约用户
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """
        将车位对象转换为字典格式
        
        返回：
            包含车位所有属性的字典
        """
        return {
            "id": self.id,
            "space_number": self.space_number,
            "floor": self.floor,
            "space_type": self.space_type,
            "status": self.status,
            "is_reserved": self.is_reserved,
            "reserved_user_id": self.reserved_user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class SpaceAllocationAlgorithm:
    """
    车位分配算法类
    
    该类实现了智能车位分配算法，根据车辆类型、用户偏好等因素，
    为进场车辆分配最合适的车位。
    
    属性：
        database: 数据库连接对象
    """
    
    def __init__(self, database):
        """
        初始化车位分配算法对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
    
    def allocate_space(self, vehicle_type, preferred_floor=None):
        """
        为车辆分配最合适的车位
        
        该方法执行以下操作：
        1. 根据车辆类型筛选可用车位
        2. 如果指定了偏好楼层，则优先考虑该楼层
        3. 按照楼层和车位号排序，选择最优车位
        
        参数：
            vehicle_type: 车辆类型
            preferred_floor: 用户偏好楼层，可选
        
        返回：
            分配到的车位ID，若没有可用车位则返回None
        """
        logger.info(f"分配车位: {vehicle_type}, 偏好楼层: {preferred_floor}")
        try:
            # 构建查询条件
            query = "SELECT * FROM parking_spaces WHERE status = 'available' AND space_type = ?"
            params = [vehicle_type]
            
            # 如果指定了偏好楼层，则优先考虑该楼层
            if preferred_floor is not None:
                query += " AND floor = ?"
                params.append(preferred_floor)
            
            # 按楼层和车位号排序，优先分配低楼层、小编号的车位
            query += " ORDER BY floor ASC, space_number ASC"
            
            # 获取可用车位
            available_space = self.database.fetchone(query, params)
            
            if available_space:
                space_id = available_space['id']
                # 更新车位状态为已占用
                self.database.update(
                    "parking_spaces",
                    {"status": "occupied", "updated_at": datetime.now()},
                    "id = ?",
                    [space_id]
                )
                logger.info(f"成功分配车位: {space_id}")
                return space_id
            
            logger.warning(f"没有可用车位: {vehicle_type}, 偏好楼层: {preferred_floor}")
            return None
        except Exception as e:
            logger.error(f"车位分配失败: {e}")
            return None
    
    def release_space(self, space_id):
        """
        释放车位，将车位状态设置为可用
        
        参数：
            space_id: 要释放的车位ID
        
        返回：
            布尔值，表示释放是否成功
        """
        logger.info(f"释放车位: {space_id}")
        try:
            # 更新车位状态为可用
            rows_affected = self.database.update(
                "parking_spaces",
                {"status": "available", "updated_at": datetime.now()},
                "id = ?",
                [space_id]
            )
            
            if rows_affected > 0:
                logger.info(f"成功释放车位: {space_id}")
                return True
            
            logger.warning(f"释放车位失败，车位不存在或状态错误: {space_id}")
            return False
        except Exception as e:
            logger.error(f"释放车位失败: {e}")
            return False
    
    def reserve_space(self, space_id, user_id):
        """
        预约车位
        
        参数：
            space_id: 要预约的车位ID
            user_id: 预约用户ID
        
        返回：
            布尔值，表示预约是否成功
        """
        logger.info(f"预约车位: {space_id}, 用户: {user_id}")
        try:
            # 检查车位是否可用
            space = self.database.fetchone("SELECT * FROM parking_spaces WHERE id = ?", [space_id])
            if not space:
                logger.warning(f"预约失败，车位不存在: {space_id}")
                return False
            
            if space['status'] != 'available' or space['is_reserved']:
                logger.warning(f"预约失败，车位已被占用或已预约: {space_id}")
                return False
            
            # 更新车位状态为已预约
            rows_affected = self.database.update(
                "parking_spaces",
                {
                    "is_reserved": True,
                    "reserved_user_id": user_id,
                    "updated_at": datetime.now()
                },
                "id = ?",
                [space_id]
            )
            
            if rows_affected > 0:
                logger.info(f"成功预约车位: {space_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"预约车位失败: {e}")
            return False
    
    def cancel_reservation(self, space_id):
        """
        取消车位预约
        
        参数：
            space_id: 要取消预约的车位ID
        
        返回：
            布尔值，表示取消预约是否成功
        """
        logger.info(f"取消预约车位: {space_id}")
        try:
            # 更新车位状态，取消预约
            rows_affected = self.database.update(
                "parking_spaces",
                {
                    "is_reserved": False,
                    "reserved_user_id": None,
                    "updated_at": datetime.now()
                },
                "id = ?",
                [space_id]
            )
            
            if rows_affected > 0:
                logger.info(f"成功取消预约车位: {space_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"取消预约车位失败: {e}")
            return False


class SpaceManager:
    """
    车位管理器类
    
    该类封装了车位管理的核心功能，包括车位的添加、删除、查询、分配、释放等操作。
    
    属性：
        database: 数据库连接对象
        allocation_algorithm: 车位分配算法对象
    """
    
    def __init__(self, database):
        """
        初始化车位管理器对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
        self.allocation_algorithm = SpaceAllocationAlgorithm(database)
    
    def init(self):
        """
        初始化车位管理器
        
        该方法执行以下操作：
        1. 检查是否需要初始化车位数据
        2. 如果没有车位数据，则创建初始车位
        """
        logger.info("初始化车位管理器")
        try:
            # 检查是否已有车位数据
            space_count = self.database.fetchone("SELECT COUNT(*) as count FROM parking_spaces")["count"]
            
            # 如果没有车位数据，则创建初始车位
            if space_count == 0:
                logger.info("没有车位数据，创建初始车位")
                self._create_initial_spaces()
        except Exception as e:
            logger.error(f"车位管理器初始化失败: {e}")
            raise
    
    def _create_initial_spaces(self):
        """
        创建初始车位数据
        
        该方法创建以下初始车位：
        - 地下1层：小型车车位20个，大型车车位5个
        - 地下2层：小型车车位30个，大型车车位8个
        - 地上1层：小型车车位15个，残疾人专用车位3个
        """
        initial_spaces = []
        
        # 地下1层：小型车车位20个，大型车车位5个
        for i in range(1, 21):
            initial_spaces.append({
                "space_number": f"B1-{i:03d}",
                "floor": -1,
                "space_type": "小型车",
                "status": "available",
                "is_reserved": False,
                "reserved_user_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
        
        for i in range(1, 6):
            initial_spaces.append({
                "space_number": f"B1-L{i:03d}",
                "floor": -1,
                "space_type": "大型车",
                "status": "available",
                "is_reserved": False,
                "reserved_user_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
        
        # 地下2层：小型车车位30个，大型车车位8个
        for i in range(1, 31):
            initial_spaces.append({
                "space_number": f"B2-{i:03d}",
                "floor": -2,
                "space_type": "小型车",
                "status": "available",
                "is_reserved": False,
                "reserved_user_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
        
        for i in range(1, 9):
            initial_spaces.append({
                "space_number": f"B2-L{i:03d}",
                "floor": -2,
                "space_type": "大型车",
                "status": "available",
                "is_reserved": False,
                "reserved_user_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
        
        # 地上1层：小型车车位15个，残疾人专用车位3个
        for i in range(1, 16):
            initial_spaces.append({
                "space_number": f"F1-{i:03d}",
                "floor": 1,
                "space_type": "小型车",
                "status": "available",
                "is_reserved": False,
                "reserved_user_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
        
        for i in range(1, 4):
            initial_spaces.append({
                "space_number": f"F1-D{i:03d}",
                "floor": 1,
                "space_type": "残疾人专用",
                "status": "available",
                "is_reserved": False,
                "reserved_user_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
        
        # 插入初始车位数据
        for space in initial_spaces:
            self.database.insert("parking_spaces", space)
        
        logger.info(f"成功创建{len(initial_spaces)}个初始车位")
    
    def add_space(self, space_number, floor, space_type):
        """
        添加新车位
        
        参数：
            space_number: 车位编号
            floor: 楼层号
            space_type: 车位类型
        
        返回：
            新添加的车位ID
        """
        logger.info(f"添加新车位: {space_number}, 楼层: {floor}, 类型: {space_type}")
        try:
            # 检查车位编号是否已存在
            existing_space = self.database.fetchone(
                "SELECT * FROM parking_spaces WHERE space_number = ?",
                [space_number]
            )
            
            if existing_space:
                logger.warning(f"车位编号已存在: {space_number}")
                return None
            
            # 创建新车位
            new_space = {
                "space_number": space_number,
                "floor": floor,
                "space_type": space_type,
                "status": "available",
                "is_reserved": False,
                "reserved_user_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 插入新车位数据
            space_id = self.database.insert("parking_spaces", new_space)
            logger.info(f"成功添加新车位: {space_id}")
            return space_id
        except Exception as e:
            logger.error(f"添加车位失败: {e}")
            return None
    
    def delete_space(self, space_id):
        """
        删除车位
        
        参数：
            space_id: 要删除的车位ID
        
        返回：
            布尔值，表示删除是否成功
        """
        logger.info(f"删除车位: {space_id}")
        try:
            # 检查车位是否存在
            existing_space = self.database.fetchone(
                "SELECT * FROM parking_spaces WHERE id = ?",
                [space_id]
            )
            
            if not existing_space:
                logger.warning(f"车位不存在: {space_id}")
                return False
            
            # 检查车位是否已被占用
            if existing_space["status"] == "occupied":
                logger.warning(f"车位已被占用，无法删除: {space_id}")
                return False
            
            # 删除车位
            rows_affected = self.database.delete("parking_spaces", "id = ?", [space_id])
            
            if rows_affected > 0:
                logger.info(f"成功删除车位: {space_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"删除车位失败: {e}")
            return False
    
    def get_space(self, space_id):
        """
        获取车位信息
        
        参数：
            space_id: 车位ID
        
        返回：
            车位信息字典，若车位不存在则返回None
        """
        try:
            space = self.database.fetchone(
                "SELECT * FROM parking_spaces WHERE id = ?",
                [space_id]
            )
            
            if space:
                return dict(space)
            return None
        except Exception as e:
            logger.error(f"获取车位信息失败: {e}")
            return None
    
    def get_all_spaces(self):
        """
        获取所有车位信息
        
        返回：
            所有车位信息的列表
        """
        try:
            spaces = self.database.fetchall("SELECT * FROM parking_spaces ORDER BY floor ASC, space_number ASC")
            return [dict(space) for space in spaces]
        except Exception as e:
            logger.error(f"获取所有车位信息失败: {e}")
            return []
    
    def get_available_spaces(self, vehicle_type=None):
        """
        获取可用车位信息
        
        参数：
            vehicle_type: 车辆类型，可选，用于筛选特定类型的可用车位
        
        返回：
            可用车位信息的列表
        """
        try:
            if vehicle_type:
                spaces = self.database.fetchall(
                    "SELECT * FROM parking_spaces WHERE status = 'available' AND space_type = ? ORDER BY floor ASC, space_number ASC",
                    [vehicle_type]
                )
            else:
                spaces = self.database.fetchall(
                    "SELECT * FROM parking_spaces WHERE status = 'available' ORDER BY floor ASC, space_number ASC"
                )
            
            return [dict(space) for space in spaces]
        except Exception as e:
            logger.error(f"获取可用车位信息失败: {e}")
            return []
    
    def get_occupied_spaces(self):
        """
        获取已占用车位信息
        
        返回：
            已占用车位信息的列表
        """
        try:
            spaces = self.database.fetchall(
                "SELECT * FROM parking_spaces WHERE status = 'occupied' ORDER BY floor ASC, space_number ASC"
            )
            return [dict(space) for space in spaces]
        except Exception as e:
            logger.error(f"获取已占用车位信息失败: {e}")
            return []
    
    def allocate_parking_space(self, vehicle_type, preferred_floor=None):
        """
        分配车位（对外接口）
        
        参数：
            vehicle_type: 车辆类型
            preferred_floor: 用户偏好楼层，可选
        
        返回：
            分配到的车位ID，若没有可用车位则返回None
        """
        return self.allocation_algorithm.allocate_space(vehicle_type, preferred_floor)
    
    def release_parking_space(self, space_id):
        """
        释放车位（对外接口）
        
        参数：
            space_id: 要释放的车位ID
        
        返回：
            布尔值，表示释放是否成功
        """
        return self.allocation_algorithm.release_space(space_id)
    
    def update_space_status(self, space_id, status):
        """
        更新车位状态
        
        参数：
            space_id: 车位ID
            status: 新的车位状态，可选值包括：
                - 'available'（可用）
                - 'occupied'（已占用）
                - 'maintenance'（维护中）
                - 'disabled'（禁用）
        
        返回：
            布尔值，表示更新是否成功
        """
        logger.info(f"更新车位状态: {space_id}, 新状态: {status}")
        try:
            # 检查状态值是否有效
            valid_statuses = ['available', 'occupied', 'maintenance', 'disabled']
            if status not in valid_statuses:
                logger.warning(f"无效的车位状态: {status}")
                return False
            
            # 更新车位状态
            rows_affected = self.database.update(
                "parking_spaces",
                {"status": status, "updated_at": datetime.now()},
                "id = ?",
                [space_id]
            )
            
            if rows_affected > 0:
                logger.info(f"成功更新车位状态: {space_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"更新车位状态失败: {e}")
            return False
    
    def get_space_statistics(self):
        """
        获取车位统计信息
        
        返回：
            包含车位统计信息的字典，包括：
                - total: 总车位数
                - available: 可用车位数
                - occupied: 已占用车位数
                - maintenance: 维护中车位数
                - disabled: 禁用车位数
                - by_type: 按类型统计的车位数
        """
        try:
            # 获取总车位数
            total = self.database.fetchone("SELECT COUNT(*) as count FROM parking_spaces")["count"]
            
            # 获取可用车位数
            available = self.database.fetchone(
                "SELECT COUNT(*) as count FROM parking_spaces WHERE status = 'available'"
            )["count"]
            
            # 获取已占用车位数
            occupied = self.database.fetchone(
                "SELECT COUNT(*) as count FROM parking_spaces WHERE status = 'occupied'"
            )["count"]
            
            # 获取维护中车位数
            maintenance = self.database.fetchone(
                "SELECT COUNT(*) as count FROM parking_spaces WHERE status = 'maintenance'"
            )["count"]
            
            # 获取禁用车位数
            disabled = self.database.fetchone(
                "SELECT COUNT(*) as count FROM parking_spaces WHERE status = 'disabled'"
            )["count"]
            
            # 获取按类型统计的车位数
            by_type = {}
            type_stats = self.database.fetchall(
                "SELECT space_type, COUNT(*) as count FROM parking_spaces GROUP BY space_type"
            )
            
            for stat in type_stats:
                by_type[stat["space_type"]] = stat["count"]
            
            return {
                "total": total,
                "available": available,
                "occupied": occupied,
                "maintenance": maintenance,
                "disabled": disabled,
                "by_type": by_type
            }
        except Exception as e:
            logger.error(f"获取车位统计信息失败: {e}")
            return None
