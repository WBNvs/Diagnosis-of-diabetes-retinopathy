# M2MRF 糖尿病视网膜病变病灶分割系统 - 测试套件规范 (TS)

## 文档说明

本文档与 `Test_Design_Document_Final.md` 保持完全一致，定义了基于风险分析的测试套件规范和 SDS 需求映射。

**注意**: 本文档包含测试执行状态，实际测试结果详情请参考 `Test_Result_Analysis_Report.md`。

---

## 1. 用户权限管理模块测试套件

### TS-UM-001: **功能正确性测试套件**

| 项目                     | 内容                                                         |
| ------------------------ | ------------------------------------------------------------ |
| **TSDI**                 | TS-UM-001                                                    |
| **执行脚本**             | `run_um_functional_tests.bat`                                |
| **测试状态**             | ✅ 已通过                                                     |
| **Category**             | Component Level - Functional Correctness                     |
| **Feature to be tested** | 用户注册/登录流程、权限分配机制、角色校验功能                |
| **Risk Mapping**         | **风险 ID 1.2.001**: 角色字段校验失效<br/>**风险 ID 1.2.002**: 权限控制失效 |
| **SDS Mapping**          | SDS 3.1 (用户管理接口), SDS 5.1.1 (User类), SDS 6.4 (数据表设计) |
| **Test Method**          | **黑盒测试+决策表方法**<br/>• 角色枚举值边界测试<br/>• 权限矩阵验证<br/>• 异常输入处理 |
| **Test Cases**           | **TC-UM-001**: 创建医生用户(role='doctor') → 201 ✅<br/>**TC-UM-002**: 创建患者用户(role='patient') → 201 ✅<br/>**TC-UM-003**: 非法角色(role='admin') → 400 ✅<br/>**TC-UM-004**: 患者访问医生API → 403 ✅<br/>**TC-UM-005**: 医生访问患者API → 403 ✅ |
| **Tools**                | • Postman<br/>• pytest<br/>• SQLAlchemy ORM                  |
| **Techniques**           | • 角色枚举值遍历测试<br/>• 权限矩阵验证<br/>• HTTP状态码断言 |
| **Pass/Fail Criteria**   | **Pass**: 所有API返回正确状态码，权限控制100%准确<br/>**Fail**: 非法角色创建成功或越权访问 |

### TS-UM-002: **安全性与可靠性测试套件**

| 项目                     | 内容                                                         |
| ------------------------ | ------------------------------------------------------------ |
| **TSDI**                 | TS-UM-002                                                    |
| **执行脚本**             | `run_um_security_tests.bat`                                  |
| **测试状态**             | ✅ 已通过                                                     |
| **Category**             | Component Level - Security & Reliability                     |
| **Feature to be tested** | 密码安全策略、会话管理、高并发处理                           |
| **Risk Mapping**         | **风险 ID 1.3.001**: 弱密码策略<br/>**风险 ID 1.3.002**: Token失效机制<br/>**风险 ID 1.1.001**: 高并发登录 |
| **SDS Mapping**          | SDS 3.1 (登录接口), SDS 5.1.1 (login方法), SDS 2.5.3 (数据流) |
| **Test Method**          | **渗透测试+压力测试**<br/>• 密码强度爆破测试<br/>• Token有效期验证<br/>• 并发登录压力测试 |
| **Test Cases**           | **TC-UM-006**: 弱密码(123456) → 注册失败400 ✅<br/>**TC-UM-007**: 过期Token访问 → 401 ✅<br/>**TC-UM-008**: 100并发登录 → 成功率>95% ✅<br/>**TC-UM-009**: 5次失败登录 → 账户锁定 ✅ |
| **Tools**                | • JMeter<br/>• OWASP ZAP<br/>• JWT解码工具                   |
| **Techniques**           | • 密码爆破模拟<br/>• Token篡改检测<br/>• 并发会话管理验证    |
| **Pass/Fail Criteria**   | **Pass**: 密码策略强制执行，Token准时失效，并发成功率≥95%<br/>**Fail**: 弱密码注册成功或并发崩溃 |

---

## 2. 数据库模块测试套件

### TS-DB-001: **事务一致性测试套件**

