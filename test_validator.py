import asyncio
from helper.validator import httpTimeOutValidator
from fetcher.proxyFetcher import ProxyFetcher

async def test_http_time_out_validator_success():
    result = await httpTimeOutValidator('47.95.35.146:8091')
    print(f"验证结果: {result}")

if __name__ == '__main__':
    # 创建事件循环并运行异步测试函数
    # asyncio.run(test_http_time_out_validator_success())
    
    print("开始测试 freeProxy21 函数...")
    try:
        # 首先使用本地数据文件测试
        print("使用本地数据文件...")
        fetcher = ProxyFetcher.freeProxy21(use_local_data=True)
        count = 0
        for proxy in fetcher:
            print(f"找到代理: {proxy.strip()}")
            count += 1
        print(f"总共找到 {count} 个代理")
        
        # 然后尝试使用网络请求
        print("\n使用网络请求...")
        fetcher = ProxyFetcher.freeProxy21(use_local_data=False)
        count = 0
        for proxy in fetcher:
            print(f"找到代理: {proxy.strip()}")
            count += 1
        print(f"总共找到 {count} 个代理")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
