所有配置文件都在 ..\DGLab.json 中，json不能备注，这里复制过来做个示范

{
  "api": {
    "url": "http://127.0.0.1:8920/api/v2/game/all/action/fire"  *这里是访问url，如果是同一台机子部署就不用动，如果不是就把前面的「http://127.0.0.1:8920」部分修改即可*
  },
  "strength": { *随机强度，都写同一个值就是固定强度，不要超出郊狼控制的范围，否则无效*
    "min": 70,
    "max": 100
  },
  "time": { *随机时间，单位秒，这个理论可以无限长，你可以试试，但不要在酒吧点炒饭*
    "min": 2,
    "max": 5
  },
  "ui": {
    "continuous_click": true, *是否可以连续点击，true为可以连续点击，false为不可以连续点击*
    "cooldown": { *随机冷却时间，最小值最大值，仅在"continuous_click": false时有效*
      "min": 3, 
      "max": 8
    }
  }
} 