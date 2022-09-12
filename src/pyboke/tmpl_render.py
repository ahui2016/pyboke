import os
from dataclasses import asdict
from operator import itemgetter
from pathlib import Path

import jinja2
import mistune

from . import model
from .model import RSS_Atom_XML, Blog_Config_Filename, Blog_Config_Path, \
    Templates_Folder_Path, TOML_Suffix, ArticleConfig, Metadata_Folder_Path, \
    Draft_TMPL_Name, Output_Folder_Path, BlogConfig, HTML_Suffix

# 注意: tmpl_render.py 不能 import util.py

loader = jinja2.FileSystemLoader(Templates_Folder_Path)
jinja_env = jinja2.Environment(
    loader=loader, autoescape=jinja2.select_autoescape()
)
md_render = mistune.create_markdown(
    plugins=["strikethrough", "footnotes", "table"]
)

# 渲染时，除了 tmplfile 之外, templates 文件夹里的全部文件都会被复制到 output 文件夹。
tmplfile = dict(
    blog_cfg=Blog_Config_Filename,
    art_cfg="article.toml",
    draft=Draft_TMPL_Name,
    base="base.html",
    index="index.html",
    year="year.html",
    article="article.html",
    rss=RSS_Atom_XML,
)


def render_blog_config(cfg):
    tmpl = jinja_env.get_template(tmplfile["blog_cfg"])
    blog_toml = tmpl.render(dict(cfg=cfg))
    print(f"render and write {Blog_Config_Path}")
    Blog_Config_Path.write_text(blog_toml, encoding="utf-8")


def get_all_articles():
    articles = Metadata_Folder_Path.glob(f"*{TOML_Suffix}")
    arts = []
    for art_path in articles:
        art = ArticleConfig.loads(art_path)
        art = asdict(art)
        art["id"] = art_path.stem
        arts.append(art)
    return sorted(arts, key=itemgetter("ctime"), reverse=True)


def get_recent_articles(arts, blog_cfg):
    return arts[:blog_cfg.home_recent_max]


def get_articles_in_years(sorted_articles):
    """全部年份的全部文章"""
    arts = {}
    for art in sorted_articles:
        yyyy = art["ctime"][:4]
        if yyyy in arts:
            arts[yyyy].append(art)
        else:
            arts[yyyy] = [art]
    return arts


def get_year_count(arts_in_years):
    return [(year, len(arts_in_years[year])) for year in arts_in_years]


def articles_in_year(sorted_articles, year):
    """指定年份的文章列表"""
    return [art for art in sorted_articles if art["ctime"][:4] == year]


def render_index_html(recent_articles, blog_cfg, year_count):
    tmpl = jinja_env.get_template(tmplfile["index"])
    html = tmpl.render(dict(blog=blog_cfg, articles=recent_articles, year_count=year_count))
    output_path = Output_Folder_Path.joinpath(tmplfile["index"])
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


def render_year_html(articles, blog_cfg, year):
    tmpl = jinja_env.get_template(tmplfile["year"])
    html = tmpl.render(dict(articles=articles, blog=blog_cfg, year=year))
    output_path = Output_Folder_Path.joinpath(f"{year}{HTML_Suffix}")
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


def render_article_html(
        md_file: Path,
        blog_cfg: BlogConfig,
        art_cfg: ArticleConfig,
):
    folder_is_empty = not os.listdir(Output_Folder_Path)

    art = asdict(art_cfg)
    art["content"] = md_render(md_file.read_text(encoding="utf-8"))
    tmpl = jinja_env.get_template(tmplfile["article"])
    html = tmpl.render(dict(blog=blog_cfg, art=art))
    html_name = md_file.with_suffix(HTML_Suffix).name
    html_path = Output_Folder_Path.joinpath(html_name)
    print(f"render and write {html_path}")
    html_path.write_text(html, encoding="utf-8")


def render_article(md_file: Path, blog_cfg: BlogConfig, force: bool):
    """
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    art_cfg_new = ArticleConfig.from_md_file(md_file, blog_cfg.title_length_max)
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
        render_article_html(md_file, blog_cfg, art_cfg)
        all_arts = get_all_articles()
        recent_arts = get_recent_articles(all_arts, blog_cfg)
        arts_in_years = get_articles_in_years(all_arts)
        year_count = get_year_count(arts_in_years)
        render_index_html(recent_arts, blog_cfg, year_count)
        render_year_html(recent_arts, blog_cfg, art_cfg.ctime[:4])

    return False


def art_cfg_path_from_md_path(md_path):
    """根据 markdown 文件的路径得出 toml 文件的路径"""
    name = md_path.with_suffix(TOML_Suffix).name
    return Metadata_Folder_Path.joinpath(name)
