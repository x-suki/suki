# Static Access · suki（静态站）

把三个本地项目的数据汇成一份**纯静态、只读**的站点（代号 **suki**，正式名待定）：
B站收藏 / Anime Note 番剧书架 / Game Note 游戏库，带笔记展示、搜索、筛选和详情弹窗。
双击 `index.html` 即可打开（file:// 直开可用），
整个文件夹也可以原样发布到 GitHub Pages / Cloudflare Pages 等任意静态托管。

## 使用

1. **同步发布**：双击 `同步数据.bat`——重新导出**本地已有**的数据并推送到 GitHub
   （只读源项目文件，不触发B站/Steam/Bangumi更新；直连失败自动改走本机代理）
2. **查看**：双击 `index.html`，或访问 GitHub Pages 线上站
3. **页内更新**：页脚「检查更新」——经 GitHub API 拉最新 data.js、页面热替换，无需重开页面
   （走 api.github.com 绕开 CDN 缓存，推送后即可拉到；未认证限额 60 次/时/IP，个人使用足够）
4. **仅本地重新导出不发布**：双击 `重新生成.bat`

## 自动发布（已启用，事件驱动）

三个源项目各自的更新/变更**成功后**，会自动异步触发本目录的 `notify_push.py`
（防抖合并 + 幂等导出 + git push，直连失败自动走代理；日志 `notify_push.log` 只留最近一次）：

- **Bili Project**：页内同步成功后（含 3 小时过期自动刷新），立即发布
- **Game Note**：同步资料页、笔记/链接增删改、上传截图、待玩区变更成功后，立即发布
- **Anime Note**：任何成功的写请求（增删改作品/笔记/媒体/设置）后，3 分钟防抖合并再发布

页面侧仍是页脚「检查更新」：从 GitHub 拉最新发布数据热替换。
手动兜底：双击 `同步数据.bat`（与自动触发完全同一套导出+推送）。
边界不变：主机关机/休眠期间无法读取磁盘，线上数据停留在最后一次发布；
私密收藏夹仍靠 `export.py` 的 `EXCLUDE_FOLDER_IDS` 把关（自动发布会如实推出去）。

## 本机刷新（在网页上一键让主机现拉现发）

「检查更新」只能拉**已发布**的数据；「本机刷新」则反过来——把按钮做成指令，
让数据主机当场从 B站/Steam/Bangumi 拉最新数据并自动发布，页面随后自动热替换：

```
线上页(你的浏览器) → fetch 127.0.0.1 触发三服务同步 → 各服务已有钩子自动推 GitHub
                    → 页面轮询检查更新 → 热替换重渲染
```

- 三服务**没在跑**时，页面会跳 `suki-refresh:` 自定义协议把它们静默拉起（处理器
  `bili_link.py` 只拉服务、不触发同步，动作串白名单，日志 `bili_link.log`）。
- **一次性安装**（当前用户注册表，无需管理员；在 cmd 里逐条执行或存成 bat）：

  ```bat
  reg add HKCU\Software\Classes\suki-refresh /ve /d "URL:suki 本机刷新" /f
  reg add HKCU\Software\Classes\suki-refresh /v "URL Protocol" /d "" /f
  reg add "HKCU\Software\Classes\suki-refresh\shell\open\command" /ve /d "\"<pythonw.exe 完整路径>\" \"<本目录完整路径>\bili_link.py\" \"%%1\"" /f
  ```

  验证：Win+R 输入 `suki-refresh:refresh`；卸载：`reg delete HKCU\Software\Classes\suki-refresh /f`
- 首次使用浏览器会问两次：**本地网络访问权限**（线上页访问 127.0.0.1 需允许）+
  **打开 suki-refresh?**（可勾选始终允许）。之后服务常驻，纯静默。
- **安全放行面**：三个服务只对 `https://x-suki.github.io` 放行各自的触发/探活端点
  （B站 status/progress/refresh · 游戏 ping/recent · 番剧 ping/refresh_all）；
  **数据端点（含 B站私密收藏夹）跨源一律不可读**，`file://` 的 null 源也不放行——
  本机刷新只在线上站可用，file:// 直开只影响"看"，不影响数据。换设备（手机等）
  打开时探测不到主机服务，会明确提示而不是误触发。
- 已知边界：GitHub API 检查更新有 60s 缓存，同步完成后页面最多再等约 1 分钟才见到新版；
  浏览器"本地网络访问"机制（Chrome/Edge LNA）仍在演进，若将来收紧，按钮会探测失败并给出引导。

顶部搜索框可跨三板块搜全部内容（标题/UP主/简介/笔记/游戏详情等）；各板块内的搜索框只搜本板块。
快捷键：`/` 聚焦当前板块搜索框 · `Esc` 关弹窗/清空 · `1~4` 切换 总览/视频/番剧/游戏。
视频卡片上的**笔记条可点击**，弹窗查看全文（含图片）；番剧/游戏卡片点击进详情弹窗，游戏笔记里的截图直接内嵌显示。

## 文件说明

| 文件 | 说明 |
|---|---|
| `export.py` | 导出器：读源项目数据 → 生成 `data.js` + 封面/截图副本 |
| `index.html` | 站点本体（手写，不参与生成，改样式直接编辑它） |
| `bili_link.py` | `suki-refresh:` 协议处理器（「本机刷新」拉起本机服务，见上文；`bili_link.log` 是它的日志） |
| `data.js` | 生成物：`window.STATIC_DATA = {...}`（用 `<script>` 而非 fetch 加载，兼容 file://） |
| `version.json` | 生成物：`{generated_at}` 轻量版本标记，页面「检查更新」先拉它对比再决定是否下载 data.js |
| `covers/anime/` `covers/game/` | 生成物：封面副本（游戏封面命名 = URL 的 md5，与 Game Note `/img` 端点同规则） |
| `gmedia/` | 生成物：游戏笔记里内嵌的截图（源文件在 Game Note `data/media/`） |
| `WORKLOG.md` | 工作日志 |

三个源项目（`../Bili Project`、`../Anime Note`、`../Game Note/steam-play-data`）**只读不写**；
某个项目数据缺失时导出器会跳过该板块并在控制台提示，站点自动隐藏对应页签。

## 隐私（发布前必读）

- **收藏夹没有公私标记**：B站缓存里不带 privacy 字段，导出器无法自动识别私密收藏夹。
  发布前逐个检查 7 个收藏夹，如有私密内容，把其 id 填进 `export.py` 顶部的
  `EXCLUDE_FOLDER_IDS` 再重新导出。
- 站点内**没有任何凭据**（SESSDATA / Steam 登录态都不在此目录），数据本身只含收藏与笔记。
- 失效视频、UP主名、笔记全文都在导出数据里，发布即公开，自行斟酌。
- `同步数据.bat` 会把导出数据直接推到公开仓库——发布前确认 `export.py` 顶部
  `EXCLUDE_FOLDER_IDS` 已排除私密收藏夹（脚本输出里也有提醒）。

## 封面来源

| 板块 | 策略 |
|---|---|
| 视频收藏 | 热链 B站 CDN（`hdslb.com`，`referrerpolicy="no-referrer"`），不占本地空间 |
| 番剧 | 本地副本（源站 Bangumi 需代理，访客未必有） |
| 游戏 | 本地副本（Game Note 已落盘的封面缓存），缺失时回退 Steam 直链 |
