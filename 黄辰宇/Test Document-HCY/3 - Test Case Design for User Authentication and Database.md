# M2MRF 糖尿病视网膜病变病灶分割系统 测试用例设计(TC)

**注意**: 本文档仅包含测试设计方法，实际测试结果请参考《测试结果分析报告》。

---

## 1. 概述

### 1.1 项目背景

M2MRF (Multi-to-Multi-scale Receptive Field) 糖尿病视网膜病变病灶分割系统是一个基于深度学习的医疗图像分析系统，采用分布式架构设计。本测试设计文档基于**已成功运行**的测试代码，涵盖用户权限管理模块和数据库模块测试。

### 1.2 测试模块划分

本测试设计分为两个主要模块：

| 模块                     | 测试范围                   | 测试文件                  |
| ------------------------ | -------------------------- | ------------------------- |
| **用户权限管理模块测试** | 功能正确性、安全可靠性     | `test_user_management.py` |
| **数据库模块测试**       | 事务一致性、性能、备份安全 | `test_database.py`        |

---

## 2. 用户权限管理模块测试用例设计

### 2.1 TS-UM-001: **功能正确性**测试套件用例

**测试文件**: `test_user_management.py`

| 测试用例 ID   | 输入数据/条件                                                | 执行步骤                                                     | 期望结果                                              |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ----------------------------------------------------- |
| **TC-UM-001** | {username: "doctor1", password: "P@ssw0rd", role: "doctor"}  | 1. POST /api/users/ 创建用户<br/>2. 查询数据库验证记录       | 1. HTTP 201 <br/>2. 数据库存在对应记录，role='doctor' |
| **TC-UM-002** | {username: "patient1", password: "Secure123", role: "patient"} | 1. POST /api/users/ 创建用户<br/>2. GET /api/users/ 验证用户列表 | 1. HTTP 201<br/>2. 用户列表包含该患者，role='patient' |
| **TC-UM-003** | {username: "test", password: "123", role: "admin"}           | POST /api/users/ 创建用户                                    | HTTP 400 错误，提示"Invalid role"                     |
| **TC-UM-004** | 患者token访问 GET /api/doctor/reports                        | 患者登录获取token 2. 用token调用医生专属API                  | HTTP 403 Forbidden                                    |

**实现代码片段**:

```python
class TestFunctionalCorrectness:
    """TS-UM-001 功能正确性测试套件"""
    
    def test_create_doctor(self):
        """TC-UM-001: 创建医生用户"""
        # 创建用户
        response = requests.post(f"{BASE_URL}/api/users/", json=VALID_DOCTOR)
        assert response.status_code == 201
        
        # 验证数据库
        user_list = requests.get(f"{BASE_URL}/api/users/").json()["data"]
        doctor_exists = any(u["username"] == VALID_DOCTOR["username"] and u["role"] == "doctor" for u in user_list)
        assert doctor_exists
```

### 2.2 TS-UM-002: **安全性与可靠性**测试套件用例

**测试文件**: `test_user_management.py`

| 测试用例 ID   | 输入数据/条件                     | 执行步骤                                                     | 期望结果                                                     |
| ------------- | --------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **TC-UM-006** | {password: "123456"}              | 注册用户时使用弱密码                                         | HTTP 400 错误，提示"Password must contain 8+ chars with special symbols" |
| **TC-UM-007** | 过期token (有效期30分钟后)        | 1. 登录获取token<br/>2. 等待35分钟<br/>3. 用token访问/api/users/ | HTTP 401 Unauthorized                                        |
| **TC-UM-008** | 100并发登录请求                   | 使用JMeter模拟100用户同时登录                                | 成功率≥95%，平均响应<500ms                                   |
| **TC-UM-009** | 连续5次错误密码                   | 使用错误密码连续尝试登录                                     | 第6次尝试返回HTTP 423 "Account locked"                       |
| **TC-UM-010** | 修改token payload {role: "admin"} | 1. 解码token<br/>2. 修改role字段<br/>3. 使用篡改token访问敏感API | HTTP 401 Unauthorized                                        |

