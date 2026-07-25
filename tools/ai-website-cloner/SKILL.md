---
name: ai-website-cloner
description: "Reverse-engineer and clone one or more websites — extract assets, CSS, and content section-by-section, then dispatch parallel builder agents to rebuild each part as pixel-perfect Next.js components. Use this skill whenever the user wants to clone, replicate, rebuild, reverse-engineer, or copy any website. Triggers: clone website, reverse-engineer site, rebuild page, pixel-perfect clone, make a copy of this site, replicate website."
agent_created: true
version: 1.0.0
language: zh
type: workflow
priority: high
triggers:
  - "克隆网站 / 反向工程网站"
  - "复制页面 / 重建站点"
  - "pixel-perfect clone / reverse-engineer site"
  - "提取网站设计 / 网站逆向"
keywords: [website-cloner, reverse-engineering, pixel-perfect, nextjs, shadcn, tailwind, website-clone, component-extraction, parallel-build, worktree]
---

# AI Website Cloner — 网站克隆技能

## 概述

将任意网站逆向工程为干净、现代的 Next.js 代码库。核心理念：指向一个 URL，AI 代理会检查网站、提取设计令牌和资源、编写组件规范，并调度并行构建器重建每个部分。

**前置条件：**
- Node.js 24+ 项目（Next.js 16 + shadcn/ui + Tailwind CSS v4 脚手架已就位）
- Browser MCP 工具可用（Chrome MCP / Playwright MCP / Puppeteer MCP 等）
- `npm run build` 基线通过

**技术栈：**
- Next.js 16 — App Router, React 19, TypeScript 严格模式
- shadcn/ui — Radix 原语 + Tailwind CSS v4
- Tailwind CSS v4 — oklch 设计令牌
- Lucide React — 默认图标

**默认范围：**
- **保真度：** Pixel-perfect — 颜色、间距、排版、动画精确匹配
- **范围内：** 视觉布局和样式、组件结构和交互、响应式设计、演示用模拟数据
- **范围外：** 真实后端/数据库、认证、实时功能、SEO 优化、可访问性审计
- **自定义：** 无 — 纯模拟

## 指导原则

这些原则是成功克隆与"差不多就行"之间的分界线。

### 1. 完整性优先于速度

每个构建器代理必须收到完成工作所需的**一切**：截图、精确 CSS 值、下载资源（本地路径）、真实文本内容、组件结构。如果构建器需要猜测任何值——颜色、字号、内边距——说明提取失败。多花一分钟提取一个属性，比发出一份不完整的简报要好。

### 2. 小任务，完美结果

当代理接到"构建整个 features 部分"时，它会忽略细节——近似间距、猜测字号、产出"差不多"但明显不对的东西。当它得到一个单一聚焦的组件加上精确 CSS 值时，每次都能完美完成。

查看每个部分并判断其复杂性。简单的 banner 只有标题和按钮？一个代理。复杂的部分有 3 种不同的卡片变体，每种有独特的悬停状态和内部布局？每个卡片变体一个代理，再加上一个用于部分包装器的代理。

**复杂性预算规则：** 如果构建器提示超过约 150 行的规范内容，则该部分对一个代理来说太复杂了。拆分为更小的部分。这是机械检查——不要用"但它们都是相关的"来覆盖。

### 3. 真实内容，真实资源

从实时网站提取实际文本、图片、视频和 SVG。这是克隆，不是模型。使用 `element.textContent`，下载每个 `<img>` 和 `<video>`，提取内联 `<svg>` 元素为 React 组件。唯一生成内容的情况是某些东西明显是服务端生成的且每次会话唯一。

**分层资源很重要。** 看起来像一张图片的部分通常是多层——背景水彩/渐变、前景 UI 模型 PNG、覆盖图标。检查每个容器的完整 DOM 树并枚举其中的所有 `<img>` 元素和背景图片，包括绝对定位的覆盖层。

### 4. 先打地基

在基础存在之前什么都构建不了：包含目标网站设计令牌（颜色、字体、间距）的全局 CSS、内容结构的 TypeScript 类型、全局资源（字体、favicon）。这是顺序的、不可商量的。此后的一切都可以并行。

### 5. 提取外观和交互

网站不是截图——它是活的东西。元素在滚动、悬停、点击、调整大小和时间作用下移动、变化、出现和消失。如果只提取每个元素的静态 CSS，克隆看起来在截图中是正确的，但实际使用时感觉是死的。

