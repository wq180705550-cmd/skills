---
name: cfa-image-to-xmind
description: >
  把 CFA/学习资料的截图或纯图片型 PDF 转成可直接打开、不报错、标记还原度高的可编辑 XMind 思维导图。
  覆盖：XMind 2020+ 文件格式规范、content.json 数组陷阱、纯图片 PDF 渲染、像素级标记(红★/红旗/黄★)定位与形状判别、
  原文逐字核对、纯英文不翻译、批量多树分文件。
  触发词：思维导图、Xmind、mind map、知识框架图、把截图/PDF 做成脑图、标记还原、优先还原标记。
agent_created: true
---

# 截图 / PDF → XMind 思维导图

## 核心目标（成功标准，可独立验证）

1. 双击能打开，**不报错**
2. 节点内容完整、层级正确衔接、不遗漏、不错配
3. 标记逐一还原（红★ / 红旗 / 黄★），形状与颜色都对
4. 加红加粗文字也要还原
5. 原文语言不变（源是英文就保持英文，**不做中文翻译**）

---

## 一、XMind 文件格式（必须严格遵守）

`.xmind` 就是一个 zip，最少三个文件：

| 文件 | 要点 |
|---|---|
| `content.json` | **顶层必须是数组**（sheet 列表）。写成对象是打开报错的头号原因 |
| `metadata.json` | 至少含 `creator: {name, version}` 和 `activeSheetId` |
| `manifest.json` | `{"file-entries": {"content.json": {}, "metadata.json": {}}}` |

topic 节点结构：

```python
def N(title, children=None, m=None):
    t = {'id': str(uuid.uuid4()), 'title': title, 'extensions': []}
    if m:                      # m 可为 str 或 list
        t['markers'] = [{'class': 'marker', 'markerId': x}
                        for x in ([m] if isinstance(m, str) else m)]
    if children:
        t['children'] = {'attached': children}
    return t
```

- `rootTopic` 额外需要 `class: "topic"` 和 `structureClass: "org.xmind.ui.logic.right"`
- marker 必须包成 `[{'class':'marker','markerId':...}]`。
  **易错点**：把字符串直接迭代会得到 `markerId='s'`、`'t'`…，必须 `isinstance` 判断包成 list

`metadata` / `sheet` 参考骨架：

```python
sheet = {'id': str(uuid.uuid4()), 'class': 'sheet', 'title': '<root title>',
         'rootTopic': root, 'topicPositioning': 'fixed',
         'theme': {'id': str(uuid.uuid4()), 'importantTopic': {}, 'map': {'id': str(uuid.uuid4())}}}
content = [sheet]
```

---

## 二、标记还原（最容易出错的一步）

### 2.1 合法 markerId

```
star-red  star-yellow  star-orange  star-green  star-blue ...   # 星，红底白五角星
flag-red  flag-yellow  flag-orange  flag-green ...              # 旗，红底白旗形
priority-1 .. priority-9
tag-* / task-* / smiley-* / people-* / arrow-* / symbol-*
```

### 2.2 **红旗与红星必须靠图形轮廓区分，不能只看颜色**

`flag-red` 和 `star-red` **都是红圆 + 白色图形**（底色都是 `#FF4747`），只看颜色完全分不出来。
唯一的权威判据是图形轮廓：

- `flag-red` = 红圆内一个**白旗**（左侧竖杆 + 右上方三角/矩形旗面）
- `star-red` = 红圆内一个**白五角星**

**查证方法**：从本机 XMind 安装包解出官方 SVG 图标直接看。

```python
import struct, json
# 路径按本机实际安装位置调整
p = r'C:\Users\Administrator\AppData\Local\Programs\Xmind\resources\app.asar'
f = open(p, 'rb')
_, hdr_size, _, json_size = struct.unpack('<IIII', f.read(16))
idx = json.loads(f.read(json_size).decode('utf-8'))
base = 16 + hdr_size             # 文件数据起始偏移

def walk(node, path, out):
    for k, v in node.get('files', {}).items():
        cur = path + '/' + k
        if v.get('files') is not None:
            walk(v, cur, out)
        else:
            out[cur] = (base + int(v['offset']), int(v['size']))

files = {}
walk(idx, '', files)
# 标记图标在 /static/snowbird/resource/markers/<组>/<markerId>.svg
# 组：flagMarkers(10) starMarkers(10) priorityMarkers(9) tagMarkers taskMarkers ...
# 解出 flag-red.svg / star-red.svg 看 <path d="..."> 即可确认形状
```