**实现代码片段**:

```python
class TestSecurityReliability:
    """TS-UM-002 安全性与可靠性测试套件"""
    
    def test_weak_password_policy(self):
        """TC-UM-006: 弱密码策略"""
        response = requests.post(f"{BASE_URL}/api/users/", json=WEAK_PASSWORD)
        assert response.status_code == 400
        assert "Password must contain" in response.json()["msg"]
```

---

## 3. 数据库模块测试设计

### 3.1 TS-DB-001: **事务一致性**测试套件用例

**测试文件**: `test_database.py`

| 测试用例 ID   | 输入数据/条件                                          | 执行步骤                                                     | 期望结果                                 |
| ------------- | ------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------------------- |
| **TC-DB-001** | User成功+Patient失败                                   | 1. 开启事务<br/>2. 插入User记录<br/>3. 强制Patient插入失败<br/>4. 提交事务 | 数据库无User记录，事务完全回滚           |
| **TC-DB-002** | 删除用户user_id=1001                                   | 1. 删除User表记录<br/>2. 检查关联Patient表                   | Patient表中user_id=1001的记录被级联删除  |
| **TC-DB-003** | {diagnosis_id: 500, patient_id: 1002, doctor_id: null} | 插入无关联医生的诊断报告                                     | 插入失败，外键约束错误                   |
| **TC-DB-004** | 并发更新同一诊断报告                                   | 1. 两个会话同时更新diagnosis_id=200的报告<br/>2. 检查最终状态 | 后提交的事务覆盖前事务，但数据完整无损坏 |

**实现代码片段**:

```python
class TestTransactionConsistency:
    """TS-DB-001 事务一致性测试套件"""
    
    def test_transaction_rollback(self, db_session):
        """TC-DB-001: 事务回滚测试"""
        # 插入用户
        user_result = db_session.execute(text("""
            INSERT INTO User (username, password, role)
            VALUES (:username, :password, :role)
        """), {
            "username": "test_user", 
            "password": FERNET.encrypt(b"Pass123").decode(),
            "role": "patient"
        })
        user_id = user_result.lastrowid
        
        # 强制失败操作 (name 为 NOT NULL)
        with pytest.raises(exc.IntegrityError):
            db_session.execute(text("""
                INSERT INTO Patient (user_id, name, date_of_birth)
                VALUES (:user_id, NULL, '2000-01-01')
            """), {"user_id": user_id})
            db_session.commit()
        
        # 验证用户记录不存在
        user = db_session.execute(
            text("SELECT * FROM User WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        assert user is None
```

### 3.2 TS-DB-002: **性能与资源**测试套件用例

**测试文件**: `test_database.py`

| 测试用例 ID   | 输入数据/条件                                          | 执行步骤                                                     | 期望结果                                      |
| ------------- | ------------------------------------------------------ | ------------------------------------------------------------ | --------------------------------------------- |
| **TC-DB-005** | SELECT * FROM Diagnose ORDER BY diagnosis_time         | 1. 执行不带索引的排序查询<br/>2. EXPLAIN分析执行计划         | 1. 查询时间<100ms<br/>2. 执行计划显示索引命中 |
| **TC-DB-006** | 50并发执行复杂查询                                     | 1. 使用Sysbench模拟50并发<br/>2. 监控连接池状态              | 1. 无连接超时错误<br/>2. 连接池利用率<80%     |
| **TC-DB-007** | WHERE confirmed=false AND diagnose_date > '2023-01-01' | 1. 执行多条件查询<br/>2. 检查执行计划                        | 1. 响应时间<200ms<br/>2. 复合索引被使用       |
| **TC-DB-008** | 大数据量分页查询(10万条记录)                           | 1. SELECT * FROM Diagnose LIMIT 10000,100<br/>2. 监控查询时间 | 查询时间<500ms                                |

**实现代码片段**:

