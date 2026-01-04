import os
import requests
import json

# 从 GitHub Secrets 获取配置
ID = os.environ.get('DNSPOD_ID')
TOKEN = os.environ.get('DNSPOD_TOKEN')
DOMAIN = os.environ.get('DOMAINS')
SUB_DOMAIN = os.environ.get('SUB_DOMAINS')

def get_best_ips(url):
    """
    从指定 URL 获取优选 IP 列表
    """
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        # 只要前 3 个最快的 IP (如果有这么多的话)
        return resp.text.strip().split('\n')[:3]
    except Exception as e:
        print(f"从 {url} 获取 IP 失败: {e}")
        return []

def get_record_id(desired_line):
    """
    获取指定线路的现有记录 ID
    """
    api_url = "https://dnsapi.cn/Record.List"
    data = {
        "login_token": f"{ID},{TOKEN}",
        "format": "json",
        "domain": DOMAIN,
        "sub_domain": SUB_DOMAIN,
        "record_type": "A"
    }
    
    try:
        response = requests.post(api_url, data=data)
        response.raise_for_status()
        records = response.json().get('records', [])
        
        # 遍历查找匹配线路的记录
        for record in records:
            if record['line'] == desired_line:
                return record['id']
                
        return None
    except Exception as e:
        print(f"查询记录列表失败: {e}")
        print(f"响应内容: {response.text if 'response' in locals() else 'No response'}")
        return None

def update_dnspod(ip, line):
    """
    调用 DNSPod API 修改或创建 A 记录
    """
    print(f"正在处理线路 [{line}] 的 IP 更新: {ip}")
    
    data = {
        "login_token": f"{ID},{TOKEN}",
        "format": "json",
        "domain": DOMAIN,
        "sub_domain": SUB_DOMAIN,
        "record_type": "A",
        "record_line": line,
        "value": ip
    }

    # 1. 查找现有记录
    record_id = get_record_id(line)

    if record_id:
        # 2. 修改记录
        modify_url = "https://dnsapi.cn/Record.Modify"
        data['record_id'] = record_id
        try:
            res = requests.post(modify_url, data=data).json()
            if res['status']['code'] == '1':
                print(f"线路 [{line}] 更新成功: {res['status']['message']}")
            else:
                print(f"线路 [{line}] 更新失败: {res['status']['message']}")
        except Exception as e:
             print(f"线路 [{line}] 修改请求异常: {e}")
    else:
        # 3. 如果不存在则新建
        create_url = "https://dnsapi.cn/Record.Create"
        try:
            res = requests.post(create_url, data=data).json()
            if res['status']['code'] == '1':
                print(f"线路 [{line}] 创建成功: {res['status']['message']}")
            else:
                print(f"线路 [{line}] 创建失败: {res['status']['message']}")
        except Exception as e:
            print(f"线路 [{line}] 创建请求异常: {e}")

if __name__ == "__main__":
    # 定义线路和对应的 IP 来源
    SOURCES = [
        {"line": "电信", "url": "https://raw.githubusercontent.com/ymyuuu/IPDB/main/telecom.txt"},
        {"line": "联通", "url": "https://raw.githubusercontent.com/ymyuuu/IPDB/main/unicom.txt"},
        {"line": "移动", "url": "https://raw.githubusercontent.com/ymyuuu/IPDB/main/mobile.txt"},
        {"line": "默认", "url": "https://raw.githubusercontent.com/ymyuuu/IPDB/main/bestcf.txt"}
    ]

    if not all([ID, TOKEN, DOMAIN, SUB_DOMAIN]):
        print("错误: 缺少必要的环境变量 (DNSPOD_ID, DNSPOD_TOKEN, DOMAINS, SUB_DOMAINS)")
        exit(1)

    for source in SOURCES:
        print(f"--- 开始处理 {source['line']} ---")
        ips = get_best_ips(source['url'])
        
        if ips:
            # 取第一个最优 IP 更新 (也可以改为循环更新多个)
            best_ip = ips[0]
            update_dnspod(best_ip, source['line'])
        else:
            print(f"未获取到 {source['line']} 的优选 IP，跳过更新")
        print("\n")
