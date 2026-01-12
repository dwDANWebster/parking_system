import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib

logger = logging.getLogger(__name__)

class User:
    def __init__(self, username, password, role):
        self.id = None
        self.username = username
        self.password = self._hash_password(password)
        self.role = role
        self.real_name = None
        self.phone = None
        self.email = None
        self.vehicle_plate = None
        self.is_member = False
        self.member_level = None
        self.member_expiry = None
        self.balance = 0.0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def _hash_password(self, password):
        # 使用SHA256哈希密码
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password):
        # 验证密码
        return self.password == self._hash_password(password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "real_name": self.real_name,
            "phone": self.phone,
            "email": self.email,
            "vehicle_plate": self.vehicle_plate,
            "is_member": self.is_member,
            "member_level": self.member_level,
            "member_expiry": self.member_expiry,
            "balance": self.balance,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class UserManager:
    def __init__(self, database):
        self.database = database
    
    def init(self):
        logger.info("初始化用户管理模块")
        # 添加初始管理员用户
        self._add_initial_admin()
        # 添加初始会员等级
        self._add_initial_member_levels()
    
    def _add_initial_admin(self):
        logger.info("添加初始管理员用户")
        try:
            # 检查管理员是否已存在
            existing = self.database.fetch_one(
                "SELECT * FROM users WHERE username = ?",
                ("admin",)
            )
            if not existing:
                # 创建管理员用户
                admin_password = hashlib.sha256("admin123".encode()).hexdigest()
                self.database.execute(
                    "INSERT INTO users (username, password, role, is_member, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    ("admin", admin_password, "admin", False, datetime.now(), datetime.now())
                )
                logger.info("初始管理员用户添加成功")
            else:
                logger.info("管理员用户已存在")
        except Exception as e:
            logger.error(f"添加初始管理员用户失败: {e}")
            raise
    
    def _add_initial_member_levels(self):
        logger.info("添加初始会员等级")
        try:
            # 定义初始会员等级
            member_levels = [
                ("普通会员", 0.9, 50.0, "享受9折优惠，每月50元"),
                ("银卡会员", 0.8, 100.0, "享受8折优惠，每月100元"),
                ("金卡会员", 0.7, 200.0, "享受7折优惠，每月200元"),
                ("钻石会员", 0.6, 300.0, "享受6折优惠，每月300元")
            ]
            
            for level_name, discount_rate, monthly_fee, benefits in member_levels:
                # 检查会员等级是否已存在
                existing = self.database.fetch_one(
                    "SELECT * FROM member_levels WHERE level_name = ?",
                    (level_name,)
                )
                if not existing:
                    self.database.execute(
                        "INSERT INTO member_levels (level_name, discount_rate, monthly_fee, benefits) VALUES (?, ?, ?, ?)",
                        (level_name, discount_rate, monthly_fee, benefits)
                    )
            
            logger.info("初始会员等级添加完成")
        except Exception as e:
            logger.error(f"添加初始会员等级失败: {e}")
            raise
    
    def register_user(self, username, password, role="user", real_name=None, phone=None, email=None):
        logger.info(f"注册用户: {username}, 角色: {role}")
        try:
            # 检查用户是否已存在
            existing = self.database.fetch_one(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            if existing:
                raise ValueError(f"用户已存在: {username}")
            
            # 哈希密码
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # 插入用户记录
            user_id = self.database.execute(
                "INSERT INTO users (username, password, role, real_name, phone, email, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (username, hashed_password, role, real_name, phone, email, datetime.now(), datetime.now())
            )
            
            logger.info(f"用户注册成功: {username}, ID: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            raise
    
    def login(self, username, password):
        logger.info(f"用户登录: {username}")
        try:
            # 获取用户信息
            result = self.database.fetch_one(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            if not result:
                raise ValueError(f"用户不存在: {username}")
            
            # 验证密码
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if result['password'] != hashed_password:
                raise ValueError("密码错误")
            
            logger.info(f"用户登录成功: {username}")
            return {
                "id": result['id'],
                "username": result['username'],
                "role": result['role'],
                "real_name": result['real_name'],
                "phone": result['phone'],
                "email": result['email'],
                "is_member": result['is_member'],
                "member_level": result['member_level'],
                "member_expiry": result['member_expiry']
            }
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            raise
    
    def get_user_by_username(self, username):
        logger.info(f"根据用户名获取用户: {username}")
        try:
            result = self.database.fetch_one(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            if result:
                user = User(result['username'], result['password'], result['role'])
                user.id = result['id']
                user.real_name = result['real_name']
                user.phone = result['phone']
                user.email = result['email']
                user.vehicle_plate = result['vehicle_plate']
                user.is_member = result['is_member']
                user.member_level = result['member_level']
                user.member_expiry = result['member_expiry']
                user.balance = result['balance']
                user.created_at = result['created_at']
                user.updated_at = result['updated_at']
                return user
            return None
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            raise
    
    def get_user_by_id(self, user_id):
        logger.info(f"根据ID获取用户: {user_id}")
        try:
            result = self.database.fetch_one(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            if result:
                user = User(result['username'], result['password'], result['role'])
                user.id = result['id']
                user.real_name = result['real_name']
                user.phone = result['phone']
                user.email = result['email']
                user.vehicle_plate = result['vehicle_plate']
                user.is_member = result['is_member']
                user.member_level = result['member_level']
                user.member_expiry = result['member_expiry']
                user.balance = result['balance']
                user.created_at = result['created_at']
                user.updated_at = result['updated_at']
                return user
            return None
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            raise
    
    def update_user(self, user_id, **kwargs):
        logger.info(f"更新用户信息: {user_id}, {kwargs}")
        try:
            # 构建更新语句
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key == "password":
                    # 哈希密码
                    value = hashlib.sha256(value.encode()).hexdigest()
                if key in ['username', 'password', 'role', 'real_name', 'phone', 'email', 'vehicle_plate', 'is_member', 'member_level', 'member_expiry', 'balance']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            update_values.append(datetime.now())
            update_fields.append("updated_at = ?")
            update_values.append(user_id)
            
            update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            
            self.database.execute(update_query, update_values)
            logger.info(f"用户信息更新成功: {user_id}")
            return True
        except Exception as e:
            logger.error(f"更新用户信息失败: {e}")
            raise
    
    def delete_user(self, user_id):
        logger.info(f"删除用户: {user_id}")
        try:
            self.database.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            logger.info(f"用户删除成功: {user_id}")
            return True
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            raise
    
    def change_password(self, user_id, old_password, new_password):
        logger.info(f"修改用户密码: {user_id}")
        try:
            # 获取用户信息
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            # 验证旧密码
            hashed_old = hashlib.sha256(old_password.encode()).hexdigest()
            if user.password != hashed_old:
                raise ValueError("旧密码错误")
            
            # 更新密码
            hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
            self.database.execute(
                "UPDATE users SET password = ?, updated_at = ? WHERE id = ?",
                (hashed_new, datetime.now(), user_id)
            )
            
            logger.info(f"用户密码修改成功: {user_id}")
            return True
        except Exception as e:
            logger.error(f"修改用户密码失败: {e}")
            raise
    
    def add_member(self, user_id, member_level, duration=1):
        logger.info(f"添加会员: {user_id}, 等级: {member_level}, 时长: {duration}个月")
        try:
            # 获取会员等级信息
            level_info = self.database.fetch_one(
                "SELECT * FROM member_levels WHERE level_name = ?",
                (member_level,)
            )
            if not level_info:
                raise ValueError(f"会员等级不存在: {member_level}")
            
            # 计算到期时间
            now = datetime.now()
            expiry = now + timedelta(days=30*duration)
            
            # 更新用户信息
            self.database.execute(
                "UPDATE users SET is_member = ?, member_level = ?, member_expiry = ?, updated_at = ? WHERE id = ?",
                (True, member_level, expiry, datetime.now(), user_id)
            )
            
            logger.info(f"会员添加成功: {user_id}, 到期时间: {expiry}")
            return True
        except Exception as e:
            logger.error(f"添加会员失败: {e}")
            raise
    
    def renew_member(self, user_id, duration=1):
        logger.info(f"续费会员: {user_id}, 时长: {duration}个月")
        try:
            # 获取用户信息
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            if not user.is_member:
                raise ValueError("用户不是会员")
            
            # 计算新的到期时间
            now = datetime.now()
            if user.member_expiry and user.member_expiry > now:
                expiry = user.member_expiry + timedelta(days=30*duration)
            else:
                expiry = now + timedelta(days=30*duration)
            
            # 更新用户信息
            self.database.execute(
                "UPDATE users SET member_expiry = ?, updated_at = ? WHERE id = ?",
                (expiry, datetime.now(), user_id)
            )
            
            logger.info(f"会员续费成功: {user_id}, 新到期时间: {expiry}")
            return True
        except Exception as e:
            logger.error(f"续费会员失败: {e}")
            raise
    
    def cancel_member(self, user_id):
        logger.info(f"取消会员: {user_id}")
        try:
            # 更新用户信息
            self.database.execute(
                "UPDATE users SET is_member = ?, member_level = NULL, member_expiry = NULL, updated_at = ? WHERE id = ?",
                (False, datetime.now(), user_id)
            )
            
            logger.info(f"会员取消成功: {user_id}")
            return True
        except Exception as e:
            logger.error(f"取消会员失败: {e}")
            raise
    
    def recharge_balance(self, user_id, amount):
        logger.info(f"充值余额: {user_id}, 金额: {amount}")
        try:
            if amount <= 0:
                raise ValueError("充值金额必须大于0")
            
            # 更新用户余额
            self.database.execute(
                "UPDATE users SET balance = balance + ?, updated_at = ? WHERE id = ?",
                (amount, datetime.now(), user_id)
            )
            
            logger.info(f"余额充值成功: {user_id}, 充值金额: {amount}")
            return True
        except Exception as e:
            logger.error(f"余额充值失败: {e}")
            raise
    
    def deduct_balance(self, user_id, amount):
        logger.info(f"扣除余额: {user_id}, 金额: {amount}")
        try:
            if amount <= 0:
                raise ValueError("扣除金额必须大于0")
            
            # 获取用户余额
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            if user.balance < amount:
                raise ValueError("余额不足")
            
            # 更新用户余额
            self.database.execute(
                "UPDATE users SET balance = balance - ?, updated_at = ? WHERE id = ?",
                (amount, datetime.now(), user_id)
            )
            
            logger.info(f"余额扣除成功: {user_id}, 扣除金额: {amount}")
            return True
        except Exception as e:
            logger.error(f"余额扣除失败: {e}")
            raise
    
    def get_all_users(self, role=None, is_member=None):
        logger.info(f"获取所有用户, 角色: {role}, 会员: {is_member}")
        try:
            query = "SELECT * FROM users"
            params = []
            conditions = []
            
            if role:
                conditions.append("role = ?")
                params.append(role)
            
            if is_member is not None:
                conditions.append("is_member = ?")
                params.append(is_member)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY updated_at DESC"
            
            results = self.database.fetch_all(query, params)
            
            users = []
            for result in results:
                user = User(result['username'], result['password'], result['role'])
                user.id = result['id']
                user.real_name = result['real_name']
                user.phone = result['phone']
                user.email = result['email']
                user.vehicle_plate = result['vehicle_plate']
                user.is_member = result['is_member']
                user.member_level = result['member_level']
                user.member_expiry = result['member_expiry']
                user.balance = result['balance']
                user.created_at = result['created_at']
                user.updated_at = result['updated_at']
                users.append(user)
            
            return users
        except Exception as e:
            logger.error(f"获取所有用户失败: {e}")
            raise
    
    def get_users_by_role(self, role):
        logger.info(f"根据角色获取用户: {role}")
        return self.get_all_users(role=role)
    
    def get_members(self):
        logger.info("获取所有会员")
        return self.get_all_users(is_member=True)
    
    def get_expiring_members(self, days=30):
        logger.info(f"获取即将到期的会员: {days}天内")
        try:
            # 计算到期时间范围
            now = datetime.now()
            expiry_date = now + timedelta(days=days)
            
            query = "SELECT * FROM users WHERE is_member = ? AND member_expiry BETWEEN ? AND ? ORDER BY member_expiry ASC"
            results = self.database.fetch_all(query, (True, now, expiry_date))
            
            users = []
            for result in results:
                user = User(result['username'], result['password'], result['role'])
                user.id = result['id']
                user.real_name = result['real_name']
                user.phone = result['phone']
                user.email = result['email']
                user.vehicle_plate = result['vehicle_plate']
                user.is_member = result['is_member']
                user.member_level = result['member_level']
                user.member_expiry = result['member_expiry']
                user.balance = result['balance']
                user.created_at = result['created_at']
                user.updated_at = result['updated_at']
                users.append(user)
            
            logger.info(f"获取到 {len(users)} 个即将到期的会员")
            return users
        except Exception as e:
            logger.error(f"获取即将到期的会员失败: {e}")
            raise
    
    def get_member_levels(self):
        logger.info("获取所有会员等级")
        try:
            results = self.database.fetch_all(
                "SELECT * FROM member_levels ORDER BY monthly_fee ASC"
            )
            
            levels = []
            for result in results:
                levels.append({
                    "id": result['id'],
                    "level_name": result['level_name'],
                    "discount_rate": result['discount_rate'],
                    "monthly_fee": result['monthly_fee'],
                    "benefits": result['benefits'],
                    "created_at": result['created_at'],
                    "updated_at": result['updated_at']
                })
            
            return levels
        except Exception as e:
            logger.error(f"获取会员等级失败: {e}")
            raise
    
    def add_member_level(self, level_name, discount_rate, monthly_fee, benefits):
        logger.info(f"添加会员等级: {level_name}")
        try:
            # 检查会员等级是否已存在
            existing = self.database.fetch_one(
                "SELECT * FROM member_levels WHERE level_name = ?",
                (level_name,)
            )
            if existing:
                raise ValueError(f"会员等级已存在: {level_name}")
            
            # 插入会员等级记录
            level_id = self.database.execute(
                "INSERT INTO member_levels (level_name, discount_rate, monthly_fee, benefits) VALUES (?, ?, ?, ?)",
                (level_name, discount_rate, monthly_fee, benefits)
            )
            
            logger.info(f"会员等级添加成功: {level_name}, ID: {level_id}")
            return level_id
        except Exception as e:
            logger.error(f"添加会员等级失败: {e}")
            raise
    
    def update_member_level(self, level_id, **kwargs):
        logger.info(f"更新会员等级: {level_id}, {kwargs}")
        try:
            # 构建更新语句
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key in ['level_name', 'discount_rate', 'monthly_fee', 'benefits']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            update_values.append(datetime.now())
            update_fields.append("updated_at = ?")
            update_values.append(level_id)
            
            update_query = f"UPDATE member_levels SET {', '.join(update_fields)} WHERE id = ?"
            
            self.database.execute(update_query, update_values)
            logger.info(f"会员等级更新成功: {level_id}")
            return True
        except Exception as e:
            logger.error(f"更新会员等级失败: {e}")
            raise
    
    def delete_member_level(self, level_id):
        logger.info(f"删除会员等级: {level_id}")
        try:
            self.database.execute(
                "DELETE FROM member_levels WHERE id = ?",
                (level_id,)
            )
            logger.info(f"会员等级删除成功: {level_id}")
            return True
        except Exception as e:
            logger.error(f"删除会员等级失败: {e}")
            raise
    
    def export_user_data(self, file_path, include_password=False):
        logger.info(f"导出用户数据到: {file_path}")
        try:
            import csv
            
            # 查询用户数据
            results = self.database.fetch_all("SELECT * FROM users ORDER BY updated_at DESC")
            
            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入表头
                if include_password:
                    writer.writerow(['ID', '用户名', '密码', '角色', '真实姓名', '电话', '邮箱', '车牌号码', '是否会员', '会员等级', '会员到期时间', '余额', '创建时间', '更新时间'])
                else:
                    writer.writerow(['ID', '用户名', '角色', '真实姓名', '电话', '邮箱', '车牌号码', '是否会员', '会员等级', '会员到期时间', '余额', '创建时间', '更新时间'])
                
                # 写入数据
                for result in results:
                    row = [
                        result['id'],
                        result['username'],
                    ]
                    
                    if include_password:
                        row.append(result['password'])
                    
                    row.extend([
                        result['role'],
                        result['real_name'],
                        result['phone'],
                        result['email'],
                        result['vehicle_plate'],
                        '是' if result['is_member'] else '否',
                        result['member_level'],
                        result['member_expiry'],
                        result['balance'],
                        result['created_at'],
                        result['updated_at']
                    ])
                    
                    writer.writerow(row)
            
            logger.info(f"用户数据导出成功: {file_path}, 共 {len(results)} 条记录")
            return len(results)
        except Exception as e:
            logger.error(f"导出用户数据失败: {e}")
            raise