# 内部数据契约1.0

宿主写JSON，用户无需填写。完整结构可看 `examples/text/input.json`，但必须根据当前材料重新分析和写作，不能套用示例答案。所有语义均由宿主生成，脚本不会从材料推断DNA或编正文。

## 根字段

- `schema_version`: `1.0`；`mode`: `standalone`或`analyzer`；`status`: `complete`或`needs_input`；`example`: 是否合成演示。
- `sources`: 对标、商品、上游结果；每项id、origin(`BENCHMARK/PRODUCT/ANALYZER`)、kind(`text/image`)、label。文本有content；图片有inspected布尔值、可选file（相对media-root路径）、可选transcription（宿主实际读到的文字）。对标可有title，用于原创标题比较。看不清不得猜录。
- `evidence`: id、source_id、location、observation、clear。文本证据另有quote，必须确实存在于content中；图片必须已实际查看，不能自称OCR核验。
- 通用statement：`{text, type, evidence_ids}`。type只能为`BENCHMARK_FACT / PRODUCT_FACT / ANALYSIS / CREATIVE`。事实必须全部引用清楚的对应origin；ANALYZER不能成为商品事实来源。原创创作的引用表示采用的材料，不表示原作者说过这段新文案。
- `product`: name,purpose,price,spec,audience,scene,pain,benefits,reason,obstacle,trial_cost,visual,showable,proof,forbidden；值是PRODUCT_FACT statement或null。name及purpose是完整任务最低条件；分析性购买理由等写进analysis.fit，不假装用户已提供。

## 完整任务

- `analysis.core`: ANALYSIS statement。
- `analysis.dna`: traffic,retention,trust,conversion,formula；ANALYSIS statement或null；formula必需。信息不足的阶段留null。
- `analysis.fit`: level=`高/中/低`，inherit/modify/abandon各至少一条ANALYSIS statement，opportunity为ANALYSIS statement。没有可继承项时也明确说明不存在及原因，不虚构肯定结论。
- `titles`: 恰好5项{id,copy:CREATIVE statement,hook,why:ANALYSIS statement}，id如T1。
- `plans`: 顺序A/B/C，title_id分别引用不同标题。angle/opening/scene/structure/product_position/benefit_order/trust/cta均非空字符串。opening必须等于paragraphs第一段，cta等于最后一段；不允许只填不同策略标签却使用相同正文。
- `plans[].cover`: concept,subject,person_product,scene,headline,composition,placement,focus,hook,reason,production,boundary这12个字符串。
- `plans[].paragraphs`: 完整正文段落字符串列表，2至16段，正文至少80个规范化字符只是结构下限，不代表质量合格。通常按内容需要写3至6段。
- `plans[].inherits`: 引用非空DNA键；differences至少两条实际变化；test有variable,observe,decision三个字符串。
- `fact_uses`: `{text,field}`列表，把草稿中商品断言的**实际短语**绑定product字段。例如`{"text":"12.9元","field":"price"}`。需要绑定所有商品事实；脚本特别检查数字和常见风险短语，其他断言由宿主语义审查。禁止用无关事实键放行效果宣称。
- `priority`: 3项，plan_id覆盖A/B/C且不重复，reason为ANALYSIS statement；顺序就是优先顺序。
- `limitations`: 事实、素材、归因等边界字符串列表。
- `review`: expression/story/structure/diversity/facts五项具体说明，每项至少12字；逐条阅读作品后填，不能由模板自动认证原创。

标题未被plans采用的两项自动显示为备用，不增加第六第七项。事实与分析字段的引用可展开查看，正文有统一原创标记并在末尾给事实绑定。

## 缺关键输入

status=`needs_input`；保留已有sources、evidence、product与可做的analysis；partial是一段已完成的清点/分析说明；titles与plans为空或省略。脚本根据缺口生成一个必要追问，不生成假三套方案。没有对标先问对标；没有商品名称/用途再问商品。缺可选价格或规格不应转为needs_input。

## 运行

`python scripts/generate_report.py input.json --media-root private-media --output outputs/run/xiaohongshu-replication-report.html`

这是宿主内部命令示意。必须正确引用实际路径，不把用户文字拼到shell。默认失败信息不输出材料或个人路径；内部定位可用--debug。输出HTML、chat-summary.md、original-notes.md。生成失败不写半份新HTML，宿主不能链接此前旧文件冒充本次成功。
