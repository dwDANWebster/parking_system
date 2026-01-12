#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报表统计模块

该模块负责智能停车场的报表统计功能，包括停车记录查询、费用统计、车位使用率分析等。
支持多种时间维度的报表生成，包括日报、周报、月报和年报。
"""

import logging
import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    报表生成器类
    
    该类负责生成各种类型的报表，包括停车记录报表、费用统计报表、车位使用率报表等。
    """
    
    def __init__(self, database):
        """
        初始化报表生成器对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
    
    def generate_daily_report(self, report_date=None):
        """
        生成日报表
        
        该方法生成指定日期的日报表，包括以下内容：
        1. 当日总停车次数
        2. 当日总费用
        3. 各车辆类型的停车次数和费用
        4. 车位使用率
        
        参数：
            report_date: 报表日期，默认为当前日期
        
        返回：
            包含日报表数据的字典
        """
        if not report_date:
            report_date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"生成日报表: {report_date}")
        try:
            # 构建查询日期范围
            start_date = f"{report_date} 00:00:00"
            end_date = f"{report_date} 23:59:59"
            
            # 获取当日总停车次数
            total_parking = self.database.fetchone(
                "SELECT COUNT(*) as count FROM parking_transactions WHERE entry_time BETWEEN ? AND ?",
                [start_date, end_date]
            )["count"]
            
            # 获取当日总费用
            total_fee = self.database.fetchone(
                "SELECT COALESCE(SUM(fee), 0) as total FROM parking_transactions WHERE entry_time BETWEEN ? AND ?",
                [start_date, end_date]
            )["total"]
            
            # 获取各车辆类型的停车次数和费用
            by_vehicle_type = {}
            transactions = self.database.fetchall(
                "SELECT vehicle_id, fee FROM parking_transactions WHERE entry_time BETWEEN ? AND ?",
                [start_date, end_date]
            )
            
            for transaction in transactions:
                vehicle = self.database.fetchone(
                    "SELECT vehicle_type FROM vehicles WHERE id = ?",
                    [transaction["vehicle_id"]]
                )
                
                if vehicle:
                    vehicle_type = vehicle["vehicle_type"]
                    if vehicle_type not in by_vehicle_type:
                        by_vehicle_type[vehicle_type] = {
                            "count": 0,
                            "total_fee": 0
                        }
                    by_vehicle_type[vehicle_type]["count"] += 1
                    by_vehicle_type[vehicle_type]["total_fee"] += transaction["fee"]
            
            # 获取车位使用率
            total_spaces = self.database.fetchone("SELECT COUNT(*) as count FROM parking_spaces")["count"]
            max_occupied = self.database.fetchone(
                "SELECT MAX(occupied_count) as max FROM (
                    SELECT COUNT(*) as occupied_count 
                    FROM parking_transactions 
                    WHERE entry_time <= ? AND (exit_time IS NULL OR exit_time >= ?)
                    GROUP BY strftime('%H:%M', entry_time)
                )",
                [end_date, start_date]
            )["max"]
            
            if not max_occupied:
                max_occupied = 0
            
            usage_rate = (max_occupied / total_spaces) * 100 if total_spaces > 0 else 0
            
            return {
                "report_date": report_date,
                "total_parking": total_parking,
                "total_fee": round(total_fee, 2),
                "by_vehicle_type": by_vehicle_type,
                "usage_rate": round(usage_rate, 2),
                "total_spaces": total_spaces,
                "max_occupied": max_occupied
            }
        except Exception as e:
            logger.error(f"生成日报表失败: {e}")
            return None
    
    def generate_weekly_report(self, year, week):
        """
        生成周报表
        
        该方法生成指定年份和周数的周报表。
        
        参数：
            year: 年份
            week: 周数
        
        返回：
            包含周报表数据的字典
        """
        logger.info(f"生成周报表: {year}年第{week}周")
        try:
            # 计算周的开始和结束日期
            first_day = datetime(year, 1, 1)
            start_date = first_day + timedelta(days=(week-1)*7)
            end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
            
            # 生成该周每天的报表
            weekly_data = []
            total_parking = 0
            total_fee = 0
            
            current_date = start_date
            while current_date <= end_date:
                daily_report = self.generate_daily_report(current_date.strftime("%Y-%m-%d"))
                if daily_report:
                    weekly_data.append(daily_report)
                    total_parking += daily_report["total_parking"]
                    total_fee += daily_report["total_fee"]
                current_date += timedelta(days=1)
            
            return {
                "year": year,
                "week": week,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "weekly_data": weekly_data,
                "total_parking": total_parking,
                "total_fee": round(total_fee, 2)
            }
        except Exception as e:
            logger.error(f"生成周报表失败: {e}")
            return None
    
    def generate_monthly_report(self, year, month):
        """
        生成月报表
        
        该方法生成指定年份和月份的月报表。
        
        参数：
            year: 年份
            month: 月份
        
        返回：
            包含月报表数据的字典
        """
        logger.info(f"生成月报表: {year}年{month}月")
        try:
            # 计算月的开始和结束日期
            start_date = datetime(year, month, 1).strftime("%Y-%m-%d 00:00:00")
            
            # 计算月的结束日期
            if month == 12:
                end_date = datetime(year, 12, 31).strftime("%Y-%m-%d 23:59:59")
            else:
                end_date = datetime(year, month+1, 1) - timedelta(seconds=1)
                end_date = end_date.strftime("%Y-%m-%d 23:59:59")
            
            # 获取当月总停车次数
            total_parking = self.database.fetchone(
                "SELECT COUNT(*) as count FROM parking_transactions WHERE entry_time BETWEEN ? AND ?",
                [start_date, end_date]
            )["count"]
            
            # 获取当月总费用
            total_fee = self.database.fetchone(
                "SELECT COALESCE(SUM(fee), 0) as total FROM parking_transactions WHERE entry_time BETWEEN ? AND ?",
                [start_date, end_date]
            )["total"]
            
            # 获取各车辆类型的停车次数和费用
            by_vehicle_type = {}
            transactions = self.database.fetchall(
                "SELECT vehicle_id, fee FROM parking_transactions WHERE entry_time BETWEEN ? AND ?",
                [start_date, end_date]
            )
            
            for transaction in transactions:
                vehicle = self.database.fetchone(
                    "SELECT vehicle_type FROM vehicles WHERE id = ?",
                    [transaction["vehicle_id"]]
                )
                
                if vehicle:
                    vehicle_type = vehicle["vehicle_type"]
                    if vehicle_type not in by_vehicle_type:
                        by_vehicle_type[vehicle_type] = {
                            "count": 0,
                            "total_fee": 0
                        }
                    by_vehicle_type[vehicle_type]["count"] += 1
                    by_vehicle_type[vehicle_type]["total_fee"] += transaction["fee"]
            
            # 获取日均停车次数和费用
            avg_daily_parking = total_parking / 30 if total_parking > 0 else 0
            avg_daily_fee = total_fee / 30 if total_fee > 0 else 0
            
            return {
                "year": year,
                "month": month,
                "start_date": start_date.split(" ")[0],
                "end_date": end_date.split(" ")[0],
                "total_parking": total_parking,
                "total_fee": round(total_fee, 2),
                "avg_daily_parking": round(avg_daily_parking, 2),
                "avg_daily_fee": round(avg_daily_fee, 2),
                "by_vehicle_type": by_vehicle_type
            }
        except Exception as e:
            logger.error(f"生成月报表失败: {e}")
            return None
    
    def generate_annual_report(self, year):
        """
        生成年报表
        
        该方法生成指定年份的年报表。
        
        参数：
            year: 年份
        
        返回：
            包含年报表数据的字典
        """
        logger.info(f"生成年报表: {year}年")
        try:
            # 计算年的开始和结束日期
            start_date = f"{year}-01-01 00:00:00"
            end_date = f"{year}-12-31 23:59:59"
            
            # 获取当年总停车次数
            total_parking = self.database.fetchone(
                "SELECT COUNT(*) as count FROM parking_transactions WHERE entry_time BETWEEN ? AND ?",
                [start_date, end_date]
            )["count"]
            
            # 获取当年总费用
            total_fee = self.database.fetchone(
                "SELECT COALESCE(SUM(fee), 0) as total FROM parking_transactions WHERE entry_time BETWEEN ? AND ?",
                [start_date, end_date]
            )["total"]
            
            # 获取各车辆类型的停车次数和费用
            by_vehicle_type = {}
            transactions = self.database.fetchall(
                "SELECT vehicle_id, fee FROM parking_transactions WHERE entry_time BETWEEN ? AND ?",
                [start_date, end_date]
            )
            
            for transaction in transactions:
                vehicle = self.database.fetchone(
                    "SELECT vehicle_type FROM vehicles WHERE id = ?",
                    [transaction["vehicle_id"]]
                )
                
                if vehicle:
                    vehicle_type = vehicle["vehicle_type"]
                    if vehicle_type not in by_vehicle_type:
                        by_vehicle_type[vehicle_type] = {
                            "count": 0,
                            "total_fee": 0
                        }
                    by_vehicle_type[vehicle_type]["count"] += 1
                    by_vehicle_type[vehicle_type]["total_fee"] += transaction["fee"]
            
            # 生成各月的报表数据
            monthly_data = []
            for month in range(1, 13):
                monthly_report = self.generate_monthly_report(year, month)
                if monthly_report:
                    monthly_data.append(monthly_report)
            
            # 获取日均停车次数和费用
            avg_daily_parking = total_parking / 365 if total_parking > 0 else 0
            avg_daily_fee = total_fee / 365 if total_fee > 0 else 0
            
            return {
                "year": year,
                "start_date": start_date.split(" ")[0],
                "end_date": end_date.split(" ")[0],
                "total_parking": total_parking,
                "total_fee": round(total_fee, 2),
                "avg_daily_parking": round(avg_daily_parking, 2),
                "avg_daily_fee": round(avg_daily_fee, 2),
                "by_vehicle_type": by_vehicle_type,
                "monthly_data": monthly_data
            }
        except Exception as e:
            logger.error(f"生成年报表失败: {e}")
            return None
    
    def export_report_to_csv(self, report_data, file_path):
        """
        将报表数据导出为CSV文件
        
        参数：
            report_data: 报表数据字典
            file_path: 导出文件路径
        
        返回：
            布尔值，表示导出是否成功
        """
        logger.info(f"导出报表到CSV: {file_path}")
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 根据报表类型选择不同的导出逻辑
            if "report_date" in report_data:
                # 日报表导出
                self._export_daily_report_to_csv(report_data, file_path)
            elif "week" in report_data:
                # 周报表导出
                self._export_weekly_report_to_csv(report_data, file_path)
            elif "month" in report_data:
                # 月报表导出
                self._export_monthly_report_to_csv(report_data, file_path)
            elif "year" in report_data and "month" not in report_data:
                # 年报表导出
                self._export_annual_report_to_csv(report_data, file_path)
            
            logger.info(f"报表导出成功: {file_path}")
            return True
        except Exception as e:
            logger.error(f"报表导出失败: {e}")
            return False
    
    def _export_daily_report_to_csv(self, report_data, file_path):
        """
        导出日报表到CSV文件
        
        参数：
            report_data: 日报表数据
            file_path: 导出文件路径
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入报表标题
            writer.writerow([f"智能停车场日报表", "", "", ""])
            writer.writerow([f"报表日期: {report_data['report_date']}", "", "", ""])
            writer.writerow(["", "", "", ""])
            
            # 写入基本统计信息
            writer.writerow(["统计项", "数值", "", ""])
            writer.writerow(["总停车次数", report_data["total_parking"], "", ""])
            writer.writerow(["总费用(元)", report_data["total_fee"], "", ""])
            writer.writerow(["车位使用率(%)", report_data["usage_rate"], "", ""])
            writer.writerow(["总车位数", report_data["total_spaces"], "", ""])
            writer.writerow(["最高占用数", report_data["max_occupied"], "", ""])
            writer.writerow(["", "", "", ""])
            
            # 写入车辆类型统计
            writer.writerow(["车辆类型", "停车次数", "总费用(元)", "平均费用(元)"])
            for vehicle_type, data in report_data["by_vehicle_type"].items():
                avg_fee = data["total_fee"] / data["count"] if data["count"] > 0 else 0
                writer.writerow([
                    vehicle_type,
                    data["count"],
                    round(data["total_fee"], 2),
                    round(avg_fee, 2)
                ])
    
    def _export_weekly_report_to_csv(self, report_data, file_path):
        """
        导出周报表到CSV文件
        
        参数：
            report_data: 周报表数据
            file_path: 导出文件路径
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入报表标题
            writer.writerow([f"智能停车场周报表", "", "", "", "", ""])
            writer.writerow([f"报表周期: {report_data['start_date']} 至 {report_data['end_date']}", "", "", "", "", ""])
            writer.writerow([f"年份: {report_data['year']}, 周数: {report_data['week']}", "", "", "", "", ""])
            writer.writerow(["", "", "", "", "", ""])
            
            # 写入每周总计
            writer.writerow(["统计项", "数值", "", "", "", ""])
            writer.writerow(["总停车次数", report_data["total_parking"], "", "", "", ""])
            writer.writerow(["总费用(元)", report_data["total_fee"], "", "", "", ""])
            writer.writerow(["", "", "", "", "", ""])
            
            # 写入每日详细数据
            writer.writerow(["日期", "停车次数", "总费用(元)", "车位使用率(%)", "总车位数", "最高占用数"])
            for daily_data in report_data["weekly_data"]:
                writer.writerow([
                    daily_data["report_date"],
                    daily_data["total_parking"],
                    daily_data["total_fee"],
                    daily_data["usage_rate"],
                    daily_data["total_spaces"],
                    daily_data["max_occupied"]
                ])
    
    def _export_monthly_report_to_csv(self, report_data, file_path):
        """
        导出月报表到CSV文件
        
        参数：
            report_data: 月报表数据
            file_path: 导出文件路径
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入报表标题
            writer.writerow([f"智能停车场月报表", "", "", "", ""])
            writer.writerow([f"年份: {report_data['year']}, 月份: {report_data['month']}", "", "", "", ""])
            writer.writerow([f"报表周期: {report_data['start_date']} 至 {report_data['end_date']}", "", "", "", ""])
            writer.writerow(["", "", "", "", ""])
            
            # 写入基本统计信息
            writer.writerow(["统计项", "数值", "", "", ""])
            writer.writerow(["总停车次数", report_data["total_parking"], "", "", ""])
            writer.writerow(["总费用(元)", report_data["total_fee"], "", "", ""])
            writer.writerow(["日均停车次数", report_data["avg_daily_parking"], "", "", ""])
            writer.writerow(["日均费用(元)", report_data["avg_daily_fee"], "", "", ""])
            writer.writerow(["", "", "", "", ""])
            
            # 写入车辆类型统计
            writer.writerow(["车辆类型", "停车次数", "总费用(元)", "平均费用(元)", ""])
            for vehicle_type, data in report_data["by_vehicle_type"].items():
                avg_fee = data["total_fee"] / data["count"] if data["count"] > 0 else 0
                writer.writerow([
                    vehicle_type,
                    data["count"],
                    round(data["total_fee"], 2),
                    round(avg_fee, 2),
                    ""
                ])
    
    def _export_annual_report_to_csv(self, report_data, file_path):
        """
        导出年报表到CSV文件
        
        参数：
            report_data: 年报表数据
            file_path: 导出文件路径
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入报表标题
            writer.writerow([f"智能停车场年报表", "", "", "", ""])
            writer.writerow([f"报表年份: {report_data['year']}", "", "", "", ""])
            writer.writerow([f"报表周期: {report_data['start_date']} 至 {report_data['end_date']}", "", "", "", ""])
            writer.writerow(["", "", "", "", ""])
            
            # 写入基本统计信息
            writer.writerow(["统计项", "数值", "", "", ""])
            writer.writerow(["总停车次数", report_data["total_parking"], "", "", ""])
            writer.writerow(["总费用(元)", report_data["total_fee"], "", "", ""])
            writer.writerow(["日均停车次数", report_data["avg_daily_parking"], "", "", ""])
            writer.writerow(["日均费用(元)", report_data["avg_daily_fee"], "", "", ""])
            writer.writerow(["", "", "", "", ""])
            
            # 写入车辆类型统计
            writer.writerow(["车辆类型", "停车次数", "总费用(元)", "平均费用(元)", ""])
            for vehicle_type, data in report_data["by_vehicle_type"].items():
                avg_fee = data["total_fee"] / data["count"] if data["count"] > 0 else 0
                writer.writerow([
                    vehicle_type,
                    data["count"],
                    round(data["total_fee"], 2),
                    round(avg_fee, 2),
                    ""
                ])
            
            writer.writerow(["", "", "", "", ""])
            
            # 写入月度数据
            writer.writerow(["月份", "停车次数", "总费用(元)", "日均停车次数", "日均费用(元)"])
            for monthly_data in report_data["monthly_data"]:
                writer.writerow([
                    monthly_data["month"],
                    monthly_data["total_parking"],
                    monthly_data["total_fee"],
                    monthly_data["avg_daily_parking"],
                    monthly_data["avg_daily_fee"]
                ])


class ReportManager:
    """
    报表管理器类
    
    该类封装了报表管理的核心功能，包括报表生成、导出、查询等操作。
    
    属性：
        database: 数据库连接对象
        report_generator: 报表生成器对象
    """
    
    def __init__(self, database):
        """
        初始化报表管理器对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
        self.report_generator = ReportGenerator(database)
    
    def init(self):
        """
        初始化报表管理器
        
        该方法执行报表管理器的初始化操作。
        """
        logger.info("初始化报表管理器")
        # 报表管理器初始化操作
    
    def generate_report(self, report_type, **kwargs):
        """
        生成报表（对外接口）
        
        参数：
            report_type: 报表类型，可选值包括：
                - 'daily': 日报表
                - 'weekly': 周报表
                - 'monthly': 月报表
                - 'annual': 年报表
            **kwargs: 报表生成参数
                - report_date: 报表日期，用于日报表
                - year: 年份，用于周报表、月报表和年报表
                - week: 周数，用于周报表
                - month: 月份，用于月报表
        
        返回：
            包含报表数据的字典，若生成失败则返回None
        """
        logger.info(f"生成报表: 类型: {report_type}, 参数: {kwargs}")
        try:
            if report_type == 'daily':
                return self.report_generator.generate_daily_report(**kwargs)
            elif report_type == 'weekly':
                return self.report_generator.generate_weekly_report(**kwargs)
            elif report_type == 'monthly':
                return self.report_generator.generate_monthly_report(**kwargs)
            elif report_type == 'annual':
                return self.report_generator.generate_annual_report(**kwargs)
            else:
                logger.error(f"不支持的报表类型: {report_type}")
                return None
        except Exception as e:
            logger.error(f"生成报表失败: {e}")
            return None
    
    def export_report(self, report_data, file_path):
        """
        导出报表（对外接口）
        
        参数：
            report_data: 报表数据字典
            file_path: 导出文件路径
        
        返回：
            布尔值，表示导出是否成功
        """
        return self.report_generator.export_report_to_csv(report_data, file_path)
    
    def get_parking_transactions(self, start_date=None, end_date=None, vehicle_type=None):
        """
        查询停车交易记录
        
        参数：
            start_date: 开始日期，可选
            end_date: 结束日期，可选
            vehicle_type: 车辆类型，可选
        
        返回：
            停车交易记录列表
        """
        logger.info(f"查询停车交易记录: 开始日期: {start_date}, 结束日期: {end_date}, 车辆类型: {vehicle_type}")
        try:
            # 构建查询条件
            query = "SELECT * FROM parking_transactions WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND entry_time >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND entry_time <= ?"
                params.append(end_date)
            
            # 查询结果
            transactions = self.database.fetchall(query, params)
            
            # 如果指定了车辆类型，则过滤结果
            if vehicle_type:
                filtered_transactions = []
                for transaction in transactions:
                    vehicle = self.database.fetchone(
                        "SELECT vehicle_type FROM vehicles WHERE id = ?",
                        [transaction["vehicle_id"]]
                    )
                    if vehicle and vehicle["vehicle_type"] == vehicle_type:
                        filtered_transactions.append(transaction)
                return [dict(t) for t in filtered_transactions]
            
            return [dict(t) for t in transactions]
        except Exception as e:
            logger.error(f"查询停车交易记录失败: {e}")
            return []
    
    def get_space_usage_rate(self, start_date, end_date):
        """
        获取车位使用率
        
        参数：
            start_date: 开始日期
            end_date: 结束日期
        
        返回：
            车位使用率（%）
        """
        logger.info(f"获取车位使用率: 开始日期: {start_date}, 结束日期: {end_date}")
        try:
            # 获取总车位数
            total_spaces = self.database.fetchone("SELECT COUNT(*) as count FROM parking_spaces")["count"]
            
            if total_spaces == 0:
                return 0
            
            # 获取平均占用数
            # 这里简化处理，实际项目中应该计算时间段内的平均占用数
            avg_occupied = self.database.fetchone(
                "SELECT AVG(occupied_count) as avg FROM (
                    SELECT COUNT(*) as occupied_count 
                    FROM parking_transactions 
                    WHERE entry_time <= ? AND (exit_time IS NULL OR exit_time >= ?)
                    GROUP BY strftime('%Y-%m-%d %H', entry_time)
                )",
                [end_date, start_date]
            )["avg"]
            
            if not avg_occupied:
                avg_occupied = 0
            
            usage_rate = (avg_occupied / total_spaces) * 100
            return round(usage_rate, 2)
        except Exception as e:
            logger.error(f"获取车位使用率失败: {e}")
            return 0
    
    def get_vehicle_type_distribution(self, start_date=None, end_date=None):
        """
        获取车辆类型分布
        
        参数：
            start_date: 开始日期，可选
            end_date: 结束日期，可选
        
        返回：
            包含车辆类型分布的字典
        """
        logger.info(f"获取车辆类型分布: 开始日期: {start_date}, 结束日期: {end_date}")
        try:
            # 构建查询条件
            query = "SELECT vehicle_type, COUNT(*) as count FROM vehicles WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND created_at >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND created_at <= ?"
                params.append(end_date)
            
            query += " GROUP BY vehicle_type"
            
            # 获取车辆类型分布
            distribution = self.database.fetchall(query, params)
            
            result = {}
            for item in distribution:
                result[item["vehicle_type"]] = item["count"]
            
            return result
        except Exception as e:
            logger.error(f"获取车辆类型分布失败: {e}")
            return {}