**在小尺寸（15px）下不要用 IoU 模板匹配**去自动分类——掩膜噪声大、极易误判。
可靠做法：把每个候选图标裁出来，用 **NEAREST 放大 18 倍**拼成一张 montage 图目视比对，一眼就能分清旗和星。

### 2.3 像素级定位标记

```python
red = (R > 140) & (R - G > 50) & (R - B > 50)
lab, n = ndimage.label(red)          # 真标记 = 正方形实心块，px 数约为边长的平方×0.8
```

**标记尺寸随图片缩放变化，不要硬编码**：不同截图里实测到过 **15×15（约 130~150 px）** 和
**18×18（约 190~200 px）** 两种规格。用「近似正方形 + 像素数占位率高」判定，不要写死尺寸。

**必须排除 ClearType 次像素抗锯齿伪影**：它们是 1px 宽的竖条、低饱和（RGB 三通道都 >110 且彼此接近）。
判据：宽度 ≤ 2px 且像素数 < 20 的，一律不当标记。

黄★扫描（确认有没有漏）：

```python
yellow = (R > 170) & (G > 140) & (B < 120) & (abs(R - G) < 80)
```

红字（加红加粗）扫描：找出**非 15×15 规格**的较大红色块；没有则说明无红字。

### 2.4 用户模板 ≠ 截图

用户常给一段固定模板（「根节点红★；节点上的红★、黄★…」），**模板措辞未必与截图一致**。
规则：
- **截图是唯一事实来源**。模板与截图冲突时按截图做，并在回复里说明差异。
- 模板未提到的标记，截图里若有也必须还原；反之亦然。
- 根节点按惯例固定给 `star-red`（截图里根节点通常不画标记）。

### 2.5 **旗还是星：小尺寸下的决定性判据（比模板匹配可靠得多）**

地图缩小后标记只有 9~14px，IoU 模板匹配噪声太大。用**几何位置**判，一步定论：

- 旗的图形 = 左侧竖杆 + 右上方旗面，竖杆贯穿全高 → **底部 25% 行的墨迹只落在最左侧**
- 星的图形 = 五角星，最低点是下方尖角 → **底部 25% 行的墨迹落在水平居中处**

```python
sub = sat_mask[y:y+h, x:x+w]                 # 单个标记的色块掩膜
rows = np.where(sub.any(1))[0]
bot = sub[int(rows.min()+(rows.max()-rows.min())*0.75): rows.max()+1]
cols = np.where(bot.any(0))[0]
rel = (cols.min()+cols.max())/2 / w          # 相对位置
# rel ≈ 0.06~0.11 → 旗（杆在左）；rel ≈ 0.5 → 星
```

理论值可自证（从官方 SVG 的 `path` 直接算）：旗的杆中心 rel = 0.083，星的底尖 rel = 0.515。
**实测过 8 个标记全部 rel≤0.11 → 8 个全是旗**，而用户模板写的是「红★」——按截图做，并在回复里说明。

### 2.6 配色比对：把「黄」定成 `flag-yellow` 还是 `flag-orange`

先取标记内**饱和度最高的像素**（多取几个取均值），再跟官方色板比：

| markerId | 官方填充色 | 备注 |
|---|---|---|
| `flag-red` / `star-red` | `#FF4747` | |
| `flag-yellow` / `star-yellow` | `#F0C800` | 偏金黄 |
| `flag-orange` / `star-orange` | `#FF9D43` | 偏橙 |
| `flag-green` | `#20C07D` | |
| `flag-blue` | `#577CFF` | |

注意：小尺寸渲染 + 缩放会让颜色漂移（实测红色 `#FF4747` 被采样成 `(249,76,81)`），
所以**只做粗判**，源图颜色落在两个标准色之间时，按用户用语定（用户说「黄」→ `flag-yellow`）。
另注意：部分地图里的旗是**纯色旗形、没有圆形底**，形状仍是旗，不影响 markerId 的选择。

---

## 三、加粗与特殊标点的判定（极易误判）

### 3.1 判定是否加粗：用「同一个词」的游程分布，不要用均值

**均值笔画宽不可靠**——受 ClearType 亚像素渲染影响，同一字重的不同文本行均值会在
1.4~1.9 之间漂移，没有区分度。更危险的是：**把裁剪图 LANCZOS 放大后目视判断，会产生
"这行看起来更粗"的错觉**（实为亚像素相位差异）。

可靠做法：挑一个**在多个候选行中重复出现的词**（如 "growth"），只比较这个词：

