# Natrium
### 这是什么?
一个可能的服务器玩家管理系统的源代码仓库. 灵感来自 `Blessing Skin`.

### 部署

在GNU/Linux环境部署该项目时, 请先使用包管理器安装 `postgresql-libs`,
以在一定程度上避免出现pipenv部署环境失败的情况:
``` bash
# 用于Ubuntu
sudo apt-get install libpq-dev

# 用于RedHat, CentOS及其他使用了RPM作为包管理器的发行版
sudo yum install postgresql-libs

# 用于Archlinux 或基于其的发行版
sudo pacman -S postgresql-libs
```

然后使用pip安装pipenv:
``` bash
sudo pip install pipenv
```

克隆本仓库或是从本项目的Release页面获取可能的打包:
``` bash
git clone https://github.com/NatriumLab/Natrium && cd Natrium
```

使用pipenv安装需求包:
``` bash
pipenv --three # 创建venv虚拟环境
pipenv install # 安装需求包
```

使用uvicorn启动本项目, 可以使用 `--port` 参数改动端口:
```
uvicorn main:app --port 8000
```