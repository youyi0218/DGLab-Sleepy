import os
import requests
import json
import random
from datetime import datetime
from pathlib import Path

def load_dglab_config():
    """从DGLab.json加载配置"""
    config_path = Path('DGLab.json')
    
    # 如果配置文件不存在，创建默认配置
    if not config_path.exists():
        default_config = {
            "api": {
                "url": "http://127.0.0.1:8920/api/v2/game/all/action/fire"
            },
            "strength": {
                "min": 70,
                "max": 100
            },
            "time": {
                "min": 2,
                "max": 5
            },
            "ui": {
                "continuous_click": true,
                "cooldown": {
                    "min": 3,
                    "max": 8
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        print("已创建默认DGLab.json配置文件，请根据需要修改")
        return default_config
    
    # 读取配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"读取DGLab.json失败: {str(e)}")
        return None

def get_api_url():
    """获取API URL"""
    config = load_dglab_config()
    if config:
        api_url = config.get('api', {}).get('url', 'http://127.0.0.1:8920/api/v2/game/all/action/fire')
        return api_url
    else:
        return 'http://127.0.0.1:8920/api/v2/game/all/action/fire'

def lightning_attack():
    """雷元素攻击 - 一键开火功能"""
    # 加载配置
    config = load_dglab_config()
    api_url = get_api_url()
    
    # 获取UI配置
    continuous_click = config.get('ui', {}).get('continuous_click', True)
    cooldown_min = config.get('ui', {}).get('cooldown', {}).get('min', 3)
    cooldown_max = config.get('ui', {}).get('cooldown', {}).get('max', 8)
    
    try:
        # 从配置文件获取参数范围
        strength_min = config.get('strength', {}).get('min', 70)
        strength_max = config.get('strength', {}).get('max', 100)
        time_min = config.get('time', {}).get('min', 2)
        time_max = config.get('time', {}).get('max', 5)
        
        # 随机生成参数
        strength = random.randint(strength_min, strength_max)  # 随机强度
        time_seconds = random.randint(time_min, time_max)  # 随机持续时间（秒）
        time_ms = time_seconds * 1000  # 转换为毫秒
        
        # 构造请求数据 - 根据API文档
        data = {
            "strength": strength,  # 强度，最高40
            "time": time_ms  # 持续时间，单位毫秒，最高30000（30秒）
        }
        
        # 发送请求
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(api_url, json=data, headers=headers)
        
        # 成功消息列表
        success_messages = [
            "以雷霆，击碎黑暗！",
            "十万伏特！",
            "此刻，寂灭之时！"
        ]
        
        # 失败消息列表
        failure_messages = [
            "可恶……竟被命运束缚了手脚！",
            "你行不行啊细狗。",
            "杂鱼，杂鱼捏~"
        ]
        
        if response.status_code == 200:
            message = random.choice(success_messages)
            
            # 如果不允许连续点击，计算随机冷却时间
            cooldown_time = 0
            if not continuous_click:
                cooldown_time = random.randint(cooldown_min, cooldown_max)
                
            return {
                "success": True, 
                "message": message,
                "details": f"强度: {strength}, 持续: {int(time_ms/1000)}秒",
                "continuous_click": continuous_click,
                "cooldown_time": cooldown_time,
                "data_sent": {
                    "strength": strength,
                    "time": time_ms
                }
            }
        else:
            message = random.choice(failure_messages)
            return {"success": False, "message": message}
    
    except Exception as e:
        return {"success": False, "message": f"发生错误: {str(e)}"}

# 用于Flask路由
def handle_lightning_attack():
    return json.dumps(lightning_attack(), ensure_ascii=False) 