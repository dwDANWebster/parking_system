import sqlite3
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='parking_system.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        logger.info(f"连接到数据库: {self.db_path}")
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self._create_tables()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def disconnect(self):
        logger.info("关闭数据库连接")
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def _create_tables(self):
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
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                is_reserved BOOLEAN DEFAULT FALSE,
                reserved_user_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 用户信息表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                real_name TEXT,
                phone TEXT,
                email TEXT,
                vehicle_plate TEXT,
                is_member BOOLEAN DEFAULT FALSE,
                member_level TEXT,
                member_expiry DATETIME,
                balance REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 停车记录表示
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                user_id INTEGER,
                parking_space_id INTEGER NOT NULL,
                entry_time DATETIME NOT NULL,
                exit_time DATETIME,
                duration INTEGER,
                fee REAL,
                payment_status TEXT,
                payment_method TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (parking_space_id) REFERENCES parking_spaces(id)
            )
        ''')
        
        # 收费规则表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fee_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                time_unit TEXT NOT NULL,
                unit_price REAL NOT NULL,
                free_duration INTEGER DEFAULT 0,
                max_daily_fee REAL,
                is_active BOOLEAN DEFAULT TRUE,
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
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 日志记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                log_level TEXT NOT NULL,
                module TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # 会员等级表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_name TEXT UNIQUE NOT NULL,
                discount_rate REAL NOT NULL,
                monthly_fee REAL NOT NULL,
                benefits TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 车位预订表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                parking_space_id INTEGER NOT NULL,
                vehicle_plate TEXT NOT NULL,
                reservation_time DATETIME NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                status TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (parking_space_id) REFERENCES parking_spaces(id)
            )
        ''')
        
        # 支付记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                transaction_id TEXT UNIQUE,
                payment_time DATETIME,
                status TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (record_id) REFERENCES parking_records(id)
            )
        ''')
        
        # 设备信息表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                ip_address TEXT,
                port INTEGER,
                status TEXT NOT NULL,
                last_online DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 报表统计表示
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_date DATE NOT NULL,
                total_vehicles INTEGER,
                total_entries INTEGER,
                total_exits INTEGER,
                total_fee REAL,
                occupancy_rate REAL,
                avg_stay_time INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        logger.info("数据库表创建完成")
    
    def execute(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"SQL执行失败: {query} - {params} - {e}")
            self.conn.rollback()
            raise
    
    def fetch_all(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"查询失败: {query} - {params} - {e}")
            raise
    
    def fetch_one(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(f"查询失败: {query} - {params} - {e}")
            raise
    
    def get_connection(self):
        return self.conn
    
    def get_cursor(self):
        return self.cursor