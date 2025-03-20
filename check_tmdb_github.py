import asyncio  # 导入 asyncio 模块
import aiohttp  # 确保也导入了 aiohttp，因为代码中使用了 aiohttp.ClientSession
import requests
from time import sleep
import random
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from retry import retry
import socket

Tmdb_Host_TEMPLATE = """# Tmdb Hosts Start
{content}
# Update time: {update_time}
# IPv4 Update url: https://raw.githubusercontent.com/938134/CheckTMDB/refs/heads/main/Tmdb_host_ipv4
# IPv6 Update url: https://raw.githubusercontent.com/938134/CheckTMDB/refs/heads/main/Tmdb_host_ipv6
# Star me: https://github.com/938134/CheckTMDB
# Tmdb Hosts End\n"""

def write_file(ipv4_hosts_content: str, ipv6_hosts_content: str, update_time: str) -> bool:
    output_doc_file_path = os.path.join(os.path.dirname(__file__), "README.md")
    template_path = os.path.join(os.path.dirname(__file__), "README_template.md")
    if os.path.exists(output_doc_file_path):
        with open(output_doc_file_path, "r", encoding='utf-8') as old_readme_md:
            old_readme_md_content = old_readme_md.read()            
            if old_readme_md_content:
                old_ipv4_block = old_readme_md_content.split("```bash")[1].split("```")[0].strip()
                old_ipv4_hosts = old_ipv4_block.split("# Update time:")[0].strip()
                old_ipv6_block = old_readme_md_content.split("```bash")[2].split("```")[0].strip()
                old_ipv6_hosts = old_ipv6_block.split("# Update time:")[0].strip()
                if ipv4_hosts_content != "":
                    new_ipv4_hosts = ipv4_hosts_content.split("# Update time:")[0].strip()
                    if old_ipv4_hosts == new_ipv4_hosts:
                        print("ipv4 host not change")
                        w_ipv4_block = old_ipv4_block
                    else:
                        w_ipv4_block = ipv4_hosts_content
                        write_host_file(ipv4_hosts_content, 'ipv4')
                else:
                    print("ipv4_hosts_content is null")
                    w_ipv4_block = old_ipv4_block
                if ipv6_hosts_content != "":
                    new_ipv6_hosts = ipv6_hosts_content.split("# Update time:")[0].strip()
                    if old_ipv6_hosts == new_ipv6_hosts:
                        print("ipv6 host not change")
                        w_ipv6_block = old_ipv6_block
                    else:
                        w_ipv6_block = ipv6_hosts_content
                        write_host_file(ipv6_hosts_content, 'ipv6')
                else:
                    print("ipv6_hosts_content is null")
                    w_ipv6_block = old_ipv6_block
                
                with open(template_path, "r", encoding='utf-8') as temp_fb:
                    template_str = temp_fb.read()
                    hosts_content = template_str.format(ipv4_hosts_str=w_ipv4_block, ipv6_hosts_str=w_ipv6_block, update_time=update_time)

                    with open(output_doc_file_path, "w", encoding='utf-8') as output_fb:
                        output_fb.write(hosts_content)
                return True
        return False
               
def write_host_file(hosts_content: str, filename: str) -> None:
    output_file_path = os.path.join(os.path.dirname(__file__), "Tmdb_host_" + filename)
    if len(sys.argv) >= 2 and sys.argv[1].upper() == '-G':
        print("\n~追加Github ip~")
        hosts_content = hosts_content + "\n" + (get_github_hosts() or "")
    with open(output_file_path, "w", encoding='utf-8') as output_fb:
        output_fb.write(hosts_content)
        print("\n~最新TMDB" + filename + "地址已更新~")

