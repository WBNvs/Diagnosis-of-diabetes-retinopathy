import pytest
import requests
import time
import threading
from datetime import datetime, timedelta
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# 基础配置
BASE_URL = "http://localhost:5000"  # Flask 后端地址
VALID_DOCTOR = {"username": "doctor1", "password": "P@ssw0rd123", "role": "doctor"}
VALID_PATIENT = {"username": "patient1", "password": "SecurePass!456", "role": "patient"}
INVALID_ROLE = {"username": "hacker", "password": "Test123!", "role": "admin"}
WEAK_PASSWORD = {"username": "weak_user", "password": "123456", "role": "patient"}

# ======================== TS-UM-001: 功能正确性测试 ========================

class TestFunctionalCorrectness:
    """TS-UM-001 功能正确性测试套件"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前清理测试用户"""
        self._delete_user(VALID_DOCTOR["username"])
        self._delete_user(VALID_PATIENT["username"])
        self._delete_user(INVALID_ROLE["username"])
        self._delete_user(WEAK_PASSWORD["username"])
        
    def _delete_user(self, username):
        """辅助函数：删除测试用户"""
        response = requests.get(f"{BASE_URL}/api/users/")
        if response.status_code == 200:
            for user in response.json()["data"]:
                if user["username"] == username:
                    requests.delete(f"{BASE_URL}/api/users/{user['userId']}")
    
    def test_create_doctor(self):
        """TC-UM-001: 创建医生用户"""
        # 创建用户
        response = requests.post(f"{BASE_URL}/api/users/", json=VALID_DOCTOR)
        assert response.status_code == 201
        
        # 验证数据库
        user_list = requests.get(f"{BASE_URL}/api/users/").json()["data"]
        doctor_exists = any(u["username"] == VALID_DOCTOR["username"] and u["role"] == "doctor" 
                            for u in user_list)
        assert doctor_exists
    
    def test_create_patient(self):
        """TC-UM-002: 创建患者用户"""
        # 创建用户
        response = requests.post(f"{BASE_URL}/api/users/", json=VALID_PATIENT)
        assert response.status_code == 201
        
        # 验证用户列表
        user_list = requests.get(f"{BASE_URL}/api/users/").json()["data"]
        patient_exists = any(u["username"] == VALID_PATIENT["username"] and u["role"] == "patient" 
                             for u in user_list)
        assert patient_exists
    
    def test_invalid_role_creation(self):
        """TC-UM-003: 非法角色创建用户"""
        response = requests.post(f"{BASE_URL}/api/users/", json=INVALID_ROLE)
        assert response.status_code == 400
        assert "Invalid role" in response.json()["msg"]
    
    def test_patient_access_doctor_api(self):
        """TC-UM-004: 患者访问医生专属API"""
        # 创建患者
        requests.post(f"{BASE_URL}/api/users/", json=VALID_PATIENT)
        
        # 患者登录
        login_res = requests.post(f"{BASE_URL}/api/auth/login", 
                                 json={"username": VALID_PATIENT["username"], 
                                       "password": VALID_PATIENT["password"]})
        token = login_res.json()["data"]["token"]
        
        # 访问医生API
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/doctor/reports", headers=headers)
        assert response.status_code == 403
    
    def test_doctor_access_patient_api(self):
        """TC-UM-005: 医生访问患者专属API"""
        # 创建医生
        requests.post(f"{BASE_URL}/api/users/", json=VALID_DOCTOR)
        
        # 医生登录
        login_res = requests.post(f"{BASE_URL}/api/auth/login", 
                                 json={"username": VALID_DOCTOR["username"], 
                                       "password": VALID_DOCTOR["password"]})
        token = login_res.json()["data"]["token"]
        
        # 访问其他患者API
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/patient/1002/history", headers=headers)
        assert response.status_code == 403

# ======================== TS-UM-002: 安全性与可靠性测试 ========================

