#!/usr/bin/python3
# coding: utf-8

import time
from datetime import datetime
from functools import wraps  # 用于修饰器

import flask
import json5
import pytz
from markupsafe import escape

import env
import utils as u
from data import data as data_init
from setting import status_list
# 导入DG-Lab API处理模块
import dglab_api
# 确保DGLab配置加载
dglab_api.load_dglab_config()

try:
    # init flask app
    app = flask.Flask(__name__)

    # disable flask access log (if not debug)
    if not env.main.debug:
        from logging import getLogger
        flask_default_logger = getLogger('werkzeug')
        flask_default_logger.disabled = True

    # init data
    d = data_init()
    d.load()
    d.start_timer_check(data_check_interval=env.main.checkdata_interval)  # 启动定时保存

    # init metrics if enabled
    if env.util.metrics:
        u.info('[metrics] metrics enabled, open /metrics to see the count.')
        d.metrics_init()
except Exception as e:
    u.error(f"Error initing: {e}")
    exit(1)
except KeyboardInterrupt:
    u.debug('Interrupt init')
    exit(0)
except u.SleepyException as e:
    u.error(f'==========\n{e}')
    exit(1)
except:
    u.error('Unexpected Error!')
    raise


# --- Functions


@app.before_request
def showip():
    '''
    在日志中显示 ip, 并记录 metrics 信息
    ~~如 Header 中 User-Agent 为 SleepyPlugin/(每次启动使用随机 uuid) 则不进行任何记录~~

    :param req: `flask.request` 对象, 用于取 ip
    :param msg: 信息 (一般是路径, 同时作为 metrics 的项名)
    '''
    # --- get path
    path = flask.request.path
    # --- log
    ip1 = flask.request.remote_addr
    ip2 = flask.request.headers.get('X-Forwarded-For')
    if ip2:
        u.info(f'- Request: {ip1} / {ip2} : {path}')
    else:
        u.info(f'- Request: {ip1} : {path}')
    # --- count
    if env.util.metrics:
        d.record_metrics(path)


def require_secret(view_func):
    '''
    require_secret 修饰器, 用于指定函数需要 secret 鉴权
    '''
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        # 1. body
        # -> {"secret": "my-secret"}
        body: dict = flask.request.get_json(silent=True) or {}
        if body.get('secret', '') == env.main.secret:
            u.debug('[Auth] Verify secret Success from Body')
            return view_func(*args, **kwargs)

        # 2. param
        # -> ?secret=my-secret
        elif flask.request.args.get('secret', '') == env.main.secret:
            u.debug('[Auth] Verify secret Success from Param')
            return view_func(*args, **kwargs)

        # 3. header (Sleepy-Secret)
        # -> Sleepy-Secret: my-secret
        elif flask.request.headers.get('Sleepy-Secret', '') == env.main.secret:
            u.debug('[Auth] Verify secret Success from Header (Sleepy-Secret)')
            return view_func(*args, **kwargs)

        # 4. header (Authorization)
        # -> Authorization: Bearer my-secret
        elif flask.request.headers.get('Authorization', '')[7:] == env.main.secret:
            u.debug('[Auth] Verify secret Success from Header (Authorization)')
            return view_func(*args, **kwargs)

        # -1. no any secret
        else:
            u.debug('[Auth] Verify secret Failed')
            return u.reterr(
                code='not authorized',
                message='wrong secret'
            ), 401
    return wrapped_view

# --- Templates


@app.route('/')
def index():
    '''
    根目录返回 html
    - Method: **GET**
    '''
    # 获取手动状态
    try:
        status: dict = status_list[d.data['status']]
    except:
        u.warning(f"Index {d.data['status']} out of range!")
        status = {
            'name': 'Unknown',
            'desc': '未知的标识符，可能是配置问题。',
            'color': 'error'
        }
    # 获取更多信息 (more_text)
    more_text: str = env.page.more_text
    if env.util.metrics:
        more_text = more_text.format(
            visit_today=d.data['metrics']['today'].get('/', 0),
            visit_month=d.data['metrics']['month'].get('/', 0),
            visit_year=d.data['metrics']['year'].get('/', 0),
            visit_total=d.data['metrics']['total'].get('/', 0)
        )
    # 返回 html
    return flask.render_template(
        'index.html',
        env=env,
        more_text=more_text,
        status=status,
        last_updated=d.data['last_updated']
    ), 200


@app.route('/'+'git'+'hub')
def git_hub():
    '''
    这里谁来了都改不了!
    '''
    return flask.redirect('ht'+'tps:'+'//git'+'hub.com/'+'sleep'+'y-proj'+'ect/sle'+'epy', 301)


@app.route('/none')
def none():
    '''
    返回 204 No Content, 可用于 Uptime Kuma 等工具监控服务器状态使用
    '''
    return '', 204


# --- DG-Lab API