async def get_csrf_token(udp: float) -> str:
    """获取 CSRF Token"""
    url = "https://dnschecker.org/ajax_files/gen_csrf.php"
    headers = {
        "referer": "https://dnschecker.org/country/cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }
    params = {"udp": udp}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            csrf_token = response.json().get("csrf")
            if csrf_token:
                print(f"获取到的 CSRF Token: {csrf_token}")
                return csrf_token
            else:
                print("无法获取 CSRF Token")
                return None
        else:
            print(f"请求失败，HTTP状态码: {response.status_code}")
            return None

async def get_domain_ips(domain: str, csrf_token: str, udp: float, record_type: str) -> list:
    """获取域名的 IPv4 或 IPv6 地址"""
    url = f"https://dnschecker.org/ajax_files/api/363/{record_type}"
    headers = {
        "csrftoken": csrf_token,
        "referer": "https://dnschecker.org/country/cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }
    params = {
        "dns_key": "country",
        "dns_value": "cn",
        "v": 0.36,
        "cd_flag": 1,
        "upd": udp,
        "domain": domain
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            response_data = response.json()
            if "result" in response_data and "ips" in response_data["result"]:
                ips_str = response_data["result"]["ips"]
                if "<br />" in ips_str:
                    return [ip.strip() for ip in ips_str.split("<br />") if ip.strip()]
                else:
                    return [ips_str.strip()] if ips_str.strip() else []
            else:
                print(f"获取 {domain} 的 IP 列表失败：返回数据格式不正确")
                return []
        else:
            print(f"请求失败，HTTP状态码: {response.status_code}")
            return []

async def ping_ip(ip: str, port: int = 80) -> tuple:
    """异步测试单个 IP 地址的延迟"""
    try:
        start_time = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{ip}:{port}", timeout=2)
            latency = (time.time() - start_time) * 1000  # 转换为毫秒
            return ip, latency
    except Exception as e:
        print(f"Ping {ip} 时发生错误: {str(e)}")
        return ip, float('inf')

async def find_fastest_ip(ips: list) -> str:
    """并发测试多个 IP 地址的延迟，并找出延迟最低的 IP"""
    if not ips:
        return None
    tasks = [ping_ip(ip) for ip in ips]
    results = await asyncio.gather(*tasks)
    fastest_ip = min(results, key=lambda x: x[1])
    print("\n所有 IP 延迟情况:")
    for ip, latency in results:
        print(f"IP: {ip} - 延迟: {latency}ms")
    if fastest_ip:
        print(f"\n最快的 IP 是: {fastest_ip[0]}，延迟: {fastest_ip[1]}ms")
    return fastest_ip[0]

async def process_domain(domain: str, csrf_token: str, udp: float) -> tuple:
    """处理单个域名"""
    ipv4_ips = await get_domain_ips(domain, csrf_token, udp, "A")
    ipv6_ips = await get_domain_ips(domain, csrf_token, udp, "AAAA")
    fastest_ipv4 = await find_fastest_ip(ipv4_ips) if ipv4_ips else None
    fastest_ipv6 = await find_fastest_ip(ipv6_ips) if ipv6_ips else None
    return domain, fastest_ipv4, fastest_ipv6

async def main():
    print("开始检测TMDB相关域名的最快IP...")
    udp = random.random() * 1000 + (int(time.time() * 1000) % 1000)
    csrf_token = await get_csrf_token(udp)
    if not csrf_token:
        print("无法获取CSRF Token，程序退出")
        sys.exit(1)
    domains_file_path = "domains.txt"
    if not os.path.exists(domains_file_path):
        print(f"错误：文件 {domains_file_path} 不存在！")
        sys.exit(1)
    with open(domains_file_path, "r", encoding="utf-8") as file:
        domains = [line.strip() for line in file.readlines() if line.strip()]
    tasks = [process_domain(domain, csrf_token, udp) for domain in domains]
    results = await asyncio.gather(*tasks)
    ipv4_results = []
    ipv6_results = []
    for domain, fastest_ipv4, fastest_ipv6 in results:
        if fastest_ipv4:
            ipv4_results.append([fastest_ipv4, domain])
        if fastest_ipv6:
            ipv6_results.append([fastest_ipv6, domain])
    update_time = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    ipv4_hosts_content = Tmdb_Host_TEMPLATE.format(content="\n".join(f"{ip:<27} {domain}" for ip, domain in ipv4_results), update_time=update_time) if ipv4_results else ""
    ipv6_hosts_content = Tmdb_Host_TEMPLATE.format(content="\n".join(f"{ip:<50} {domain}" for ip, domain in ipv6_results), update_time=update_time) if ipv6_results else ""
    # 这里可以根据需要将 ipv4_hosts_content 和 ipv6_hosts_content 写入文件

if __name__ == "__main__":
    asyncio.run(main())