| 项目                     | 内容                                                         |
| ------------------------ | ------------------------------------------------------------ |
| **TSDI**                 | TS-DB-001                                                    |
| **执行脚本**             | `run_db_transaction_tests.bat`                               |
| **测试状态**             | ✅ 已通过                                                     |
| **Category**             | Component Level - Data Consistency                           |
| **Feature to be tested** | 事务原子性、外键约束、级联操作                               |
| **Risk Mapping**         | **风险 ID 2.1.001**: 事务控制失效<br/>**风险 ID 2.1.002**: 外键约束缺失 |
| **SDS Mapping**          | SDS 2.2.4 (ACID特性), SDS 6.2 (数据库设计), SDS 6.4 (ER图)   |
| **Test Method**          | **事务回滚测试+外键验证** <br/>• 模拟部分写入失败<br/>• 孤儿记录检测 <br/>• 级联删除验证 |
| **Test Cases**           | **TC-DB-001**: User表成功+Patient表失败 → 事务回滚 ✅ <br/>**TC-DB-002**: 删除用户→关联Patient级联删除 ✅ <br/>**TC-DB-003**: 插入无医生诊断报告 → 外键阻断 ✅ |
| **Tools**                | • MySQL Workbench <br/>• pytest-django  <br/>• 数据库快照工具 |
| **Techniques**           | • 强制事务中断 <br/>• 外键约束测试<br/>• 数据完整性检查      |
| **Pass/Fail Criteria**   | **Pass**: 事务100%回滚，无孤儿记录，外键约束生效 <br/>**Fail**: 数据不一致或约束失效 |

### TS-DB-002: **性能与资源测试套件**

| 项目                     | 内容                                                         |
| ------------------------ | ------------------------------------------------------------ |
| **TSDI**                 | TS-DB-002                                                    |
| **执行脚本**             | `run_db_performance_tests.bat`                               |
| **测试状态**             | ✅ 已通过                                                     |
| **Category**             | Component Level - Performance & Scalability                  |
| **Feature to be tested** | 查询性能、连接池管理、索引优化                               |
| **Risk Mapping**         | **风险ID 2.2.001**：未索引慢查询<br/>**风险ID 2.2.002**：连接池耗尽 |
| **SDS Mapping**          | SDS 6.2 (高并发支持), SDS 2.2.4 (连接池机制)                 |
| **Test Method**          | **性能基准测试+压力测试**<br/>• 索引有效性验证 <br/>• 连接池饱和测试<br/>• 慢查询分析 |
| **Test Cases**           | **TC-DB-004**: 诊断报告按时间排序 → <100ms ✅<br/>**TC-DB-005**: 50并发DB操作 → 无连接超时 ✅<br/>**TC-DB-006**: EXPLAIN分析查询计划 → 索引命中 ✅ |
| **Tools**                | • MySQL EXPLAIN<br/>• Sysbench <br/>• 慢查询日志分析         |
| **Techniques**           | • 索引优化验证<br/>• 连接池监控<br/>• 查询执行计划分析       |

### TS-DB-003: **备份与安全测试套件**

| 项目                     | 内容                                                         |
| ------------------------ | ------------------------------------------------------------ |
| **TSDI**                 | TS-DB-003                                                    |
| **执行脚本**             | `run_db_backup_tests.bat`                                    |
| **测试状态**             | ✅ 已通过                                                     |
| **Category**             | Component Level - Disaster Recovery                          |
| **Feature to be tested** | 备份恢复机制、敏感数据脱敏                                   |
| **Risk Mapping**         | **风险ID 2.3.001**：备份失效<br/>**风险ID 2.3.002**：敏感数据泄露 |
| **SDS Mapping**          | SDS 6.1 (数据脱敏), SDS 6.2 (备份机制)                       |
| **Test Method**          | **备份恢复演练+安全审计**<br/>• 备份完整性检查<br/>• 模拟灾难恢复 <br/>• 敏感字段加密验证 |
| **Test Cases**           | **TC-DB-007**: 恢复24h前备份 → 数据一致 ✅<br/>**TC-DB-008**: 检查密码字段 → AES-256加密 ✅<br/>**TC-DB-009**: 日志文件审计 → 无明文敏感信息 ✅ |
| **Tools**                | • mysqldump <br/>• openssl<br/>• 日志分析脚本                |
| **Techniques**           | • 备份文件校验<br/>• 加密存储验证 <br/>• 日志脱敏检查        |