```python
class TestPerformanceResources:
    """TS-DB-002 性能与资源测试套件"""
    
    def test_query_performance_with_index(self, db_engine):
        """TC-DB-005: 索引查询性能测试"""
        # 确保索引存在
        with db_engine.connect() as conn:
            inspector = inspect(conn)
            indexes = inspector.get_indexes('Diagnose')
            if not any(idx['name'] == 'idx_diagnosis_time' for idx in indexes):
                conn.execute(text("CREATE INDEX idx_diagnosis_time ON Diagnose(diagnosis_time)"))
        
        # 执行排序查询
        start_time = time.time()
        with db_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM Diagnose 
                ORDER BY diagnosis_time DESC 
                LIMIT 100
            """)).fetchall()
        query_time = (time.time() - start_time) * 1000  # 毫秒
        
        # 验证性能
        assert len(result) == 100
        assert query_time < 100, f"查询耗时 {query_time:.2f}ms 超过100ms阈值"
```

### 3.3 TS-DB-003: **备份与安全**测试套件用例

**测试文件**: `test_database.py`

| 测试用例 ID   | 输入数据/条件    | 执行步骤                                                    | 期望结果                            |
| ------------- | ---------------- | ----------------------------------------------------------- | ----------------------------------- |
| **TC-DB-009** | 24小时前备份文件 | 1. 停止数据库服务<br/>2. 恢复备份<br/>3. 启动服务并验证数据 | 数据完整一致，无丢失记录            |
| **TC-DB-010** | 检查密码字段值   | 1. SELECT password FROM User WHERE user_id=1001             | 返回加密字符串(AES-256格式)，非明文 |
| **TC-DB-011** | 检查日志文件内容 | 1. 搜索日志文件中的密码字段<br/>2. 检查敏感数据             | 日志中无明文密码，敏感字段显示为*** |
| **TC-DB-012** | 模拟磁盘故障     | 1. 破坏数据文件<br/>2. 从备份恢复                           | 1小时内完成恢复，数据损失≤5分钟     |

**实现代码片段**:

```python
class TestBackupSecurity:
    """TS-DB-003 备份与安全测试套件"""
    
    def test_backup_and_restore(self, db_engine):
        """TC-DB-009: 备份恢复测试"""
        # 执行备份
        backup_cmd = (
            f"mysqldump -h{DB_CONFIG['host']} -u{DB_CONFIG['user']} "
            f"-p{DB_CONFIG['password']} {DB_CONFIG['database']} > {BACKUP_FILE}"
        )
        subprocess.run(backup_cmd, shell=True, check=True)
        assert os.path.exists(BACKUP_FILE), "备份文件未创建"
        
        # 修改原始数据
        with db_engine.connect() as conn:
            conn.execute(text("""
                UPDATE User SET username = 'modified_user' 
                WHERE username = 'backup_test'
            """))
            conn.commit()
        
        # 执行恢复
        restore_cmd = (
            f"mysql -h{DB_CONFIG['host']} -u{DB_CONFIG['user']} "
            f"-p{DB_CONFIG['password']} {DB_CONFIG['database']} < {BACKUP_FILE}"
        )
        subprocess.run(restore_cmd, shell=True, check=True)
        
        # 验证数据恢复
        with db_engine.connect() as conn:
            user = conn.execute(text("""
                SELECT username FROM User 
                WHERE username = 'backup_test'
            """)).fetchone()
            assert user is not None, "备份恢复失败，数据未还原"
```

---

## 4. 风险覆盖矩阵与 SDS 映射

### 4.1 用户权限管理模块测试风险覆盖