对于每个元素，提取其**外观**（通过 `getComputedStyle()` 的精确计算 CSS）**和**其**行为**（什么变化、什么触发变化、以及过渡如何发生）。不是"看起来像 16px"——提取实际计算值。不是"导航在滚动时变化"——记录确切的触发条件、前后状态和过渡。

### 6. 在构建前确定交互模型

这是克隆中最昂贵的错误：在内置点击式 UI 时原文是滚动驱动的，反之亦然。在编写任何交互式部分的构建器提示之前，必须明确回答：**这个部分是点击驱动的、滚动驱动的、悬停驱动的、时间驱动的，还是组合？**

**如何确定：**
1. **先不点。** 缓慢滚动该部分并观察是否有东西随滚动自行变化
2. 如果有，是滚动驱动的。提取机制：`IntersectionObserver`、`scroll-snap`、`position: sticky`、`animation-timeline` 或 JS 滚动监听器
3. 如果滚动时没有变化，然后再点击/悬停测试点击/悬停驱动的交互性
4. 在组件规范中明确记录交互模型

### 7. 提取每个状态，不只是默认状态

许多组件有多个可视化状态——标签栏每个标签显示不同的卡片、页眉在滚动位置 0 和 100 时看起来不同、卡片有悬停效果。必须提取**所有**状态，不仅仅是页面加载时可见的。

### 8. 规范文件是唯一事实源

每个组件在构建器被分派**之前**在 `docs/research/components/` 中获取一个规范文件。这个文件是提取工作和构建器代理之间的契约。构建器在其提示中内联接收规范文件内容——该文件也作为可审计的制品持久化。

规范文件不是可选的。如果未先编写规范文件就分派构建器，那就是根据浏览器 MCP 会话中能记住的内容发送不完整的指令，构建器将猜测填补空白。

### 9. 构建必须始终可编译

每个构建器代理在完成前必须验证 `npx tsc --noEmit` 通过。合并 worktrees 后，必须验证 `npm run build` 通过。损坏的构建永远不可接受——即使是暂时的。

## Pre-Flight 检查

1. **确认 Browser MCP 可用。** 检查可用的浏览器工具（Chrome MCP、Playwright MCP、Browserbase MCP、Puppeteer MCP 等）。优先使用 Chrome MCP。如无可用，询问用户。此技能没有浏览器自动化无法工作。
2. **解析目标 URL。** 从用户输入中提取一个或多个 URL。标准化并验证每个 URL；如无效，要求用户更正。对每个有效 URL，通过浏览器 MCP 确认可访问。
3. **验证项目基线可构建。** 运行 `npm run build`。Next.js + shadcn/ui + Tailwind v4 脚手架应已就位。
4. **创建输出目录。** 确保 `docs/research/`、`docs/research/components/`、`docs/design-references/`、`scripts/` 存在。多站点时，准备每个站点的独立文件夹 `docs/research/<hostname>/` 和 `docs/design-references/<hostname>/`。
5. **多站点处理。** 询问用户是否并行处理（推荐，如资源允许）或顺序处理。

## Phase 1：侦察（Reconnaissance）

导航到目标 URL 并进行全面侦察。

### 截图
- 分别在桌面端（1440px）和移动端（390px）视口拍摄**全页截图**
- 保存到 `docs/design-references/`，使用描述性名称

### 全局提取

**字体：** 检查 `<link>` 标签中的 Google Fonts 或自托管字体。检查关键元素（标题、正文、代码、标签）的计算 `font-family`。记录每个实际使用的字体族、字重和样式。在 `src/app/layout.tsx` 中使用 `next/font/google` 或 `next/font/local` 配置。

**颜色：** 从页面各处的计算样式中提取网站调色板。在 `:root` 和 `.dark` CSS 变量块中更新 `src/app/globals.css`。映射到 shadcn 令牌名称（background、foreground、primary、muted 等）。对不映射到 shadcn 令牌的颜色添加自定义属性。

**Favicon 和 Meta：** 下载 favicon、apple-touch-icon、OG 图片、webmanifest 到 `public/seo/`。更新 `layout.tsx` 元数据。

**全局 UI 模式：** 识别全站 CSS 或 JS：自定义滚动条隐藏、页面容器上的 scroll-snap、全局关键帧动画、backdrop filter、用作覆盖层的渐变、**平滑滚动库**（Lenis、Locomotive Scroll——检查 `.lenis`、`.locomotive-scroll` 或自定义滚动容器类）。添加到 `globals.css` 并记录需要安装的库。

### 强制性交互扫描

这是截图后但其他操作前的专用遍历。

