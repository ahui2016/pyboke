from pathlib import Path

import jinja2

from . import model
from .model import RSS_Atom_XML, Blog_Config_Filename, Blog_Config_Path, \
    Templates_Folder_Path, TOML_Suffix, ArticleConfig, Metadata_Folder_Path

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


def render_article_html(md_file: Path, art_cfg: ArticleConfig):
    pass


def render_article(md_file: Path, title_length: int, force: bool):
    """
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    art_cfg_new = ArticleConfig.from_md_file(md_file, title_length)
    if not art_cfg_new.title:
        return "无法获取文章标题，请修改文章的标题(文件的第一行内容)"

    art_toml_path = art_cfg_path_from_md_path(md_file)
    need_to_render = False

    # article toml 不存在，以 art_cfg_new 为准
    if not art_toml_path.exists():
        print(f"发现新文章: {art_cfg_new.title}")
        art_cfg = art_cfg_new
        need_to_render = True
    else:
        # article toml 存在，以 art_toml_path 的文件内容为准
        art_cfg = ArticleConfig.loads(art_toml_path)

        # 文章内容发生了变化，自动更新 title, checksum, mtime
        if art_cfg.checksum != art_cfg_new.checksum:
            art_cfg.title = art_cfg_new.title
            art_cfg.checksum = art_cfg_new.checksum
            art_cfg.mtime = model.now()
            need_to_render = True

    # 需要渲染 toml
    if need_to_render:
        tmpl = jinja_env.get_template(tmplfile["art_cfg"])
        art_toml_data = tmpl.render(dict(art=art_cfg))
        print(f"render and write {art_toml_path}")
        art_toml_path.write_text(art_toml_data, encoding="utf-8")

    # 需要渲染 html
    if need_to_render or force:
        print("render_article_html")
        render_article_html(md_file, art_cfg)

    return False


def art_cfg_path_from_md_path(md_path):
    """根据 markdown 文件的路径得出 toml 文件的路径"""
    name = md_path.with_suffix(TOML_Suffix).name
    return Metadata_Folder_Path.joinpath(name)
