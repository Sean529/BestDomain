# BestDomain (DNSPod 适配版)

本项目已重构，专门用于将 Cloudflare 优选 IP 自动更新到 **腾讯云 (DNSPod)** 的 DNS 记录中。

## 功能
- 自动获取最新的 Cloudflare 优选 IP (来源: [ymyuuu/IPDB](https://github.com/ymyuuu/IPDB))
- 自动更新 DNSPod 指定子域名的 A 记录
- 支持 GitHub Actions 定时运行

## 使用说明

### 1. 获取 DNSPod 密钥
1. 访问 [DNSPod 密钥管理](https://console.dnspod.cn/account/token/token)。
2. 创建一个新的密钥，记下 **ID** 和 **Token**。

### 2. 设置 GitHub Secrets
在你的 GitHub 仓库中，进入 **Settings -> Secrets and variables -> Actions**，添加以下 Secrets：

| Secret 名称 | 说明 | 示例 |
| :--- | :--- | :--- |
| `DNSPOD_ID` | DNSPod 密钥 ID | `123456` |
| `DNSPOD_TOKEN` | DNSPod 密钥 Token | `a1b2c3d4...` |
| `DOMAINS` | 你的主域名 | `hiyinni.com` |
| `SUB_DOMAINS` | 需要优选 IP 的主机记录 | `cdn` |

### 3. 配置定时任务
默认配置为每小时运行一次。你可以在 [.github/workflows/main.yml](.github/workflows/main.yml) 中修改 `cron` 表达式。