**滚动扫描：** 通过浏览器 MCP 从页面顶部缓慢滚动到底部。在每个部分暂停观察：
- 页眉是否变化？记录触发时的滚动位置
- 元素是否进入视口时动画？记录哪些和动画类型
- 侧边栏或标签指示器是否随滚动自动切换？记录机制
- 是否有 scroll-snap 点？记录哪些容器
- 是否有平滑滚动库？检查非原生滚动行为

**点击扫描：** 点击每个看起来可交互的元素：
- 每个按钮、标签、卡片、链接
- 记录发生了什么：内容变化？模态框打开？下拉菜单出现？
- 对标签/药丸：点击**每个**并记录每个状态下出现的内容

**悬停扫描：** 将鼠标悬停在可能有悬停状态的每个元素上：
- 按钮、卡片、链接、图片、导航项
- 记录什么变化：颜色、缩放、阴影、下划线、透明度

**响应式扫描：** 在 3 种视口宽度下测试：
- 桌面：1440px、平板：768px、移动：390px
- 在每个宽度下，注意哪些部分的布局变化以及大约在什么断点

将所有发现保存到 `docs/research/BEHAVIORS.md`。

### 页面拓扑

从上到下映射页面的每个不同部分。给每个取一个工作名称。记录：
- 视觉顺序
- 哪些是固定/粘性覆盖层 vs. 流式内容
- 整体页面布局（滚动容器、列结构、z-index 层级）
- 各部分之间的依赖关系
- 每个部分的交互模型

保存为 `docs/research/PAGE_TOPOLOGY.md`。

## Phase 2：基础构建（Foundation Build）

此阶段是顺序的。自行执行（非委托）因为这涉及多个文件：

1. **更新 `layout.tsx` 中的字体**以匹配目标网站实际字体
2. **更新 `globals.css`**：目标颜色令牌、间距值、关键帧动画、工具类、全局滚动行为
3. **在 `src/types/` 中创建 TypeScript 接口**用于观察到的内容结构
4. **提取 SVG 图标：** 找到页面上所有内联 `<svg>` 元素，去重，保存为命名 React 组件在 `src/components/icons.tsx` 中
5. **下载全局资源：** 编写并运行 Node.js 脚本下载所有图片、视频和其他二进制资源到 `public/`
6. **验证：** `npm run build` 通过

### 资源发现脚本模式

通过浏览器 MCP 枚举页面上的所有资源：

```javascript
// 通过浏览器 MCP 运行此脚本来发现所有资源
JSON.stringify({
  images: [...document.querySelectorAll('img')].map(img => ({
    src: img.src || img.currentSrc,
    alt: img.alt,
    width: img.naturalWidth,
    height: img.naturalHeight,
    parentClasses: img.parentElement?.className,
    siblings: img.parentElement ? [...img.parentElement.querySelectorAll('img')].length : 0,
    position: getComputedStyle(img).position,
    zIndex: getComputedStyle(img).zIndex
  })),
  videos: [...document.querySelectorAll('video')].map(v => ({
    src: v.src || v.querySelector('source')?.src,
    poster: v.poster, autoplay: v.autoplay, loop: v.loop, muted: v.muted
  })),
  backgroundImages: [...document.querySelectorAll('*')].filter(el => {
    const bg = getComputedStyle(el).backgroundImage;
    return bg && bg !== 'none';
  }).map(el => ({ url: getComputedStyle(el).backgroundImage, element: el.tagName + '.' + el.className?.split(' ')[0] })),
  svgCount: document.querySelectorAll('svg').length,
  fonts: [...new Set([...document.querySelectorAll('*')].slice(0, 200).map(el => getComputedStyle(el).fontFamily))],
  favicons: [...document.querySelectorAll('link[rel*="icon"]')].map(l => ({ href: l.href, sizes: l.sizes?.toString() }))
});
```

然后编写下载脚本，分批并行下载所有内容（每次 4 个）。

## Phase 3：组件规范与分派

这是核心循环。对页面拓扑中的每个部分（从上到下）做**三件事**：**提取** → **编写规范文件** → **分派构建器**。

### Step 1：提取

对每个部分，使用浏览器 MCP 提取一切：

1. **截图**该部分（滚动到它，截图视口）。保存到 `docs/design-references/`

2. **提取 CSS：** 对部分中的每个元素运行提取脚本。不要手工测量个别属性：

