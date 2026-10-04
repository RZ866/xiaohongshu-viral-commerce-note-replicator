# 真实规范与安装机制

创建文件前已检查本机官方skill-creator、openai.yaml说明、quick_validate.py、skill-installer及实际install-skill-from-github.py，查看bundled documents Skill作为官方结构示例，并检查现有Analyzer的入口、模板与生成器。没有把DOCX示例的工作流套进本项目。

遵循真实结构：SKILL.md的name/description/license；agents/openai.yaml单独负责展示；references渐进披露，scripts做确定性任务，assets放模板。名称小写短横线且少于64字符。validator校验入口，不证明创作质量。

## 需求与能力的调整

1. “经过验证的爆款逻辑”：用户只有截图时无法验证表现，保留机制但标假设，不把商品事实与效果混淆。
2. “安装即用”：需宿主原生视觉和文件能力；脚本需已有Python3.10+。本项目不额外要求OCR、密钥或数据接口，但不能宣称所有平台零运行时前提。
3. “生成封面”：交付用户要求的封面策划，未调用图像工具生成成品，不假称提供图片。
4. “反洗稿测试”：程序检查可观察重复；独立前向测试与人工对照补充语义检查，不虚构原创率或法律认证。
5. “GitHub安装”：官方安装器根URL还要传--path .和明确--name；README给宿主正确指令。已有目录拒绝覆盖。本项目ZIP用真实安装器验证，只替换下载响应，不等于新仓库已在线发布。
6. “适合发布”：本轮创建独立本地项目与发行ZIP，未擅自创建新远端或写入全局Skill目录。Analyzer真实公开地址已在上游联动说明中给出。

本机可读取用户上传附件的本地路径、原生查看图片、生成本地可链接HTML。本项目不把本机绝对路径写入公开文件；对其他宿主需以其实际工具能力为准。WorkBuddy与手机硬件未实机验收。

官方参考入口：[Build skills](https://developers.openai.com/plugins/build/skills)。本次实现判断以实际读取的本机官方规范和运行结果为依据，不冒称已查询未读取的新版本网页。

## 发布补充（2026-10-04）
用户授权后已创建独立公开仓库 RZ866/xiaohongshu-viral-commerce-note-replicator。官方安装器真实网络下载、安装后61项测试及六类报告生成通过；GitHub Actions四组跨平台检查通过。上文未发布描述是开发阶段记录；未进行全局安装，WorkBuddy仍未实机验收。
