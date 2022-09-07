# PyBoke

Static Blog Generator (极简博客生成器)

- 使用过程极简
- 功能极简，代码极简

- 文章文件名、图片文件名由用户设定，只允许使用 0-9a-zA-Z_-
- 文章文件名、图片文件名相当于 ID

## 创建一个新博客


1. `mkdir my-blog` (新建一个空文件夹)
2. `cd my-blog` (进入空文件夹内)
3. `boke init` (如果检测到文件夹不是空的，会拒绝初始化)

然后可以在当前文件内看到以下文件与文件夹：

- articles (文章文件 (markdown 格式, .md 后缀名) 请放在这里)
- articles/pics (供 markdown 文件使用的本地图片)
- output (程序生成的 HTML, RSS 等文件将会输出到该文件夹)
- templates (Jinja2模板 与 CSS文件)
- boke.toml (博客名称、作者名称等等)

请用文本编辑器打开 boke.toml 填写博客名称、作者名称等。
（用 Jinja2 生成 toml?）

建议尽量少用图片，本程序未为大量图片做优化。

## 添加文章

- 文件后缀必须是 ".md", 文件内容必须采用 Markdown 格式, 必须采用 utf-8 编码。
- 文件名只能使用 0-9, a-z, A-Z, _(下划线), -(短横线)。
- 把 md 文件放入 articles 文件夹，执行 `boke post`,
  会在 metadata 文件夹自动生成 toml 文件，并给出提示信息。
- 新文章的 toml 里有 ctime, mtime, hash, 如果文件 hash 发生变化就更新 mtime

## 修改文章内容

- 直接修改 articles 里的 md 文件。
- 然后执行 `boke update articles/filename` 指定更新一个文件。
- 也可执行 `boke update all` 自动检查每一个文件是否被修改过，并且更新。

## 只更新日期

如果文章内容无变化，只更新 mtime, 有两种方法:

1. 修改 toml 文件里的 mtime, 然后执行 `boke update articles/filename`
   强制重新生成 HTML。
2. 不修改 toml, 直接执行 `boke updateMtimeNow articles/filename`
   会自动将 mtime 修改为当前时间，并重新生成 HTML。

其中第 1 种方法也可用来修改 ctime 及其他信息。

## 删除文章

有两种方法：

1. 直接删除 articles 文件夹里的文件，然后执行 `boke update all`
2. 使用命令 `boke delete articles/filename`
