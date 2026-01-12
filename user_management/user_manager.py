#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块

该模块负责智能停车场的用户管理，包括用户信息维护、权限管理、密码加密等功能。
实现了基于SHA256的密码加密，支持多种用户角色和权限控制。
"""

import logging
import hashlib
import random
import string
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class User:
    """
    用户信息类
    
    该类封装了用户的基本信息，包括用户名、密码、姓名、角色、联系方式等属性。
    
    属性：
        id: 用户ID，数据库自动生成
        username: 用户名，唯一标识
        password_hash: 密码哈希值，使用SHA256加密
        name: 用户姓名
        role: 用户角色，如'admin'（管理员）、'operator'（操作员）、'user'（普通用户）等
        phone: 手机号码
        email: 电子邮箱
        status: 用户状态，如'active'（活跃）、'inactive'（非活跃）、'locked'（锁定）等
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    def __init__(self, username, password_hash, name, role, phone=None, email=None, status='active'):
        """
        初始化用户对象
        
        参数：
            username: 用户名
            password_hash: 密码哈希值
            name: 用户姓名
            role: 用户角色
            phone: 手机号码，可选
            email: 电子邮箱，可选
            status: 用户状态，默认为'active'
        """
        self.id = None
        self.username = username
        self.password_hash = password_hash
        self.name = name
        self.role = role
        self.phone = phone
        self.email = email
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """
        将用户对象转换为字典格式
        
        返回：
            包含用户所有属性的字典
        """
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "name": self.name,
            "role": self.role,
            "phone": self.phone,
            "email": self.email,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class PasswordManager:
    """
    密码管理类
    
    该类负责密码的加密、验证和生成，使用SHA256算法进行密码哈希。
    """
    
    @staticmethod
    def hash_password(password, salt=None):
        """
        对密码进行哈希处理
        
        该方法使用SHA256算法对密码进行哈希处理，可选添加盐值。
        
        参数：
            password: 原始密码
            salt: 盐值，可选，若不提供则自动生成
        
        返回：
            包含盐值和哈希密码的字典
        """
        if not salt:
            # 生成随机盐值
            salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        # 组合密码和盐值
        salted_password = password + salt
        
        # 使用SHA256算法进行哈希处理
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
        
        return {
            "salt": salt,
            "password_hash": hashed_password
        }
    
    @staticmethod
    def verify_password(password, salt, password_hash):
        """
        验证密码是否正确
        
        该方法使用提供的密码和盐值，生成哈希值并与存储的哈希密码进行比较。
        
        参数：
            password: 待验证的密码
            salt: 盐值
            password_hash: 存储的哈希密码
        
        返回：
            布尔值，表示密码验证是否成功
        """
        # 使用相同的盐值对密码进行哈希处理
        salted_password = password + salt
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
        
        # 比较生成的哈希值与存储的哈希值
        return hashed_password == password_hash
    
    @staticmethod
    def generate_random_password(length=8):
        """
        生成随机密码
        
        该方法生成指定长度的随机密码，包含大小写字母、数字和特殊字符。
        
        参数：
            length: 密码长度，默认为8
        
        返回：
            生成的随机密码
        """
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choices(characters, k=length))