```python
def run_hist(reg_dark):
    """水平游程长度分布 = 竖笔画宽度分布"""
    out = []
    for row in reg_dark:
        c = 0
        for v in row:
            if v: c += 1
            elif c: out.append(c); c = 0
        if c: out.append(c)
    return [r for r in out if 1 <= r <= 8]
```

判据：Regular 文本 **1px 游程占 36~44%、2px 占 40~52%**；Bold 会让分布整体右移
（1px 降到 <15%，2~3px 成为主体）。若同一词的 1px 占比在两行接近，就是同一字重。

### 3.2 区分 en dash / em dash / 连字符

用**同一份资料里已知的连字符做基准校准**（跨图也行，字体字号一致即可）。
方法：取中间高度行，量横线墨迹宽度（多阈值扫描确认稳定值）。

实测参考：连字符 ink = **2px**；"Cobb–Douglas" 的横线 ink = **12px（6 倍）** → 是长破折号。

**注意陷阱**：CJK 字体的 en dash 常被渲染成约 0.8em 宽，所以**仅凭宽度无法区分 en 与 em dash**。
此时按排印规范定：复合人名/术语（Cobb–Douglas、Mundell-Fleming）用 **en dash（U+2013）**，
它在 XMind 里的观感与 em dash 几乎无差别。

### 3.3 撇号

`Solow's` 这类撇号在截图中常只有 2×3 像素，**从形状无法区分 `'`(U+0027) 与 `’`(U+2019)**。
判据改为看文档整体排印风格：若文中已使用排印型长破折号，则取 **`’`(U+2019)**。

### 3.4 上标符号

`g* and G*` 这类上标星号，XMind 的 `title` 是纯文本，无法做上标，
按 **`g* and G*`** 平铺写入，并用 Read 工具确认星号数量与位置。数学下标同理用 Unicode 下标字符。

---

## 四、源材料处理

### 纯图片型 PDF → PNG

```python
import pymupdf                      # 环境：venv 内已装 pymupdf / pypdf / scipy / Pillow
doc = pymupdf.open(pdf_path)
for i, page in enumerate(doc):
    page.get_pixmap(dpi=200).save(f'p{i}.png')
```

### 文字核对

小字号看不清时：`PIL.crop` 目标区域 → `resize(..., Image.LANCZOS)` 放大 3~4× → 用 Read 工具读图。
**逐块核对**，不要凭整体缩略图猜文字。注意区分易混字符：大小写（`FX Market` 的 F/X/M）、
连字符（`Mundell-Fleming`、`Mark-to-market`、`Portfolio balance`）、斜杠（`Flow supply/demand channel`）。

**中英混排小字（≤8px）用 20× NEAREST 逐字切**：LANCZOS 会把 7px 的字形插值糊成假笔画。
判"全角逗号 `，` 还是半角 `,`"、"`π` 还是 `m`"这类问题时，直接打印像素 ASCII 图 + 列墨迹量，
找列墨迹的**局部极小值**当字形边界。例：源图实测为 `1、先算mu与nd`（确为拉丁字母 mu/nd，不是 πu/πd）。

### 前景遮挡（视频截图常见）

讲师人像/字幕条会**压住节点文字**。表现：某行文字在某个 x 处突然断掉，右侧落在人像色块里。

```python
# 先框出人像区域（饱和肤色大色块），再把该区域从 dark 掩膜里剔除
skin = (R>170) & (G>120) & (R-B>40) & (R-G>25)      # 逐图调参
# 被遮挡的行：可见部分远短于同类节点 → 标出来，别硬猜
```

处理原则：**可见多少写多少，被遮挡部分按同源材料补全并在回复里明确说明**。
例：`options on cu…`（被讲师挡住尾部）→ 按另一张图里的 `European options on equities and currencies` 补为
`options on currencies`，并在交付说明中写明「末尾被讲师遮挡，已按图2 补全」。

---

## 五、交付前自检（缺一不可）

```python
z = zipfile.ZipFile(out)
assert z.testzip() is None
d = json.loads(z.read('content.json'))       # 顶层必须是 list
assert isinstance(d, list)

# 1) 节点总数与截图一致  2) 全部 UUID v4 且唯一  3) 无 CJK 残留
#    re.search(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', title)
# 4) marker 清单与截图逐一对照  5) rootTopic 有 class / structureClass
```

打印出「层级缩进树 + 标记清单」跟截图并排核对一遍再交付。

---

## 六、常见坑

