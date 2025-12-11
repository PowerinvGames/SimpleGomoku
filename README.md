# 五子棋游戏 (Gomoku)

一个使用Python和Arcade库开发的五子棋游戏，采用Clean Code架构设计。

## 功能特点

- 完整的五子棋游戏逻辑
- 美观的中文界面
- 支持悔棋功能
- 可配置的游戏设置
- 详细的日志记录
- 分层架构设计，易于维护和扩展

## 项目结构

```
SimpleGomoku/
├── python/                    # 源代码目录
│   ├── main.py               # 程序入口点
│   ├── Config.py             # 配置管理
│   ├── Logger.py             # 日志管理
│   ├── Board.py              # 棋盘逻辑
│   ├── GameLogic.py          # 游戏逻辑
│   ├── GameWindow.py         # 游戏窗口
│   ├── models/               # 数据模型
│   │   ├── __init__.py
│   │   └── GameModels.py
│   └── ui/                   # UI组件
│       ├── __init__.py
│       ├── BoardView.py
│       ├── Button.py
│       └── StatusPanel.py
├── resources/                # 资源文件
│   ├── HarmonyOS_SansSC_Regular.ttf  # 中文字体
│   └── config.properties     # 配置文件
├── requirements.txt          # 项目依赖
└── README.md                # 说明文档
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行游戏

```bash
cd python
python main.py
```

或者直接运行：

```bash
python python/main.py
```

## 游戏操作

- **鼠标点击**：在棋盘上落子
- **新游戏**：开始全新的游戏
- **重新开始**：重置当前游戏
- **悔棋**：撤销上一步操作
- **退出游戏**：关闭游戏窗口

### 快捷键

- **ESC**：退出游戏
- **R**：重新开始游戏
- **N**：新游戏
- **Ctrl+Z**：悔棋

## 配置说明

游戏的所有可配置项都在 `resources/config.properties` 文件中，包括：

- 窗口大小和标题
- 棋盘大小和颜色
- 棋子颜色和大小
- 按钮样式
- 界面文本（支持中文）
- 游戏规则（获胜连子数等）

修改配置文件后，重启游戏即可生效。

## 架构设计

项目采用分层架构设计：

1. **配置层** (`Config.py`)：集中管理所有配置
2. **日志层** (`Logger.py`)：统一的日志记录
3. **数据模型层** (`models/`)：定义游戏数据结构
4. **业务逻辑层** (`Board.py`, `GameLogic.py`)：游戏核心逻辑
5. **UI层** (`ui/`, `GameWindow.py`)：用户界面组件
6. **入口点** (`main.py`)：程序启动

这种设计使得：
- 各层职责清晰，易于维护
- 可以轻松更换UI框架
- 配置集中管理，易于修改
- 代码高度可复用

## 开发说明

### 代码规范

- 遵循Clean Code原则
- 使用大驼峰命名法（类名）
- 每个类一个文件
- 所有import从python目录开始
- 使用Logger代替print

### 扩展游戏

1. **添加新功能**：在相应的层中添加代码
2. **修改UI**：修改ui目录下的组件
3. **更改配置**：修改config.properties文件
4. **添加新游戏模式**：扩展GameLogic类

## 许可证

本项目仅供学习使用，遵循MIT许可证。