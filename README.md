# Static Access · suki（静态站）

把三个本地项目的数据汇成一份**纯静态、只读**的站点（代号 **suki**，正式名待定）：
B站收藏 / Anime Note 番剧书架 / Game Note 游戏库，带笔记展示、搜索、筛选和详情弹窗。
双击 `index.html` 即可打开（file:// 直开可用），
整个文件夹也可以原样发布到 GitHub Pages / Cloudflare Pages 等任意静态托管。

## 使用

1. **更新数据**：双击 `重新生成.bat`（或命令行 `python export.py`）——只读三个项目的数据文件，不影响原项目
2. **查看**：双击 `index.html`
3. **页内刷新（免 bat，三板块都行）**：页脚「导入更新」→ 选包含项目数据的文件夹——
   选 `D:\AAA_articafts` 三个板块一起刷，只选某个项目目录就只刷它。
   视频收藏吃 `favorites_cache.json`+`notes.json`；番剧吃 `anime_note.db`+封面；
   游戏吃 `steam.db`+封面/截图（SQLite 由页面内置的迷你读取器解析，零依赖；
   图片副本存 IndexedDB）。数据只存本浏览器、比发布版新才生效，「还原发布版」一键回退。
4. **发布**：把整个文件夹（`index.html` + `data.js` + `covers/` + `gmedia/`）上传到静态托管即可

快捷键：`/` 聚焦搜索 · `Esc` 关弹窗/清空 · `1~4` 切换 总览/视频/番剧/游戏。
视频卡片上的**笔记条可点击**，弹窗查看全文（含图片）；番剧/游戏卡片点击进详情弹窗，游戏笔记里的截图直接内嵌显示。

## 文件说明

| 文件 | 说明 |
|---|---|
| `export.py` | 导出器：读源项目数据 → 生成 `data.js` + 封面/截图副本 |
| `index.html` | 站点本体（手写，不参与生成，改样式直接编辑它） |
| `data.js` | 生成物：`window.STATIC_DATA = {...}`（用 `<script>` 而非 fetch 加载，兼容 file://） |
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
- 页内「导入更新」产生的数据与图片副本只存在你自己浏览器的 localStorage / IndexedDB 里，不会进入仓库或发布物。

## 封面来源

| 板块 | 策略 |
|---|---|
| 视频收藏 | 热链 B站 CDN（`hdslb.com`，`referrerpolicy="no-referrer"`），不占本地空间 |
| 番剧 | 本地副本（源站 Bangumi 需代理，访客未必有） |
| 游戏 | 本地副本（Game Note 已落盘的封面缓存），缺失时回退 Steam 直链 |