---

## 3. 测试执行总结

### 3.1 测试完成状态

| 测试模块         | 测试套件数 | 测试用例数 | 通过率 | 状态    |
| ---------------- | ---------- | ---------- | ------ | ------- |
| **用户权限管理模块测试** | 2 个套件 | 9 个用例  | 100%   | ✅ 完成 |
| **数据库模块测试** | 3 个套件  | 9 个用例 | 100%   | ✅ 完成 |
| **总计**         | 5 个套件 | 18 个用例 | 100%   | ✅ 完成 |

### 3.2 质量指标达成

| 质量维度       | 目标值   | 实际值 | 状态    |
| -------------- | -------- | ------ | ------- |
| **功能正确率** | ≥ 90% | 100% | ✅ 达标 |
| **数据库性能** | < 10s    | 0.1s | ✅ 达标 |
| **并发成功率** | ≥ 80%    | 100%   | ✅ 达标 |

---

## 4. 风险覆盖与 SDS 映射总结

### 4.1 用户权限管理模块测试风险覆盖

| 测试套件      | 覆盖的风险 ID             | 对应 SDS       |
| ------------- | ------------------------- | -------------- |
| **TS-UM-001** | 1.2.001, 1.2.002          | SDS 3.1, 5.1.1 |
| **TS-UM-002** | 1.3.001, 1.3.002, 1.1.001 | SDS 3.1, 2.5.3 |

### 4.2 数据库模块风险覆盖

| 测试套件      | 覆盖的风险 ID    | 对应 SDS       |
| ------------- | ---------------- | -------------- |
| **TS-DB-001** | 2.1.201, 2.1.202 | SDS 2.2.4, 6.4 |
| **TS-DB-002** | 2.2.201, 2.2.202 | SDS 6.2        |
| **TS-DB-003** | 2.3.201, 2.3.202 | SDS 6.1, 6.2   |

### 4.3 测试完整性验证

#### 4.3.1 风险优先级覆盖

| 优先级         | 风险数量 | 已覆盖 | 覆盖率 | 测试策略 |
| -------------- | -------- | ------ | ------ | -------- |
| **高 (≥20)**   | 5        | 5      | 100%   | 广泛测试 |
| **中 (12-16)** | 6        | 6      | 100%   | 重点测试 |
| **低 (≤9)**    | 1        | 1      | 100%   | 适度测试 |

#### 4.3.2 SDS 需求覆盖

| SDS 分类           | 需求数量 | 已测试 | 覆盖率 |
| ------------------ | -------- | ------ | ------ |
| **功能需求 (1.x)** | 4        | 4      | 100%   |
| **系统架构 (2.x)** | 8        | 8      | 100%   |
| **诊断功能 (3.x)** | 3        | 3      | 100%   |
| **性能需求 (4.x)** | 2        | 2      | 100%   |
| **质量属性 (6.x)** | 3        | 3      | 100%   |

### 4.4 测试执行状态汇总

| 质量维度       | 测试结果 | 目标值  | 实际值     | 风险缓解效果 |
| -------------- | -------- | ------- | ---------- | ------------ |
| **功能正确性** | ✅ 通过  | 100%    | 100%       | 完美         |
| **性能效率**   | ✅ 通过  | <30s    | 0.1s | 远超预期     |
| **系统可靠性** | ✅ 通过  | ≥75%    | 100%       | 完美         |

**备注**:

- 所有 11 个高中优先级风险均得到有效缓解
- 20 个 SDS 需求 100% 覆盖测试
- 18 个测试用例全部通过，0 失败
- 系统整体质量评级：A 级 (优秀)

**相关文档**:

- 测试设计详情: `Test_Design_Document_Final.md`
- 测试结果分析: `Test_Result_Analysis_Report.md`
- 风险分析表: `Risk Analysis Table for User Authentication and Database.md`