| 风险 ID     | 风险描述                           | 测试套件  | 测试用例             | SDS 映射       | 缓解策略                       |
| ----------- | ---------------------------------- | --------- | -------------------- | -------------- | ------------------------------ |
| **1.3.001** | 弱密码策略导致账户被暴力破解       | TS-UM-002 | TC-UM-006            | SDS 3.1, 5.1.1 | 密码强度校验，登录失败锁定机制 |
| **1.3.002** | Token 未设置有效期导致会话劫持风险 | TS-UM-002 | TC-UM-007, TC-UM-010 | SDS 3.1, 5.1.1 | Token 短有效期+即时失效机制    |
| **1.2.001** | 创建用户时未校验角色字段合法性     | TS-UM-001 | TC-UM-003            | SDS 3.1, 6.4   | 角色枚举值校验+数据库约束      |
| **1.2.002** | 权限控制失效导致越权访问           | TS-UM-001 | TC-UM-004, TC-UM-005 | SDS 2.4, 5.1.1 | 基于角色的中间件鉴权           |
| **1.1.001** | 高并发登录导致认证服务崩溃         | TS-UM-002 | TC-UM-008            | SDS 2.5.3, 4.1 | Redis 缓存+连接池优化          |

### 4.2 数据库模块测试风险覆盖

| 风险 ID     | 风险描述                         | 测试套件  | 测试用例             | SDS 映射       | 缓解策略                   |
| ----------- | -------------------------------- | --------- | -------------------- | -------------- | -------------------------- |
| **1.1.001** | 数据库连接泄漏耗尽资源           | TS-DB-002 | TC-DB-006            | SDS 2.2.4, 6.2 | 上下文管理器自动释放连接   |
| **2.1.001** | 事务控制失效导致数据不一致       | TS-DB-001 | TC-DB-001            | SDS 2.2.4, 6.2 | 数据库事务回滚机制         |
| **2.1.002** | 外键约束缺失产生孤儿记录         | TS-DB-001 | TC-DB-002, TC-DB-003 | SDS 6.4        | ON DELETE CASCADE 级联操作 |
| **2.2.001** | 未索引高频字段导致慢查询(>100ms) | TS-DB-002 | TC-DB-005, TC-DB-007 | SDS 6.2, 6.4   | 查询计划分析+复合索引优化  |
| **2.2.002** | 连接池配置不当导致高并发耗尽     | TS-DB-002 | TC-DB-006            | SDS 2.2.4, 6.2 | 动态连接池大小调整         |
| **2.3.001** | 备份机制失效导致数据无法恢复     | TS-DB-003 | TC-DB-009, TC-DB-012 | SDS 2.2.4, 6.2 | 每日全量+增量备份验证      |
| **2.3.002** | 敏感数据未脱敏违反隐私合规       | TS-DB-003 | TC-DB-010, TC-DB-011 | SDS 5.1.1, 6.1 | AES-256 加密+日志脱敏      |

### 4.3 SDS 需求映射

| SDS ID        | 需求描述               | 对应测试套件         | 验证方法                     |
| ------------- | ---------------------- | -------------------- | ---------------------------- |
| **SDS 2.2.4** | 数据库事务与连接池机制 | TS-DB-001, TS-DB-002 | 事务回滚测试，连接池压力测试 |
| **SDS 3.1**   | 用户管理接口规范       | TS-UM-001, TS-UM-002 | API 功能+安全性验证          |
| **SDS 4.1**   | 前端应用层技术实现     | TS-UM-002 (并发测试) | 高并发响应验证               |
| **SDS 5.1.1** | User 类密码加密存储    | TS-DB-003            | 加密字段验证                 |
| **SDS 6.1**   | 敏感数据脱敏要求       | TS-DB-003            | 日志审计+加密验证            |
| **SDS 6.2**   | 数据库高并发支持       | TS-DB-002            | 压力测试+执行计划分析        |
| **SDS 6.4**   | 数据表外键约束设计     | TS-DB-001            | 级联操作验证                 |

## 5.  性能基准指标

| 测试指标       | 目标值 | 实测值 | 验证用例  |
| :------------- | :----- | :----- | :-------- |
| 并发登录响应   | <500ms | 320ms  | TC-UM-008 |
| 数据库查询性能 | <100ms | 78ms   | TC-DB-005 |
| 备份恢复时间   | <1小时 | 45分钟 | TC-DB-012 |
