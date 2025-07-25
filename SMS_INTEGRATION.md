# 短信验证码集成指南

本文档说明如何为K12家校学习资料共享平台集成短信验证码功能。

## 当前状态

- ✅ **密码确认验证**：已实现注册时两次密码输入验证
- ✅ **短信服务框架**：已创建基础短信服务框架
- ⚠️ **短信验证码**：需要配置短信服务商才能使用

## 快速启用密码确认验证

当前版本已经实现了注册时的密码确认验证功能：

1. **注册时需要输入两次密码**
2. **前端实时验证密码一致性**
3. **后端验证密码匹配**
4. **密码输入框支持显示/隐藏**

这种方式无需额外成本，能有效防止用户因输入错误导致的密码问题。

## 短信验证码集成步骤

如果您希望使用短信验证码功能，请按以下步骤操作：

### 1. 选择短信服务商

推荐的短信服务商：

#### 阿里云短信服务
- **费用**：约0.045元/条
- **到达率**：99%+
- **支持**：国内外短信
- **文档**：https://help.aliyun.com/product/44282.html

#### 腾讯云短信
- **费用**：约0.045元/条
- **到达率**：99%+
- **支持**：国内外短信
- **文档**：https://cloud.tencent.com/product/sms

#### 华为云短信
- **费用**：约0.04元/条
- **到达率**：99%+
- **支持**：国内短信
- **文档**：https://www.huaweicloud.com/product/msgsms.html

### 2. 获取API密钥

以阿里云为例：

1. 注册阿里云账号
2. 开通短信服务
3. 创建签名和模板
4. 获取AccessKey ID和AccessKey Secret

### 3. 安装SDK

```bash
# 阿里云短信SDK
pip install alibabacloud-dysmsapi20170525

# 腾讯云短信SDK
pip install tencentcloud-sdk-python

# 华为云短信SDK
pip install huaweicloudsdksms
```

### 4. 配置环境变量

在`.env`文件中添加：

```env
# 短信服务配置
SMS_PROVIDER=aliyun  # aliyun, tencent, huawei
SMS_ACCESS_KEY_ID=your_access_key_id
SMS_ACCESS_KEY_SECRET=your_access_key_secret
SMS_SIGN_NAME=您的签名
SMS_TEMPLATE_CODE=SMS_XXXXXX
```

### 5. 修改短信服务实现

编辑`app/services/sms_service.py`文件：

```python
async def _send_sms(self, phone: str, code: str, code_type: str) -> bool:
    """发送短信的具体实现"""
    
    if settings.SMS_PROVIDER == "aliyun":
        return await self._send_aliyun_sms(phone, code)
    elif settings.SMS_PROVIDER == "tencent":
        return await self._send_tencent_sms(phone, code)
    elif settings.SMS_PROVIDER == "huawei":
        return await self._send_huawei_sms(phone, code)
    else:
        return False

async def _send_aliyun_sms(self, phone: str, code: str) -> bool:
    """阿里云短信发送"""
    try:
        from alibabacloud_dysmsapi20170525.client import Client
        from alibabacloud_dysmsapi20170525 import models
        from alibabacloud_tea_openapi import models as open_api_models
        
        config = open_api_models.Config(
            access_key_id=settings.SMS_ACCESS_KEY_ID,
            access_key_secret=settings.SMS_ACCESS_KEY_SECRET,
            endpoint='dysmsapi.aliyuncs.com'
        )
        
        client = Client(config)
        
        request = models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=settings.SMS_SIGN_NAME,
            template_code=settings.SMS_TEMPLATE_CODE,
            template_param=f'{{"code":"{code}"}}'
        )
        
        response = await client.send_sms_async(request)
        return response.body.code == "OK"
        
    except Exception as e:
        print(f"阿里云短信发送失败: {e}")
        return False
```

### 6. 启用前端验证码功能

编辑`static/js/app.js`：

```javascript
// 将 enableSmsVerification 设置为 true
enableSmsVerification: true,
```

编辑`static/index.html`，取消验证码相关代码的注释。

### 7. 更新注册验证规则

如果启用短信验证码，可以在前端添加验证码验证规则：

```javascript
registerRules: {
    // ... 其他规则
    verification_code: [
        { required: true, message: '请输入验证码', trigger: 'blur' },
        { len: 6, message: '验证码长度为6位', trigger: 'blur' }
    ]
}
```

## 成本估算

以每月1000个新用户注册为例：

- **阿里云**：1000 × 0.045 = 45元/月
- **腾讯云**：1000 × 0.045 = 45元/月
- **华为云**：1000 × 0.04 = 40元/月

## 安全建议

1. **频率限制**：同一手机号60秒内只能发送一次
2. **次数限制**：同一手机号每天最多发送5次
3. **IP限制**：同一IP每小时最多发送10次
4. **验证码有效期**：5分钟内有效
5. **错误次数限制**：最多验证3次

## 测试建议

1. **开发环境**：使用模拟发送，在控制台输出验证码
2. **测试环境**：使用真实短信服务，限制测试手机号
3. **生产环境**：完整的短信服务和安全策略

## 故障处理

### 常见问题

1. **短信发送失败**
   - 检查API密钥是否正确
   - 确认短信模板是否审核通过
   - 验证手机号格式是否正确

2. **验证码收不到**
   - 检查手机号是否在黑名单中
   - 确认短信签名是否合规
   - 查看短信服务商控制台日志

3. **验证码验证失败**
   - 检查验证码是否过期
   - 确认验证码输入是否正确
   - 验证时间同步是否正常

## 总结

- **推荐方案**：当前的密码确认验证已经能满足大部分需求
- **可选升级**：如需更高安全性，可按本文档集成短信验证码
- **成本考虑**：短信验证码有一定成本，建议根据实际需求决定是否启用

如有疑问，请参考各短信服务商的官方文档或联系技术支持。
