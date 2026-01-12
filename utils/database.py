#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块

该模块负责智能停车场管理系统的数据库连接、表结构创建、以及基本的数据库操作封装。
使用SQLite作为数据库引擎，支持多线程访问，包含所有系统所需的表结构定义。
"""

import sqlite3
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    """
    数据库管理类
    
    该类封装了数据库连接、断开、表创建以及基本的CRUD操作，提供了线程安全的数据库访问。
    
    属性：
        db_path: 数据库文件路径，默认为'parking_system.db'
        conn: SQLite数据库连接对象
        cursor: 数据库游标对象
    """
    
    def __init__(self, db_path='parking_system.db'):
        """
        初始化数据库管理对象
        
        参数：
            db_path: 数据库文件路径，默认为'parking_system.db'
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """
        连接到数据库并创建表结构
        
        该方法执行以下操作：
        1. 建立SQLite数据库连接
        2. 设置row_factory为sqlite3.Row，方便结果集访问
        3. 创建所有系统所需的表结构
        
        异常：
            若连接失败或表创建失败，抛出异常并记录错误日志
        """
        logger.info(f"连接到数据库: {self.db_path}")
        try:
            # 建立数据库连接，允许多线程访问
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            # 设置结果集为字典格式，方便访问
            self.conn.row_factory = sqlite3.Row
            # 创建游标对象
            self.cursor = self.conn.cursor()
            # 创建所有表结构
            self._create_tables()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def disconnect(self):
        """
        关闭数据库连接
        
        该方法安全地关闭数据库连接，释放资源。
        """
        logger.info("关闭数据库连接")
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def _create_tables(self):
        """
        创建系统所需的所有表结构
        
        该方法创建以下表：
        1. vehicles - 车辆信息表
        2. parking_spaces - 车位信息表
        3. users - 用户信息表
        4. parking_transactions - 停车交易记录表
        5. fee_rules - 收费规则表
        6. system_configs - 系统配置表
        7. logs - 系统日志表
        """
        logger.info("创建数据库表")
        
        # 车辆信息表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT UNIQUE NOT NULL,
                vehicle_type TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                color TEXT,
                entry_time DATETIME,
                exit_time DATETIME,
                parking_space_id INTEGER,
                status TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parking_space_id) REFERENCES parking_spaces(id)
            )
        ''')
        
        # 车位信息表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_spaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                space_number TEXT UNIQUE NOT NULL,
                floor INTEGER NOT NULL,
                space_type TEXT NOT NULL,
                status TEXT NOT NULL,
                is_reserved BOOLEAN DEFAULT 0,
                reserved_user_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reserved_user_id) REFERENCES users(id)
            )
        ''')
        
        # 用户信息表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                status TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 停车交易记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                parking_space_id INTEGER NOT NULL,
                entry_time DATETIME NOT NULL,
                exit_time DATETIME,
                duration INTEGER,
                fee DECIMAL(10, 2),
                payment_status TEXT,
                payment_method TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY (parking_space_id) REFERENCES parking_spaces(id)
            )
        ''')
        
        # 收费规则表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fee_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_type TEXT NOT NULL,
                free_duration INTEGER DEFAULT 0,
                hourly_rate DECIMAL(10, 2) DEFAULT 0,
                daily_max DECIMAL(10, 2) DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 系统配置表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                config_type TEXT DEFAULT 'string',
                description TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 系统日志表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                user_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 提交事务
        self.conn.commit()
        logger.info("数据库表创建完成")
    
    def execute(self, query, params=None):
        """
        执行SQL查询
        
        参数：
            query: SQL查询语句
            params: 查询参数，可选
        
        返回：
            执行结果的游标对象
        
        异常：
            若执行失败，抛出异常并记录错误日志
        """
        try:
            if params:
                return self.cursor.execute(query, params)
            return self.cursor.execute(query)
        except Exception as e:
            logger.error(f"SQL执行失败: {query}, 参数: {params}, 错误: {e}")
            raise
    
    def fetchone(self, query, params=None):
        """
        执行SQL查询并返回第一条结果
        
        参数：
            query: SQL查询语句
            params: 查询参数，可选
        
        返回：
            查询结果的第一条记录，若没有结果则返回None
        """
        self.execute(query, params)
        return self.cursor.fetchone()
    
    def fetchall(self, query, params=None):
        """
        执行SQL查询并返回所有结果
        
        参数：
            query: SQL查询语句
            params: 查询参数，可选
        
        返回：
            查询结果的所有记录列表
        """
        self.execute(query, params)
        return self.cursor.fetchall()
    
    def commit(self):
        """
        提交事务
        
        该方法提交当前事务，将所有未提交的更改保存到数据库。
        """
        try:
            self.conn.commit()
            logger.debug("事务提交成功")
        except Exception as e:
            logger.error(f"事务提交失败: {e}")
            raise
    
    def rollback(self):
        """
        回滚事务
        
        该方法回滚当前事务，撤销所有未提交的更改。
        """
        try:
            self.conn.rollback()
            logger.debug("事务回滚成功")
        except Exception as e:
            logger.error(f"事务回滚失败: {e}")
            raise
    
    def insert(self, table, data):
        """
        插入数据到指定表
        
        参数：
            table: 表名
            data: 要插入的数据字典
        
        返回：
            插入记录的ID
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute(query, values)
        self.commit()
        return self.cursor.lastrowid
    
    def update(self, table, data, condition, params):
        """
        更新指定表的数据
        
        参数：
            table: 表名
            data: 要更新的数据字典
            condition: WHERE条件
            params: 条件参数
        
        返回：
            更新的行数
        """
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + params
        
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        cursor = self.execute(query, values)
        self.commit()
        return cursor.rowcount
    
    def delete(self, table, condition, params):
        """
        删除指定表的数据
        
        参数：
            table: 表名
            condition: WHERE条件
            params: 条件参数
        
        返回：
            删除的行数
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        cursor = self.execute(query, params)
        self.commit()
        return cursor.rowcount
    
    def select(self, table, columns='*', condition=None, params=None, order_by=None):
        """
        查询指定表的数据
        
        参数：
            table: 表名
            columns: 要查询的列，默认为'*'
            condition: WHERE条件，可选
            params: 条件参数，可选
            order_by: ORDER BY子句，可选
        
        返回：
            查询结果的所有记录列表
        """
        query = f"SELECT {columns} FROM {table}"
        
        if condition:
            query += f" WHERE {condition}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        return self.fetchall(query, params)
