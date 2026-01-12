#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
费用管理模块

该模块负责智能停车场的费用管理，包括收费规则维护、停车费用计算等功能。
实现了灵活的收费规则配置，支持多种车辆类型和收费标准。
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class FeeRule:
    """
    收费规则类
    
    该类封装了收费规则的基本信息，包括车辆类型、免费时长、每小时费率、每日最大费用等属性。
    
    属性：
        id: 规则ID，数据库自动生成
        vehicle_type: 车辆类型，如'小型车'、'大型车'、'残疾人专用'等
        free_duration: 免费停车时长（分钟）
        hourly_rate: 每小时收费标准（元）
        daily_max: 每日最大收费（元）
        is_active: 是否激活
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    def __init__(self, vehicle_type, free_duration=30, hourly_rate=5, daily_max=50, is_active=True):
        """
        初始化收费规则对象
        
        参数：
            vehicle_type: 车辆类型
            free_duration: 免费停车时长（分钟），默认为30分钟
            hourly_rate: 每小时收费标准（元），默认为5元/小时
            daily_max: 每日最大收费（元），默认为50元/天
            is_active: 是否激活，默认为True
        """
        self.id = None
        self.vehicle_type = vehicle_type
        self.free_duration = free_duration
        self.hourly_rate = hourly_rate
        self.daily_max = daily_max
        self.is_active = is_active
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """
        将收费规则对象转换为字典格式
        
        返回：
            包含收费规则所有属性的字典
        """
        return {
            "id": self.id,
            "vehicle_type": self.vehicle_type,
            "free_duration": self.free_duration,
            "hourly_rate": self.hourly_rate,
            "daily_max": self.daily_max,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class FeeCalculator:
    """
    费用计算器类
    
    该类负责根据停车时长和收费规则计算停车费用。
    """
    
    def __init__(self, database):
        """
        初始化费用计算器对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
    
    def calculate_fee(self, vehicle_type, duration):
        """
        计算停车费用
        
        该方法根据车辆类型和停车时长计算停车费用，执行以下逻辑：
        1. 获取对应车辆类型的收费规则
        2. 如果停车时长小于等于免费时长，则费用为0
        3. 否则，计算超出免费时长的部分
        4. 按照每小时费率计算费用
        5. 确保每日费用不超过最大限额
        
        参数：
            vehicle_type: 车辆类型
            duration: 停车时长（分钟）
        
        返回：
            计算出的停车费用（元）
        """
        logger.info(f"计算停车费用: {vehicle_type}, 时长: {duration}分钟")
        try:
            # 获取对应车辆类型的收费规则
            fee_rule = self.database.fetchone(
                "SELECT * FROM fee_rules WHERE vehicle_type = ? AND is_active = 1",
                [vehicle_type]
            )
            
            # 如果没有找到对应规则，则使用默认规则
            if not fee_rule:
                logger.warning(f"未找到收费规则，使用默认规则: {vehicle_type}")
                free_duration = 30
                hourly_rate = 5
                daily_max = 50
            else:
                free_duration = fee_rule["free_duration"]
                hourly_rate = fee_rule["hourly_rate"]
                daily_max = fee_rule["daily_max"]
            
            # 如果停车时长小于等于免费时长，则费用为0
            if duration <= free_duration:
                logger.info(f"停车时长在免费范围内: {duration}分钟 <= {free_duration}分钟")
                return 0.0
            
            # 计算超出免费时长的部分
            chargeable_duration = duration - free_duration
            
            # 按照每小时费率计算费用
            # 不足1小时按1小时计算
            hours = chargeable_duration / 60
            if chargeable_duration % 60 > 0:
                hours += 1
            
            fee = hours * hourly_rate
            
            # 确保每日费用不超过最大限额
            if fee > daily_max:
                fee = daily_max
            
            logger.info(f"计算停车费用成功: {vehicle_type}, 时长: {duration}分钟, 费用: {fee}元")
            return round(fee, 2)
        except Exception as e:
            logger.error(f"计算停车费用失败: {e}")
            return 0.0


