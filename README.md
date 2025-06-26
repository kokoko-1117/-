# 智能家居数据库工具使用指南

##  快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
python smart_home_db_tool.py --init
```

### 3. 进入交互模式
```bash
python smart_home_db_tool.py
```

##  功能特性

###  已实现的核心功能

1. **数据库初始化**：自动创建project2025数据库，包含智能家居系统的完整关系模式
2. **SQL查询验证**：智能检查SQL语法，提供用户友好的错误信息和修改建议
3. **查询结果可视化**：自动生成图表和表格，直观展示查询结果
4. **查询执行计划**：显示SQL查询的执行计划，帮助优化性能
5. **自然语言查询**：实验性功能，支持简单的中文自然语言转SQL
6. **系统重置**：安全重置数据库，支持重新设计关系模式

###  数据库设计（智能家居系统）

根据题目二的要求，设计了以下6个核心表：

1. **users（用户表）**
   - user_id, username, email, phone, created_at, last_login, is_active

2. **devices（设备表）**
   - device_id, device_name, device_type, room, brand, model, status, installed_at, last_maintenance

3. **usage_logs（使用记录表）**
   - log_id, user_id, device_id, action, value, timestamp, duration_minutes

4. **security_events（安防事件表）**
   - event_id, device_id, event_type, severity, description, timestamp, handled, handled_by

5. **user_feedback（用户反馈表）**
   - feedback_id, user_id, device_id, rating, comment, feedback_type, timestamp, status

6. **rooms（房间表）**
   - room_id, room_name, floor, area_sqm, room_type

##  命令行参数

```bash
# 初始化数据库
python smart_home_db_tool.py --init

# 显示数据库架构
python smart_home_db_tool.py --schema

# 执行SQL查询
python smart_home_db_tool.py --query "SELECT * FROM users"

# 自然语言查询
python smart_home_db_tool.py --nl "查询所有用户"

# 重置系统
python smart_home_db_tool.py --reset

# 指定数据库文件
python smart_home_db_tool.py --db custom.db --init
```

##  交互模式命令

进入交互模式后可以使用以下命令：

```
>>> help                    # 显示帮助信息
>>> schema                  # 显示数据库架构
>>> reset                   # 重置系统
>>> SELECT * FROM users;    # 执行SQL查询
>>> nl: 查询所有用户        # 自然语言查询
>>> quit                    # 退出程序
```

##  查询示例

### SQL查询示例

```sql
-- 查询所有在线设备
SELECT device_name, device_type, room, status 
FROM devices 
WHERE status = 'online';

-- 统计每个房间的设备数量
SELECT room, COUNT(*) as device_count 
FROM devices 
GROUP BY room 
ORDER BY device_count DESC;

-- 查询今天的使用记录
SELECT u.username, d.device_name, ul.action, ul.timestamp
FROM usage_logs ul
JOIN users u ON ul.user_id = u.user_id
JOIN devices d ON ul.device_id = d.device_id
WHERE DATE(ul.timestamp) = DATE('now');

-- 查询高优先级安防事件
SELECT se.event_type, se.severity, se.description, se.timestamp, d.device_name
FROM security_events se
JOIN devices d ON se.device_id = d.device_id
WHERE se.severity IN ('high', 'critical')
ORDER BY se.timestamp DESC;

-- 分析用户使用习惯
SELECT u.username, 
       COUNT(*) as usage_count,
       AVG(ul.duration_minutes) as avg_duration
FROM usage_logs ul
JOIN users u ON ul.user_id = u.user_id
GROUP BY u.user_id, u.username
ORDER BY usage_count DESC;
```

### 自然语言查询示例

```
nl: 查询所有用户
nl: 显示今天的使用记录
nl: 列出所有在线设备
nl: 查找本周的安防事件
nl: 显示所有房间信息
```

## 可视化功能

工具会自动为查询结果生成：

1. **数据表格**：使用tabulate库格式化显示
2. **统计图表**：
   - 单数值列：直方图
   - 多数值列：散点图
   - 数据统计摘要
3. **查询执行计划**：显示SQL优化信息
4. **执行时间统计**：性能监控

##  错误处理与建议

系统提供智能的错误检测和建议：

```
❌ 表名不存在: user
💡 建议: 可用的表包括: users, devices, usage_logs, security_events, user_feedback, rooms

❌ SQL语法错误: no such column: name
💡 建议: 请检查列名、表名和SQL语法是否正确
```

## 实验性功能

### 自然语言查询
- 支持中文查询转换为SQL
- 识别常用查询模式
- 自动添加时间条件和限制条件

### 查询优化建议
- 显示查询执行计划
- 性能监控和统计
- 索引建议（未来版本）

##  技术实现

- **数据库**：SQLite（轻量级，无需额外配置）
- **SQL解析**：sqlparse库进行语法分析
- **可视化**：matplotlib + seaborn + pandas
- **表格显示**：tabulate库
- **自然语言处理**：基于关键词匹配的简单NLP

##  系统扩展

工具设计了模块化架构，便于扩展：

1. **新增表结构**：修改`initialize_database()`方法
2. **扩展NL功能**：改进`natural_language_query()`方法
3. **新增可视化类型**：扩展`visualize_results()`方法
4. **添加数据分析**：集成更多统计分析功能

##  故障排除

### 常见问题

1. **ModuleNotFoundError**
   ```bash
   pip install -r requirements.txt
   ```

2. **数据库权限错误**
   ```bash
   # 确保当前目录有写权限
   chmod 755 .
   ```

3. **图表显示问题**
   ```bash
   # 如果在服务器环境，可能需要设置matplotlib后端
   export MPLBACKEND=Agg
   ```


