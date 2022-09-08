import jinja2

from .model import RSS_Atom_XML, Blog_Config_Filename, Blog_Config_Path, Templates_Folder_Path


loader = jinja2.FileSystemLoader(Templates_Folder_Path)
jinja_env = jinja2.Environment(
    loader=loader, autoescape=jinja2.select_autoescape()
)


# 渲染时，除了 tmplfile 之外, templates 文件夹里的全部文件都会被复制到 output 文件夹。
tmplfile = dict(
    blog_cfg=Blog_Config_Filename,
    base="base.html",
    index="index.html",
    article="article.html",
    rss=RSS_Atom_XML,
)


def render_blog_config(cfg):
    tmpl = jinja_env.get_template(tmplfile["blog_cfg"])
    blog_toml = tmpl.render(dict(cfg=cfg))
    print(f"render and write {Blog_Config_Path}")
    Blog_Config_Path.write_text(blog_toml, encoding="utf-8")

