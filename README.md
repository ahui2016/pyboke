# PyBoke

Static Blog Generator (极简博客生成器)

- 使用过程极简
- 功能极简，代码极简

- 文章文件名、图片文件名由用户设定，只允许使用 0-9, a-z, A-Z, _(下划线), -(短横线), .(点)。
- 文章文件名、图片文件名相当于 ID

## 一大特点：添加/修改/删除文章都非常方便

1. 添加文章：直接在 articles 文件夹里新建 '.md' 后缀名的文件，采用 markdown 格式编写内容。
2. 修改文章：直接修改 articles 文件夹里的文件。
3. 删除文章：直接删除 articles 文件夹里的文件。
4. 执行命令 `boke render -all`

进一步说明究竟有多简单：

- 添加文章时，不需要在任何地方填写文章标题、标签、日期、作者姓名…… 这些全部都不用管，只管写文章。
- 可以在添加/修改了一篇或多篇文章后，包括删除一些文章后，再统一执行 `boke render -all` 即可。

## 创建一个新博客

1. `mkdir my-blog` (新建一个空文件夹)
2. `cd my-blog` (进入空文件夹内)
3. `boke init` (如果检测到文件夹不是空的，会拒绝初始化)

然后可以在当前文件内看到以下文件与文件夹：

- articles (文章文件 (markdown 格式, .md 后缀名) 请放在这里)
- articles/pics (供 markdown 文件使用的本地图片)
- articles/metadata (与 markdown 文件一一对应的 toml 文件)
- drafts (待发布的草稿放在这里)
- output (程序生成的 HTML, RSS 等文件将会输出到该文件夹)
- templates (Jinja2模板 与 CSS文件)
- boke.toml (博客名称、作者名称等等)

请用文本编辑器打开 boke.toml 填写博客名称、作者名称等。

建议尽量少用图片，本程序未为大量图片做优化。

## 添加文章

- 文件后缀必须是 ".md", 文件内容必须采用 Markdown 格式, 必须采用 utf-8 编码。
- 文件名只能使用 0-9, a-z, A-Z, _(下划线), -(短横线), .(点)。
- 把 md 文件放入 articles 文件夹，执行 `boke render articles/filename`,
  会在 **articles/metadata** 文件夹里生成 TOML 文件，
  在 **output** 文件夹生成 HTML 文件。
- 其中, TOML 里有文章的标题、作者、创建日期、修改日期等信息。
- 大多数情况下你都可以忘记 articles/metadata 里的 toml 文件，不需要修改它。

## 修改文章内容

- 直接修改 articles 里的 md 文件。
- 然后执行 `boke render articles/filename`, 即可自动更新指定文件的 toml 和 html
- 该命令与前面所述 "添加文章" 的命令是一样的，作用都是渲染 toml 和 html

## 批量处理

- 执行 `boke render -all` 可自动检查全部文件是否被修改过，如有则更新其 toml 和 html
  (如有新文章，也会自动生成 toml 和 html)。

## 强制渲染

使用前述的 `boke render` 命令时，如果文章内容无变化，会自动忽略。  
也就是说，如果只修改 toml 的内容，不修改 markdown 文件的内容，就不会触发渲染处理。

因此，如果想在不修改文章内容的情况下，修改文章的作者或日期，就需要强制渲染。

- `boke render -force articles/filename` 强制渲染指定的一篇文章。
- `boke render --title-index` 强制渲染全部标题索引（在发现未触发更新时使用）
- `boke render -force -all` 强制渲全部文章。

大多数情况下不需要强制渲染，但有一种情况：修改了 blog.toml 里的博客名称、作者名称
等信息后，需要执行 `boke render -force -all` 强制渲全部文章。

### 手动更新文章创建日期

如果想修改一篇文章的创建日期，可手动修改该文章的 toml 文件中的 ctime,
然后执行命令 `boke render -years`

### 手动更新文章修改日期

如果修改了文章的内容，在执行上述 `boke render` 相关命令时会自动更新文章的修改日期。

如果想手动设定一篇文章的修改日期，可手动修改该文章的 toml 文件中的 mtime,
然后执行命令 `boke render articles/XXX.md -force`

## 删除文章

有两种方法：

1. 使用命令 `boke delete articles/filename`
2. 直接删除 articles 文件夹里的文件，然后执行 `boke render -all`

## RSS

注意，在正式对外发布你的博客时，请在 blog.toml 中填写你的博客网址 (website),
第一次生成 atom.xml 需要执行 `boke render -rss`,
后续在执行其它命令时会自动重新渲染 atom.xml

本软件只提供有限的 RSS 功能：

1. 只包含最新发布的 10 篇文章（并且该数字写死在代码里，用户不能自由设定）
2. 只包含内容摘要，不包含全文

## 草稿

如上文所示，添加文章只需要把 markdown 文件放进 articles 文件夹即可，
操作非常简单明瞭。

但考虑到有时文章写到一半不想发布，需要一个存放草稿的地方，因此提供了一个
drafts 文件夹，草稿可以放在这里。（但其实草稿放在硬盘里的其它文件夹也行，
这个 drafts 文件夹只是提供方便，并非强制要求）

### `boke new drafts/abc.md`

该命令用来新建一个 markdown 文件，并确保其采用 UTF-8 编码。  
这个命令也只是提供方便，你完全可以不使用该命令，而是自己用其它方法创建文件。

### `boke post drafts/abc.md`

该命令的作用是把 drafts 文件夹里的指定文件移动到 articles 文件夹里，并对其执行渲染
(生成 toml 和 html 文件)。

这个命令也只是提供方便，你完全可以不使用该命令，而是自己移动文件，然后自己执行
`boke render` 命令。

### 提醒：小心覆盖文件

在终端用 `cp` 命令复制文件到 articles 文件夹时，如有同名文件，会直接覆盖。

因此建议用 `boke post` 命令，可以防止覆盖。  
(注意: 由于涉及文件移动, `boke post` 只能用来发布 drafts 文件夹里的文章。)

## Themes (主题)

- 主题名称只能由英文字母组成，不分大小写，不可包含空格。

## 替换图片地址

- 在 markdown 中可使用 `![photo-1](../output/pics/XXX.jpg)` 的形式插入图片。
- 本地图片建议放在 output/pics 文件夹内。
- 图片文件名建议使用半角英文数字，尽量不使用中文和特殊字符
- 在每篇文章对应的 toml 文件的 pairs 项目里，可指定图片的替换地址，比如：
  ```toml
  pairs =  [
    [ '''../output/pics/abc.jpg''', '''https://example.com/abc.jpg''' ],
  ]
  ```
- markdown 文件的内容保持不变, HTML 文件中如有第一个字符串，会被替代为第二个字符串。
- 不只是图片地址，该功能可以替换任何字符，但主要用途是替换图片地址。
- HTML 显示图片的宽度上限可以统一设定，详见 blog.toml 及文章对应的 toml。
