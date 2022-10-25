# PyBoke

Static Blog Generator (极简博客生成器)

- 使用过程极简
- 功能极简，代码极简

因为功能少、代码简单，任何懂编程的人（只要懂 Python 基础）
就能在短时间内完全看明白本软件的全部代码并且随心所欲地修改。

## 添加/修改/删除文章都非常方便

1. **添加文章**：直接在 articles 文件夹里新建 '.md' 后缀名的文件，采用 markdown 格式编写内容。
2. **修改文章**：直接修改 articles 文件夹里的文件。
3. **删除文章**：直接删除 articles 文件夹里的文件。
4. 执行命令 `boke render -all`

- 添加文章时，不需要在任何地方填写文章标题、文章分类、标签、日期……
  这些全部都不用管，只管写文章。
- 不需要每次都执行 `boke render`, 可以在添加/修改了一篇或多篇文章后，
  包括删除一些文章后，再统一执行 `boke render -all` 即可。

## 安装与初始化

要求 Python 3.10 或以上，如果你的系统中未安装 Python 3.10,
推荐使用 [pyenv](https://github.com/pyenv/pyenv) 或
[miniconda](https://docs.conda.io/en/latest/miniconda.html)
来安装最新版本的 Python。

例如，安装 miniconda 后，可以这样创建 3.10 环境：

```sh
$ conda create --name py310 python=3.10
$ conda activate py310
```

安装非常简单，只要 `pip install pyboke` 即可。  
另外推荐采用 [pipx](https://pypa.github.io/pipx/) 进行安装。

## 创建一个新博客

1. `mkdir my-blog` _(新建一个空文件夹)_
2. `cd my-blog` _(进入空文件夹内)_
3. `boke init` _(初始化博客，创建一些必要的文件和文件夹)_

然后可以在当前文件内看到以下文件与文件夹：

- **articles** (全部文章都在这里，采用 markdown 格式, `.md` 后缀名)
- **articles/metadata** (与 markdown 文件一一对应的 toml 文件)
- **drafts** (待发布的草稿放在这里)
- **output** (程序生成的 HTML, RSS 等文件将会输出到该文件夹)
- **templates** (Jinja2模板 与 CSS文件)
- **boke.toml** (博客名称、作者名称等)

请用文本编辑器打开 boke.toml 填写博客名称、作者名称等。

执行命令 `boke -info` 查看博客信息。

## 添加文章

- 文件后缀必须是 ".md", 文件内容必须采用 Markdown 格式, 使用 utf-8 编码。
- 文件名只能使用 0-9, a-z, A-Z, _(下划线), -(短横线), .(点)。
- 把 md 文件放入 articles 文件夹，执行 `boke render articles/filename`,
  会在 **articles/metadata** 文件夹里生成 TOML 文件，
  在 **output** 文件夹生成 HTML 文件。
- 其中, TOML 里有文章的标题、作者、创建日期、修改日期等信息。
- 大多数情况下你都可以忘记 articles/metadata 里的 toml 文件，不需要修改它。
- 推荐使用 `boke new` 和 `boke post` 命令，详见后文 **草稿** 部分。

## 修改文章内容

- 直接修改 articles 里的 md 文件。
- 然后执行 `boke render articles/filename`, 即可自动更新指定文件的 toml 和 html
- 该命令与前面所述 "添加文章" 的命令是一样的，作用都是渲染 toml 和 html
- 使用命令 `boke render -h` 可查看帮助信息。

## 批量处理

执行 `boke render -all` 可检查全部文章是否被修改过、有无新文章、是否删除了文章，
并进行自动处理。

## 强制渲染

使用前述的 `boke render` 命令时，如果文章内容无变化，会自动忽略。  
也就是说，如果只修改 toml 的内容，不修改 markdown 文件的内容，就不会触发渲染处理。

因此，如果想在不修改文章内容的情况下，修改文章的作者或日期，就需要强制渲染。

- `boke render -force articles/filename` 强制渲染指定的一篇文章，并且渲染首页、索引等。
- `boke render -index` 只强制渲染首页、索引等，不渲染文章
- `boke render -force -all` 强制渲染全部文章及首页、索引等。

大多数情况下不需要强制渲染，但有一种情况：修改了 blog.toml 里的博客名称、作者名称
等信息后，需要执行 `boke render -force -all` 强制渲全部文章。

### 更改文章修改日期

如果修改了文章的内容，在执行上述 `boke render` 相关命令时会自动更新文章的修改日期。

如果想手动设定一篇文章的修改日期或创建日期，可修改该文章的 toml 文件中的 mtime 和 ctime,
然后执行命令 `boke render articles/XXX.md -force`

(toml 文件在 articles/metadata 文件夹里)

## 删除文章

有两种方法：

1. 使用命令 `boke delete articles/filename`
2. 直接删除 articles 文件夹里的文件，然后执行 `boke render -all`

## RSS

- 在正式对外发布你的博客时，请在 blog.toml 中填写你的博客网址 (website),
- 第一次生成 atom.xml 需要执行 `boke render -rss`,
- 后续在执行其它命令时会自动重新渲染 atom.xml

本软件只提供有限的 RSS 功能：

1. 只包含最新发布的 10 篇文章（并且该数字写死在代码里，用户不能自由设定）
2. 只包含内容摘要，不包含全文

### 排序

- RSS 按照文章的修改日期排序
- 博客首页的 "最新发布" 按照文章的创建日期排序

## 草稿

如上文所示，添加文章只需要把 markdown 文件放进 articles 文件夹即可，操作非常简单明瞭。

但考虑到有时文章未写完，暂时不发布，需要一个存放草稿的地方，因此提供了一个
drafts 文件夹，草稿可以放在这里。

### `boke new drafts/abc.md`

该命令用来新建一个 markdown 文件，并确保其采用 UTF-8 编码。  
(该命令只是提供方便，也可不使用该命令，用其它方法创建文件。)

### `boke post drafts/abc.md`

该命令的作用是把 drafts 文件夹里的指定文件移动到 articles 文件夹里，并执行渲染
(生成 toml 和 html 文件)。

这个命令也只是提供方便，你完全可以不使用该命令，而是自己移动文件，然后自己执行
`boke render` 命令。

### 提醒：小心覆盖文件

在终端用 `cp` 命令复制文件到 articles 文件夹，或使用 `mv` 命令更改文件名时，
如有同名文件，会直接覆盖。

因此建议使用 `boke post` 命令和 `boke rename` 命令，可防止覆盖。

例: `boke post drafts/abc.md`

### 更改文件名

更改 articles 文件夹内的文件名时，必须同时更改对应的 toml 及 html 的文件名。

建议使用 `boke rename` 命令，可自动更改对应的 toml 及 html 的文件名。

- 例: `boke rename articles/old-name.md articles/new-name.md`
- 或: `boke rename articles/old-name.md new-name.md`
- 这两个命令的效果是一样的(第二个文件名的文件夹会被忽略)。

## Preview (预览)

- 预览是指将一个 Markdown 文件转换为 HTML, 输出文件名固定为 output/temp.html
- 预览并非发布文章或修改文章，不会对博客产生任何修改。

例: `boke render -preview darfts/abc.md`  
或: `boke render -preview articles/abc.md`

## Themes (主题)

- 本软件自带四种主题(样式): mvp, new, simple, water
- 使用命令 `boke render -theme name` 可更改主题

### 添加更多主题

自带的主题是我从网上找来的：

- mvp: <https://andybrewer.github.io/mvp/>
- new: <https://newcss.net>
- simple: <https://simplecss.org/>
- water: <https://watercss.kognise.dev/>

网上还有一些类似的极简 CSS 主题[^css-themes], 你可以自己找来放在 templates/themes 文件夹里，
然后用 `boke render -theme name` 指定主题即可。

使用命令 `boke -info` 可查看当前正在使用的主题及可供选择的主题。

## 自定义模板

本软件采用 [Jinja2](https://jinja.palletsprojects.com/en/latest/templates/) 语法
生成 HTML, 模板文件在 templates 文件夹里, Jinja 语法易学易用，自带模板的内容也很简单，
你可自行修改模板。

### 忽略文章

（这是高级功能，多数情况下不需要学习和使用。）

在自定义模板时，可能需要增加一些特殊的页面，比如 "关于我", "关于本站" 等等，
这些页面可以当作一篇普通的文章来发布，然后在 template/index.html 里添加固定的链接。

如果不希望这些特殊文章出现在 "最新发布", "标题索引" 等列表中，可以将其对应的
toml 文件中的 `ignored` 修改为 `true`.

注意，这个忽略功能并非隐藏文章， 被忽略的文章不会出现在最新发布、索引列表里，
但仍会出现在 RSS 里。

## LICENSE (许可证)

使用本软件生成的博客，默认声明了 CC0-1.0 许可证，意味着允许他人免费转载你的文章（包括商用）。
如果不想采用 CC0 许可证，可以在 `boke init` 之后进入 output 文件夹删除 LICENSE.txt 文件，
并进入 templates 文件夹用文本编辑器或代码编辑器打开 index.html 和 article.html, 删除
`| LICENSE <a href="LICENSE.txt">CC0-1.0</a>`

另外，如果采用其他许可证，可以替换 output 及 templates 文件夹内的 LICENSE.txt 文件的内容，
并修改 index.html 和 article.html 里的许可证名称。

## 替换图片地址

- 在 markdown 中可使用 `![photo-1](../output/pics/XXX.jpg)` 的形式插入图片。
- 本地图片建议放在 output/pics 文件夹内。
- 图片文件名建议使用半角英文数字，尽量不使用中文和特殊字符
- 在每篇文章对应的 toml 文件的 pairs 项目里，可指定图片的替换地址，例如：
  ```toml
  pairs =  [
    [ '''../output/pics/abc.jpg''', '''https://example.com/abc.jpg''' ],
  ]
  ```
- markdown 文件的内容保持不变, HTML 文件中如有第一个字符串，会被替代为第二个字符串。
- 不只是图片地址，该功能可以替换任何字符，但主要用途是替换图片地址。
- HTML 显示图片的宽度上限可以统一设定，详见 blog.toml 及文章对应的 toml。

## 全文搜索

本软件不提供全文搜索功能，但由于本质上全部文章都是 markdown 纯文本，因此可使用
各种工具进行搜索。

例如可以使用 [ripgrep](https://github.com/BurntSushi/ripgrep), 在博客的根目录执行
`rg -i 'keyword' articles` 即可查找包含 `keyword` 的文章，其中 `-i` 表示不分大小写。

如果不搜索文章正文内容，只搜索文章标题，可打开网页 title-index.html(标题索引),
按 `Ctrl+F` 在页面内搜索。


[^css-themes]: 例如这里就有一些极简 CSS 主题: [github.com/dohliam/dropin-minimal-css](https://github.com/dohliam/dropin-minimal-css)

## 我的博客

作为参考，可以看看我的博客，就是用 PyBoke 生成的。
<https://ahui2016.github.io/>