class FeeManager:
    """
    费用管理器类
    
    该类封装了费用管理的核心功能，包括收费规则的添加、删除、查询和费用计算等操作。
    
    属性：
        database: 数据库连接对象
        fee_calculator: 费用计算器对象
    """
    
    def __init__(self, database):
        """
        初始化费用管理器对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
        self.fee_calculator = FeeCalculator(database)
    
    def init(self):
        """
        初始化费用管理器
        
        该方法执行以下操作：
        1. 检查是否需要初始化收费规则数据
        2. 如果没有收费规则数据，则创建初始收费规则
        """
        logger.info("初始化费用管理器")
        try:
            # 检查是否已有收费规则数据
            rule_count = self.database.fetchone("SELECT COUNT(*) as count FROM fee_rules")["count"]
            
            # 如果没有收费规则数据，则创建初始收费规则
            if rule_count == 0:
                logger.info("没有收费规则数据，创建初始收费规则")
                self._create_initial_fee_rules()
        except Exception as e:
            logger.error(f"费用管理器初始化失败: {e}")
            raise
    
    def _create_initial_fee_rules(self):
        """
        创建初始收费规则数据
        
        该方法创建初始收费规则，包括小型车、大型车和残疾人专用车的收费标准。
        """
        initial_rules = [
            {
                "vehicle_type": "小型车",
                "free_duration": 30,
                "hourly_rate": 5.0,
                "daily_max": 50.0,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "vehicle_type": "大型车",
                "free_duration": 30,
                "hourly_rate": 10.0,
                "daily_max": 100.0,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "vehicle_type": "残疾人专用",
                "free_duration": 60,
                "hourly_rate": 3.0,
                "daily_max": 30.0,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        # 插入初始收费规则数据
        for rule in initial_rules:
            self.database.insert("fee_rules", rule)
        
        logger.info(f"成功创建{len(initial_rules)}个初始收费规则")
    
    def add_fee_rule(self, vehicle_type, free_duration=30, hourly_rate=5.0, daily_max=50.0, is_active=True):
        """
        添加新收费规则
        
        参数：
            vehicle_type: 车辆类型
            free_duration: 免费停车时长（分钟），默认为30分钟
            hourly_rate: 每小时收费标准（元），默认为5元/小时
            daily_max: 每日最大收费（元），默认为50元/天
            is_active: 是否激活，默认为True
        
        返回：
            新添加的收费规则ID
        """
        logger.info(f"添加新收费规则: {vehicle_type}")
        try:
            # 检查是否已存在相同车辆类型的收费规则
            existing_rule = self.database.fetchone(
                "SELECT * FROM fee_rules WHERE vehicle_type = ?",
                [vehicle_type]
            )
            
            if existing_rule:
                logger.warning(f"收费规则已存在: {vehicle_type}")
                return None
            
            # 创建新收费规则
            new_rule = {
                "vehicle_type": vehicle_type,
                "free_duration": free_duration,
                "hourly_rate": hourly_rate,
                "daily_max": daily_max,
                "is_active": is_active,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 插入新收费规则数据
            rule_id = self.database.insert("fee_rules", new_rule)
            logger.info(f"成功添加新收费规则: {rule_id}")
            return rule_id
        except Exception as e:
            logger.error(f"添加收费规则失败: {e}")
            return None
    
    def update_fee_rule(self, rule_id, update_data):
        """
        更新收费规则
        
        参数：
            rule_id: 收费规则ID
            update_data: 要更新的收费规则信息字典
        
        返回：
            布尔值，表示更新是否成功
        """
        logger.info(f"更新收费规则: {rule_id}, 数据: {update_data}")
        try:
            # 检查收费规则是否存在
            existing_rule = self.database.fetchone(
                "SELECT * FROM fee_rules WHERE id = ?",
                [rule_id]
            )
            
            if not existing_rule:
                logger.warning(f"收费规则不存在: {rule_id}")
                return False
            
            # 更新收费规则
            update_data["updated_at"] = datetime.now()
            rows_affected = self.database.update(
                "fee_rules",
                update_data,
                "id = ?",
                [rule_id]
            )
            
            if rows_affected > 0:
                logger.info(f"成功更新收费规则: {rule_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"更新收费规则失败: {e}")
            return False
    
    def delete_fee_rule(self, rule_id):
        """
        删除收费规则
        
        参数：
            rule_id: 要删除的收费规则ID
        
        返回：
            布尔值，表示删除是否成功
        """
        logger.info(f"删除收费规则: {rule_id}")
        try:
            # 检查收费规则是否存在
            existing_rule = self.database.fetchone(
                "SELECT * FROM fee_rules WHERE id = ?",
                [rule_id]
            )
            
            if not existing_rule:
                logger.warning(f"收费规则不存在: {rule_id}")
                return False
            
            # 删除收费规则
            rows_affected = self.database.delete("fee_rules", "id = ?", [rule_id])
            
            if rows_affected > 0:
                logger.info(f"成功删除收费规则: {rule_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"删除收费规则失败: {e}")
            return False
    
    def get_fee_rule(self, rule_id):
        """
        获取收费规则信息
        
        参数：
            rule_id: 收费规则ID
        
        返回：
            收费规则信息字典，若收费规则不存在则返回None
        """
        try:
            fee_rule = self.database.fetchone(
                "SELECT * FROM fee_rules WHERE id = ?",
                [rule_id]
            )
            
            if fee_rule:
                return dict(fee_rule)
            return None
        except Exception as e:
            logger.error(f"获取收费规则失败: {e}")
            return None
    
    def get_all_fee_rules(self):
        """
        获取所有收费规则信息
        
        返回：
            所有收费规则信息的列表
        """
        try:
            fee_rules = self.database.fetchall("SELECT * FROM fee_rules ORDER BY created_at DESC")
            return [dict(rule) for rule in fee_rules]
        except Exception as e:
            logger.error(f"获取所有收费规则失败: {e}")
            return []
    
    def get_fee_rule_by_vehicle_type(self, vehicle_type):
        """
        根据车辆类型获取收费规则
        
        参数：
            vehicle_type: 车辆类型
        
        返回：
            收费规则信息字典，若收费规则不存在则返回None
        """
        try:
            fee_rule = self.database.fetchone(
                "SELECT * FROM fee_rules WHERE vehicle_type = ?",
                [vehicle_type]
            )
            
            if fee_rule:
                return dict(fee_rule)
            return None
        except Exception as e:
            logger.error(f"根据车辆类型获取收费规则失败: {e}")
            return None
    
    def calculate_parking_fee(self, vehicle_type, duration):
        """
        计算停车费用（对外接口）
        
        参数：
            vehicle_type: 车辆类型
            duration: 停车时长（分钟）
        
        返回：
            计算出的停车费用（元）
        """
        return self.fee_calculator.calculate_fee(vehicle_type, duration)
    
    def get_fee_statistics(self, start_date=None, end_date=None):
        """
        获取费用统计信息
        
        参数：
            start_date: 统计开始日期，可选
            end_date: 统计结束日期，可选
        
        返回：
            包含费用统计信息的字典，包括：
                - total_fee: 总费用
                - total_transactions: 总交易数
                - average_fee: 平均每笔费用
                - by_vehicle_type: 按车辆类型统计的费用
        """
        logger.info(f"获取费用统计信息: 开始日期: {start_date}, 结束日期: {end_date}")
        try:
            # 构建查询条件
            query = "SELECT * FROM parking_transactions WHERE fee IS NOT NULL"
            params = []
            
            if start_date:
                query += " AND entry_time >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND entry_time <= ?"
                params.append(end_date)
            
            # 获取所有交易记录
            transactions = self.database.fetchall(query, params)
            
            # 计算统计信息
            total_fee = 0
            total_transactions = len(transactions)
            by_vehicle_type = {}
            
            for transaction in transactions:
                total_fee += transaction["fee"]
                
                # 获取车辆类型
                vehicle = self.database.fetchone(
                    "SELECT vehicle_type FROM vehicles WHERE id = ?",
                    [transaction["vehicle_id"]]
                )
                
                if vehicle:
                    vehicle_type = vehicle["vehicle_type"]
                    if vehicle_type not in by_vehicle_type:
                        by_vehicle_type[vehicle_type] = {
                            "total_fee": 0,
                            "count": 0
                        }
                    by_vehicle_type[vehicle_type]["total_fee"] += transaction["fee"]
                    by_vehicle_type[vehicle_type]["count"] += 1
            
            # 计算平均每笔费用
            average_fee = 0
            if total_transactions > 0:
                average_fee = total_fee / total_transactions
            
            logger.info(f"获取费用统计信息成功: 总费用: {total_fee}元, 总交易数: {total_transactions}")
            return {
                "total_fee": round(total_fee, 2),
                "total_transactions": total_transactions,
                "average_fee": round(average_fee, 2),
                "by_vehicle_type": by_vehicle_type
            }
        except Exception as e:
            logger.error(f"获取费用统计信息失败: {e}")
            return None
