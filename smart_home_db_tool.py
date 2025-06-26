#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能家居数据库命令行工具
实现项目2025数据库的管理和查询功能
"""

import sqlite3
import os
import sys
import re
import json
from datetime import datetime, timedelta
import random
import argparse
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tabulate import tabulate
import sqlparse
from sqlparse import sql, tokens
import warnings
warnings.filterwarnings('ignore')

class SmartHomeDatabaseTool:
    def __init__(self, db_name="project2025.db"):
        """初始化数据库工具"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        
    def initialize_database(self):
        """初始化数据库，创建智能家居相关表"""
        try:
            # 连接数据库
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            
            print(f"正在初始化数据库 {self.db_name}...")
            
            # 创建用户表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
            ''')
            
            # 创建设备表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                device_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name VARCHAR(100) NOT NULL,
                device_type VARCHAR(50) NOT NULL,  -- 空调、灯光、门锁、摄像头等
                room VARCHAR(50) NOT NULL,
                brand VARCHAR(50),
                model VARCHAR(50),
                status VARCHAR(20) DEFAULT 'offline',  -- online, offline, error
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_maintenance TIMESTAMP
            )
            ''')
            
            # 创建使用记录表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                device_id INTEGER,
                action VARCHAR(50) NOT NULL,  -- turn_on, turn_off, adjust_temperature等
                value TEXT,  -- 具体操作值，如温度、亮度等
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes INTEGER,  -- 使用时长
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
            ''')
            
            # 创建安防事件表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                event_type VARCHAR(50) NOT NULL,  -- motion_detected, door_opened, alarm等
                severity VARCHAR(20) DEFAULT 'low',  -- low, medium, high, critical
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                handled BOOLEAN DEFAULT FALSE,
                handled_by INTEGER,
                FOREIGN KEY (device_id) REFERENCES devices(device_id),
                FOREIGN KEY (handled_by) REFERENCES users(user_id)
            )
            ''')
            
            # 创建用户反馈表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                device_id INTEGER,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                comment TEXT,
                feedback_type VARCHAR(30),  -- bug_report, feature_request, general
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'pending',  -- pending, reviewed, resolved
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
            ''')
            
            # 创建房间表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name VARCHAR(50) UNIQUE NOT NULL,
                floor INTEGER DEFAULT 1,
                area_sqm REAL,
                room_type VARCHAR(30)  -- bedroom, living_room, kitchen, bathroom等
            )
            ''')
            
            self.conn.commit()
            print("✓ 数据库表创建成功")
            
            # 插入示例数据
            self._insert_sample_data()
            
            print("✓ 数据库初始化完成！")
            
        except sqlite3.Error as e:
            print(f"✗ 数据库初始化失败: {e}")
            return False
        
        return True
    
    def _insert_sample_data(self):
        """插入示例数据"""
        print("正在插入示例数据...")
        
        # 插入房间数据
        rooms_data = [
            ('客厅', 1, 35.5, 'living_room'),
            ('主卧室', 2, 20.0, 'bedroom'),
            ('次卧室', 2, 15.0, 'bedroom'),
            ('厨房', 1, 12.0, 'kitchen'),
            ('卫生间', 1, 8.0, 'bathroom'),
            ('书房', 2, 18.0, 'study')
        ]
        
        self.cursor.executemany(
            'INSERT OR IGNORE INTO rooms (room_name, floor, area_sqm, room_type) VALUES (?, ?, ?, ?)',
            rooms_data
        )
        
        # 插入用户数据
        users_data = [
            ('张三', 'zhangsan@email.com', '13800138001'),
            ('李四', 'lisi@email.com', '13800138002'),
            ('王五', 'wangwu@email.com', '13800138003'),
            ('赵六', 'zhaoliu@email.com', '13800138004')
        ]
        
        self.cursor.executemany(
            'INSERT OR IGNORE INTO users (username, email, phone) VALUES (?, ?, ?)',
            users_data
        )
        
        # 插入设备数据
        devices_data = [
            ('客厅空调', '空调', '客厅', '美的', 'KFR-35GW', 'online'),
            ('客厅智能电视', '电视', '客厅', '小米', 'Mi TV 4A', 'online'),
            ('主卧空调', '空调', '主卧室', '格力', 'KFR-26GW', 'online'),
            ('主卧智能灯', '灯光', '主卧室', '飞利浦', 'Hue White', 'online'),
            ('厨房智能灯', '灯光', '厨房', '飞利浦', 'Hue White', 'online'),
            ('前门智能锁', '门锁', '客厅', '鹿客', 'Classic 2S', 'online'),
            ('客厅摄像头', '摄像头', '客厅', '小米', 'Mi Home Security', 'online'),
            ('厨房烟雾探测器', '传感器', '厨房', '米家', 'JTYJ-GD-01LM', 'online')
        ]
        
        self.cursor.executemany(
            'INSERT OR IGNORE INTO devices (device_name, device_type, room, brand, model, status) VALUES (?, ?, ?, ?, ?, ?)',
            devices_data
        )
        
        # 插入使用记录数据
        base_time = datetime.now() - timedelta(days=30)
        usage_logs_data = []
        
        for i in range(100):
            user_id = random.randint(1, 4)
            device_id = random.randint(1, 8)
            actions = ['turn_on', 'turn_off', 'adjust_temperature', 'adjust_brightness', 'unlock', 'lock']
            action = random.choice(actions)
            value = str(random.randint(16, 30)) if 'temperature' in action else str(random.randint(1, 100))
            timestamp = base_time + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            duration = random.randint(5, 240)
            
            usage_logs_data.append((user_id, device_id, action, value, timestamp, duration))
        
        self.cursor.executemany(
            'INSERT INTO usage_logs (user_id, device_id, action, value, timestamp, duration_minutes) VALUES (?, ?, ?, ?, ?, ?)',
            usage_logs_data
        )
        
        # 插入安防事件数据
        security_events_data = []
        event_types = ['motion_detected', 'door_opened', 'alarm_triggered', 'smoke_detected']
        severities = ['low', 'medium', 'high']
        
        for i in range(50):
            device_id = random.choice([6, 7, 8])  # 门锁、摄像头、烟雾探测器
            event_type = random.choice(event_types)
            severity = random.choice(severities)
            description = f"检测到{event_type}事件"
            timestamp = base_time + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            handled = random.choice([True, False])
            handled_by = random.randint(1, 4) if handled else None
            
            security_events_data.append((device_id, event_type, severity, description, timestamp, handled, handled_by))
        
        self.cursor.executemany(
            'INSERT INTO security_events (device_id, event_type, severity, description, timestamp, handled, handled_by) VALUES (?, ?, ?, ?, ?, ?, ?)',
            security_events_data
        )
        
        self.conn.commit()
        print("✓ 示例数据插入完成")
    
    def validate_sql(self, sql_query: str) -> Dict[str, Any]:
        """验证SQL查询语句的正确性"""
        try:
            # 解析SQL语句
            parsed = sqlparse.parse(sql_query)
            
            if not parsed:
                return {
                    'valid': False,
                    'error': 'SQL语句为空或无法解析',
                    'suggestion': '请输入有效的SQL查询语句'
                }
            
            # 检查SQL语句类型
            first_token = parsed[0].token_first(skip_ws=True, skip_cm=True)
            if first_token and first_token.ttype is tokens.Keyword.DML:
                statement_type = first_token.value.upper()
            else:
                return {
                    'valid': False,
                    'error': '无法识别SQL语句类型',
                    'suggestion': '请确保使用SELECT、INSERT、UPDATE或DELETE语句'
                }
            
            # 检查表名是否存在
            table_names = self._extract_table_names(sql_query)
            existing_tables = self._get_existing_tables()
            
            invalid_tables = set(table_names) - set(existing_tables)
            if invalid_tables:
                return {
                    'valid': False,
                    'error': f'表名不存在: {", ".join(invalid_tables)}',
                    'suggestion': f'可用的表包括: {", ".join(existing_tables)}'
                }
            
            # 尝试执行查询（仅用于语法检查）
            if statement_type == 'SELECT':
                try:
                    self.cursor.execute(f'EXPLAIN QUERY PLAN {sql_query}')
                except sqlite3.Error as e:
                    return {
                        'valid': False,
                        'error': f'SQL语法错误: {str(e)}',
                        'suggestion': '请检查列名、表名和SQL语法是否正确'
                    }
            
            return {
                'valid': True,
                'message': 'SQL语句语法正确',
                'statement_type': statement_type,
                'tables': table_names
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'SQL验证失败: {str(e)}',
                'suggestion': '请检查SQL语句格式是否正确'
            }
    
    def _extract_table_names(self, sql_query: str) -> List[str]:
        """从SQL查询中提取表名"""
        parsed = sqlparse.parse(sql_query)
        table_names = []
        
        for statement in parsed:
            for token in statement.flatten():
                if token.ttype is None and isinstance(token.parent, sql.Statement):
                    # 简单的表名提取（可以进一步优化）
                    tables = ['users', 'devices', 'usage_logs', 'security_events', 'user_feedback', 'rooms']
                    if token.value.lower() in tables:
                        table_names.append(token.value.lower())
        
        return list(set(table_names))
    
    def _get_existing_tables(self) -> List[str]:
        """获取现有表名"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in self.cursor.fetchall()]
    
    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """执行SQL查询并返回结果"""
        validation_result = self.validate_sql(sql_query)
        
        if not validation_result['valid']:
            return validation_result
        
        try:
            start_time = datetime.now()
            
            if validation_result['statement_type'] == 'SELECT':
                # 获取查询执行计划
                self.cursor.execute(f'EXPLAIN QUERY PLAN {sql_query}')
                query_plan = self.cursor.fetchall()
                
                # 执行查询
                self.cursor.execute(sql_query)
                results = self.cursor.fetchall()
                
                # 获取列名
                column_names = [description[0] for description in self.cursor.description]
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                return {
                    'valid': True,
                    'statement_type': 'SELECT',
                    'results': results,
                    'columns': column_names,
                    'row_count': len(results),
                    'execution_time': execution_time,
                    'query_plan': query_plan
                }
            else:
                # 执行非SELECT语句
                self.cursor.execute(sql_query)
                self.conn.commit()
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                return {
                    'valid': True,
                    'statement_type': validation_result['statement_type'],
                    'affected_rows': self.cursor.rowcount,
                    'execution_time': execution_time,
                    'message': f'{validation_result["statement_type"]} 语句执行成功'
                }
                
        except sqlite3.Error as e:
            return {
                'valid': False,
                'error': f'查询执行失败: {str(e)}',
                'suggestion': '请检查SQL语句是否正确'
            }
    
    def visualize_results(self, query_result: Dict[str, Any]):
        """可视化查询结果"""
        if not query_result.get('valid') or query_result.get('statement_type') != 'SELECT':
            print("只能可视化SELECT查询的结果")
            return
        
        results = query_result['results']
        columns = query_result['columns']
        
        if not results:
            print("查询结果为空，无法可视化")
            return
        
        # 创建DataFrame
        df = pd.DataFrame(results, columns=columns)
        
        print(f"\n📊 查询结果可视化 (共{len(results)}行)")
        print("=" * 50)
        
        # 显示表格
        print("\n📋 数据表格:")
        print(tabulate(df.head(20), headers=df.columns, tablefmt='grid', showindex=False))
        
        if len(results) > 20:
            print(f"... (显示前20行，共{len(results)}行)")
        
        # 如果有数值列，创建图表
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        
        if len(numeric_columns) > 0:
            plt.figure(figsize=(12, 8))
            
            if len(numeric_columns) == 1:
                # 单个数值列 - 直方图
                plt.subplot(2, 1, 1)
                plt.hist(df[numeric_columns[0]], bins=20, alpha=0.7, color='skyblue')
                plt.title(f'{numeric_columns[0]} 分布')
                plt.xlabel(numeric_columns[0])
                plt.ylabel('频次')
                
            elif len(numeric_columns) >= 2:
                # 多个数值列 - 散点图
                plt.subplot(2, 1, 1)
                plt.scatter(df[numeric_columns[0]], df[numeric_columns[1]], alpha=0.6)
                plt.xlabel(numeric_columns[0])
                plt.ylabel(numeric_columns[1])
                plt.title(f'{numeric_columns[0]} vs {numeric_columns[1]}')
            
            # 显示查询执行计划
            if 'query_plan' in query_result:
                plt.subplot(2, 1, 2)
                plan_text = '\n'.join([f"Step {i+1}: {step}" for i, step in enumerate(query_result['query_plan'])])
                plt.text(0.1, 0.5, f"查询执行计划:\n{plan_text}", fontsize=10, 
                        transform=plt.gca().transAxes, verticalalignment='center')
                plt.axis('off')
                plt.title('查询执行计划')
            
            plt.tight_layout()
            plt.show()
        
        # 显示统计信息
        print(f"\n📈 统计信息:")
        print(f"执行时间: {query_result.get('execution_time', 0):.4f}秒")
        print(f"返回行数: {query_result.get('row_count', 0)}")
        
        if len(numeric_columns) > 0:
            print(f"\n📊 数值列统计:")
            print(df[numeric_columns].describe())
    
    def natural_language_query(self, nl_query: str) -> str:
        """实验性功能：自然语言查询转SQL"""
        nl_query = nl_query.lower().strip()
        
        # 简单的关键词映射
        keyword_mappings = {
            # 查询类型
            '查询': 'SELECT',
            '查找': 'SELECT',
            '显示': 'SELECT',
            '列出': 'SELECT',
            
            # 表名映射
            '用户': 'users',
            '设备': 'devices',
            '使用记录': 'usage_logs',
            '安防事件': 'security_events',
            '反馈': 'user_feedback',
            '房间': 'rooms',
            
            # 常用条件
            '所有': '*',
            '今天': 'DATE(timestamp) = DATE("now")',
            '昨天': 'DATE(timestamp) = DATE("now", "-1 day")',
            '本周': 'timestamp >= DATE("now", "-7 days")',
            '本月': 'timestamp >= DATE("now", "start of month")',
        }
        
        sql_query = ""
        
        # 简单的模式匹配
        if any(word in nl_query for word in ['查询', '查找', '显示', '列出']):
            sql_query = "SELECT "
            
            if '所有' in nl_query:
                sql_query += "* "
            else:
                sql_query += "* "  # 默认选择所有列
            
            sql_query += "FROM "
            
            # 确定表名
            if '用户' in nl_query:
                sql_query += "users "
            elif '设备' in nl_query:
                sql_query += "devices "
            elif '使用记录' in nl_query:
                sql_query += "usage_logs "
            elif '安防事件' in nl_query:
                sql_query += "security_events "
            elif '反馈' in nl_query:
                sql_query += "user_feedback "
            elif '房间' in nl_query:
                sql_query += "rooms "
            else:
                return "无法识别查询的表，请指定用户、设备、使用记录、安防事件、反馈或房间"
            
            # 添加条件
            conditions = []
            if '今天' in nl_query:
                conditions.append('DATE(timestamp) = DATE("now")')
            elif '昨天' in nl_query:
                conditions.append('DATE(timestamp) = DATE("now", "-1 day")')
            elif '本周' in nl_query:
                conditions.append('timestamp >= DATE("now", "-7 days")')
            elif '本月' in nl_query:
                conditions.append('timestamp >= DATE("now", "start of month")')
            
            if '在线' in nl_query:
                conditions.append("status = 'online'")
            elif '离线' in nl_query:
                conditions.append("status = 'offline'")
            
            if conditions:
                sql_query += "WHERE " + " AND ".join(conditions)
            
            sql_query += " LIMIT 10"  # 限制结果数量
        
        else:
            return "抱歉，目前只支持简单的查询语句。请尝试使用'查询所有用户'、'显示今天的使用记录'等格式"
        
        return sql_query
    
    def reset_system(self):
        """重置系统"""
        try:
            print("⚠️  确定要重置系统吗？这将删除所有数据！(y/N): ", end="")
            confirm = input().strip().lower()
            
            if confirm == 'y' or confirm == 'yes':
                # 删除所有表
                tables = self._get_existing_tables()
                for table in tables:
                    self.cursor.execute(f'DROP TABLE IF EXISTS {table}')
                
                self.conn.commit()
                print("✓ 系统重置完成！")
                
                # 重新初始化
                self.initialize_database()
            else:
                print("取消重置操作")
                
        except Exception as e:
            print(f"✗ 重置失败: {e}")
    
    def show_schema(self):
        """显示数据库架构"""
        tables = self._get_existing_tables()
        
        print("\n📋 数据库架构:")
        print("=" * 50)
        
        for table in tables:
            self.cursor.execute(f'PRAGMA table_info({table})')
            columns = self.cursor.fetchall()
            
            print(f"\n🗂️  表: {table}")
            print("-" * 30)
            
            for col in columns:
                col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
                pk_marker = " (主键)" if pk else ""
                null_marker = " NOT NULL" if not_null else ""
                default_marker = f" DEFAULT {default}" if default else ""
                
                print(f"  {col_name}: {col_type}{pk_marker}{null_marker}{default_marker}")
    
    def interactive_mode(self):
        """交互式命令行模式"""
        print("\n🏠 智能家居数据库工具 - 交互模式")
        print("输入 'help' 查看可用命令，输入 'quit' 退出")
        print("=" * 50)
        
        while True:
            try:
                command = input("\n>>> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break
                elif command.lower() == 'help':
                    self._show_help()
                elif command.lower() == 'schema':
                    self.show_schema()
                elif command.lower() == 'reset':
                    self.reset_system()
                elif command.lower().startswith('nl:'):
                    # 自然语言查询
                    nl_query = command[3:].strip()
                    sql_query = self.natural_language_query(nl_query)
                    print(f"转换的SQL: {sql_query}")
                    
                    if sql_query and not sql_query.startswith('抱歉'):
                        result = self.execute_query(sql_query)
                        if result['valid']:
                            self.visualize_results(result)
                        else:
                            print(f"❌ {result['error']}")
                            if 'suggestion' in result:
                                print(f"💡 建议: {result['suggestion']}")
                elif command:
                    # SQL查询
                    result = self.execute_query(command)
                    if result['valid']:
                        if result.get('statement_type') == 'SELECT':
                            self.visualize_results(result)
                        else:
                            print(f"✓ {result.get('message', '执行成功')}")
                            print(f"影响行数: {result.get('affected_rows', 0)}")
                    else:
                        print(f"❌ {result['error']}")
                        if 'suggestion' in result:
                            print(f"💡 建议: {result['suggestion']}")
                            
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
🆘 可用命令:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 基本命令:
  help          - 显示此帮助信息
  schema        - 显示数据库架构
  reset         - 重置系统（删除所有数据）
  quit/exit/q   - 退出程序

💬 自然语言查询 (实验性):
  nl: <查询>    - 使用自然语言查询
  示例: nl: 查询所有用户
        nl: 显示今天的使用记录
        nl: 列出所有在线设备

🔍 SQL查询:
  直接输入SQL语句即可执行
  示例: SELECT * FROM users;
        SELECT device_name, status FROM devices WHERE status='online';
        SELECT COUNT(*) FROM usage_logs WHERE DATE(timestamp) = DATE('now');

📊 支持的表:
  users         - 用户表
  devices       - 设备表
  usage_logs    - 使用记录表
  security_events - 安防事件表
  user_feedback - 用户反馈表
  rooms         - 房间表

💡 提示:
  - 查询结果会自动可视化显示
  - 系统会检查SQL语法并提供错误建议
  - 支持查询执行计划显示
        """
        print(help_text)
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='智能家居数据库命令行工具')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--reset', action='store_true', help='重置系统')
    parser.add_argument('--schema', action='store_true', help='显示数据库架构')
    parser.add_argument('--query', type=str, help='执行SQL查询')
    parser.add_argument('--nl', type=str, help='自然语言查询')
    parser.add_argument('--db', type=str, default='project2025.db', help='数据库文件名')
    
    args = parser.parse_args()
    
    # 创建工具实例
    tool = SmartHomeDatabaseTool(args.db)
    
    try:
        if args.init:
            tool.initialize_database()
        elif args.reset:
            tool.initialize_database()  # 会检查数据库是否存在
            tool.reset_system()
        elif args.schema:
            if not os.path.exists(args.db):
                print("数据库不存在，请先运行 --init 初始化")
                return
            tool.conn = sqlite3.connect(args.db)
            tool.cursor = tool.conn.cursor()
            tool.show_schema()
        elif args.query:
            if not os.path.exists(args.db):
                print("数据库不存在，请先运行 --init 初始化")
                return
            tool.conn = sqlite3.connect(args.db)
            tool.cursor = tool.conn.cursor()
            result = tool.execute_query(args.query)
            if result['valid']:
                tool.visualize_results(result)
            else:
                print(f"❌ {result['error']}")
                if 'suggestion' in result:
                    print(f"💡 建议: {result['suggestion']}")
        elif args.nl:
            if not os.path.exists(args.db):
                print("数据库不存在，请先运行 --init 初始化")
                return
            tool.conn = sqlite3.connect(args.db)
            tool.cursor = tool.conn.cursor()
            sql_query = tool.natural_language_query(args.nl)
            print(f"转换的SQL: {sql_query}")
            if sql_query and not sql_query.startswith('抱歉'):
                result = tool.execute_query(sql_query)
                if result['valid']:
                    tool.visualize_results(result)
                else:
                    print(f"❌ {result['error']}")
        else:
            # 交互模式
            if not os.path.exists(args.db):
                print("数据库不存在，正在初始化...")
                tool.initialize_database()
            else:
                tool.conn = sqlite3.connect(args.db)
                tool.cursor = tool.conn.cursor()
            
            tool.interactive_mode()
    
    finally:
        tool.close()


if __name__ == "__main__":
    main()
