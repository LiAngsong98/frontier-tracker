# 我花了一个周末，做了一个「自动刷文献」工具

读研以来，每周最痛苦的事不是写论文，而是**刷文献**。

打开 Google Scholar，搜关键词，翻几页，点进去看摘要，发现不是想要的，再翻……周而复始，一个下午过去了，真正有用的论文可能只找到两三篇。

更烦的是，你明明知道有几本核心期刊（比如你方向的 CAS 1 区、JCR Q1），但每次都要手动去翻。有时候偷懒一周没刷，下次打开就堆了几十篇未读，心理压力更大。

于是我想：**能不能让机器帮我刷？**

---

## 我做了什么

**frontier-tracker** — 一个学术前沿文献自动追踪工具。

它的逻辑很简单：

1. **你告诉它关注哪些期刊** — 比如 Nature、Science、Remote Sensing of Environment、Ecological Indicators……随你定
2. **它自动扫描最近一周的新论文** — 通过 OpenAlex API 抓取元数据（标题、作者、摘要、DOI）
3. **按你的研究方向智能筛选** — 用你定义的关键词 profile，把论文分成「核心」「近端」「背景」「噪音」四层
4. **生成一份 HTML 周报** — 打开就能看，带摘要、带链接，按相关度排序

整个过程 **5 分钟跑完**，覆盖 76+ 本顶级期刊，每周自动产出一份干净的文献周报。

---

## 它不是什么

- **不是文献管理器** — 不替代 Zotero、EndNote，它只管「发现」这一步
- **不是 AI 选论文** — 不用大模型判断论文好坏，纯关键词 + 规则，可解释、可调参
- **不是只服务一个方向** — 通过切换 profile，同一套代码可以追踪遥感、生态、GIS、环境科学……任何方向

---

## 技术细节（给技术向读者）

**摘要补全：** OpenAlex 的 `abstract_inverted_index` 能覆盖约 44% 的最新论文。为了补全剩下的，我加了三路 fallback：

- OpenAlex（按 DOI 重查）
- Crossref（abstract 字段，去 HTML 标签）
- Semantic Scholar（abstract + tldr AI 高亮摘要）

对于发表不到一周的新论文，三个 API 可能都还没索引——这是正常的延迟，不是 bug。但对发表 1-3 个月的论文，三路 fallback 能把覆盖率从 44% 拉到 70-80%。

**Profile 系统：** 每个研究方向用一个 markdown 文件描述，包含三层关键词：

```markdown
## Core keywords
remote sensing
deep learning
land cover classification
...

## Proxy keywords
GIS
spatial analysis
...

## Eco-context keywords
ecosystem
vegetation
...
```

筛选逻辑是：标题 + 摘要命中 Core → 核心；命中 Proxy → 近端；命中 Eco → 背景；都不命中 → 噪音。你可以随时编辑 profile 文件，重新跑一遍就行。

---

## 怎么用

```bash
git clone https://github.com/LiAngsong98/frontier-tracker.git
cd frontier-tracker
pip install requests openpyxl

# 第一步：创建你的期刊关注列表
python -X utf8 scripts/build_top_family_watchlist.py

# 第二步：扫描最近一周
python -X utf8 scripts/scan_recent_papers.py \
  --watchlist your_watchlist.json \
  --output scan.json

# 第三步：按 profile 筛选
python -X utf8 scripts/screen_by_profile.py \
  --input scan.json \
  --profile references/example-profile.md \
  --output screened.json

# 第四步：生成报告
# 打开 outputs/reports/ 下的 HTML 文件
```

第一次用需要花 10 分钟配置你的 research profile，之后每周一键跑就行。

---

## 为什么做这个

说实话，市面上不缺文献工具。Google Scholar Alerts、ResearchGate 推荐、各种 RSS 订阅……我都试过。

问题是：**它们推的不是我想要的。**

Google Scholar 的推荐算法会推一堆相关但不核心的论文；ResearchGate 的推荐取决于你关注了谁；RSS 订阅需要你手动维护源。

frontier-tracker 的逻辑是反过来的：**你先定义什么是重要的，然后让机器去筛。** 不依赖任何推荐算法，不依赖社交网络，纯靠你对领域的理解 + 关键词规则。

这很朴素，但很可靠。

---

## 未来计划

- [ ] 支持更多数据源（PubMed、arXiv、Web of Science）
- [ ] 自动化 cron 定时扫描
- [ ] 支持 Zotero / Obsidian 笔记导出
- [ ] 多 profile 并行（同时追踪 2-3 个方向）

---

## 最后

GitHub 地址：https://github.com/LiAngsong98/frontier-tracker

如果你觉得有用，欢迎 star ⭐。如果有问题或建议，欢迎 issue。

**每周省下 2 小时刷文献的时间，用来写论文不香吗？**

---

*作者简介：[待补充]*

*研究方向：[待补充]*
