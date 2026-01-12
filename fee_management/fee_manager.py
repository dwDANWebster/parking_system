import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class FeeRule:
    def __init__(self, rule_name, vehicle_type, time_unit, unit_price, free_duration=0, max_daily_fee=None):
        self.id = None
        self.rule_name = rule_name
        self.vehicle_type = vehicle_type
        self.time_unit = time_unit
        self.unit_price = unit_price
        self.free_duration = free_duration
        self.max_daily_fee = max_daily_fee
        self.is_active = True
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "rule_name": self.rule_name,
            "vehicle_type": self.vehicle_type,
            "time_unit": self.time_unit,
            "unit_price": self.unit_price,
            "free_duration": self.free_duration,
            "max_daily_fee": self.max_daily_fee,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class FeeCalculator:
    def __init__(self, database):
        self.database = database
    
    def calculate_fee(self, vehicle_id, duration, user_id=None):
        logger.info(f"计算停车费用: 车辆ID {vehicle_id}, 时长 {duration}分钟, 用户ID {user_id}")
        try:
            # 获取车辆信息
            vehicle = self.database.fetch_one(
                "SELECT * FROM vehicles WHERE id = ?",
                (vehicle_id,)
            )
            if not vehicle:
                raise ValueError(f"车辆不存在: {vehicle_id}")
            
            # 获取适用的计费规则
            rule = self.database.fetch_one(
                "SELECT * FROM fee_rules WHERE vehicle_type = ? AND is_active = ?",
                (vehicle['vehicle_type'], True)
            )
            
            if not rule:
                # 如果没有对应类型的规则，使用默认规则（小型车）
                rule = self.database.fetch_one(
                    "SELECT * FROM fee_rules WHERE vehicle_type = ? AND is_active = ?",
                    ("小型车", True)
                )
            
            if not rule:
                raise ValueError("没有可用的计费规则")
            
            # 计算费用
            fee = 0.0
            
            # 扣除免费时长
            if duration > rule['free_duration']:
                payable_duration = duration - rule['free_duration']
                
                # 根据时间单位计算费用
                if rule['time_unit'] == "hour":
                    # 按小时计算，不足1小时按1小时计算
                    hours = payable_duration / 60
                    fee = rule['unit_price'] * round(hours + 0.5)
                elif rule['time_unit'] == "half_hour":
                    # 按半小时计算，不足半小时按半小时计算
                    half_hours = payable_duration / 30
                    fee = rule['unit_price'] * round(half_hours + 0.5)
                else:
                    # 按分钟计算
                    fee = rule['unit_price'] * payable_duration
            
            # 应用每日最高费用限制
            if rule['max_daily_fee'] and fee > rule['max_daily_fee']:
                fee = rule['max_daily_fee']
            
            # 应用会员折扣
            if user_id:
                user = self.database.fetch_one(
                    "SELECT * FROM users WHERE id = ?",
                    (user_id,)
                )
                if user and user['is_member']:
                    # 获取会员等级折扣
                    member_level = self.database.fetch_one(
                        "SELECT * FROM member_levels WHERE level_name = ?",
                        (user['member_level'],)
                    )
                    if member_level:
                        fee *= member_level['discount_rate']
                        logger.info(f"应用会员折扣: {member_level['discount_rate']}, 折扣后费用: {fee}")
            
            # 四舍五入到小数点后两位
            fee = round(fee, 2)
            
            logger.info(f"停车费用计算完成: {fee}元")
            return fee
        except Exception as e:
            logger.error(f"计算停车费用失败: {e}")
            raise
    
    def calculate_daily_fee(self, vehicle_id, entry_time, exit_time, user_id=None):
        logger.info(f"按时间段计算停车费用: 车辆ID {vehicle_id}, 入场时间 {entry_time}, 出场时间 {exit_time}, 用户ID {user_id}")
        try:
            # 计算总时长
            entry = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
            exit_ = datetime.strptime(exit_time, '%Y-%m-%d %H:%M:%S')
            duration = int((exit_ - entry).total_seconds() / 60)
            
            # 调用基本计算方法
            return self.calculate_fee(vehicle_id, duration, user_id)
        except Exception as e:
            logger.error(f"按时间段计算停车费用失败: {e}")
            raise

