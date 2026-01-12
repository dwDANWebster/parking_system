import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ReportManager:
    def __init__(self, database):
        self.database = database
    
    def init(self):
        logger.info("初始化报表统计模块")
        # 初始化报表配置
        self._init_report_configs()
    
    def _init_report_configs(self):
        logger.info("初始化报表配置")
        # 添加一些初始的报表配置
        pass
    
    def generate_daily_report(self, date=None):
        logger.info(f"生成每日报表: {date}")
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            # 统计当日车辆进出情况
            entry_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE DATE(entry_time) = ?",
                (date,)
            )['count']
            
            exit_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE DATE(exit_time) = ?",
                (date,)
            )['count']
            
            # 统计当日收费情况
            total_fee = self.database.fetch_one(
                "SELECT SUM(amount) as total FROM payments WHERE DATE(payment_time) = ? AND status = ?",
                (date, "success")
            )['total'] or 0.0
            
            # 统计当日车辆类型分布
            vehicle_type_stats = self.database.fetch_all(
                "SELECT v.vehicle_type, COUNT(*) as count FROM parking_records pr "
                "JOIN vehicles v ON pr.vehicle_id = v.id "
                "WHERE DATE(pr.entry_time) = ? GROUP BY v.vehicle_type",
                (date,)
            )
            
            # 统计平均停留时间
            avg_stay_time = self.database.fetch_one(
                "SELECT AVG(duration) as avg FROM parking_records WHERE DATE(entry_time) = ? AND duration IS NOT NULL",
                (date,)
            )['avg'] or 0
            
            # 统计车位使用率
            # 获取总车位数
            total_spaces = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_spaces"
            )['count']
            
            # 统计高峰期最大占用数（每小时统计一次）
            max_occupied = 0
            for hour in range(24):
                # 统计该小时内同时停车的最大数量
                # 这里简化处理，统计该小时内的平均占用数
                occupied = self.database.fetch_one(
                    "SELECT COUNT(*) as count FROM parking_records WHERE DATE(entry_time) = ? AND strftime('%H', entry_time) <= ? AND (exit_time IS NULL OR strftime('%H', exit_time) > ?)",
                    (date, f"{hour:02d}", f"{hour:02d}")
                )['count']
                if occupied > max_occupied:
                    max_occupied = occupied
            
            occupancy_rate = (max_occupied / total_spaces) * 100 if total_spaces > 0 else 0
            
            # 统计支付方式分布
            payment_method_stats = self.database.fetch_all(
                "SELECT payment_method, COUNT(*) as count, SUM(amount) as total FROM payments WHERE DATE(payment_time) = ? AND status = ? GROUP BY payment_method",
                (date, "success")
            )
            
            report = {
                "date": date,
                "basic_stats": {
                    "entry_count": entry_count,
                    "exit_count": exit_count,
                    "total_fee": total_fee,
                    "avg_stay_time": round(avg_stay_time, 2),
                    "occupancy_rate": round(occupancy_rate, 2),
                    "max_occupied": max_occupied
                },
                "vehicle_type_stats": [
                    {
                        "vehicle_type": row['vehicle_type'],
                        "count": row['count']
                    }
                    for row in vehicle_type_stats
                ],
                "payment_method_stats": [
                    {
                        "payment_method": row['payment_method'],
                        "count": row['count'],
                        "total": row['total']
                    }
                    for row in payment_method_stats
                ]
            }
            
            logger.info(f"每日报表生成完成: {date}")
            return report
        except Exception as e:
            logger.error(f"生成每日报表失败: {e}")
            raise
    
    def generate_weekly_report(self, start_date=None, end_date=None):
        logger.info(f"生成周报: {start_date} 到 {end_date}")
        try:
            if not start_date:
                # 默认生成本周的报表
                today = datetime.now()
                start_date = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
                end_date = (today + timedelta(days=6 - today.weekday())).strftime('%Y-%m-%d')
            
            # 统计周内车辆进出情况
            entry_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE entry_time BETWEEN ? AND ?",
                (start_date, end_date)
            )['count']
            
            exit_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE exit_time BETWEEN ? AND ?",
                (start_date, end_date)
            )['count']
            
            # 统计周内收费情况
            total_fee = self.database.fetch_one(
                "SELECT SUM(amount) as total FROM payments WHERE payment_time BETWEEN ? AND ? AND status = ?",
                (start_date, end_date, "success")
            )['total'] or 0.0
            
            # 统计周内车辆类型分布
            vehicle_type_stats = self.database.fetch_all(
                "SELECT v.vehicle_type, COUNT(*) as count FROM parking_records pr "
                "JOIN vehicles v ON pr.vehicle_id = v.id "
                "WHERE pr.entry_time BETWEEN ? AND ? GROUP BY v.vehicle_type",
                (start_date, end_date)
            )
            
            # 统计周内每日收入
            daily_fee_stats = []
            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            while current_date <= end:
                date_str = current_date.strftime('%Y-%m-%d')
                daily_fee = self.database.fetch_one(
                    "SELECT SUM(amount) as total FROM payments WHERE DATE(payment_time) = ? AND status = ?",
                    (date_str, "success")
                )['total'] or 0.0
                daily_fee_stats.append({
                    "date": date_str,
                    "fee": daily_fee
                })
                current_date += timedelta(days=1)
            
            # 统计周内平均停留时间
            avg_stay_time = self.database.fetch_one(
                "SELECT AVG(duration) as avg FROM parking_records WHERE entry_time BETWEEN ? AND ? AND duration IS NOT NULL",
                (start_date, end_date)
            )['avg'] or 0
            
            # 统计周内车位使用率
            total_spaces = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_spaces"
            )['count']
            
            # 统计每天的最大占用数
            max_occupied = 0
            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            while current_date <= end:
                date_str = current_date.strftime('%Y-%m-%d')
                for hour in range(24):
                    occupied = self.database.fetch_one(
                        "SELECT COUNT(*) as count FROM parking_records WHERE DATE(entry_time) <= ? AND (exit_time IS NULL OR DATE(exit_time) >= ?) AND strftime('%H', entry_time) <= ? AND (exit_time IS NULL OR strftime('%H', exit_time) > ?)",
                        (date_str, date_str, f"{hour:02d}", f"{hour:02d}")
                    )['count']
                    if occupied > max_occupied:
                        max_occupied = occupied
                current_date += timedelta(days=1)
            
            occupancy_rate = (max_occupied / total_spaces) * 100 if total_spaces > 0 else 0
            
            report = {
                "start_date": start_date,
                "end_date": end_date,
                "basic_stats": {
                    "entry_count": entry_count,
                    "exit_count": exit_count,
                    "total_fee": total_fee,
                    "avg_stay_time": round(avg_stay_time, 2),
                    "occupancy_rate": round(occupancy_rate, 2),
                    "max_occupied": max_occupied
                },
                "vehicle_type_stats": [
                    {
                        "vehicle_type": row['vehicle_type'],
                        "count": row['count']
                    }
                    for row in vehicle_type_stats
                ],
                "daily_fee_stats": daily_fee_stats
            }
            
            logger.info(f"周报生成完成: {start_date} 到 {end_date}")
            return report
        except Exception as e:
            logger.error(f"生成周报失败: {e}")
            raise
    
    def generate_monthly_report(self, year=None, month=None):
        logger.info(f"生成月报: {year}年{month}月")
        try:
            if not year or not month:
                now = datetime.now()
                year = now.year
                month = now.month
            
            # 生成月份的开始和结束日期
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year}-12-31"
            else:
                end_date = f"{year}-{month+1:02d}-01"
            
            # 统计月内车辆进出情况
            entry_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE entry_time BETWEEN ? AND ?",
                (start_date, end_date)
            )['count']
            
            exit_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE exit_time BETWEEN ? AND ?",
                (start_date, end_date)
            )['count']
            
            # 统计月内收费情况
            total_fee = self.database.fetch_one(
                "SELECT SUM(amount) as total FROM payments WHERE payment_time BETWEEN ? AND ? AND status = ?",
                (start_date, end_date, "success")
            )['total'] or 0.0
            
            # 统计月内车辆类型分布
            vehicle_type_stats = self.database.fetch_all(
                "SELECT v.vehicle_type, COUNT(*) as count FROM parking_records pr "
                "JOIN vehicles v ON pr.vehicle_id = v.id "
                "WHERE pr.entry_time BETWEEN ? AND ? GROUP BY v.vehicle_type",
                (start_date, end_date)
            )
            
            # 统计月内每日收入
            daily_fee_stats = []
            from calendar import monthrange
            days_in_month = monthrange(year, month)[1]
            for day in range(1, days_in_month + 1):
                date_str = f"{year}-{month:02d}-{day:02d}"
                daily_fee = self.database.fetch_one(
                    "SELECT SUM(amount) as total FROM payments WHERE DATE(payment_time) = ? AND status = ?",
                    (date_str, "success")
                )['total'] or 0.0
                daily_fee_stats.append({
                    "date": date_str,
                    "fee": daily_fee
                })
            
            # 统计月内平均停留时间
            avg_stay_time = self.database.fetch_one(
                "SELECT AVG(duration) as avg FROM parking_records WHERE entry_time BETWEEN ? AND ? AND duration IS NOT NULL",
                (start_date, end_date)
            )['avg'] or 0
            
            # 统计月内车位使用率
            total_spaces = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_spaces"
            )['count']
            
            # 统计每天的最大占用数
            max_occupied = 0
            for day in range(1, days_in_month + 1):
                date_str = f"{year}-{month:02d}-{day:02d}"
                for hour in range(24):
                    occupied = self.database.fetch_one(
                        "SELECT COUNT(*) as count FROM parking_records WHERE DATE(entry_time) <= ? AND (exit_time IS NULL OR DATE(exit_time) >= ?) AND strftime('%H', entry_time) <= ? AND (exit_time IS NULL OR strftime('%H', exit_time) > ?)",
                        (date_str, date_str, f"{hour:02d}", f"{hour:02d}")
                    )['count']
                    if occupied > max_occupied:
                        max_occupied = occupied
            
            occupancy_rate = (max_occupied / total_spaces) * 100 if total_spaces > 0 else 0
            
            report = {
                "year": year,
                "month": month,
                "start_date": start_date,
                "end_date": end_date,
                "basic_stats": {
                    "entry_count": entry_count,
                    "exit_count": exit_count,
                    "total_fee": total_fee,
                    "avg_stay_time": round(avg_stay_time, 2),
                    "occupancy_rate": round(occupancy_rate, 2),
                    "max_occupied": max_occupied
                },
                "vehicle_type_stats": [
                    {
                        "vehicle_type": row['vehicle_type'],
                        "count": row['count']
                    }
                    for row in vehicle_type_stats
                ],
                "daily_fee_stats": daily_fee_stats
            }
            
            logger.info(f"月报生成完成: {year}年{month}月")
            return report
        except Exception as e:
            logger.error(f"生成月报失败: {e}")
            raise
    
    def generate_annual_report(self, year=None):
        logger.info(f"生成年报: {year}年")
        try:
            if not year:
                year = datetime.now().year
            
            # 生成年份的开始和结束日期
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            # 统计年内车辆进出情况
            entry_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE entry_time BETWEEN ? AND ?",
                (start_date, end_date)
            )['count']
            
            exit_count = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_records WHERE exit_time BETWEEN ? AND ?",
                (start_date, end_date)
            )['count']
            
            # 统计年内收费情况
            total_fee = self.database.fetch_one(
                "SELECT SUM(amount) as total FROM payments WHERE payment_time BETWEEN ? AND ? AND status = ?",
                (start_date, end_date, "success")
            )['total'] or 0.0
            
            # 统计年内车辆类型分布
            vehicle_type_stats = self.database.fetch_all(
                "SELECT v.vehicle_type, COUNT(*) as count FROM parking_records pr "
                "JOIN vehicles v ON pr.vehicle_id = v.id "
                "WHERE pr.entry_time BETWEEN ? AND ? GROUP BY v.vehicle_type",
                (start_date, end_date)
            )
            
            # 统计年内月度收入
            monthly_fee_stats = []
            for month in range(1, 13):
                month_start = f"{year}-{month:02d}-01"
                if month == 12:
                    month_end = f"{year}-12-31"
                else:
                    month_end = f"{year}-{month+1:02d}-01"
                monthly_fee = self.database.fetch_one(
                    "SELECT SUM(amount) as total FROM payments WHERE payment_time BETWEEN ? AND ? AND status = ?",
                    (month_start, month_end, "success")
                )['total'] or 0.0
                monthly_fee_stats.append({
                    "month": month,
                    "fee": monthly_fee
                })
            
            # 统计年内平均停留时间
            avg_stay_time = self.database.fetch_one(
                "SELECT AVG(duration) as avg FROM parking_records WHERE entry_time BETWEEN ? AND ? AND duration IS NOT NULL",
                (start_date, end_date)
            )['avg'] or 0
            
            # 统计年内车位使用率
            total_spaces = self.database.fetch_one(
                "SELECT COUNT(*) as count FROM parking_spaces"
            )['count']
            
            # 统计每天的最大占用数
            max_occupied = 0
            for month in range(1, 13):
                from calendar import monthrange
                days_in_month = monthrange(year, month)[1]
                for day in range(1, days_in_month + 1):
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    for hour in range(24):
                        occupied = self.database.fetch_one(
                            "SELECT COUNT(*) as count FROM parking_records WHERE DATE(entry_time) <= ? AND (exit_time IS NULL OR DATE(exit_time) >= ?) AND strftime('%H', entry_time) <= ? AND (exit_time IS NULL OR strftime('%H', exit_time) > ?)",
                            (date_str, date_str, f"{hour:02d}", f"{hour:02d}")
                        )['count']
                        if occupied > max_occupied:
                            max_occupied = occupied
            
            occupancy_rate = (max_occupied / total_spaces) * 100 if total_spaces > 0 else 0
            
            report = {
                "year": year,
                "start_date": start_date,
                "end_date": end_date,
                "basic_stats": {
                    "entry_count": entry_count,
                    "exit_count": exit_count,
                    "total_fee": total_fee,
                    "avg_stay_time": round(avg_stay_time, 2),
                    "occupancy_rate": round(occupancy_rate, 2),
                    "max_occupied": max_occupied
                },
                "vehicle_type_stats": [
                    {
                        "vehicle_type": row['vehicle_type'],
                        "count": row['count']
                    }
                    for row in vehicle_type_stats
                ],
                "monthly_fee_stats": monthly_fee_stats
            }
            
            logger.info(f"年报生成完成: {year}年")
            return report
        except Exception as e:
            logger.error(f"生成年报失败: {e}")
            raise
    
    def export_report_to_csv(self, report_data, file_path):
        logger.info(f"导出报表到CSV: {file_path}")
        try:
            import csv
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 根据报表类型写入不同的内容
                if 'date' in report_data:
                    # 每日报表
                    writer.writerow(['每日报表', report_data['date']])
                    writer.writerow([])
                    
                    # 基本统计
                    writer.writerow(['基本统计'])
                    writer.writerow(['项目', '数值'])
                    writer.writerow(['入场车辆数', report_data['basic_stats']['entry_count']])
                    writer.writerow(['出场车辆数', report_data['basic_stats']['exit_count']])
                    writer.writerow(['总收入(元)', report_data['basic_stats']['total_fee']])
                    writer.writerow(['平均停留时间(分钟)', report_data['basic_stats']['avg_stay_time']])
                    writer.writerow(['车位使用率(%)', report_data['basic_stats']['occupancy_rate']])
                    writer.writerow(['高峰期最大占用数', report_data['basic_stats']['max_occupied']])
                    
                    writer.writerow([])
                    
                    # 车辆类型分布
                    writer.writerow(['车辆类型分布'])
                    writer.writerow(['车辆类型', '数量'])
                    for stat in report_data['vehicle_type_stats']:
                        writer.writerow([stat['vehicle_type'], stat['count']])
                    
                    writer.writerow([])
                    
                    # 支付方式统计
                    writer.writerow(['支付方式统计'])
                    writer.writerow(['支付方式', '笔数', '金额(元)'])
                    for stat in report_data['payment_method_stats']:
                        writer.writerow([stat['payment_method'], stat['count'], stat['total']])
                
                elif 'start_date' in report_data and 'end_date' in report_data:
                    if 'month' in report_data:
                        # 月报
                        writer.writerow(['月报', f"{report_data['year']}年{report_data['month']}月"])
                    elif len(report_data['start_date']) == 10 and len(report_data['end_date']) == 10:
                        # 周报或自定义时间段报表
                        writer.writerow(['报表', f"{report_data['start_date']} 到 {report_data['end_date']}"])
                    
                    writer.writerow([])
                    
                    # 基本统计
                    writer.writerow(['基本统计'])
                    writer.writerow(['项目', '数值'])
                    writer.writerow(['入场车辆数', report_data['basic_stats']['entry_count']])
                    writer.writerow(['出场车辆数', report_data['basic_stats']['exit_count']])
                    writer.writerow(['总收入(元)', report_data['basic_stats']['total_fee']])
                    writer.writerow(['平均停留时间(分钟)', report_data['basic_stats']['avg_stay_time']])
                    writer.writerow(['车位使用率(%)', report_data['basic_stats']['occupancy_rate']])
                    writer.writerow(['高峰期最大占用数', report_data['basic_stats']['max_occupied']])
                    
                    writer.writerow([])
                    
                    # 车辆类型分布
                    writer.writerow(['车辆类型分布'])
                    writer.writerow(['车辆类型', '数量'])
                    for stat in report_data['vehicle_type_stats']:
                        writer.writerow([stat['vehicle_type'], stat['count']])
                    
                    writer.writerow([])
                    
                    # 收入统计
                    writer.writerow(['收入统计'])
                    if 'daily_fee_stats' in report_data:
                        writer.writerow(['日期', '收入(元)'])
                        for stat in report_data['daily_fee_stats']:
                            writer.writerow([stat['date'], stat['fee']])
                    elif 'monthly_fee_stats' in report_data:
                        writer.writerow(['月份', '收入(元)'])
                        for stat in report_data['monthly_fee_stats']:
                            writer.writerow([stat['month'], stat['fee']])
                
                elif 'year' in report_data:
                    # 年报
                    writer.writerow(['年报', f"{report_data['year']}年"])
                    writer.writerow([])
                    
                    # 基本统计
                    writer.writerow(['基本统计'])
                    writer.writerow(['项目', '数值'])
                    writer.writerow(['入场车辆数', report_data['basic_stats']['entry_count']])
                    writer.writerow(['出场车辆数', report_data['basic_stats']['exit_count']])
                    writer.writerow(['总收入(元)', report_data['basic_stats']['total_fee']])
                    writer.writerow(['平均停留时间(分钟)', report_data['basic_stats']['avg_stay_time']])
                    writer.writerow(['车位使用率(%)', report_data['basic_stats']['occupancy_rate']])
                    writer.writerow(['高峰期最大占用数', report_data['basic_stats']['max_occupied']])
                    
                    writer.writerow([])
                    
                    # 车辆类型分布
                    writer.writerow(['车辆类型分布'])
                    writer.writerow(['车辆类型', '数量'])
                    for stat in report_data['vehicle_type_stats']:
                        writer.writerow([stat['vehicle_type'], stat['count']])
                    
                    writer.writerow([])
                    
                    # 月度收入统计
                    writer.writerow(['月度收入统计'])
                    writer.writerow(['月份', '收入(元)'])
                    for stat in report_data['monthly_fee_stats']:
                        writer.writerow([stat['month'], stat['fee']])
            
            logger.info(f"报表导出成功: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出报表失败: {e}")
            raise
    
    def get_vehicle_trend(self, days=30):
        logger.info(f"获取车辆趋势数据: 最近{days}天")
        try:
            # 计算开始日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 统计每日车辆进出情况
            trend_data = []
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                
                entry_count = self.database.fetch_one(
                    "SELECT COUNT(*) as count FROM parking_records WHERE DATE(entry_time) = ?",
                    (date_str,)
                )['count']
                
                exit_count = self.database.fetch_one(
                    "SELECT COUNT(*) as count FROM parking_records WHERE DATE(exit_time) = ?",
                    (date_str,)
                )['count']
                
                trend_data.append({
                    "date": date_str,
                    "entry_count": entry_count,
                    "exit_count": exit_count
                })
                
                current_date += timedelta(days=1)
            
            logger.info(f"获取车辆趋势数据完成: 最近{days}天")
            return trend_data
        except Exception as e:
            logger.error(f"获取车辆趋势数据失败: {e}")
            raise
    
    def get_fee_trend(self, days=30):
        logger.info(f"获取收入趋势数据: 最近{days}天")
        try:
            # 计算开始日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 统计每日收入情况
            trend_data = []
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                
                total_fee = self.database.fetch_one(
                    "SELECT SUM(amount) as total FROM payments WHERE DATE(payment_time) = ? AND status = ?",
                    (date_str, "success")
                )['total'] or 0.0
                
                trend_data.append({
                    "date": date_str,
                    "fee": total_fee
                })
                
                current_date += timedelta(days=1)
            
            logger.info(f"获取收入趋势数据完成: 最近{days}天")
            return trend_data
        except Exception as e:
            logger.error(f"获取收入趋势数据失败: {e}")
            raise
    
    def get_occupancy_trend(self, days=7, intervals=24):
        logger.info(f"获取车位占用趋势数据: 最近{days}天，每{24//intervals}小时统计一次")
        try:
            # 计算开始日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 统计每小时的车位占用情况
            trend_data = []
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                
                for hour in range(0, 24, 24//intervals):
                    hour_str = f"{hour:02d}:00"
                    
                    occupied = self.database.fetch_one(
                        "SELECT COUNT(*) as count FROM parking_records WHERE DATE(entry_time) <= ? AND (exit_time IS NULL OR DATE(exit_time) >= ?) AND strftime('%H', entry_time) <= ? AND (exit_time IS NULL OR strftime('%H', exit_time) > ?)",
                        (date_str, date_str, f"{hour:02d}", f"{hour:02d}")
                    )['count']
                    
                    total_spaces = self.database.fetch_one(
                        "SELECT COUNT(*) as count FROM parking_spaces"
                    )['count']
                    
                    occupancy_rate = (occupied / total_spaces) * 100 if total_spaces > 0 else 0
                    
                    trend_data.append({
                        "datetime": f"{date_str} {hour_str}",
                        "occupied": occupied,
                        "occupancy_rate": round(occupancy_rate, 2)
                    })
                
                current_date += timedelta(days=1)
            
            logger.info(f"获取车位占用趋势数据完成: 最近{days}天")
            return trend_data
        except Exception as e:
            logger.error(f"获取车位占用趋势数据失败: {e}")
            raise