@app.route('/dglab/lightning', methods=['POST'])
def dglab_lightning():
    '''
    DG-Lab 雷元素攻击（一键开火功能）
    - 无需鉴权（可根据需要添加鉴权）
    - Method: **POST**
    '''
    return dglab_api.handle_lightning_attack(), 200

@app.route('/dglab/config', methods=['GET'])
def dglab_config():
    '''
    获取DG-Lab配置
    - 无需鉴权
    - Method: **GET**
    '''
    config = dglab_api.load_dglab_config()
    ui_config = {
        'continuous_click': config.get('ui', {}).get('continuous_click', True)
    }
    return u.format_dict(ui_config), 200


# --- Read-only


@app.route('/query')
def query(ret_as_dict: bool = False):
    '''
    获取当前状态
    - 无需鉴权
    - Method: **GET**

    :param ret_as_dict: 使函数直接返回 dict 而非 `u.format_dict()` 格式化后的 response
    '''
    # 获取手动状态
    st: int = d.data['status']
    try:
        stinfo = status_list[st]
    except:
        stinfo = {
            'id': -1,
            'name': '[未知]',
            'desc': f'未知的标识符 {st}，可能是配置问题。',
            'color': 'error'
        }
    # 获取设备状态
    if d.data['private_mode']:
        # 隐私模式
        devicelst = {}
    elif env.page.using_first:
        # 使用中优先
        devicelst = {}  # devicelst = device_using
        device_not_using = {}
        for n in d.data['device_status']:
            i = d.data['device_status'][n]
            if i['using']:
                devicelst[n] = i
            else:
                device_not_using[n] = i
        if env.page.sorted:
            devicelst = dict(sorted(devicelst.items()))
            device_not_using = dict(sorted(device_not_using.items()))
        devicelst.update(device_not_using)  # append not_using items to end
    else:
        # 正常获取
        devicelst: dict = d.data['device_status']
        if env.page.sorted:
            devicelst = dict(sorted(devicelst.items()))

    # 构造返回
    timenow = datetime.now(pytz.timezone(env.main.timezone))
    ret = {
        'time': timenow.strftime('%Y-%m-%d %H:%M:%S'),
        'timezone': env.main.timezone,
        'success': True,
        'status': st,
        'info': stinfo,
        'device': devicelst,
        'device_status_slice': env.status.device_slice,
        'last_updated': d.data['last_updated'],
        'refresh': env.status.refresh_interval
    }
    if ret_as_dict:
        return ret
    else:
        return u.format_dict(ret), 200


@app.route('/status_list')
def get_status_list():
    '''
    获取 `status_list`
    - 无需鉴权
    - Method: **GET**
    '''
    return u.format_dict(status_list), 200


# --- Status API


@app.route('/set')
@require_secret
def set_normal():
    '''
    设置状态
    - http[s]://<your-domain>[:your-port]/set?status=<a-number>
    - Method: **GET**
    '''
    status = escape(flask.request.args.get('status'))
    try:
        status = int(status)
    except:
        return u.reterr(
            code='bad request',
            message="argument 'status' must be int"
        ), 400
    d.dset('status', status)
    return u.format_dict({
        'success': True,
        'code': 'OK',
        'set_to': status
    }), 200


# --- Device API

@app.route('/device/set', methods=['GET', 'POST'])
@require_secret
def device_set():
    '''
    设置单个设备的信息/打开应用
    - Method: **GET / POST**
    '''
    if flask.request.method == 'GET':
        try:
            device_id = escape(flask.request.args.get('id'))
            device_show_name = escape(flask.request.args.get('show_name'))
            device_using = u.tobool(escape(flask.request.args.get('using')), throw=True)
            app_name = escape(flask.request.args.get('app_name'))
        except:
            return u.reterr(
                code='bad request',
                message='missing param or wrong param type'
            ), 400
    elif flask.request.method == 'POST':
        req = flask.request.get_json()
        try:
            device_id = req['id']
            device_show_name = req['show_name']
            device_using = u.tobool(req['using'], throw=True)
            app_name = req['app_name']
        except:
            return u.reterr(
                code='bad request',
                message='missing param or wrong param type'
            ), 400
    devices: dict = d.dget('device_status')
    if (not device_using) and env.status.not_using:
        # 如未在使用且锁定了提示，则替换
        app_name = env.status.not_using
    devices[device_id] = {
        'show_name': device_show_name,
        'using': device_using,
        'app_name': app_name
    }
    d.data['last_updated'] = datetime.now(pytz.timezone(env.main.timezone)).strftime('%Y-%m-%d %H:%M:%S')
    d.check_device_status()
    return u.format_dict({
        'success': True,
        'code': 'OK'
    }), 200