class PaymentProcessor:
    def __init__(self, database):
        self.database = database
    
    def process_payment(self, record_id, amount, payment_method, user_id=None):
        logger.info(f"处理支付: 记录ID {record_id}, 金额 {amount}元, 支付方式 {payment_method}, 用户ID {user_id}")
        try:
            # 验证停车记录
            record = self.database.fetch_one(
                "SELECT * FROM parking_records WHERE id = ?",
                (record_id,)
            )
            if not record:
                raise ValueError(f"停车记录不存在: {record_id}")
            
            if record['payment_status'] == "paid":
                raise ValueError(f"停车记录已支付: {record_id}")
            
            # 生成交易ID
            import uuid
            transaction_id = str(uuid.uuid4())
            
            # 创建支付记录
            payment_id = self.database.execute(
                "INSERT INTO payments (record_id, amount, payment_method, transaction_id, payment_time, status) VALUES (?, ?, ?, ?, ?, ?)",
                (record_id, amount, payment_method, transaction_id, datetime.now(), "success")
            )
            
            # 更新停车记录状态
            self.database.execute(
                "UPDATE parking_records SET fee = ?, payment_status = ?, payment_method = ? WHERE id = ?",
                (amount, "paid", payment_method, record_id)
            )
            
            # 如果是余额支付，扣除用户余额
            if payment_method == "balance" and user_id:
                self.database.execute(
                    "UPDATE users SET balance = balance - ? WHERE id = ?",
                    (amount, user_id)
                )
            
            logger.info(f"支付处理成功: 交易ID {transaction_id}, 支付ID {payment_id}")
            return {
                "payment_id": payment_id,
                "transaction_id": transaction_id,
                "amount": amount,
                "payment_method": payment_method,
                "payment_time": datetime.now()
            }
        except Exception as e:
            logger.error(f"处理支付失败: {e}")
            raise
    
    def refund_payment(self, payment_id):
        logger.info(f"处理退款: 支付ID {payment_id}")
        try:
            # 获取支付记录
            payment = self.database.fetch_one(
                "SELECT * FROM payments WHERE id = ?",
                (payment_id,)
            )
            if not payment:
                raise ValueError(f"支付记录不存在: {payment_id}")
            
            if payment['status'] != "success":
                raise ValueError(f"支付记录状态错误: {payment['status']}")
            
            # 获取停车记录
            record = self.database.fetch_one(
                "SELECT * FROM parking_records WHERE id = ?",
                (payment['record_id'],)
            )
            if not record:
                raise ValueError(f"停车记录不存在: {payment['record_id']}")
            
            # 更新支付记录状态
            self.database.execute(
                "UPDATE payments SET status = ? WHERE id = ?",
                ("refunded", payment_id)
            )
            
            # 更新停车记录状态
            self.database.execute(
                "UPDATE parking_records SET payment_status = ? WHERE id = ?",
                ("refunded", payment['record_id'])
            )
            
            # 如果是余额支付，退还用户余额
            if payment['payment_method'] == "balance":
                # 获取用户ID（假设停车记录关联了用户）
                vehicle = self.database.fetch_one(
                    "SELECT * FROM vehicles WHERE id = ?",
                    (record['vehicle_id'],)
                )
                if vehicle:
                    # 查找关联的用户
                    user = self.database.fetch_one(
                        "SELECT * FROM users WHERE vehicle_plate = ?",
                        (vehicle['plate_number'],)
                    )
                    if user:
                        self.database.execute(
                            "UPDATE users SET balance = balance + ? WHERE id = ?",
                            (payment['amount'], user['id'])
                        )
            
            logger.info(f"退款处理成功: 支付ID {payment_id}")
            return True
        except Exception as e:
            logger.error(f"处理退款失败: {e}")
            raise

