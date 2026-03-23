# Any-API-Check

Any-API-Check 是一个桌面工具，用来集中管理中转站和兼容 API 站点，处理余额查询、签到、WAF Cookie、模型同步和接口验证。

## 功能

- 站点管理，维护 URL、API Key、Cookie、标签、代理和高级接口字段
- Provider 管理，自定义登录路径、签到路径、用户信息路径和 WAF Cookie 名称
- 余额查询，支持 Bearer、URL Key 和 Cookie 两种账户查询路径
- 浏览器登录辅助，借助 Edge 持久化会话处理 Cloudflare 或其他 WAF
- 签到中心，支持单站签到、全部签到、签到日志查看和 Cookie 刷新
- 模型记录，支持站点模型发现、流式探测、非流式探测和单模型验证
- 验证与对话，可做连通性、真实性和聊天接口测试
- 总览面板，展示余额、类型分布、签到趋势、充值趋势和最近动作日志
- 托盘运行，支持最小化到系统托盘

## 项目结构

- `app.py` 应用入口
- `relay_console/main.py` 桌面启动逻辑
- `relay_console/bridge.py` 前后端桥接和动作分发
- `relay_console/runtime/` API、数据库、图表、预设和工具函数
- `relay_console/web/` 前端页面和静态资源
- `config/templates/` 默认模板文件
- `config/presets/` 内置预设和 CLI 资源
- `scripts/build_windows.py` PyInstaller 打包脚本
- `scripts/build_installer.py` Inno Setup 安装包脚本
- `build/installer/Any-API-Check.iss` 安装器定义

## 运行环境

- Python 3.11
- Windows 桌面环境
- Edge WebView2 运行时
- 可选，Playwright 浏览器辅助流程
- 可选，Inno Setup 6 用于生成安装包

## 安装与运行

先安装依赖。

```bash
pip install -r requirements.txt
```

开发运行。

```bash
python app.py
```

调试模式。

```bash
python app.py --debug
```

## 打包

生成 onedir 桌面包。

```bash
python scripts/build_windows.py
```

生成安装包。

```bash
python scripts/build_installer.py
```

如果只想把已有的 onedir 目录封成安装包。

```bash
python scripts/build_installer.py --skip-build --source-dir dist\Any-API-Check
```

## 数据存储

源码运行时，运行数据默认写在项目根目录。

- `config/app.db`
- `config/browser_profiles/`
- `debug/requests.log`

冻结后的 Windows 打包版，运行数据会迁移到用户目录，不再写进 `dist`。

- `%LOCALAPPDATA%\Any-API-Check\config\app.db`
- `%LOCALAPPDATA%\Any-API-Check\config\browser_profiles\`
- `%LOCALAPPDATA%\Any-API-Check\debug\requests.log`

内置模板和资源仍然从程序目录读取。

- `config/templates/`
- `config/presets/cli_tools.json`
- `config/presets/cli_system.json`

自定义预设会保存在运行时目录。

- `%LOCALAPPDATA%\Any-API-Check\config\presets\api_presets.json`

## 安装包说明

安装包基于 Inno Setup，默认安装到当前用户目录。

- 安装目录 `%LOCALAPPDATA%\Programs\Any-API-Check`
- 运行数据目录 `%LOCALAPPDATA%\Any-API-Check`

这样重装或升级程序时，不会把数据库和浏览器会话塞回程序目录。

## 开发说明

如果要提交仓库，建议不要把这些内容一起提交。

- `dist/`
- `dist_verify/`
- `dist_installer/`
- `build/pyinstaller*/`
- `build/spec*/`
- `config/app.db`
- `config/browser_profiles/`
- `config/browser_profiles/login_helper_cookies.json`
- `debug/`

## 已知说明

- 浏览器登录辅助依赖本机 Edge
- 安装器脚本默认用英文界面，如果本机 Inno Setup 没带中文语言包，会自动使用英文安装向导