@app.route('/device/remove')
@require_secret
def remove_device():
    '''
    移除单个设备的状态
    - Method: **GET**
    '''
    device_id = escape(flask.request.args.get('id'))
    try:
        del d.data['device_status'][device_id]
        d.data['last_updated'] = datetime.now(pytz.timezone(env.main.timezone)).strftime('%Y-%m-%d %H:%M:%S')
        d.check_device_status()
    except KeyError:
        return u.reterr(
            code='not found',
            message='cannot find item'
        ), 404
    return u.format_dict({
        'success': True,
        'code': 'OK'
    }), 200


@app.route('/device/clear')
@require_secret
def clear_device():
    '''
    清除所有设备状态
    - Method: **GET**
    '''
    d.data['device_status'] = {}
    d.data['last_updated'] = datetime.now(pytz.timezone(env.main.timezone)).strftime('%Y-%m-%d %H:%M:%S')
    d.check_device_status()
    return u.format_dict({
        'success': True,
        'code': 'OK'
    }), 200


@app.route('/device/private_mode')
@require_secret
def private_mode():
    '''
    隐私模式, 即不在 /query 中显示设备状态 (仍可正常更新)
    - Method: **GET**
    '''
    private = u.tobool(escape(flask.request.args.get('private')))
    if private == None:
        return u.reterr(
            code='invaild request',
            message='"private" arg only supports boolean type'
        ), 400
    d.data['private_mode'] = private
    d.data['last_updated'] = datetime.now(pytz.timezone(env.main.timezone)).strftime('%Y-%m-%d %H:%M:%S')
    return u.format_dict({
        'success': True,
        'code': 'OK'
    }), 200


@app.route('/save_data')
@require_secret
def save_data():
    '''
    保存内存中的状态信息到 `data.json`
    - Method: **GET**
    '''
    try:
        d.save()
    except Exception as e:
        return u.reterr(
            code='exception',
            message=f'{e}'
        ), 500
    return u.format_dict({
        'success': True,
        'code': 'OK',
        'data': d.data
    }), 200


@app.route('/events')
def events():
    '''
    SSE 事件流，用于推送状态更新
    - Method: **GET**
    '''
    def event_stream():
        last_update = None
        last_heartbeat = time.time()
        while True:
            current_time = time.time()
            # 检查数据是否已更新
            current_update = d.data['last_updated']

            # 如果数据有更新，发送更新事件并重置心跳计时器
            if last_update != current_update:
                last_update = current_update
                # 重置心跳计时器
                last_heartbeat = current_time

                # 获取 /query 返回数据
                ret = query(ret_as_dict=True)
                yield f"event: update\ndata: {json5.dumps(ret, quote_keys=True)}\n\n"
            # 只有在没有数据更新的情况下才检查是否需要发送心跳
            elif current_time - last_heartbeat >= 30:
                timenow = datetime.now(pytz.timezone(env.main.timezone))
                yield f"event: heartbeat\ndata: {timenow.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                last_heartbeat = current_time

            time.sleep(1)  # 每秒检查一次更新

    response = flask.Response(event_stream(), mimetype="text/event-stream", status=200)
    response.headers["Cache-Control"] = "no-cache"  # 禁用缓存
    response.headers["X-Accel-Buffering"] = "no"  # 禁用 Nginx 缓冲
    return response


# --- Special

if env.util.metrics:
    @app.route('/metrics')
    def metrics():
        '''
        获取统计信息
        - Method: **GET**
        '''
        resp = d.get_metrics_resp()
        return resp, 200

if env.util.steam_enabled:
    @app.route('/steam-iframe')
    def steam():
        return flask.render_template(
            'steam-iframe.html',
            env=env,
            steamids=env.util.steam_ids,
            steam_refresh_interval=env.util.steam_refresh_interval
        ), 200

# --- End

if __name__ == '__main__':
    u.info(f'=============== hi {env.page.user}! ===============')
    # --- plugins - undone
    # u.info(f'Loading plugins...')
    # all_plugins = u.list_dir(u.get_path('plugin'), include_subfolder=False, ext='.py')
    # enabled_plugins = []
    # for i in all_plugins:
    #     pass
    # --- launch
    # 检查是否启用 HTTPS
    if env.main.https_enabled:
        ssl_context = (env.main.ssl_cert, env.main.ssl_key)
        u.info(f'Starting HTTPS server: {env.main.host}:{env.main.port}{" (debug enabled)" if env.main.debug else ""}')
        u.info(f'Using SSL certificate: {env.main.ssl_cert}')
        u.info(f'Using SSL key: {env.main.ssl_key}')
    else:
        ssl_context = None
        u.info(f'Starting HTTP server: {env.main.host}:{env.main.port}{" (debug enabled)" if env.main.debug else ""}')

    try:
        app.run(  # 启↗动↘
            host=env.main.host,
            port=env.main.port,
            debug=env.main.debug,
            ssl_context=ssl_context
        )
    except Exception as e:
        u.error(f"Error running server: {e}")
    print()
    u.info('Server exited, saving data...')
    d.save()
    u.info('Bye.')
