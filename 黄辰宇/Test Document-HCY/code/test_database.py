import pytest
import time
import os
import subprocess
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, exc, inspect
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet

# ======================== 数据库配置 ========================
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "rootmysql.1024",
    "database": "ddr_database"
}
TEST_DB_URI = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# 备份配置
BACKUP_DIR = "./db_backups"
BACKUP_FILE = f"{BACKUP_DIR}/dr_test_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

# 加密配置
ENCRYPTION_KEY = Fernet.generate_key()
FERNET = Fernet(ENCRYPTION_KEY)

# ======================== 测试准备 ========================
@pytest.fixture(scope="module")
def db_engine():
    """创建数据库引擎"""
    engine = create_engine(TEST_DB_URI, pool_size=20, max_overflow=10)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """创建数据库会话，测试后回滚"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def setup_module(module):
    """模块级别设置：创建备份目录"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 创建测试表结构
    engine = create_engine(TEST_DB_URI)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS User (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role ENUM('patient', 'doctor') NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS Patient (
                patient_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(100) NOT NULL,
                gender ENUM('male', 'female'),
                date_of_birth DATE NOT NULL,
                contact_info VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS Diagnose (
                diagnosis_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                diagnosis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path VARCHAR(255),
                confirmed BOOLEAN DEFAULT FALSE,
                diagnose_date DATE NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES User(user_id)
            )
        """))
        conn.commit()
    engine.dispose()

# ======================== TS-DB-001: 事务一致性测试 ========================

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
    
    def test_foreign_key_cascade_delete(self, db_session):
        """TC-DB-002: 外键级联删除测试"""
        # 插入用户和患者
        user_result = db_session.execute(text("""
            INSERT INTO User (username, password, role)
            VALUES (:username, :password, :role)
        """), {
            "username": "cascade_test", 
            "password": FERNET.encrypt(b"Pass123").decode(),
            "role": "patient"
        })
        user_id = user_result.lastrowid
        
        db_session.execute(text("""
            INSERT INTO Patient (user_id, name, date_of_birth)
            VALUES (:user_id, :name, :dob)
        """), {
            "user_id": user_id,
            "name": "Test Patient",
            "dob": "1990-01-01"
        })
        db_session.commit()
        
        # 删除用户
        db_session.execute(text("DELETE FROM User WHERE user_id = :user_id"), {"user_id": user_id})
        db_session.commit()
        
        # 验证患者记录也被删除
        patient = db_session.execute(
            text("SELECT * FROM Patient WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        assert patient is None
    
    def test_foreign_key_constraint(self, db_session):
        """TC-DB-003: 外键约束测试"""
        # 尝试插入无关联医生的诊断报告
        with pytest.raises(exc.IntegrityError):
            db_session.execute(text("""
                INSERT INTO Diagnose (patient_id, doctor_id, diagnose_date)
                VALUES (:patient_id, :doctor_id, CURDATE())
            """), {
                "patient_id": 999,  # 不存在
                "doctor_id": 999     # 不存在
            })
            db_session.commit()
    
    def test_concurrent_update(self, db_engine):
        """TC-DB-004: 并发更新测试"""
        # 创建测试数据
        with db_engine.connect() as conn:
            conn.execute(text("DELETE FROM Diagnose WHERE diagnosis_id = 999"))
            conn.execute(text("""
                INSERT INTO Diagnose (diagnosis_id, patient_id, doctor_id, diagnose_date)
                VALUES (999, 1, 1, CURDATE())
            """))
            conn.commit()
        
        # 并发更新函数
        def update_diagnosis(session_id):
            with db_engine.connect() as conn:
                conn.execute(text("SET SESSION transaction_isolation='READ-COMMITTED'"))
                transaction = conn.begin()
                try:
                    # 模拟业务处理时间
                    time.sleep(0.5 if session_id == 1 else 1)
                    
                    # 会话1: 更新为confirmed
                    if session_id == 1:
                        conn.execute(text("""
                            UPDATE Diagnose SET confirmed = TRUE 
                            WHERE diagnosis_id = 999
                        """))
                    
                    # 会话2: 更新为image_path
                    else:
                        conn.execute(text("""
                            UPDATE Diagnose SET image_path = '/path/to/image.jpg' 
                            WHERE diagnosis_id = 999
                        """))
                    
                    transaction.commit()
                except Exception:
                    transaction.rollback()
                    raise
        
        # 启动两个并发会话
        threads = []
        for i in range(1, 3):
            t = threading.Thread(target=update_diagnosis, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 验证最终状态
        with db_engine.connect() as conn:
            result = conn.execute(
                text("SELECT confirmed, image_path FROM Diagnose WHERE diagnosis_id = 999")
            ).fetchone()
            
            # 根据提交顺序，最后一个提交的会覆盖前面的
            assert result == (False, '/path/to/image.jpg') or result == (True, None)

# ======================== TS-DB-002: 性能与资源测试 ========================

class TestPerformanceResources:
    """TS-DB-002 性能与资源测试套件"""
    
    @pytest.fixture(autouse=True)
    def setup_data(self, db_engine):
        """准备测试数据"""
        with db_engine.connect() as conn:
            # 清空并填充诊断表
            conn.execute(text("TRUNCATE TABLE Diagnose"))
            
            # 插入10万条测试数据
            for i in range(1, 100001):
                conn.execute(text("""
                    INSERT INTO Diagnose (patient_id, doctor_id, diagnosis_time, 
                                        diagnose_date, confirmed)
                    VALUES (:patient_id, :doctor_id, NOW(), CURDATE(), :confirmed)
                """), {
                    "patient_id": i % 1000 + 1,
                    "doctor_id": i % 50 + 1,
                    "confirmed": i % 2 == 0
                })
                
                # 每1000条提交一次
                if i % 1000 == 0:
                    conn.commit()
            conn.commit()
    
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
    
    def test_connection_pool_stress(self, db_engine):
        """TC-DB-006: 连接池压力测试"""
        # 获取连接池状态
        def get_pool_status():
            return {
                "checkedin": db_engine.pool.status().checkedin,
                "checkedout": db_engine.pool.status().checkedout,
                "overflow": db_engine.pool.status().overflow
            }
        
        initial_status = get_pool_status()
        
        # 并发查询函数
        def run_query(query_id):
            try:
                with db_engine.connect() as conn:
                    conn.execute(text("SELECT SLEEP(0.1)"))
            except Exception as e:
                return f"Query {query_id} failed: {str(e)}"
            return None
        
        # 启动50个并发连接
        threads = []
        results = []
        for i in range(50):
            t = threading.Thread(target=lambda i=i: results.append(run_query(i)))
            threads.append(t)
            t.start()
        
        # 监控连接池状态
        time.sleep(0.5)  # 等待连接建立
        stress_status = get_pool_status()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 检查错误
        errors = [res for res in results if res is not None]
        assert not errors, f"连接错误: {errors}"
        
        # 验证连接池状态
        final_status = get_pool_status()
        assert stress_status['overflow'] == 0, "连接池溢出"
        assert final_status['checkedout'] == 0, "连接未正确释放"
        assert final_status['overflow'] == 0, "最终状态有溢出连接"
    
    def test_composite_index_performance(self, db_engine):
        """TC-DB-007: 复合索引性能测试"""
        # 创建复合索引
        with db_engine.connect() as conn:
            inspector = inspect(conn)
            indexes = inspector.get_indexes('Diagnose')
            if not any(idx['name'] == 'idx_confirmed_date' for idx in indexes):
                conn.execute(text("""
                    CREATE INDEX idx_confirmed_date 
                    ON Diagnose(confirmed, diagnose_date)
                """))
        
        # 执行多条件查询
        start_time = time.time()
        with db_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM Diagnose 
                WHERE confirmed = FALSE 
                AND diagnose_date > '2023-01-01'
                LIMIT 1000
            """)).fetchall()
        query_time = (time.time() - start_time) * 1000  # 毫秒
        
        # 验证性能
        assert len(result) > 0
        assert query_time < 200, f"查询耗时 {query_time:.2f}ms 超过200ms阈值"
    
    def test_pagination_performance(self, db_engine):
        """TC-DB-008: 大数据量分页性能测试"""
        # 执行分页查询
        start_time = time.time()
        with db_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM Diagnose 
                ORDER BY diagnosis_id
                LIMIT 10000, 100
            """)).fetchall()
        query_time = (time.time() - start_time) * 1000  # 毫秒
        
        # 验证性能
        assert len(result) == 100
        assert query_time < 500, f"分页查询耗时 {query_time:.2f}ms 超过500ms阈值"

# ======================== TS-DB-003: 备份与安全测试 ========================

class TestBackupSecurity:
    """TS-DB-003 备份与安全测试套件"""
    
    @pytest.fixture(autouse=True)
    def setup_data(self, db_engine):
        """准备测试数据"""
        with db_engine.connect() as conn:
            # 插入测试用户
            conn.execute(text("DELETE FROM User WHERE username = 'backup_test'"))
            conn.execute(text("""
                INSERT INTO User (username, password, role)
                VALUES ('backup_test', :password, 'patient')
            """), {"password": FERNET.encrypt(b"Backup@123").decode()})
            conn.commit()
    
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
    
    def test_password_encryption(self, db_engine):
        """TC-DB-010: 密码加密验证"""
        with db_engine.connect() as conn:
            # 获取加密密码
            encrypted_password = conn.execute(text("""
                SELECT password FROM User 
                WHERE username = 'backup_test'
            """)).scalar()
            
            # 验证加密格式
            assert encrypted_password.startswith('gAAAA'), "密码未加密存储"
            
            # 解密验证
            decrypted = FERNET.decrypt(encrypted_password.encode()).decode()
            assert decrypted == "Backup@123", "密码解密后不匹配"
    
    def test_log_sanitization(self, db_engine):
        """TC-DB-011: 日志脱敏测试"""
        # 模拟包含敏感信息的查询
        with db_engine.connect() as conn:
            try:
                # 故意触发错误（包含密码）
                conn.execute(text("""
                    SELECT * FROM User 
                    WHERE username = 'backup_test' 
                    AND password = 'Backup@123'
                """))
            except exc.ProgrammingError as e:
                error_message = str(e)
        
        # 验证日志中不包含明文密码
        assert "Backup@123" not in error_message, "日志中包含明文密码"
        assert "*****" in error_message or "REDACTED" in error_message, "日志未脱敏"
    
    def test_disaster_recovery(self, db_engine):
        """TC-DB-012: 灾难恢复测试"""
        # 创建备份
        backup_cmd = (
            f"mysqldump -h{DB_CONFIG['host']} -u{DB_CONFIG['user']} "
            f"-p{DB_CONFIG['password']} {DB_CONFIG['database']} > {BACKUP_FILE}"
        )
        subprocess.run(backup_cmd, shell=True, check=True)
        
        # 模拟数据损坏
        with db_engine.connect() as conn:
            conn.execute(text("DROP TABLE User"))
            conn.commit()
        
        # 记录恢复开始时间
        recovery_start = datetime.now()
        
        # 执行恢复
        restore_cmd = (
            f"mysql -h{DB_CONFIG['host']} -u{DB_CONFIG['user']} "
            f"-p{DB_CONFIG['password']} {DB_CONFIG['database']} < {BACKUP_FILE}"
        )
        subprocess.run(restore_cmd, shell=True, check=True)
        
        # 验证恢复成功
        recovery_time = (datetime.now() - recovery_start).total_seconds() / 60
        assert recovery_time < 60, f"恢复时间 {recovery_time:.1f} 分钟超过1小时阈值"
        
        with db_engine.connect() as conn:
            tables = conn.execute(text("SHOW TABLES LIKE 'User'")).fetchone()
            assert tables is not None, "User表未恢复"
            
            user_count = conn.execute(text("SELECT COUNT(*) FROM User")).scalar()
            assert user_count > 0, "用户数据未恢复"

# ======================== 测试执行入口 ========================

if __name__ == "__main__":
    pytest.main([
        "-v", 
        "--html=test_reports/db_test_report.html",
        "--capture=no"
    ])