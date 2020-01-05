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

在Windows环境中部署时, 请先安装`Visual C++ Build Tools 14`, 以防止安装模块 `httptools` 时发生不可名状的错误.  
[`Stack OverFlow` 上的相关问题](https://developercommunity.visualstudio.com/content/problem/431673/microsoft-visual-c-140-is-required.html)  
若是您觉得太麻烦, 请使用WSL, 虽然我没用, 但为了你的时间着想, 还是请在GNU/Linux环境部署.

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

启动:
``` bash
pipenv shell
python main.py

# or
pipenv run main
```