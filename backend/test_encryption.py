#!/usr/bin/env python3
"""
测试RabbitMQ密码加密功能
"""
import base64
from cryptography.fernet import Fernet

# 生成一个有效的测试密钥
TEST_KEY = Fernet.generate_key()

def encrypt_password(password: str) -> str:
    """加密密码"""
    f = Fernet(TEST_KEY)
    encrypted = f.encrypt(password.encode())
    return encrypted.decode()

def decrypt_password(encrypted_password: str) -> str:
    """解密密码"""
    f = Fernet(TEST_KEY)
    decrypted = f.decrypt(encrypted_password.encode())
    return decrypted.decode()

# 测试
print('='*60)
print('密码加密/解密功能测试')
print('='*60)

test_cases = [
    'simple123',
    'my-secret-password-123',
    'P@ssw0rd!@#$%^&*()',
    'a' * 50,  # 长密码
]

all_passed = True

for test_password in test_cases:
    try:
        # 加密
        encrypted = encrypt_password(test_password)
        # 解密
        decrypted = decrypt_password(encrypted)

        # 验证
        if decrypted == test_password:
            print(f'✅ 测试通过: {test_password[:20]:20} -> 加密成功 -> 解密正确')
        else:
            print(f'❌ 测试失败: 密码不一致')
            print(f'   原始: {test_password}')
            print(f'   解密: {decrypted}')
            all_passed = False
    except Exception as e:
        print(f'❌ 测试失败: {test_password[:20]:20} - {e}')
        all_passed = False

print('='*60)
if all_passed:
    print('✅ 所有测试通过！')
else:
    print('❌ 部分测试失败')

# 显示加密示例
print('\n加密示例:')
sample = 'my-rabbitmq-password'
encrypted = encrypt_password(sample)
print(f'原始密码: {sample}')
print(f'加密后: {encrypted}')
print(f'加密长度: {len(encrypted)} 字符')
