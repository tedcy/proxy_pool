import asyncio
from helper.validator import httpTimeOutValidator

async def test_http_time_out_validator_success():
    result = await httpTimeOutValidator('47.95.35.146:8091')
    print(f"验证结果: {result}")

if __name__ == '__main__':
    # 创建事件循环并运行异步测试函数
    asyncio.run(test_http_time_out_validator_success())
