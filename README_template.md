# CheckTMDB

每日自动更新TMDB，themoviedb、thetvdb、github 国内可正常连接IP，解决DNS污染，供tinyMediaManager(TMM削刮器)、Kodi的刮削器、群晖VideoStation的海报墙、Plex Server的元数据代理、Emby Server元数据下载器、Infuse、Nplayer等正常削刮影片信息。

## 一、前景

自从我早两年使用了黑群NAS以后，下了好多的电影电视剧，发现电视端无法生成正常的海报墙。查找资料得知应该是 themoviedb.org、tmdb.org 无法正常访问，因为DNS受到了污染无法正确解析到TMDB的IP，故依葫芦画瓢写了一个python脚本，每日定时通过[dnschecker](https://dnschecker.org/)查询出最佳IP，并自动同步到路由器外挂hosts，可正常削刮。

**本项目无需安装任何程序**

通过修改本地、路由器 hosts 文件，即可正常削刮影片信息。

## 二、使用方法

### 2.1 手动方式

#### 2.1.1 IPv4地址复制下面的内容

```bash
{ipv4_hosts_str}
```

该内容会自动定时更新， 数据更新时间：{update_time}

#### 2.1.2 IPv6地址复制下面的内容

```bash
{ipv6_hosts_str}
```

该内容会自动定时更新， 数据更新时间：{update_time}

> [!NOTE]
> 由于项目搭建在Github Aciton，延时数据获取于Github Action 虚拟主机网络环境，请自行测试可用性，建议使用本地网络环境自动设置。

2.1.2 修改 hosts 文件
hosts 文件在每个系统的位置不一，详情如下：

Windows 系统：C:\Windows\System32\drivers\etc\hosts
Linux 系统：/etc/hosts
Mac（苹果电脑）系统：/etc/hosts
Android（安卓）系统：/system/etc/hosts
iPhone（iOS）系统：/etc/hosts
修改方法，把第一步的内容复制到文本末尾：

Windows 使用记事本。
Linux、Mac 使用 Root 权限：sudo vi /etc/hosts。
iPhone、iPad 须越狱、Android 必须要 root。
2.1.3 激活生效
大部分情况下是直接生效，如未生效可尝试下面的办法，刷新 DNS：

Windows：在 CMD 窗口输入：ipconfig /flushdns

Linux 命令：sudo nscd restart，如报错则须安装：sudo apt install nscd 或 sudo /etc/init.d/nscd restart

Mac 命令：sudo killall -HUP mDNSResponder

Tips： 上述方法无效可以尝试重启机器。

2.2 自动方式（SwitchHosts）
Tip：推荐 SwitchHosts 工具管理 hosts

以 SwitchHosts 为例，看一下怎么使用的，配置参考下面：

Hosts 类型: Remote

Hosts 标题: 随意

URL: https://raw.hellogithub.com/hosts

自动刷新: 最好选 1 小时

如图：



这样每次 hosts 有更新都能及时进行更新，免去手动更新。

2.3 一行命令
Windows
使用命令需要安装git bash 复制以下命令保存到本地命名为fetch_github_hosts

_hosts=$(mktemp /tmp/hostsXXX)
hosts=/c/Windows/System32/drivers/etc/hosts
remote=https://raw.hellogithub.com/hosts
reg='/# GitHub520 Host Start/,/# Github520 Host End/d'

sed "$reg" $hosts > "$_hosts"
curl "$remote" >> "$_hosts"
cat "$_hosts" > "$hosts"

rm "$_hosts"
在CMD中执行以下命令，执行前需要替换git-bash.exe和fetch_github_hosts为你本地的路径，注意前者为windows路径格式后者为shell路径格式

"C:\Program Files\Git\git-bash.exe" -c "/c/Users/XXX/fetch_github_hosts"

可以将上述命令添加到windows的task schedular（任务计划程序）中以定时执行

GNU（Ubuntu/CentOS/Fedora）
sudo sh -c 'sed -i "/# GitHub520 Host Start/Q" /etc/hosts && curl https://raw.hellogithub.com/hosts >> /etc/hosts'

BSD/macOS
sudo sed -i "" "/# GitHub520 Host Start/,/# Github520 Host End/d" /etc/hosts && curl https://raw.hellogithub.com/hosts | sudo tee -a /etc/hosts

将上面的命令添加到 cron，可定时执行。使用前确保 GitHub520 内容在该文件最后部分。

在 Docker 中运行，若遇到 Device or resource busy 错误，可使用以下命令执行

cp /etc/hosts ~/hosts.new && sed -i "/# GitHub520 Host Start/Q" ~/hosts.new && curl https://raw.hellogithub.com/hosts >> ~/hosts.new && cp -f ~/hosts.new /etc/hosts

2.4 AdGuard 用户（自动方式）
在 过滤器>DNS 封锁清单>添加阻止列表>添加一个自定义列表，配置如下：

名称：随意

URL：https://raw.hellogithub.com/hosts（和上面 SwitchHosts 使用的一样）

如图：

![6c8edd526e092070dcc79eceb839c2d5_AdGuard-rules](https://github.com/user-attachments/assets/3de7e705-583d-4219-9f51-f8cfeca313a0)


更新间隔在 设置 > 常规设置 > 过滤器更新间隔（设置一小时一次即可），记得勾选上 使用过滤器和 Hosts 文件以拦截指定域名

![79b2783eca4aca9343342f21caae6292_AdGuard-rules2](https://github.com/user-attachments/assets/f06a78e6-e5d7-4e29-8263-69dba75225f1)

Tip：不要添加在 DNS 允许清单 内，只能添加在 DNS 封锁清单 才管用。 另外，AdGuard for Mac、AdGuard for Windows、AdGuard for Android、AdGuard for IOS 等等 AdGuard 家族软件 添加方法均类似。

三、效果对比
之前的样子：
<img width="979" alt="7a0e60b15436847dbc2006687572d1ad_old" src="https://github.com/user-attachments/assets/db349bce-20ce-45a4-a61b-d95d79c55715" />

修改完 hosts 的样子：
<img width="964" alt="140b91c32028d1f7a3e00faddaf8807e_new" src="https://github.com/user-attachments/assets/d976f77e-422a-4fc6-a5b6-90b00edbbae9" />

#### 2.1.3 修改 hosts 文件

hosts 文件在每个系统的位置不一，详情如下：

- Windows 系统：`C:\Windows\System32\drivers\etc\hosts`
- Linux 系统：`/etc/hosts`
- Mac（苹果电脑）系统：`/etc/hosts`
- Android（安卓）系统：`/system/etc/hosts`
- iPhone（iOS）系统：`/etc/hosts`

修改方法，把第一步的内容复制到文本末尾：

1. Windows 使用记事本。
2. Linux、Mac 使用 Root 权限：`sudo vi /etc/hosts`。
3. iPhone、iPad 须越狱、Android 必须要 root。

#### 2.1.4 激活生效

大部分情况下是直接生效，如未生效可尝试下面的办法，刷新 DNS：

1. Windows：在 CMD 窗口输入：`ipconfig /flushdns`

2. Linux 命令：`sudo nscd restart`，如报错则须安装：`sudo apt install nscd` 或 `sudo /etc/init.d/nscd restart`

3. Mac 命令：`sudo killall -HUP mDNSResponder`

**Tips：** 上述方法无效可以尝试重启机器。

### 2.2 自动方式

#### 2.2.1 安装 SwitchHosts

GitHub 发行版：https://github.com/oldj/SwitchHosts/releases/latest

#### 2.2.2 添加 hosts

点击左上角“+”，并进行以下配置：

- Hosts 类型：`远程`
- Hosts 标题：任意
- URL  `https://raw.githubusercontent.com/938134/check_hosts/refs/heads/main/hosts`
- 自动刷新：`1 小时`

#### 2.2.3 启用 hosts

在左侧边栏启用 hosts，首次使用时软件会自动获取内容。如果无法连接到 GitHub，可以尝试用同样的方法添加 [GitHub520](https://github.com/521xueweihan/GitHub520) hosts。

## 其他

- [x] 自学薄弱编程基础，大部分代码基于AI辅助生成，此项目过程中，主要人为解决的是：通过 [dnschecker](https://dnschecker.org/) 提交时，通过计算出正确的udp参数，获取正确的csrftoken，携带正确的referer提交！
- [x] README.md 及 部分代码 参考[GitHub520](https://github.com/521xueweihan/GitHub520)
- [x] * 本项目仅在本机测试通过，如有问题欢迎提 [issues](https://github.com/cnwikee/CheckTMDB/issues/new)