| 症状 | 根因 | 解法 |
|---|---|---|
| XMind 打开报错 | `content.json` 写成了对象 | 改成数组（sheet list） |
| 打开报错 | 缺 metadata.json / manifest.json | 两个都补齐 |
| 标记变成 's' 't' 'a' 'r' | marker 传字符串被逐字符迭代 | `isinstance(m, str)` 包成 list |
| 星/旗标错 | 只看颜色，没看形状 | 解 app.asar 的 SVG 看轮廓 |
| 公式下标错 | 凭视觉猜下标 | 放大裁切逐字确认（ₜ 不是 ₄） |
| 误判加粗 | 放大图目视"看着更粗" | 用同一个词的游程分布直方图判定，别看均值也别靠眼睛 |
| 把长破折号当连字符 | 没做基准校准 | 拿已知连字符的 ink 宽度做基准，长破折号约为其 6 倍 |
| 混入中文 | 习惯性翻译 | 明确「保持原版英文」，交付前查 CJK（源图本身就是中文的节点要保留） |
| 把叶节点当父节点 | 只看缩进/目视 | 按 §8 解码连接线：横线断掉=叶子，spine 有父级接入线才有子级 |
| 把折叠按钮 `⊕` 当成标记 | 没放大看 | 放大 8× 确认是圆圈+`+`；marker 在文字左侧，`⊕` 在右侧 |
| 硬把图1 的标记套到图2 上 | 没做骨架比对 | 两图常是**不同的树**；按 §9 先比对，不一致就停下来问用户 |
| 同级子项被当成父子 | 只看目视缩进 | 看 connector 起点 x 是否相同 + 是否共用一条 spine（§8.3） |
| 小字用 LANCZOS 放大后逐字判读 | 插值糊出假笔画 | 用 NEAREST + 像素 ASCII，按列墨迹局部极小值切字 |
| 节点文字被讲师挡住仍硬猜 | 没检测前景遮挡 | 先剔人像色块；可见多少写多少，补全部分在回复里说明 |
| 文件莫名消失 | 用户目录被清理/误删 | 提醒用户另存到独立目录或云盘 |

## 七、批量多树

用户常说「N 个树分开、各自独立文件」。做法：每个树一个 sheet 单独打包成一个 `.xmind`，
文件命名用英文 + 下划线（`06_Market-Based_Valuation.xmind`），按 CFA 科目分目录：
`经济/ 财报/ 公金/ 另类/ 数量/ 组合/ 固收/ 权益/ 衍生品/`（目录已存在就直接放，不存在则新建）。

构建脚本是**一次性**的，用完即删（`_tmp_xxx/` 临时目录一并清掉），不要留在工作区。

---

## 八、从连接线解码父子关系（花括号/大括号版式）

何旋系 CFA 框架图用的是**花括号（brace）连接线**版式，不是 XMind 默认的直线。
「谁是谁的孩子」不能靠目视缩进猜，必须**像素级解码线段**。

### 8.1 先分离「线」和「文字」

```python
dark  = a < 175
hline = ndimage.binary_opening(dark, np.ones((1,11), bool))   # 水平长 run → 横线
vline = ndimage.binary_opening(dark, np.ones((11,1), bool))   # 垂直长 run → 竖线
lines = ndimage.binary_dilation(hline|vline, np.ones((3,3), bool))
text  = dark & ~lines                                        # 剩下的才是文字
```

再用 `binary_dilation(text, np.ones((1,9)))` + `ndimage.label` 把文字**合并成行**，
输出每行的 `(y0,y1,x0,x1)` —— 这份坐标表就是还原层级的底稿。
**暗底浅字的节点**（如 L1 标题）会被当成实心块滤掉，需要单独裁切后 `255 - v` 反相再读。

### 8.2 版式的三条规则（实测确认）

1. **一个主题的「连接线」画在该主题文字的下面**，y ≈ 文字中心 + 9~10px，
   并且从**父级 spine 的 x** 开始向右延伸（不是从自己的文字左边缘开始）。
2. **子级 spine 是一条竖线**，跨度从第一个子级到最后一个子级；
   **父级从 spine 的竖直中点接入**（`parent_y ≈ (spine_y0+spine_y1)/2`）。
3. 因此当子级是**奇数个**时，**中间那个子级的 y 会与父级接入点重合**，两条线共线连成一条长线
   —— 这是正常现象，别误判成「多了一个子级」。

### 8.3 判定谁挂在谁下面：找 spine 的「父级接入线」

对每个 spine（竖线段）：
- 在它的 `y0..y1` 范围内，找**从 spine 左侧接进来的横线段** → 那条横线的起点所在主题 = 父级
- 在它的 `y0..y1` 范围内，找**从 spine 右侧出去的横线段** → 那些是子级
- 若某条横线**贯穿 spine**（左右都有），说明它既是父级接入线、又是中间子级的连接线（规则 3）

