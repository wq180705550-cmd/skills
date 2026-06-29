# 浏览器提取脚本参考

## 1. 全资源发现脚本

通过浏览器 MCP 运行，枚举页面上的所有资源：

```javascript
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

## 2. 逐组件 CSS 提取脚本

对每个部分，替换 `SELECTOR` 为组件实际 CSS 选择器后运行：

```javascript
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
    props.forEach(p => {
      const v = cs[p];
      if (v && v !== 'none' && v !== 'normal' && v !== 'auto' && v !== '0px' && v !== 'rgba(0, 0, 0, 0)') styles[p] = v;
    });
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

## 3. 多状态样式提取脚本

对滚动触发、悬停、标签切换等多状态元素使用：

```javascript
// State A: 在当前状态捕获样式（如 scroll position 0）
// 然后触发状态变化（滚动、点击、悬停 via browser MCP）
// State B: 在相同元素上重新运行提取脚本
// A 和 B 之间的差异就是行为规范
```

记录差异：`"属性 X 从 VALUE_A 变为 VALUE_B，由 TRIGGER 触发，过渡: TRANSITION_CSS"`

## 4. 资源下载脚本模式

```javascript
// scripts/download-assets.mjs — 用于批量下载资源的脚本模板
import fs from 'fs';
import path from 'path';
import https from 'https';
import http from 'http';

const ASSETS = [
  // 从浏览器 MCP 提取的资源 URL 列表
  // { url: 'https://example.com/image.jpg', path: 'public/images/image.jpg' }
];

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const dir = path.dirname(dest);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const file = fs.createWriteStream(dest);
    const protocol = url.startsWith('https') ? https : http;
    protocol.get(url, response => {
      response.pipe(file);
      file.on('finish', () => { file.close(); resolve(); });
    }).on('error', reject);
  });
}

// 批量并行下载（每次 4 个）
async function batchDownload(assets, batchSize = 4) {
  for (let i = 0; i < assets.length; i += batchSize) {
    const batch = assets.slice(i, i + batchSize);
    await Promise.all(batch.map(a => download(a.url, a.path)));
  }
}

await batchDownload(ASSETS);
console.log('Done:', ASSETS.length, 'assets downloaded');
```

## 5. 响应式扫描辅助

通过浏览器 MCP 在 3 种视口宽度下测试：

```javascript
// 设置视口宽度并截图
// 桌面: 1440px -> await page.setViewport({ width: 1440, height: 900 })
// 平板: 768px -> await page.setViewport({ width: 768, height: 1024 })
// 移动: 390px -> await page.setViewport({ width: 390, height: 844 })
// 在每个宽度下截图并记录布局变化
```