class TestSecurityReliability:
    """TS-UM-002 安全性与可靠性测试套件"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前清理测试用户"""
        self._delete_user(VALID_DOCTOR["username"])
        self._delete_user(WEAK_PASSWORD["username"])
        
    def _delete_user(self, username):
        """辅助函数：删除测试用户"""
        response = requests.get(f"{BASE_URL}/api/users/")
        if response.status_code == 200:
            for user in response.json()["data"]:
                if user["username"] == username:
                    requests.delete(f"{BASE_URL}/api/users/{user['userId']}")
    
    def test_weak_password_policy(self):
        """TC-UM-006: 弱密码策略"""
        response = requests.post(f"{BASE_URL}/api/users/", json=WEAK_PASSWORD)
        assert response.status_code == 400
        assert "Password must contain" in response.json()["msg"]
    
    def test_token_expiration(self):
        """TC-UM-007: Token过期验证"""
        # 创建并登录用户
        requests.post(f"{BASE_URL}/api/users/", json=VALID_DOCTOR)
        login_res = requests.post(f"{BASE_URL}/api/auth/login", 
                                 json={"username": VALID_DOCTOR["username"], 
                                       "password": VALID_DOCTOR["password"]})
        token = login_res.json()["data"]["token"]
        
        # 等待Token过期 (假设Token有效期为30分钟)
        time.sleep(35 * 60)  # 等待35分钟
        
        # 使用过期Token访问
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
        assert response.status_code == 401
    
    def test_high_concurrency_login(self):
        """TC-UM-008: 高并发登录测试"""
        # 创建测试用户
        requests.post(f"{BASE_URL}/api/users/", json=VALID_DOCTOR)
        
        # 并发测试参数
        NUM_THREADS = 100
        results = []
        lock = threading.Lock()
        
        def login_task():
            """单个登录任务"""
            start_time = time.time()
            try:
                res = requests.post(f"{BASE_URL}/api/auth/login", 
                                    json={"username": VALID_DOCTOR["username"], 
                                          "password": VALID_DOCTOR["password"]},
                                    timeout=5)
                with lock:
                    results.append({
                        "status": res.status_code,
                        "time": time.time() - start_time
                    })
            except Exception as e:
                with lock:
                    results.append({"error": str(e)})
        
        # 启动并发线程
        threads = []
        for _ in range(NUM_THREADS):
            t = threading.Thread(target=login_task)
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 结果分析
        success_count = sum(1 for r in results if r.get("status") == 200)
        response_times = [r["time"] for r in results if "time" in r]
        
        # 断言
        assert success_count >= 95  # 成功率≥95%
        assert sum(response_times) / len(response_times) < 0.5  # 平均响应<500ms
    
    def test_account_lock_after_failed_attempts(self):
        """TC-UM-009: 账户锁定机制"""
        # 创建测试用户
        requests.post(f"{BASE_URL}/api/users/", json=VALID_DOCTOR)
        
        # 连续5次错误密码
        for _ in range(5):
            response = requests.post(f"{BASE_URL}/api/auth/login", 
                                    json={"username": VALID_DOCTOR["username"], 
                                          "password": "wrong_password"})
            assert response.status_code == 401
        
        # 第6次尝试
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                                json={"username": VALID_DOCTOR["username"], 
                                      "password": VALID_DOCTOR["password"]})
        assert response.status_code == 423  # 账户锁定
    
    def test_token_tamper_protection(self):
        """TC-UM-010: Token防篡改"""
        # 创建并登录用户
        requests.post(f"{BASE_URL}/api/users/", json=VALID_DOCTOR)
        login_res = requests.post(f"{BASE_URL}/api/auth/login", 
                                 json={"username": VALID_DOCTOR["username"], 
                                       "password": VALID_DOCTOR["password"]})
        token = login_res.json()["data"]["token"]
        
        # 篡改Token
        decoded = jwt.decode(token, options={"verify_signature": False})
        decoded["role"] = "admin"  # 提升权限
        
        # 重新编码篡改后的Token
        public_key = """
        -----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnzyis1ZjfNB0bBgKFMSv
        vkTtwlvBsaJq7S5wA+kzeVOVpVWwkWdVha4s38XM/pa/yr47av7+z3VTmvDRyAHc
        aT92whREFpLv9cj5lTeJSibyr/Mrm/YtjCZVWgaOYIhwrXwKLqPr/11inWsAkfIy
        tvHWTxZYEcXLgAXFuUuaS3uF9gEiNQwzGTU1v0FqkqTBr4B8nW3HCN47XUu0t8Y0
        e+lf4s4OxQawWD79J9/5d3Ry0vbV3Am1FtGJiJvOwRsIfVChDpYStTcHTCMqtvWb
        V6L11BWkpzGXSW4Hv43qa+GSYOD2QU68Mb59oSk2OB+BtOLpJofmbGEGgvmwyCI9
        MwIDAQAB
        -----END PUBLIC KEY-----
        """
        public_key = serialization.load_pem_public_key(
            public_key.encode(), 
            backend=default_backend()
        )
        
        tampered_token = jwt.encode(decoded, public_key, algorithm="RS256")
        
        # 使用篡改Token访问
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
        assert response.status_code == 401  # 未授权

# ======================== 测试执行入口 ========================

if __name__ == "__main__":
    pytest.main(["-v", "--html=test_reports/um_test_report.html"])