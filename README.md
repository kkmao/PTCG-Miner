# PTCG-Miner
中文 / [English](./README_EN.md)

# 环境部署

- Python >= 3.12
- Tesseract OCR

# 安装依赖

```sh
pip install -r requirements.txt
```

# 配置
请在项目根目录下创建`settings.yaml`文件，并按照以下格式进行配置：
```yaml
debug: false
# reroll 配置项
reroll:
  pack: "MEWTWO" # 刷包选项: MEWTWO, CHARIZARD, PIKACHU, MEW
  delay_ms: 300 # 操作间隔
  game_speed: 3 # 游戏速度
  swipe_speed: 480 # 划卡包速度 [480, 1000]
  confidence: 0.8 # 图像识别精度，没有异常不要修改
  timeout: 45 # 超时时间，操作超时会重启游戏
  language: "Chinese" # 游戏语言，目前仅支持中文
  account_name: "SlvGP" # 创建账号的名称
  max_packs_to_open: 4 # 开卡包数量, [1, 4]
# 模拟器的ADB端口号
adb_ports:
  - "16416"
  - "16448"
  - "16480"
# 验包配置项
pack_checker:
  use_checker: true # 是否启用自动验包功能
  url: "http://example.com"
  username: "your_username"
  password: "your_password"
# tesseract路径，使用自动验包功能时需要配置
tesseract_path: "C:/Program Files/Tesseract-OCR/tesseract.exe"
```

# 运行
```sh
python3 main.py
```



# 日志
日志文件将保存在` ./log/reroll.log` 中。
