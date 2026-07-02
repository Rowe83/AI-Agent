import requests
import logging

# 1. 启动符合工业标准的基础日志记录器
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)

def parse_and_audit_llm_response(api_url):
    logging.info(f"📡 开始请求大模型网关: {api_url}")
    
    try:
        # 模拟请求一个网络沙箱
        res = requests.post(api_url, json={"prompt": "Ping"}, timeout=3)
        res.raise_for_status() # 状态码非 200 触发 HTTPError 异常
        
        # 2. 假设网络成功，解析响应
        payload = res.json()
        
        # ⚠️ 故意模拟一个潜在的“脏数据”结构
        # 假设真实业务必须要拿 choices[0]["score"]，如果大模型抽风没吐出 choices 就会触发 KeyError
        raw_score = payload["json"]["prompt"] 
        
        # ⚠️ 故意将字符串转为浮点数，如果大模型吐出的是 "ERROR" 就会触发 ValueError
        final_score = float(raw_score) 
        
    except requests.RequestException as net_err:
        logging.error(f"❌ [网络故障] 无法连接到 AI 服务网关: {net_err}")
    except KeyError as key_err:
        logging.error(f"❌ [报文畸形] 大模型返回数据缺少核心字段: {key_err}")
    except ValueError as val_err:
        logging.error(f"❌ [数据变异] 无法对指标进行类型转换: {val_err}")
    except Exception as unknown_err:
        logging.critical(f"🚨 [系统崩溃] 遭遇未知的灾难性危机: {unknown_err}")
    else:
        # 🌟 只有完美无瑕通过时才运行
        logging.info(f"🎉 [审计通过] 成功捕获大模型指标，最终结算分: {final_score}")
    finally:
        # 🌟 无论成败，都要合入审计回执
        logging.info("🏁 [管道闭环] 当前请求会话上下文已安全销毁。")

if __name__ == "__main__":
    # 场景 A：故意请求一个会触发 404 的错误地址，观测 Requests 拦截
    parse_and_audit_llm_response("https://httpbin.org/status/404")
    
    print("\n" + "="*50 + "\n")
    
    # 场景 B：故意请求正确地址，但由于我们代码里逻辑写的 `float(payload["json"]["prompt"])` 
    # 此时传入的值是 "Ping" 字符串，强转 float 必然引爆 ValueError
    parse_and_audit_llm_response("https://httpbin.org/post")