import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ParkingSpace:
    def __init__(self, space_number, floor, space_type):
        self.id = None
        self.space_number = space_number
        self.floor = floor
        self.space_type = space_type
        self.status = "available"
        self.is_reserved = False
        self.reserved_user_id = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
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
    def __init__(self, database):
        self.database = database
    
    def allocate_space(self, vehicle_type, preferred_floor=None):
        logger.info(f"分配车位: {vehicle_type}, 偏好楼层: {preferred_floor}")
        try:
            # 构建查询条件
            query = "SELECT * FROM parking_spaces WHERE status = 'available' AND space_type = ?"
            params = [vehicle_type]
            
            if preferred_floor is not None:
                query += " AND floor = ?"
                params.append(preferred_floor)
            
            # 按楼层和车位号排序
            query += " ORDER BY floor ASC, space_number ASC"
            
            # 获取可用车位
            result = self.database.fetch_one(query, params)
            
            if result:
                logger.info(f"分配到车位: {result['space_number']}, 楼层: {result['floor']}")
                return result['id']
            
            # 如果没有偏好楼层的车位，尝试其他楼层
            if preferred_floor is not None:
                logger.info(f"偏好楼层 {preferred_floor} 没有可用车位，尝试其他楼层")
                query = "SELECT * FROM parking_spaces WHERE status = 'available' AND space_type = ? ORDER BY floor ASC, space_number ASC"
                result = self.database.fetch_one(query, [vehicle_type])
                if result:
                    logger.info(f"分配到车位: {result['space_number']}, 楼层: {result['floor']}")
                    return result['id']
            
            # 如果没有对应类型的车位，尝试普通车位（小型车）
            if vehicle_type != "小型车":
                logger.info(f"没有 {vehicle_type} 类型的可用车位，尝试小型车车位")
                query = "SELECT * FROM parking_spaces WHERE status = 'available' AND space_type = '小型车' ORDER BY floor ASC, space_number ASC"
                result = self.database.fetch_one(query)
                if result:
                    logger.info(f"分配到小型车车位: {result['space_number']}, 楼层: {result['floor']}")
                    return result['id']
            
            logger.warning(f"没有可用车位: {vehicle_type}")
            return None
        except Exception as e:
            logger.error(f"车位分配失败: {e}")
            raise
    
    def get_nearest_available_spaces(self, entrance_floor, count=10):
        logger.info(f"获取离入口最近的可用车位: 入口楼层 {entrance_floor}, 数量 {count}")
        try:
            # 按楼层距离排序，获取最近的可用车位
            query = '''
                SELECT *, ABS(floor - ?) as distance 
                FROM parking_spaces 
                WHERE status = 'available' 
                ORDER BY distance ASC, space_number ASC 
                LIMIT ?
            '''
            results = self.database.fetch_all(query, (entrance_floor, count))
            
            spaces = []
            for result in results:
                space = ParkingSpace(
                    result['space_number'],
                    result['floor'],
                    result['space_type']
                )
                space.id = result['id']
                space.status = result['status']
                space.is_reserved = result['is_reserved']
                space.reserved_user_id = result['reserved_user_id']
                space.created_at = result['created_at']
                space.updated_at = result['updated_at']
                spaces.append(space)
            
            logger.info(f"找到 {len(spaces)} 个最近的可用车位")
            return spaces
        except Exception as e:
            logger.error(f"获取最近可用车位失败: {e}")
            raise

