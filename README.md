# sleepy

> 欢迎来到 Sleepy Project 的YouYi分支。

一个用于 ~~*视奸*~~ 同时可以当 ~~*杨永信*~~ 的 Flask 应用，让他人能知道你不在而不是故意吊他/她。 ~~即便是，他人也可以让你不是~~

[**功能**](#功能) / [**演示**](#preview) / [**部署**](#部署--更新) / [**服务端配置**](#服务器配置) / [**使用**](#使用) / [**Client**](#client) / [**API**](#api) / [**关于**](#关于)

## 功能

- [x] 自行设置在线状态 *(活着 / 似了 等, 也可 **[自定义](./setting/README.md#status_listjson)** 状态列表)*
- [x] 实时更新设备使用状态 *(包括 是否正在使用 / 打开的应用名, 通过 **[client](./client/README.md)** 主动推送)*
- [x] 美观的展示页面 [见 [Preview](#preview)]
- [x] 开放的 Query / Metrics [接口](./doc/api.md), 方便统计
- [x] 支持 HTTPS (需要自行配置 SSL 证书)
- [x] 接入[郊狼api](https://github.com/hyperzlib/DG-Lab-Coyote-Game-Hub)

> [!TIP]
> 如有 Bug / 建议, 可 [issue](https://github.com/youyi0218/DGLab-Sleepy/issues/new) <br/>

### Preview

个人站点: 不放了，放群里都被电成皮卡丘了

HuggingFace 部署预览: 没做也不打算做，理论上和原仓库部署方式一样，需求多会考虑接入。

Vercel 部署预览: 同上


## 部署 / 更新

请移步 **[部署教程](./doc/deploy.md)** 或 **[b站链接](./doc/update.md)** 

## Client

搭建完服务端后，你可在 **[`/client`](./client/README.md)** 找到客户端 (用于**手动更新状态**/**自动更新设备打开应用**)

*目前已有 [Windows](./client/README.md#windevice), [Linux](./client/README.md#linux), [MacOS / IOS](./client/README.md#appleshortcuts), [Android](./client/README.md#autoxjsscript), [油猴脚本](./client/README.md#browserscript) 等客户端*

## API

详细的 API 文档见 [doc/api.md](./doc/api.md).

## 优化站点

见 [Best Practice](./doc/best_practice.md).

> [!TIP]
> 想自定义你的状态列表 / metrics 统计白名单? **[见 `setting` 目录](./setting/README.md)**

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=youyi0218/DGLab-Sleepy&type=Date)](https://www.star-history.com/#youyi0218/DGLab-Sleepy&Date)

## 关于

本项目灵感由 Bilibili UP [我会永远喜欢胡桃](https://www.bilibili.com/video/BV1t6LAz2EDz) 而来, 但是up主的仓库年久失修所以采取 https://github.com/sleepy-project/sleepy 通过cursor重新接入了郊狼api，此十分感谢所有这个这个仓库的提交者做出的贡献。

---

这个仓库只是做的玩的，郊狼api项目也 ~~年久失修（主要是action构建的文件都过期了，我尝试自己构建死活打不开，只能通过下载releas的上古版本使用）了不过胜在能用~~ ，大概率不会跟着原始项目更新了，如果有需求可以自行接入(郊狼api)[https://github.com/hyperzlib/DG-Lab-Coyote-Game-Hub/blob/main/docs/api.md]