**踩过的坑**：只看「视觉缩进」会得出错误结论。实测有一例：
`Pricing` 的横线在 x577→623 **直接断掉**（无竖线接下去）→ 它是**叶节点**；
而 `Interest rate swap / Currency swap / Equity swap` 三个共用一条 spine（x≈631），
该 spine 的父级接入线在 y255 从 x577 进来 → 父级是 **`Value`**，不是 `Pricing`。
（语义上看着别扭，但像素就是这么画的——**以像素为准**。）

### 8.4 待确认时的高效做法

怀疑某处结构时，直接打印局部 **ASCII 线段图**最快：

```python
print('    ' + ''.join(str((X0+i*SX)//100%10) for i in range((X1-X0)//SX)))
for oy in range(Y0, Y1, SY):
    row = ''.join('#' if lines[oy:oy+SY, ox:ox+SX].any()
                  else ('.' if dark[oy:oy+SY, ox:ox+SX].any() else ' ')
                  for ox in range(X0, X1, SX))
    print(f'{oy:4d}' + row)
```

`#` = 线、`.` = 文字、空格 = 空。一张图就能看清所有肘形拐角。

### 8.5 **`⊕` 小圆圈不是标记，不要还原**

地图里某些主题右端会有一个淡蓝色小圆圈（内含 `+`），放大后是 **XMind 的「折叠分支」按钮**
（表示该主题下面还有被折叠的子节点）。**它不是 marker**，不要写成任何 markerId。
判据：放大 8× 后能看见圆内的 `+`；且它出现在主题文字**右侧**，而 marker 永远在文字**左侧**。

---

## 九、双图合并工作流（「图1 标记 + 图2 内容」）

用户常一次给两张图：**图1 提供标记位置，图2 提供完整内容**。
**动手前必须先做骨架比对** —— 很多情况下两图并不是同一棵树。

### 9.1 第一步：骨架比对（强制）

分别提取两图的「全部文本行 (y0,y1,x0,x1)」与标记坐标，然后：

1. 列出图1 的全部节点名、层级、标记；
2. 列出图2 的全部节点名、层级、标记（常常**一个标记都没有**——这时图2 就纯是内容源）；
3. 逐条比对。若出现「图1 有而图2 没有」或「图2 有而图1 没有」的节点，
   说明**不是同一棵树**，此时不要硬套标记。

> 实测案例：图1 是讲师总结页（`Components of Binomial Option Valuation Model`、`More Understanding of
> Risk Neutral Probability`、`Other Greeks`…），图2 是详细提纲（`Binomial model`、`Arbitrage opportunity
> discovery`、计算四步骤、`Using BSM model`…），两者只在部分概念上重叠。

### 9.2 第二步：骨架不一致 → 停下来问用户

不要自己选。用 `AskUserQuestion` 给 3 个选项（并把「两图有何不同」写成一张对照表放在提问前面）：

| 选项 | 含义 |
|---|---|
| **合并成一棵（推荐）** | 以图1 为骨架＋保留其全部标记，把图2 的详细节点挂到对应位置。标记零遗漏＋内容全保留 |
| 只做图2＋语义映射 | 完全按图2 出，标记按语义挂上去；图1 中无对应者的标记会丢失 |
| 两棵分开做 | 各出一个 xmind 文件 |

### 9.3 第三步：合并策略（用户选「合并」时）

- **骨架、节点名、标记全部取自图1**（图1 是权威框架，这样标记才能逐一落位）。
- 图2 独有的节点按**图2 原文**新增，挂在语义对应的图1 父节点下。
- 图2 与图1 是同一概念的节点：把图2 的**子节点**挂到图1 节点下，不再重复建同名节点。
- 图2 里「拆分型」的结构（如 `Two-period binomial model for European/American option`）
  遇到图1 已有中间层（`Two-Period Binomial Model` → `European Option`/`American Option`）时，
  **保留图1 的层级**（标记就挂在那一层），把图2 的子节点挂到最里层。

### 9.4 第四步：标记总数回查（交付前最后一道闸）

```python
# 图1 实测标记数：red=N1, yellow=N2  →  交付文件里 star-red/flag-red 合计必须 == N1
#                                                    star-yellow 合计必须 == N2
```

本次实例：图1 实测 16 红（含 2 个红旗）＋ 14 黄 = 30；交付文件 30 个，逐一吻合。
**标记数对不上就是漏了或多了**，必须回到像素坐标逐个复核。