class SpaceManager:
    def __init__(self, database):
        self.database = database
        self.allocation_algorithm = SpaceAllocationAlgorithm(database)
    
    def init(self):
        logger.info("初始化车位管理模块")
        # 添加一些初始车位
        self._add_initial_spaces()
    
    def _add_initial_spaces(self):
        logger.info("添加初始车位")
        # 添加100个初始车位，分布在5个楼层
        try:
            for floor in range(1, 6):
                for i in range(1, 21):
                    space_number = f"{floor:02d}{i:03d}"
                    # 每楼层前5个为大型车车位，其余为小型车车位
                    space_type = "大型车" if i <= 5 else "小型车"
                    
                    # 检查车位是否已存在
                    existing = self.database.fetch_one(
                        "SELECT * FROM parking_spaces WHERE space_number = ?",
                        (space_number,)
                    )
                    if not existing:
                        self.database.execute(
                            "INSERT INTO parking_spaces (space_number, floor, space_type, status) VALUES (?, ?, ?, ?)",
                            (space_number, floor, space_type, "available")
                        )
            
            logger.info("初始车位添加完成")
        except Exception as e:
            logger.error(f"添加初始车位失败: {e}")
            raise
    
    def add_space(self, space_number, floor, space_type):
        logger.info(f"添加车位: {space_number}, 楼层: {floor}, 类型: {space_type}")
        try:
            # 检查车位是否已存在
            existing = self.database.fetch_one(
                "SELECT * FROM parking_spaces WHERE space_number = ?",
                (space_number,)
            )
            if existing:
                raise ValueError(f"车位已存在: {space_number}")
            
            # 插入车位记录
            space_id = self.database.execute(
                "INSERT INTO parking_spaces (space_number, floor, space_type, status) VALUES (?, ?, ?, ?)",
                (space_number, floor, space_type, "available")
            )
            
            logger.info(f"车位添加成功: {space_number}, ID: {space_id}")
            return space_id
        except Exception as e:
            logger.error(f"添加车位失败: {e}")
            raise
    
    def get_space_by_number(self, space_number):
        logger.info(f"根据车位号获取车位: {space_number}")
        try:
            result = self.database.fetch_one(
                "SELECT * FROM parking_spaces WHERE space_number = ?",
                (space_number,)
            )
            if result:
                space = ParkingSpace(
                    result['space_number'],
                    result['floor'],
                    result['space_type']
                )
                space.id = result['id']
                space.status = result['status']
                space.is_reserved = result['is_reserved']
                space.reserved_user_id = result['reserved_user_id']
                space.created_at = result['created_at']
                space.updated_at = result['updated_at']
                return space
            return None
        except Exception as e:
            logger.error(f"获取车位失败: {e}")
            raise
    
    def get_space_by_id(self, space_id):
        logger.info(f"根据ID获取车位: {space_id}")
        try:
            result = self.database.fetch_one(
                "SELECT * FROM parking_spaces WHERE id = ?",
                (space_id,)
            )
            if result:
                space = ParkingSpace(
                    result['space_number'],
                    result['floor'],
                    result['space_type']
                )
                space.id = result['id']
                space.status = result['status']
                space.is_reserved = result['is_reserved']
                space.reserved_user_id = result['reserved_user_id']
                space.created_at = result['created_at']
                space.updated_at = result['updated_at']
                return space
            return None
        except Exception as e:
            logger.error(f"获取车位失败: {e}")
            raise
    
    def update_space(self, space_id, **kwargs):
        logger.info(f"更新车位信息: {space_id}, {kwargs}")
        try:
            # 构建更新语句
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key in ['space_number', 'floor', 'space_type', 'status', 'is_reserved', 'reserved_user_id']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            update_values.append(datetime.now())
            update_fields.append("updated_at = ?")
            update_values.append(space_id)
            
            update_query = f"UPDATE parking_spaces SET {', '.join(update_fields)} WHERE id = ?"
            
            self.database.execute(update_query, update_values)
            logger.info(f"车位信息更新成功: {space_id}")
            return True
        except Exception as e:
            logger.error(f"更新车位信息失败: {e}")
            raise
    
    def delete_space(self, space_id):
        logger.info(f"删除车位: {space_id}")
        try:
            self.database.execute(
                "DELETE FROM parking_spaces WHERE id = ?",
                (space_id,)
            )
            logger.info(f"车位删除成功: {space_id}")
            return True
        except Exception as e:
            logger.error(f"删除车位失败: {e}")
            raise
    
    def occupy_space(self, space_id):
        logger.info(f"占用车位: {space_id}")
        try:
            self.database.execute(
                "UPDATE parking_spaces SET status = 'occupied', updated_at = ? WHERE id = ?",
                (datetime.now(), space_id)
            )
            logger.info(f"车位占用成功: {space_id}")
            return True
        except Exception as e:
            logger.error(f"占用车位失败: {e}")
            raise
    
    def release_space(self, space_id):
        logger.info(f"释放车位: {space_id}")
        try:
            self.database.execute(
                "UPDATE parking_spaces SET status = 'available', updated_at = ? WHERE id = ?",
                (datetime.now(), space_id)
            )
            logger.info(f"车位释放成功: {space_id}")
            return True
        except Exception as e:
            logger.error(f"释放车位失败: {e}")
            raise
    
    def reserve_space(self, space_id, user_id):
        logger.info(f"预订车位: {space_id}, 用户: {user_id}")
        try:
            self.database.execute(
                "UPDATE parking_spaces SET is_reserved = ?, reserved_user_id = ?, updated_at = ? WHERE id = ?",
                (True, user_id, datetime.now(), space_id)
            )
            logger.info(f"车位预订成功: {space_id}, 用户: {user_id}")
            return True
        except Exception as e:
            logger.error(f"预订车位失败: {e}")
            raise
    
    def cancel_reservation(self, space_id):
        logger.info(f"取消预订车位: {space_id}")
        try:
            self.database.execute(
                "UPDATE parking_spaces SET is_reserved = ?, reserved_user_id = NULL, updated_at = ? WHERE id = ?",
                (False, datetime.now(), space_id)
            )
            logger.info(f"取消预订成功: {space_id}")
            return True
        except Exception as e:
            logger.error(f"取消预订失败: {e}")
            raise
    
    def get_all_spaces(self, status=None, space_type=None):
        logger.info(f"获取所有车位, 状态: {status}, 类型: {space_type}")
        try:
            query = "SELECT * FROM parking_spaces"
            params = []
            conditions = []
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if space_type:
                conditions.append("space_type = ?")
                params.append(space_type)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY floor ASC, space_number ASC"
            
            results = self.database.fetch_all(query, params)
            
            spaces = []
            for result in results:
                space = ParkingSpace(
                    result['space_number'],
                    result['floor'],
                    result['space_type']
                )
                space.id = result['id']
                space.status = result['status']
                space.is_reserved = result['is_reserved']
                space.reserved_user_id = result['reserved_user_id']
                space.created_at = result['created_at']
                space.updated_at = result['updated_at']
                spaces.append(space)
            
            return spaces
        except Exception as e:
            logger.error(f"获取所有车位失败: {e}")
            raise
    
    def get_available_spaces(self, space_type=None):
        logger.info(f"获取可用车位, 类型: {space_type}")
        return self.get_all_spaces("available", space_type)
    
    def get_occupied_spaces(self, space_type=None):
        logger.info(f"获取已占用车位, 类型: {space_type}")
        return self.get_all_spaces("occupied", space_type)
    
    def get_reserved_spaces(self):
        logger.info("获取已预订车位")
        try:
            query = "SELECT * FROM parking_spaces WHERE is_reserved = ? ORDER BY floor ASC, space_number ASC"
            results = self.database.fetch_all(query, (True,))
            
            spaces = []
            for result in results:
                space = ParkingSpace(
                    result['space_number'],
                    result['floor'],
                    result['space_type']
                )
                space.id = result['id']
                space.status = result['status']
                space.is_reserved = result['is_reserved']
                space.reserved_user_id = result['reserved_user_id']
                space.created_at = result['created_at']
                space.updated_at = result['updated_at']
                spaces.append(space)
            
            return spaces
        except Exception as e:
            logger.error(f"获取已预订车位失败: {e}")
            raise
    
    def get_space_statistics(self, floor=None):
        logger.info(f"获取车位统计数据, 楼层: {floor}")
        try:
            query = "SELECT COUNT(*) as total FROM parking_spaces"
            params = []
            
            if floor is not None:
                query += " WHERE floor = ?"
                params.append(floor)
            
            total = self.database.fetch_one(query, params)['count']
            
            # 获取可用车位数量
            available_query = "SELECT COUNT(*) as count FROM parking_spaces WHERE status = 'available'"
            available_params = []
            if floor is not None:
                available_query += " AND floor = ?"
                available_params.append(floor)
            available = self.database.fetch_one(available_query, available_params)['count']
            
            # 获取占用车位数量
            occupied_query = "SELECT COUNT(*) as count FROM parking_spaces WHERE status = 'occupied'"
            occupied_params = []
            if floor is not None:
                occupied_query += " AND floor = ?"
                occupied_params.append(floor)
            occupied = self.database.fetch_one(occupied_query, occupied_params)['count']
            
            # 获取预订车位数量
            reserved_query = "SELECT COUNT(*) as count FROM parking_spaces WHERE is_reserved = ?"
            reserved_params = [True]
            if floor is not None:
                reserved_query += " AND floor = ?"
                reserved_params.append(floor)
            reserved = self.database.fetch_one(reserved_query, reserved_params)['count']
            
            # 计算利用率
            utilization = 0.0
            if total > 0:
                utilization = (occupied / total) * 100
            
            return {
                'total': total,
                'available': available,
                'occupied': occupied,
                'reserved': reserved,
                'utilization': utilization
            }
        except Exception as e:
            logger.error(f"获取车位统计数据失败: {e}")
            raise
    
    def get_floor_statistics(self):
        logger.info("获取各楼层车位统计数据")
        try:
            # 获取所有楼层
            floors = self.database.fetch_all("SELECT DISTINCT floor FROM parking_spaces ORDER BY floor ASC")
            
            floor_stats = []
            for floor in floors:
                floor_num = floor['floor']
                stats = self.get_space_statistics(floor_num)
                floor_stats.append({
                    'floor': floor_num,
                    **stats
                })
            
            logger.info(f"获取到 {len(floor_stats)} 个楼层的统计数据")
            return floor_stats
        except Exception as e:
            logger.error(f"获取各楼层车位统计数据失败: {e}")
            raise
    
    def export_space_data(self, file_path):
        logger.info(f"导出车位数据到: {file_path}")
        try:
            import csv
            
            # 查询所有车位数据
            results = self.database.fetch_all("SELECT * FROM parking_spaces ORDER BY floor ASC, space_number ASC")
            
            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(['ID', '车位号', '楼层', '车位类型', '状态', '是否预订', '预订用户ID', '创建时间', '更新时间'])
                
                # 写入数据
                for result in results:
                    writer.writerow([
                        result['id'],
                        result['space_number'],
                        result['floor'],
                        result['space_type'],
                        result['status'],
                        '是' if result['is_reserved'] else '否',
                        result['reserved_user_id'],
                        result['created_at'],
                        result['updated_at']
                    ])
            
            logger.info(f"车位数据导出成功: {file_path}, 共 {len(results)} 条记录")
            return len(results)
        except Exception as e:
            logger.error(f"导出车位数据失败: {e}")
            raise