```javascript
// 逐组件提取——通过浏览器 MCP 运行
// 将 SELECTOR 替换为组件实际 CSS 选择器
(function(selector) {
  const el = document.querySelector(selector);
  if (!el) return JSON.stringify({ error: 'Element not found: ' + selector });
  const props = [
    'fontSize','fontWeight','fontFamily','lineHeight','letterSpacing','color',
    'textTransform','textDecoration','backgroundColor','background',
    'padding','paddingTop','paddingRight','paddingBottom','paddingLeft',
    'margin','marginTop','marginRight','marginBottom','marginLeft',
    'width','height','maxWidth','minWidth','maxHeight','minHeight',
    'display','flexDirection','justifyContent','alignItems','gap',
    'gridTemplateColumns','gridTemplateRows',
    'borderRadius','border','borderTop','borderBottom','borderLeft','borderRight',
    'boxShadow','overflow','overflowX','overflowY',
    'position','top','right','bottom','left','zIndex',
    'opacity','transform','transition','cursor',
    'objectFit','objectPosition','mixBlendMode','filter','backdropFilter',
    'whiteSpace','textOverflow','WebkitLineClamp'
  ];
  function extractStyles(element) {
    const cs = getComputedStyle(element);
    const styles = {};
    props.forEach(p => { const v = cs[p]; if (v && v !== 'none' && v !== 'normal' && v !== 'auto' && v !== '0px' && v !== 'rgba(0, 0, 0, 0)') styles[p] = v; });
    return styles;
  }
  function walk(element, depth) {
    if (depth > 4) return null;
    const children = [...element.children];
    return {
      tag: element.tagName.toLowerCase(),
      classes: element.className?.toString().split(' ').slice(0, 5).join(' '),
      text: element.childNodes.length === 1 && element.childNodes[0].nodeType === 3 ? element.textContent.trim().slice(0, 200) : null,
      styles: extractStyles(element),
      images: element.tagName === 'IMG' ? { src: element.src, alt: element.alt, naturalWidth: element.naturalWidth, naturalHeight: element.naturalHeight } : null,
      childCount: children.length,
      children: children.slice(0, 20).map(c => walk(c, depth + 1)).filter(Boolean)
    };
  }
  return JSON.stringify(walk(el, 0), null, 2);
})('SELECTOR');
```

3. **提取多状态样式：** 对有多个状态的元素（滚动触发、悬停、活跃标签），捕获两个状态，记录差异。

4. **提取真实内容：** 所有文本、alt 属性、aria 标签、占位符文本。对标签/有状态内容，点击每个标签并提取每个状态的内容。

5. **识别资源：** 该部分使用的下载图片/视频、图标组件。检查分层图片。

6. **评估复杂性：** 有多少个不同的子组件？标准：~150 行规范内容后拆分。

### Step 2：编写组件规范文件

对每个部分（或子组件）在 `docs/research/components/` 中创建规范文件。路径：`docs/research/components/<component-name>.spec.md`

**模板：**

```markdown
# <ComponentName> Specification

## Overview
- **Target file:** `src/components/<ComponentName>.tsx`
- **Screenshot:** `docs/design-references/<screenshot-name>.png`
- **Interaction model:** <static | click-driven | scroll-driven | time-driven>

## DOM Structure
<描述元素层级——什么包含什么>

## Computed Styles (exact values from getComputedStyle)

### Container
- display: ...
- padding: ...
- maxWidth: ...
- (每个相关属性的精确值)

### <Child element 1>
- fontSize: ...
- color: ...
- (每个相关属性)

## States & Behaviors

### <Behavior name, e.g., "Scroll-triggered floating mode">
- **Trigger:** <精确机制>
- **State A (before):** ...
- **State B (after):** ...
- **Transition:** ...
- **Implementation approach:** ...

## Per-State Content (if applicable)
...

## Assets
- Background image: `public/images/<file>.webp`
- Icons used: <ArrowIcon>, <SearchIcon> from icons.tsx

## Text Content (verbatim)
<从实时网站复制的所有文本>

## Responsive Behavior
- **Desktop (1440px):** <布局描述>
- **Tablet (768px):** <变化>
- **Mobile (390px):** <变化>
- **Breakpoint:** layout switches at ~<N>px
```

填写每个部分。如不适用，写"N/A"。

### Step 3：分派构建器

基于复杂性，通过 `Agent` 工具分派构建器代理（并行执行）：

**简单部分**（1-2 个子组件）：一个构建器代理得到整个部分。

**复杂部分**（3+ 不同子组件）：拆分。每个子组件一个代理，再加一个用于部分包装器。

**每个构建器代理收到的内容：**
- 其组件规范文件的完整内容（内联在提示中）
- 截图路径
- 要导入的共享组件（`icons.tsx`、`cn()`、shadcn 原语）
- 目标文件路径
- 完成前 `npx tsc --noEmit` 验证指令
- 响应式行为信息

