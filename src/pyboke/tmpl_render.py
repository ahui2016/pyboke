from dataclasses import asdict
from operator import itemgetter
from pathlib import Path

import jinja2
import mistune

from . import model
from .model import RSS_Atom_XML, Blog_Config_Filename, Blog_Config_Path, \
    Templates_Folder_Path, TOML_Suffix, ArticleConfig, Metadata_Folder_Path, \
    Draft_TMPL_Name, Output_Folder_Path, BlogConfig, HTML_Suffix, TitleIndex, \
    Indexes_Folder_Path, Title_Index_Length, RSS_Entries_Max, MD_Suffix, RSS_Content_Size, \
    RSS_Path, Articles_Folder_Path

# 注意: tmpl_render.py 不能 import util.py

loader = jinja2.FileSystemLoader(Templates_Folder_Path)
jinja_env = jinja2.Environment(
    loader=loader, autoescape=jinja2.select_autoescape()
)

# 渲染时，除了 tmplfile 之外, templates 文件夹里的全部文件都会被复制到 output 文件夹。
tmplfile = dict(
    blog_cfg=Blog_Config_Filename,
    art_cfg="article.toml",
    draft=Draft_TMPL_Name,
    base="base.html",
    index="index.html",
    year="year.html",
    title_index="title-index.html",
    indexes="indexes.html",
    article="article.html",
    rss=RSS_Atom_XML,
)


def render_blog_config(cfg):
    tmpl = jinja_env.get_template(tmplfile["blog_cfg"])
    blog_toml = tmpl.render(dict(cfg=cfg))
    print(f"render and write {Blog_Config_Path}")
    Blog_Config_Path.write_text(blog_toml, encoding="utf-8")


def blog_updated_at_now(cfg):
    """更新博客的更新时间"""
    cfg.blog_updated = model.now()
    render_blog_config(cfg)


def render_rss(cfg, force):
    if cfg.blog_updated > cfg.rss_updated or force:
        all_arts = get_all_articles()
        rss_arts = get_rss_articles(all_arts)
        really_render_rss(rss_arts, cfg)


def really_render_rss(articles, blog_cfg):
    tmpl = jinja_env.get_template(tmplfile["rss"])
    xml = tmpl.render(dict(blog=blog_cfg, entries=articles))
    print(f"render and write {RSS_Path}")
    RSS_Path.write_text(xml, encoding="utf-8")
    blog_cfg.rss_updated = model.now()
    render_blog_config(blog_cfg)


def get_rss_articles(sorted_articles):
    """
    sorted_articles 应已按文章创建时间排序。
    sorted_articles 是一个 dict, 已经有 id, 详见 get_all_articles()
    """
    recent_arts = get_recent_articles(sorted_articles, RSS_Entries_Max)
    for art in recent_arts:
        md_file = Articles_Folder_Path.joinpath(f"{art['id']}{MD_Suffix}")
        content = md_file.read_text(encoding="utf-8")
        if len(content) > RSS_Content_Size:
            content = content[:RSS_Content_Size] + "..."
        art["content"] = content
    return recent_arts


def get_all_articles():
    """注意返回的不是 ArticleConfig, 而是 dict"""
    articles = Metadata_Folder_Path.glob(f"*{TOML_Suffix}")
    arts = []
    for art_path in articles:
        art = ArticleConfig.loads(art_path)
        art = asdict(art)
        art["id"] = art_path.stem
        arts.append(art)
    return sorted(arts, key=itemgetter("ctime"), reverse=True)


def get_recent_articles(sorted_articles, n):
    return sorted_articles[:n]


def get_articles_in_years(sorted_articles):
    """获取全部年份的全部文章"""
    arts = {}
    for art in sorted_articles:
        yyyy = art["ctime"][:4]
        if yyyy in arts:
            arts[yyyy].append(art)
        else:
            arts[yyyy] = [art]
    return arts


'''
def get_articles_in_year(sorted_articles, year):
    """获取指定年份的全部文章"""
    return [art for art in sorted_articles if art["ctime"][:4] == year]
'''


def get_year_count(arts_in_years):
    return [(year, len(arts_in_years[year])) for year in arts_in_years]


def articles_in_year(sorted_articles, year):
    """指定年份的文章列表"""
    return [art for art in sorted_articles if art["ctime"][:4] == year]


def get_title_indexes(sorted_articles):
    indexes = {}
    for art in sorted_articles:
        index = art["title"][:Title_Index_Length]
        if index in indexes:
            indexes[index].articles.append(art)
        else:
            indexes[index] = TitleIndex(
                name=index,
                id=index.encode().hex(),
                articles=[art]
            )
    return indexes


def render_index_html(recent_articles, blog_cfg, arts_in_years):
    tmpl = jinja_env.get_template(tmplfile["index"])
    html = tmpl.render(dict(
        blog=blog_cfg,
        articles=recent_articles,
        year_count=get_year_count(arts_in_years),
        parent_dir=""
    ))
    output_path = Output_Folder_Path.joinpath(tmplfile["index"])
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


def render_year_html(articles, blog_cfg, year):
    tmpl = jinja_env.get_template(tmplfile["year"])
    html = tmpl.render(dict(
        articles=articles,
        blog=blog_cfg,
        year=year,
        parent_dir=""
    ))
    output_path = Output_Folder_Path.joinpath(f"{year}{HTML_Suffix}")
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