class UserManager:
    """
    用户管理器类
    
    该类封装了用户管理的核心功能，包括用户的添加、删除、查询、登录验证等操作。
    
    属性：
        database: 数据库连接对象
        password_manager: 密码管理对象
    """
    
    def __init__(self, database):
        """
        初始化用户管理器对象
        
        参数：
            database: 数据库连接对象
        """
        self.database = database
        self.password_manager = PasswordManager()
    
    def init(self):
        """
        初始化用户管理器
        
        该方法执行以下操作：
        1. 检查是否需要初始化用户数据
        2. 如果没有用户数据，则创建初始管理员用户
        """
        logger.info("初始化用户管理器")
        try:
            # 检查是否已有用户数据
            user_count = self.database.fetchone("SELECT COUNT(*) as count FROM users")["count"]
            
            # 如果没有用户数据，则创建初始管理员用户
            if user_count == 0:
                logger.info("没有用户数据，创建初始管理员用户")
                self._create_initial_users()
        except Exception as e:
            logger.error(f"用户管理器初始化失败: {e}")
            raise
    
    def _create_initial_users(self):
        """
        创建初始用户数据
        
        该方法创建初始管理员用户，用于系统首次登录。
        """
        # 生成管理员密码哈希
        admin_password = "admin123"
        password_hash = self.password_manager.hash_password(admin_password)
        
        initial_users = [
            {
                "username": "admin",
                "password_hash": password_hash["password_hash"],
                "name": "系统管理员",
                "role": "admin",
                "phone": "13800138000",
                "email": "admin@example.com",
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "username": "operator",
                "password_hash": password_hash["password_hash"],
                "name": "操作员",
                "role": "operator",
                "phone": "13900139000",
                "email": "operator@example.com",
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        # 插入初始用户数据
        for user in initial_users:
            self.database.insert("users", user)
        
        logger.info(f"成功创建{len(initial_users)}个初始用户")
        logger.info(f"初始管理员用户名: admin, 密码: {admin_password}")
    
    def add_user(self, username, password, name, role, phone=None, email=None):
        """
        添加新用户
        
        参数：
            username: 用户名
            password: 原始密码
            name: 用户姓名
            role: 用户角色
            phone: 手机号码，可选
            email: 电子邮箱，可选
        
        返回：
            新添加的用户ID
        """
        logger.info(f"添加新用户: {username}, 角色: {role}")
        try:
            # 检查用户名是否已存在
            existing_user = self.database.fetchone(
                "SELECT * FROM users WHERE username = ?",
                [username]
            )
            
            if existing_user:
                logger.warning(f"用户名已存在: {username}")
                return None
            
            # 对密码进行哈希处理
            password_hash = self.password_manager.hash_password(password)
            
            # 创建新用户
            new_user = {
                "username": username,
                "password_hash": password_hash["password_hash"],
                "name": name,
                "role": role,
                "phone": phone,
                "email": email,
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 插入新用户数据
            user_id = self.database.insert("users", new_user)
            logger.info(f"成功添加新用户: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"添加用户失败: {e}")
            return None
    
    def delete_user(self, user_id):
        """
        删除用户
        
        参数：
            user_id: 要删除的用户ID
        
        返回：
            布尔值，表示删除是否成功
        """
        logger.info(f"删除用户: {user_id}")
        try:
            # 检查用户是否存在
            existing_user = self.database.fetchone(
                "SELECT * FROM users WHERE id = ?",
                [user_id]
            )
            
            if not existing_user:
                logger.warning(f"用户不存在: {user_id}")
                return False
            
            # 不允许删除管理员用户
            if existing_user["role"] == "admin":
                logger.warning(f"不允许删除管理员用户: {user_id}")
                return False
            
            # 删除用户
            rows_affected = self.database.delete("users", "id = ?", [user_id])
            
            if rows_affected > 0:
                logger.info(f"成功删除用户: {user_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False
    
    def get_user(self, user_id):
        """
        获取用户信息
        
        参数：
            user_id: 用户ID
        
        返回：
            用户信息字典，若用户不存在则返回None
        """
        try:
            user = self.database.fetchone(
                "SELECT * FROM users WHERE id = ?",
                [user_id]
            )
            
            if user:
                return dict(user)
            return None
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def get_user_by_username(self, username):
        """
        根据用户名获取用户信息
        
        参数：
            username: 用户名
        
        返回：
            用户信息字典，若用户不存在则返回None
        """
        try:
            user = self.database.fetchone(
                "SELECT * FROM users WHERE username = ?",
                [username]
            )
            
            if user:
                return dict(user)
            return None
        except Exception as e:
            logger.error(f"根据用户名获取用户信息失败: {e}")
            return None
    
    def get_all_users(self):
        """
        获取所有用户信息
        
        返回：
            所有用户信息的列表
        """
        try:
            users = self.database.fetchall("SELECT * FROM users ORDER BY created_at DESC")
            return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"获取所有用户信息失败: {e}")
            return []
    
    def authenticate_user(self, username, password):
        """
        验证用户身份
        
        该方法验证用户名和密码是否正确。
        
        参数：
            username: 用户名
            password: 密码
        
        返回：
            包含用户ID和角色的字典，若验证失败则返回None
        """
        logger.info(f"验证用户身份: {username}")
        try:
            # 获取用户信息
            user = self.get_user_by_username(username)
            
            if not user:
                logger.warning(f"用户不存在: {username}")
                return None
            
            if user["status"] != "active":
                logger.warning(f"用户状态异常: {username}, 状态: {user['status']}")
                return None
            
            # 验证密码
            # 注意：这里使用了固定盐值，实际项目中应该将盐值存储在数据库中
            is_valid = self.password_manager.verify_password(password, "", user["password_hash"])
            
            if is_valid:
                logger.info(f"用户身份验证成功: {username}")
                return {
                    "user_id": user["id"],
                    "role": user["role"]
                }
            
            logger.warning(f"密码验证失败: {username}")
            return None
        except Exception as e:
            logger.error(f"用户身份验证失败: {e}")
            return None
    
    def update_user_info(self, user_id, update_data):
        """
        更新用户信息
        
        参数：
            user_id: 用户ID
            update_data: 要更新的用户信息字典
        
        返回：
            布尔值，表示更新是否成功
        """
        logger.info(f"更新用户信息: {user_id}, 数据: {update_data}")
        try:
            # 检查用户是否存在
            existing_user = self.get_user(user_id)
            if not existing_user:
                logger.warning(f"用户不存在: {user_id}")
                return False
            
            # 如果更新数据中包含密码，则对密码进行哈希处理
            if "password" in update_data:
                password = update_data.pop("password")
                password_hash = self.password_manager.hash_password(password)
                update_data["password_hash"] = password_hash["password_hash"]
            
            # 更新用户信息
            update_data["updated_at"] = datetime.now()
            rows_affected = self.database.update(
                "users",
                update_data,
                "id = ?",
                [user_id]
            )
            
            if rows_affected > 0:
                logger.info(f"成功更新用户信息: {user_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"更新用户信息失败: {e}")
            return False
    
    def change_user_status(self, user_id, status):
        """
        更改用户状态
        
        参数：
            user_id: 用户ID
            status: 新的用户状态，可选值包括：
                - 'active'（活跃）
                - 'inactive'（非活跃）
                - 'locked'（锁定）
        
        返回：
            布尔值，表示状态更改是否成功
        """
        logger.info(f"更改用户状态: {user_id}, 新状态: {status}")
        try:
            # 检查状态值是否有效
            valid_statuses = ['active', 'inactive', 'locked']
            if status not in valid_statuses:
                logger.warning(f"无效的用户状态: {status}")
                return False
            
            # 不允许锁定管理员用户
            user = self.get_user(user_id)
            if user and user["role"] == "admin" and status == "locked":
                logger.warning(f"不允许锁定管理员用户: {user_id}")
                return False
            
            # 更新用户状态
            rows_affected = self.database.update(
                "users",
                {"status": status, "updated_at": datetime.now()},
                "id = ?",
                [user_id]
            )
            
            if rows_affected > 0:
                logger.info(f"成功更改用户状态: {user_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"更改用户状态失败: {e}")
            return False
    
    def get_user_statistics(self):
        """
        获取用户统计信息
        
        返回：
            包含用户统计信息的字典，包括：
                - total: 总用户数
                - active: 活跃用户数
                - inactive: 非活跃用户数
                - locked: 锁定用户数
                - by_role: 按角色统计的用户数
        """
        try:
            # 获取总用户数
            total = self.database.fetchone("SELECT COUNT(*) as count FROM users")["count"]
            
            # 获取活跃用户数
            active = self.database.fetchone(
                "SELECT COUNT(*) as count FROM users WHERE status = 'active'"
            )["count"]
            
            # 获取非活跃用户数
            inactive = self.database.fetchone(
                "SELECT COUNT(*) as count FROM users WHERE status = 'inactive'"
            )["count"]
            
            # 获取锁定用户数
            locked = self.database.fetchone(
                "SELECT COUNT(*) as count FROM users WHERE status = 'locked'"
            )["count"]
            
            # 获取按角色统计的用户数
            by_role = {}
            role_stats = self.database.fetchall(
                "SELECT role, COUNT(*) as count FROM users GROUP BY role"
            )
            
            for stat in role_stats:
                by_role[stat["role"]] = stat["count"]
            
            return {
                "total": total,
                "active": active,
                "inactive": inactive,
                "locked": locked,
                "by_role": by_role
            }
        except Exception as e:
            logger.error(f"获取用户统计信息失败: {e}")
            return None
