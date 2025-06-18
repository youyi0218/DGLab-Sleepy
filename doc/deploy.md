## 手动部署

本方式理论上全平台通用, 安装了 Python >= **3.6** 即可 (建议: **3.10+**)

> 优点: 数据文件 (`data.json`) 可持久化，不会因为重启而被删除

### 安装

1. Clone 本仓库 (建议先 Fork / Use this template)

```shell
git clone --depth=1 -b main https://github.com/youyi0218/DGLab-Sleepy.git
```

国内用户可以用镜像站
```
git clone https://kkgithub.com/youyi0218/DGLab-Sleepy.git
```
2. 安装依赖

```shell
pip install -r requirements.txt
```

3. 编辑配置文件

在项目目录创建 `.env` 文件:

```ini
sleepy_main_host = "0.0.0.0" # 监听地址
sleepy_main_port = "9010" # 端口号
sleepy_secret = "改成别人猜不出来的密钥" # 密钥，相当于密码
sleepy_page_user = "君の名は。" # 将显示在网页中
sleepy_page_favicon = "./static/favicon.ico" # 网站图标, 可替换 static/favicon.ico 自定义 (也可以用其他格式的, 自己改路径)
sleepy_page_more_text = "欢迎来到我的状态页!" # 说两句? (也可以留空)
sleepy_page_using_first = true # 使用中设备优先显示
```

更多配置项详见 [此处](./env.md)

### 启动

> **使用宝塔面板 (uwsgi) 等部署时，请确定只为本程序分配了 1 个进程, 如设置多个服务进程可能导致数据不同步!!!**

有两种启动方式:

```shell
# 直接启动
python3 server.py
# 简易启动器
python3 start.py
```

默认服务 http 端口: **`9010`**

## hunggingface和vercel
因为这个项目有关联郊狼，但是郊狼你也不可能一直沾身上，同时需要一个手机一直连着socket，所以我认为hgface和vercel部署不太现实，我就没做部署。关于一键部署可以去网盘下一键包