def render_all_years(articles, blog_cfg):
    """注意：通常还需要渲染首页。

    :return: 返回 arts_in_years 方便在外面渲染首页。
    """
    arts_in_years = get_articles_in_years(articles)
    for year in arts_in_years:
        render_year_html(arts_in_years[year], blog_cfg, year)
    return arts_in_years


def render_title_index_list(indexes, blog_cfg):
    tmpl = jinja_env.get_template(tmplfile["title_index"])
    html = tmpl.render(dict(
        indexes=indexes.values(),
        blog=blog_cfg,
        parent_dir=""
    ))
    output_path = Output_Folder_Path.joinpath(tmplfile["title_index"])
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


def render_title_index(tmpl, title_index, blog_cfg):
    html = tmpl.render(dict(
        index_name=title_index.name,
        articles=title_index.articles,
        blog=blog_cfg,
        parent_dir="../"
    ))
    output_path = Indexes_Folder_Path.joinpath(f"{title_index.id}{HTML_Suffix}")
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


def render_one_title_index(article, all_articles, blog_cfg):
    indexes = get_title_indexes(all_articles)
    index = article.title[:Title_Index_Length]

    tmpl = jinja_env.get_template(tmplfile["indexes"])
    render_title_index(tmpl, indexes[index], blog_cfg)

    # 如果只有一篇文章，则可以认为该 index 是新增的。
    if len(indexes[index].articles) == 1:
        render_title_index_list(indexes, blog_cfg)


def render_all_title_indexes(articles, blog_cfg):
    title_indexes = get_title_indexes(articles)

    tmpl = jinja_env.get_template(tmplfile["indexes"])
    for index in title_indexes.values():
        render_title_index(tmpl, index, blog_cfg)

    render_title_index_list(title_indexes, blog_cfg)


def render_article_html(
        md_file : Path,
        md_text : str,
        blog_cfg: BlogConfig,
        art_cfg : ArticleConfig,
):
    art = asdict(art_cfg)
    art["content"] = mistune.html(md_text)
    tmpl = jinja_env.get_template(tmplfile["article"])
    html = tmpl.render(dict(blog=blog_cfg, art=art, parent_dir=""))
    html_name = md_file.with_suffix(HTML_Suffix).name
    html_path = Output_Folder_Path.joinpath(html_name)
    print(f"render and write {html_path}")
    html_path.write_text(html, encoding="utf-8")


def render_all_articles(blog_cfg: BlogConfig, force: bool):
    """
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """

    # TODO: delete files

    all_md_files = Articles_Folder_Path.glob(f"*{MD_Suffix}")
    updated_articles = []
    for md_file in all_md_files:
        err, art_cfg = add_or_update_article(md_file, blog_cfg, force)
        if err:
            return err
        if art_cfg:
            updated_articles.append(art_cfg)

    if len(updated_articles) == 0:
        return False

    render_all_title_indexes(updated_articles, blog_cfg)

    all_arts = get_all_articles()
    recent_arts = get_recent_articles(all_arts, blog_cfg.home_recent_max)
    arts_in_years = render_all_years(all_arts, blog_cfg)
    render_index_html(recent_arts, blog_cfg, arts_in_years)

    rss_arts = get_rss_articles(all_arts)
    really_render_rss(rss_arts, blog_cfg)


def render_article(md_file: Path, blog_cfg: BlogConfig, force: bool):
    """
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    err, art_cfg = add_or_update_article(md_file, blog_cfg, force)

    if err:
        return err

    if art_cfg:
        all_arts = get_all_articles()
        recent_arts = get_recent_articles(all_arts, blog_cfg.home_recent_max)
        arts_in_years = get_articles_in_years(all_arts)
        render_index_html(recent_arts, blog_cfg, arts_in_years)
        year = art_cfg.ctime[:4]
        render_year_html(arts_in_years[year], blog_cfg, year)
        render_one_title_index(art_cfg, all_arts, blog_cfg)
        rss_arts = get_rss_articles(all_arts)
        really_render_rss(rss_arts, blog_cfg)

    return False


def add_or_update_article(md_file: Path, blog_cfg: BlogConfig, force: bool):
    """
    在渲染全部文章时，本函数处理其中一个文件。

    :return: 发生错误时返回 (str, None), 否则反回 (None, ArticleConfig) 或 (None, None).
    """
    md_file_data = md_file.read_bytes()
    art_cfg_new = ArticleConfig.from_md_file(md_file_data, blog_cfg.title_length_max)
    if not art_cfg_new.title:
        return "无法获取文章标题，请修改文章的标题(文件的第一行内容)", None

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
        blog_updated_at_now(blog_cfg)

    # 需要渲染 html
    if need_to_render or force:
        render_article_html(md_file, md_file_data.decode(), blog_cfg, art_cfg)
        return None, art_cfg

    return None, None


def art_cfg_path_from_md_path(md_path):
    """根据 markdown 文件的路径得出 toml 文件的路径"""
    name = md_path.with_suffix(TOML_Suffix).name
    return Metadata_Folder_Path.joinpath(name)
