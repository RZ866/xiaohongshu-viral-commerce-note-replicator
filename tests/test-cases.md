# 测试与复现

## 用户要求的12项核心场景

| 场景 | 具体验证 |
|---|---|
| 1 对标截图+商品文字 | 原创文字卡实际查看，嵌入HTML，完整五标题三方案 |
| 2 对标文字+商品截图 | 原创商品卡实际查看，引用PRODUCT证据，图片自包含 |
| 3 Analyzer+商品 | 上游DNA保持分析类型，不升级商品事实 |
| 4 只有对标 | 清点已有内容，问商品名称与用途，不编三套 |
| 5 只有商品 | 问对标，不假造爆款DNA |
| 6 商品可选信息缺失 | 未知项明确展示，仍完成可做的创作 |
| 7 第一人称故事 | 原作者亲属/七天不能移植，未提供的体验短语被拦截 |
| 8 效果宣称 | 不把对标效果变成用户商品效果；无关事实绑定也不能放行常见风险词 |
| 9 三篇差异 | 正文、开头、场景、结构、商品位置、信任、CTA比较，重复反例拒绝 |
| 10 标题原创 | 五标题不同钩子，原题/近义题反例拒绝；人工检查句式与机制 |
| 11 HTML | 桌面/手机视口、中文、嵌图、离线、A4 PDF和实际截图 |
| 12 安全 | script/标签/引号/中文/Emoji转义、目录逃逸拒绝，实际浏览器不执行 |

## 开发者命令

```sh
python -m unittest discover -s tests -v
python tests/make_examples.py
python tests/prepare_browser.py
node tests/browser_check.cjs --browser /path/to/chromium
python scripts/package_release.py
python tests/verify_installer.py --installer /path/to/official/install-skill-from-github.py --package dist/xiaohongshu-viral-commerce-note-replicator-v1.0.0.zip
```

Python运行时仅标准库。浏览器检查需要开发环境的Node/Playwright/Chromium，演示图重绘可选Pillow与中文字体，官方validator需要PyYAML。它们不进入安装包。实际运行本机官方quick_validate.py，不复制改写验证器冒充官方检查。

## 专项语义验收

反洗稿：比较原标题句法、特色表达、故事关系和段落功能；新商品事实是否来自自身资料。程序相似度仅辅助，无法识别全部语义换词。

三方案差异：读实际正文，不仅看标签。A/B/C至少在三个关键维度不同；封面大字不许承诺正文无法证明的结果。五标题中恰好三个与正文对应，其余两个备用。

独立前向测试应只给Skill与新原始材料，不提供目标答案。本版使用另外一组原创挂钩对标和收纳袋商品，测试过程中未读取示例答案。QA产物隔离，不公开到仓库。

没有将手写JSON渲染测试称为“所有真实视觉模型均通过”，没有验证WorkBuddy实机、新仓库在线安装或真实交易表现。
