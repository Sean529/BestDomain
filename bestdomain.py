import os
import requests
import json

# 从 GitHub Secrets 获取配置
ID = os.environ.get('DNSPOD_ID')
TOKEN = os.environ.get('DNSPOD_TOKEN')
DOMAIN = os.environ.get('DOMAINS')
SUB_DOMAIN = os.environ.get('SUB_DOMAINS')

def get_best_ips():
    # 从 IPDB 获取优选 IP 列表
    url = "https://raw.githubusercontent.com/ymyuuu/IPDB/main/bestcf.txt"
    resp = requests.get(url)
    return resp.text.strip().split('\n')[:3]  # 只要前 3 个最快的 IP

def update_dnspod(ip):
    # 调用 DNSPod API 修改 A 记录
    api_url = "https://dnsapi.cn/Record.List"
    data = {
        "login_token": f"{ID},{TOKEN}",
        "format": "json",
        "domain": DOMAIN,
        "sub_domain": SUB_DOMAIN,
        "record_type": "A"
    }
    
    # 1. 获取现有记录 ID
    try:
        response = requests.post(api_url, data=data)
        response.raise_for_status() # Check for HTTP errors
        records = response.json().get('records', [])
    except Exception as e:
        print(f"获取记录失败: {e}")
        print(f"响应内容: {response.text if 'response' in locals() else 'No response'}")
        return

    if records:
        record_id = records[0]['id']
        # 2. 修改记录
        modify_url = "https://dnsapi.cn/Record.Modify"
        data.update({
            "record_id": record_id,
            "value": ip,
            "record_line": "默认"
        })
        try:
            res = requests.post(modify_url, data=data).json()
            print(f"IP {ip} 更新结果: {res['status']['message']}")
        except Exception as e:
             print(f"修改记录失败: {e}")
    else:
        # 3. 如果不存在则新建
        create_url = "https://dnsapi.cn/Record.Create"
        data.update({
            "value": ip,
            "record_line": "默认"
        })
        try:
            res = requests.post(create_url, data=data).json()
            print(f"IP {ip} 创建结果: {res['status']['message']}")
        except Exception as e:
            print(f"创建记录失败: {e}")

if __name__ == "__main__":
    ips = get_best_ips()
    # 为简单起见，这里更新第一个最快 IP，你也可以循环更新多个
    if ips:
        update_dnspod(ips[0])
    else:
        print("未获取到优选IP")
