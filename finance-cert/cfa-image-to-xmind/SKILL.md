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
lab, n = ndimage.label(red)          # 真标记 = 15×15 左右、130~150 px 的实心块
```

**必须排除 ClearType 次像素抗锯齿伪影**：它们是 1px 宽的竖条、低饱和（RGB 三通道都 >110 且彼此接近）。
判据：宽度 ≤ 2px 且像素数 < 20 的，一律不当标记。真标记宽高都是 13~17px。

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

---

## 三、源材料处理

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

---

## 四、交付前自检（缺一不可）

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

## 五、常见坑

| 症状 | 根因 | 解法 |
|---|---|---|
| XMind 打开报错 | `content.json` 写成了对象 | 改成数组（sheet list） |
| 打开报错 | 缺 metadata.json / manifest.json | 两个都补齐 |
| 标记变成 's' 't' 'a' 'r' | marker 传字符串被逐字符迭代 | `isinstance(m, str)` 包成 list |
| 星/旗标错 | 只看颜色，没看形状 | 解 app.asar 的 SVG 看轮廓 |
| 公式下标错 | 凭视觉猜下标 | 放大裁切逐字确认（ₜ 不是 ₄） |
| 混入中文 | 习惯性翻译 | 明确「保持原版英文」，交付前查 CJK |
| 文件莫名消失 | 用户目录被清理/误删 | 提醒用户另存到独立目录或云盘 |

## 六、批量多树

用户常说「N 个树分开、各自独立文件」。做法：每个树一个 sheet 单独打包成一个 `.xmind`，
文件命名用英文 + 下划线（`06_Market-Based_Valuation.xmind`），按 CFA 科目分目录：
`经济/ 财报/ 公金/ 另类/ 数量/ 组合/ 固收/ 权益/`。

构建脚本是**一次性**的，用完即删（`_tmp_xxx/` 临时目录一并清掉），不要留在工作区。
