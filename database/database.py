#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型和连接管理
使用SQLAlchemy进行数据库操作
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from database.sample_data import PhoneSpec

@dataclass
class PhoneRecord:
    """手机记录"""
    id: int
    name: str
    cpu: str
    ram_gb: int
    storage_gb: int
    screen_size_inch: float
    camera_mp: int
    battery_mah: int
    weight_g: int
    price: int
    highlights: str  # JSON字符串
    rating: float
    sales: int
    heat_control_score: float
    network_stability_score: float
    created_at: str
    updated_at: str

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "phone_recommendation.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建手机表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS phones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    cpu TEXT NOT NULL,
                    ram_gb INTEGER NOT NULL,
                    storage_gb INTEGER NOT NULL,
                    screen_size_inch REAL NOT NULL,
                    camera_mp INTEGER NOT NULL,
                    battery_mah INTEGER NOT NULL,
                    weight_g INTEGER NOT NULL,
                    price INTEGER NOT NULL,
                    highlights TEXT NOT NULL,
                    rating REAL NOT NULL,
                    sales INTEGER NOT NULL,
                    heat_control_score REAL DEFAULT 3.0,
                    network_stability_score REAL DEFAULT 3.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # 创建用户会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_demand TEXT,
                    recommendations TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # 创建推荐历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recommendation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    system_response TEXT NOT NULL,
                    recommendations TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
    
    def insert_phone(self, phone: PhoneSpec) -> int:
        """插入手机数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO phones (
                    name, cpu, ram_gb, storage_gb, screen_size_inch, camera_mp,
                    battery_mah, weight_g, price, highlights, rating, sales,
                    heat_control_score, network_stability_score, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                phone.name, phone.cpu, phone.ram_gb, phone.storage_gb,
                phone.screen_size_inch, phone.camera_mp, phone.battery_mah,
                phone.weight_g, phone.price, json.dumps(phone.highlights),
                phone.rating, phone.sales, phone.heat_control_score,
                phone.network_stability_score, now, now
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_all_phones(self) -> List[PhoneRecord]:
        """获取所有手机数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM phones ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            phones = []
            for row in rows:
                phone = PhoneRecord(
                    id=row[0], name=row[1], cpu=row[2], ram_gb=row[3],
                    storage_gb=row[4], screen_size_inch=row[5], camera_mp=row[6],
                    battery_mah=row[7], weight_g=row[8], price=row[9],
                    highlights=row[10], rating=row[11], sales=row[12],
                    heat_control_score=row[13], network_stability_score=row[14],
                    created_at=row[15], updated_at=row[16]
                )
                phones.append(phone)
            
            return phones
    
    def get_phones_by_price_range(self, min_price: int, max_price: int) -> List[PhoneRecord]:
        """根据价格范围获取手机"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM phones 
                WHERE price >= ? AND price <= ?
                ORDER BY price ASC
            ''', (min_price, max_price))
            
            rows = cursor.fetchall()
            phones = []
            for row in rows:
                phone = PhoneRecord(
                    id=row[0], name=row[1], cpu=row[2], ram_gb=row[3],
                    storage_gb=row[4], screen_size_inch=row[5], camera_mp=row[6],
                    battery_mah=row[7], weight_g=row[8], price=row[9],
                    highlights=row[10], rating=row[11], sales=row[12],
                    heat_control_score=row[13], network_stability_score=row[14],
                    created_at=row[15], updated_at=row[16]
                )
                phones.append(phone)
            
            return phones
    
    def search_phones(self, keyword: str) -> List[PhoneRecord]:
        """搜索手机"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM phones 
                WHERE name LIKE ? OR cpu LIKE ? OR highlights LIKE ?
                ORDER BY rating DESC
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            
            rows = cursor.fetchall()
            phones = []
            for row in rows:
                phone = PhoneRecord(
                    id=row[0], name=row[1], cpu=row[2], ram_gb=row[3],
                    storage_gb=row[4], screen_size_inch=row[5], camera_mp=row[6],
                    battery_mah=row[7], weight_g=row[8], price=row[9],
                    highlights=row[10], rating=row[11], sales=row[12],
                    heat_control_score=row[13], network_stability_score=row[14],
                    created_at=row[15], updated_at=row[16]
                )
                phones.append(phone)
            
            return phones
    
    def update_phone(self, phone_id: int, **kwargs) -> bool:
        """更新手机数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 构建更新语句
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            set_clause += ", updated_at = ?"
            
            values = list(kwargs.values())
            values.append(datetime.now().isoformat())
            values.append(phone_id)
            
            cursor.execute(f'UPDATE phones SET {set_clause} WHERE id = ?', values)
            conn.commit()
            
            return cursor.rowcount > 0
    
    def delete_phone(self, phone_id: int) -> bool:
        """删除手机数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM phones WHERE id = ?', (phone_id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def save_session(self, session_id: str, user_demand: str = None, 
                    recommendations: str = None) -> bool:
        """保存用户会话"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_sessions 
                (session_id, user_demand, recommendations, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, user_demand, recommendations, now, now))
            
            conn.commit()
            return True
    
    def save_recommendation_history(self, session_id: str, user_input: str, 
                                  system_response: str, recommendations: str = None) -> bool:
        """保存推荐历史"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO recommendation_history 
                (session_id, user_input, system_response, recommendations, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, user_input, system_response, recommendations, now))
            
            conn.commit()
            return True
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """获取会话历史"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_input, system_response, recommendations, created_at
                FROM recommendation_history 
                WHERE session_id = ?
                ORDER BY created_at ASC
            ''', (session_id,))
            
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    'user_input': row[0],
                    'system_response': row[1],
                    'recommendations': row[2],
                    'created_at': row[3]
                })
            
            return history
    
    def get_statistics(self) -> Dict:
        """获取数据库统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 手机总数
            cursor.execute('SELECT COUNT(*) FROM phones')
            total_phones = cursor.fetchone()[0]
            
            # 价格统计
            cursor.execute('SELECT MIN(price), MAX(price), AVG(price) FROM phones')
            price_stats = cursor.fetchone()
            
            # 评分统计
            cursor.execute('SELECT AVG(rating) FROM phones')
            avg_rating = cursor.fetchone()[0]
            
            # 会话总数
            cursor.execute('SELECT COUNT(*) FROM user_sessions')
            total_sessions = cursor.fetchone()[0]
            
            return {
                'total_phones': total_phones,
                'min_price': price_stats[0],
                'max_price': price_stats[1],
                'avg_price': price_stats[2],
                'avg_rating': avg_rating,
                'total_sessions': total_sessions
            } 