from pathlib import Path

import jinja2

from .model import RSS_Atom_XML, Blog_Config_Filename, Blog_Config_Path, Templates_Folder_Path, TOML_Suffix, \
    Articles_Folder_Path, ArticleConfig

loader = jinja2.FileSystemLoader(Templates_Folder_Path)
jinja_env = jinja2.Environment(
    loader=loader, autoescape=jinja2.select_autoescape()
)


# 渲染时，除了 tmplfile 之外, templates 文件夹里的全部文件都会被复制到 output 文件夹。
tmplfile = dict(
    blog_cfg=Blog_Config_Filename,
    art_cfg="article.toml",
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


def render_art_cfg_post(md_file: Path, art_cfg: ArticleConfig):
    art_toml_path = md_file.with_suffix(TOML_Suffix)
    if art_toml_path.exists():
        return f"文章已存在，不可重复发布: {art_toml_path}"

def render_art_cfg_update(md_file: Path, art_cfg: ArticleConfig):
    pass

def render_article_config(md_file: Path, art_cfg: ArticleConfig):
    """
    :return: 如果未写文件，返回 False, 写了文件则返回 True
    """
    tmpl = jinja_env.get_template(tmplfile["art_cfg"])
    art_toml_data = tmpl.render(dict(art=art_cfg))
    art_toml_path = md_file.with_suffix(TOML_Suffix)
    if art_toml_path.exists():
        return False
    print(f"render and write {art_toml_path}")
    art_toml_path.write_text(art_toml_data, encoding="utf-8")
    return True