class FeeManager:
    def __init__(self, database):
        self.database = database
        self.calculator = FeeCalculator(database)
        self.payment_processor = PaymentProcessor(database)
    
    def init(self):
        logger.info("初始化收费管理模块")
        # 添加初始计费规则
        self._add_initial_fee_rules()
    
    def _add_initial_fee_rules(self):
        logger.info("添加初始计费规则")
        try:
            # 定义初始计费规则
            fee_rules = [
                # 小型车：首30分钟免费，每小时5元，每日最高50元
                ("小型车计费规则", "小型车", "hour", 5.0, 30, 50.0),
                # 大型车：首15分钟免费，每小时10元，每日最高100元
                ("大型车计费规则", "大型车", "hour", 10.0, 15, 100.0),
                # 新能源汽车：首60分钟免费，每小时3元，每日最高30元
                ("新能源汽车计费规则", "新能源汽车", "hour", 3.0, 60, 30.0)
            ]
            
            for rule_name, vehicle_type, time_unit, unit_price, free_duration, max_daily_fee in fee_rules:
                # 检查规则是否已存在
                existing = self.database.fetch_one(
                    "SELECT * FROM fee_rules WHERE rule_name = ?",
                    (rule_name,)
                )
                if not existing:
                    self.database.execute(
                        "INSERT INTO fee_rules (rule_name, vehicle_type, time_unit, unit_price, free_duration, max_daily_fee, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (rule_name, vehicle_type, time_unit, unit_price, free_duration, max_daily_fee, True)
                    )
            
            logger.info("初始计费规则添加完成")
        except Exception as e:
            logger.error(f"添加初始计费规则失败: {e}")
            raise
    
    def add_fee_rule(self, rule_name, vehicle_type, time_unit, unit_price, free_duration=0, max_daily_fee=None):
        logger.info(f"添加计费规则: {rule_name}, {vehicle_type}")
        try:
            # 检查规则是否已存在
            existing = self.database.fetch_one(
                "SELECT * FROM fee_rules WHERE rule_name = ?",
                (rule_name,)
            )
            if existing:
                raise ValueError(f"计费规则已存在: {rule_name}")
            
            # 插入规则记录
            rule_id = self.database.execute(
                "INSERT INTO fee_rules (rule_name, vehicle_type, time_unit, unit_price, free_duration, max_daily_fee, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (rule_name, vehicle_type, time_unit, unit_price, free_duration, max_daily_fee, True)
            )
            
            logger.info(f"计费规则添加成功: {rule_name}, ID: {rule_id}")
            return rule_id
        except Exception as e:
            logger.error(f"添加计费规则失败: {e}")
            raise
    
    def update_fee_rule(self, rule_id, **kwargs):
        logger.info(f"更新计费规则: {rule_id}, {kwargs}")
        try:
            # 构建更新语句
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key in ['rule_name', 'vehicle_type', 'time_unit', 'unit_price', 'free_duration', 'max_daily_fee', 'is_active']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            update_values.append(datetime.now())
            update_fields.append("updated_at = ?")
            update_values.append(rule_id)
            
            update_query = f"UPDATE fee_rules SET {', '.join(update_fields)} WHERE id = ?"
            
            self.database.execute(update_query, update_values)
            logger.info(f"计费规则更新成功: {rule_id}")
            return True
        except Exception as e:
            logger.error(f"更新计费规则失败: {e}")
            raise
    
    def delete_fee_rule(self, rule_id):
        logger.info(f"删除计费规则: {rule_id}")
        try:
            self.database.execute(
                "DELETE FROM fee_rules WHERE id = ?",
                (rule_id,)
            )
            logger.info(f"计费规则删除成功: {rule_id}")
            return True
        except Exception as e:
            logger.error(f"删除计费规则失败: {e}")
            raise
    
    def get_all_fee_rules(self, is_active=None):
        logger.info(f"获取所有计费规则, 状态: {is_active}")
        try:
            query = "SELECT * FROM fee_rules"
            params = []
            
            if is_active is not None:
                query += " WHERE is_active = ?"
                params.append(is_active)
            
            query += " ORDER BY updated_at DESC"
            
            results = self.database.fetch_all(query, params)
            
            rules = []
            for result in results:
                rule = FeeRule(
                    result['rule_name'],
                    result['vehicle_type'],
                    result['time_unit'],
                    result['unit_price'],
                    result['free_duration'],
                    result['max_daily_fee']
                )
                rule.id = result['id']
                rule.is_active = result['is_active']
                rule.created_at = result['created_at']
                rule.updated_at = result['updated_at']
                rules.append(rule)
            
            return rules
        except Exception as e:
            logger.error(f"获取所有计费规则失败: {e}")
            raise
    
    def get_fee_rule_by_id(self, rule_id):
        logger.info(f"根据ID获取计费规则: {rule_id}")
        try:
            result = self.database.fetch_one(
                "SELECT * FROM fee_rules WHERE id = ?",
                (rule_id,)
            )
            if result:
                rule = FeeRule(
                    result['rule_name'],
                    result['vehicle_type'],
                    result['time_unit'],
                    result['unit_price'],
                    result['free_duration'],
                    result['max_daily_fee']
                )
                rule.id = result['id']
                rule.is_active = result['is_active']
                rule.created_at = result['created_at']
                rule.updated_at = result['updated_at']
                return rule
            return None
        except Exception as e:
            logger.error(f"获取计费规则失败: {e}")
            raise
    
    def calculate_parking_fee(self, record_id, user_id=None):
        logger.info(f"计算停车记录费用: {record_id}, 用户ID {user_id}")
        try:
            # 获取停车记录
            record = self.database.fetch_one(
                "SELECT * FROM parking_records WHERE id = ?",
                (record_id,)
            )
            if not record:
                raise ValueError(f"停车记录不存在: {record_id}")
            
            if not record['duration']:
                # 如果没有时长记录，计算实际时长
                entry_time = datetime.strptime(record['entry_time'], '%Y-%m-%d %H:%M:%S')
                if record['exit_time']:
                    exit_time = datetime.strptime(record['exit_time'], '%Y-%m-%d %H:%M:%S')
                else:
                    exit_time = datetime.now()
                duration = int((exit_time - entry_time).total_seconds() / 60)
                
                # 更新停车记录时长
                self.database.execute(
                    "UPDATE parking_records SET duration = ? WHERE id = ?",
                    (duration, record_id)
                )
            else:
                duration = record['duration']
            
            # 计算费用
            fee = self.calculator.calculate_fee(record['vehicle_id'], duration, user_id)
            
            logger.info(f"停车记录费用计算完成: {fee}元")
            return fee
        except Exception as e:
            logger.error(f"计算停车记录费用失败: {e}")
            raise
    
    def process_exit_payment(self, plate_number, payment_method, user_id=None):
        logger.info(f"处理车辆出场支付: 车牌 {plate_number}, 支付方式 {payment_method}")
        try:
            # 获取车辆信息
            vehicle = self.database.fetch_one(
                "SELECT * FROM vehicles WHERE plate_number = ? AND status = ?",
                (plate_number, "parking")
            )
            if not vehicle:
                raise ValueError(f"车辆不在停车场内: {plate_number}")
            
            # 获取当前停车记录
            record = self.database.fetch_one(
                "SELECT * FROM parking_records WHERE vehicle_id = ? AND exit_time IS NULL",
                (vehicle['id'],)
            )
            if not record:
                raise ValueError(f"未找到有效停车记录: {plate_number}")
            
            # 计算费用
            fee = self.calculate_parking_fee(record['id'], user_id)
            
            # 处理支付
            payment_result = self.payment_processor.process_payment(
                record['id'], fee, payment_method, user_id
            )
            
            logger.info(f"车辆出场支付处理完成: 车牌 {plate_number}, 费用 {fee}元")
            return {
                "record_id": record['id'],
                "plate_number": plate_number,
                "fee": fee,
                **payment_result
            }
        except Exception as e:
            logger.error(f"处理车辆出场支付失败: {e}")
            raise
    
    def get_payment_history(self, user_id=None, start_date=None, end_date=None):
        logger.info(f"获取支付历史: 用户ID {user_id}, 开始日期 {start_date}, 结束日期 {end_date}")
        try:
            query = "SELECT p.*, pr.entry_time, pr.exit_time, v.plate_number FROM payments p "
            query += "JOIN parking_records pr ON p.record_id = pr.id "
            query += "JOIN vehicles v ON pr.vehicle_id = v.id "
            
            params = []
            conditions = []
            
            if user_id:
                # 获取用户的停车记录
                conditions.append("pr.user_id = ?")
                params.append(user_id)
            
            if start_date:
                conditions.append("p.payment_time >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("p.payment_time <= ?")
                params.append(end_date)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.payment_time DESC"
            
            results = self.database.fetch_all(query, params)
            
            payments = []
            for result in results:
                payments.append({
                    "payment_id": result['id'],
                    "record_id": result['record_id'],
                    "plate_number": result['plate_number'],
                    "amount": result['amount'],
                    "payment_method": result['payment_method'],
                    "transaction_id": result['transaction_id'],
                    "payment_time": result['payment_time'],
                    "status": result['status'],
                    "entry_time": result['entry_time'],
                    "exit_time": result['exit_time']
                })
            
            logger.info(f"获取支付历史完成: 共 {len(payments)} 条记录")
            return payments
        except Exception as e:
            logger.error(f"获取支付历史失败: {e}")
            raise
    
    def get_daily_fee_summary(self, date=None):
        logger.info(f"获取每日收费汇总: 日期 {date}")
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            # 统计当日总收入
            total_fee = self.database.fetch_one(
                "SELECT SUM(amount) as total FROM payments WHERE DATE(payment_time) = ? AND status = ?",
                (date, "success")
            )['total'] or 0.0
            
            # 统计各支付方式收入
            method_stats = self.database.fetch_all(
                "SELECT payment_method, COUNT(*) as count, SUM(amount) as total FROM payments WHERE DATE(payment_time) = ? AND status = ? GROUP BY payment_method",
                (date, "success")
            )
            
            # 统计车辆类型收入
            vehicle_type_stats = self.database.fetch_all(
                "SELECT v.vehicle_type, COUNT(*) as count, SUM(p.amount) as total FROM payments p "
                "JOIN parking_records pr ON p.record_id = pr.id "
                "JOIN vehicles v ON pr.vehicle_id = v.id "
                "WHERE DATE(p.payment_time) = ? AND p.status = ? GROUP BY v.vehicle_type",
                (date, "success")
            )
            
            logger.info(f"获取每日收费汇总完成: 日期 {date}, 总收入 {total_fee}元")
            return {
                "date": date,
                "total_fee": total_fee,
                "method_stats": [
                    {
                        "payment_method": row['payment_method'],
                        "count": row['count'],
                        "total": row['total']
                    }
                    for row in method_stats
                ],
                "vehicle_type_stats": [
                    {
                        "vehicle_type": row['vehicle_type'],
                        "count": row['count'],
                        "total": row['total']
                    }
                    for row in vehicle_type_stats
                ]
            }
        except Exception as e:
            logger.error(f"获取每日收费汇总失败: {e}")
            raise
    
    def export_payment_data(self, file_path, start_date=None, end_date=None):
        logger.info(f"导出支付数据到: {file_path}")
        try:
            import csv
            
            # 查询支付数据
            query = "SELECT p.*, pr.entry_time, pr.exit_time, v.plate_number FROM payments p "
            query += "JOIN parking_records pr ON p.record_id = pr.id "
            query += "JOIN vehicles v ON pr.vehicle_id = v.id "
            
            params = []
            conditions = []
            
            if start_date:
                conditions.append("p.payment_time >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("p.payment_time <= ?")
                params.append(end_date)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.payment_time DESC"
            
            results = self.database.fetch_all(query, params)
            
            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(['支付ID', '记录ID', '车牌号码', '金额', '支付方式', '交易ID', '支付时间', '状态', '入场时间', '出场时间'])
                
                # 写入数据
                for result in results:
                    writer.writerow([
                        result['id'],
                        result['record_id'],
                        result['plate_number'],
                        result['amount'],
                        result['payment_method'],
                        result['transaction_id'],
                        result['payment_time'],
                        result['status'],
                        result['entry_time'],
                        result['exit_time']
                    ])
            
            logger.info(f"支付数据导出成功: {file_path}, 共 {len(results)} 条记录")
            return len(results)
        except Exception as e:
            logger.error(f"导出支付数据失败: {e}")
            raise