**不要等待。** 分派了一个部分的构建器后，立即继续提取下一个部分。构建器在并行 worktrees 中工作。

### Step 4：合并

构建器代理完成工作后：
- 将其 worktree 分支合并到 main
- 智能地解决冲突
- 每次合并后验证 `npm run build` 通过
- 如果合并引入类型错误，立即修复

提取 → 规范 → 分派 → 合并循环持续到所有部分构建完成。

## Phase 4：页面组装

所有部分构建并合并后，在 `src/app/page.tsx` 中串联一切：

- 导入所有部分组件
- 从拓扑文档实现页面级布局（滚动容器、列结构、粘性定位、z-index 层级）
- 连接真实内容到组件属性
- 实现页面级行为：scroll snap、滚动驱动动画、IntersectionObserver、平滑滚动
- 验证：`npm run build` 干净通过

## Phase 5：视觉 QA 差异对比

组装后，不要宣布克隆完成。进行并排对比截图：

1. 在相同视口宽度下打开原始网站和克隆版本
2. 在桌面端（1440px）从上到下逐部分对比
3. 在移动端（390px）再次对比
4. 对每个差异：
   - 检查组件规范文件——值提取正确吗？
   - 如果规范错误：从浏览器 MCP 重新提取、更新规范、修复组件
   - 如果规范正确但构建器错了：修复组件以匹配规范
5. 测试所有交互行为：滚动、点击每个按钮/标签、悬停交互元素
6. 验证平滑滚动感觉正确、页眉过渡正常、标签切换工作、动画播放

仅在此视觉 QA 通过后，克隆才算完成。

## 分派前检查清单

分派**任何**构建器代理前，验证每个框都可勾选。如果不行，回去提取更多。

- [ ] 规范文件已写入 `docs/research/components/<name>.spec.md`，所有部分已填写
- [ ] 规范中的每个 CSS 值来自 `getComputedStyle()`，非估算
- [ ] 交互模型已识别并记录（static / click / scroll / time）
- [ ] 对有状态组件：每个状态的内容和样式已捕获
- [ ] 对滚动驱动组件：触发阈值、前后样式和过渡已记录
- [ ] 对悬停状态：前后值和过渡时序已记录
- [ ] 部分中的所有图片已识别（包括覆盖层和分层组合）
- [ ] 响应式行为至少记录了桌面和移动端
- [ ] 文本内容来自站点，未改写
- [ ] 构建器提示在约 150 行规范内；如超，部分需拆分

## 禁止的操作

这些是之前克隆失败的教训——每个都花费了数小时返工：

- ❌ **不要在原文是滚动驱动时构建点击式标签（或反之）。** 先滚动再点击确定交互模型——这是 #1 最昂贵的错误
- ❌ **不要只提取默认状态。** 有选项卡时点击每个标签提取内容。页眉随滚动变化时捕获位置 0 和位置 100+ 的样式
- ❌ **不要遗漏叠加/分层图片。** 每个容器都要检查多个 `<img>` 和定位覆盖层
- ❌ **不要为实际上是视频/动画的内容构建模型组件。** 检查 `<video>`、Lottie、canvas
- ❌ **不要近似 CSS 类。** "看起来像 text-lg" 在计算值不同时是错误的。提取确切值
- ❌ **不要在一个巨量提交中构建所有东西。** 整个流水线的意义在于增量进展和每次验证构建
- ❌ **不要在构建器提示中引用文档。** 每个构建器在其提示中内联获得 CSS 规范——永远不要"参见 DESIGN_TOKENS.md"
- ❌ **不要跳过资源提取。** 没有真实图片、视频和字体，无论 CSS 多完美，克隆看起来总是假的
- ❌ **不要给构建器代理太大范围。** 如果构建器提示因部分变长而变长，那是需要拆分的信号
- ❌ **不要把不相关的部分打包到一个代理中。** CTA 和 footer 是不同的组件
- ❌ **不要跳过响应式提取。** 只在桌面检查，平板和移动端会坏
- ❌ **不要忘记平滑滚动库。** 检查 Lenis（`.lenis` 类）、Locomotive Scroll 或类似
- ❌ **不要在没有规范文件时分派构建器。** 规范文件强迫穷举式提取并创建可审计的制品

## 完成报告

完成后，报告：
- 构建的总部分数
- 创建的组件总数
- 编写的规范文件数（应与组件数匹配）
- 下载的资源总数（图片、视频、SVG、字体）
- 构建状态（`npm run build` 结果）
- 视觉 QA 结果（任何剩余差异）
- 已知差距或限制
