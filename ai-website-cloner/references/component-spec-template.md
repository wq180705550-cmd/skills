# 组件规范文件模板

## 模板文件

`docs/research/components/<component-name>.spec.md`

```markdown
# <ComponentName> Specification

## Overview
- **Target file:** `src/components/<ComponentName>.tsx`
- **Screenshot:** `docs/design-references/<screenshot-name>.png`
- **Interaction model:** < static | click-driven | scroll-driven | time-driven >

## DOM Structure
<Describe the element hierarchy — what contains what>

## Computed Styles (exact values from getComputedStyle)

### Container
- display: ...
- padding: ...
- maxWidth: ...
- (every relevant property with exact values)

### <Child element 1>
- fontSize: ...
- color: ...
- (every relevant property)

### <Child element N>
- ...

## States & Behaviors

### <Behavior name, e.g., "Scroll-triggered floating mode">
- **Trigger:** <exact mechanism — scroll position 50px, IntersectionObserver rootMargin "-30% 0px", click on .tab-button, hover>
- **State A (before):** maxWidth: 100vw, boxShadow: none, borderRadius: 0
- **State B (after):** maxWidth: 1200px, boxShadow: 0 4px 20px rgba(0,0,0,0.1), borderRadius: 16px
- **Transition:** transition: all 0.3s ease
- **Implementation approach:** <CSS transition + scroll listener | IntersectionObserver | CSS animation-timeline | etc.>

### Hover states
- **<Element>:** <property>: <before> -> <after>, transition: <value>

## Per-State Content (if applicable)

### State: "Featured"
- Title: "..."
- Subtitle: "..."
- Cards: [{ title, description, image, link }, ...]

### State: "Productivity"
- Title: "..."
- Cards: [...]

## Assets
- Background image: `public/images/<file>.webp`
- Overlay image: `public/images/<file>.png`
- Icons used: <ArrowIcon>, <SearchIcon> from icons.tsx

## Text Content (verbatim)
<All text content, copy-pasted from the live site>

## Responsive Behavior
- **Desktop (1440px):** <layout description>
- **Tablet (768px):** <what changes — e.g., "maintains 2-column, gap reduces to 16px">
- **Mobile (390px):** <what changes — e.g., "stacks to single column, images full-width">
- **Breakpoint:** layout switches at ~<N>px
```

## 使用规范

1. **每个组件一个文件** — 即使两个组件看起来相似，也要分别编写规范
2. **所有 CSS 值来自 getComputedStyle** — 禁止估算
3. **内容逐字复制** — 文本、alt 属性、aria 标签从实时网站精确复制
4. **状态不可遗漏** — 默认状态 + 所有替代状态
5. **不做假设** — 不确定时，回到浏览器 MCP 重新提取
6. **N/A 用于不适用的部分** — 但仍然要明确写 N/A 而非留空

## 文件命名规则

- 使用 PascalCase 组件名：`HeroSection.spec.md`、`FeaturesGrid.spec.md`
- 用小写连字符的目录路径：`docs/research/components/hero-section.spec.md`
- 文件名应与目标组件名对应：`src/components/HeroSection.tsx` → `docs/research/components/HeroSection.spec.md`
