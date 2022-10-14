from dataclasses import asdict
from operator import itemgetter
from pathlib import Path

import jinja2
import mistune

from . import model
from .model import RSS_Atom_XML, Blog_Config_Filename, Blog_Config_Path, \
    Templates_Folder_Path, TOML_Suffix, ArticleConfig, Metadata_Folder_Path, \
    Draft_TMPL_Name, Output_Folder_Path, BlogConfig, HTML_Suffix, TitleIndex, \
    Title_Index_Length, RSS_Entries_Max, MD_Suffix, RSS_Content_Size, RSS_Path, \
    Articles_Folder_Path, Temp_HTML_Path

# 注意: tmpl_render.py 不能 import util.py

loader = jinja2.FileSystemLoader(Templates_Folder_Path)
jinja_env = jinja2.Environment(
    loader=loader, autoescape=jinja2.select_autoescape()
)

# 渲染时，除了 tmplfile 之外, templates 文件夹里的全部文件都会被复制到 output 文件夹。
tmplfile = dict(
    blog_cfg    = Blog_Config_Filename,
    art_cfg     = "article.toml",
    draft       = Draft_TMPL_Name,
    base        = "base.html",
    index       = "index.html",
    years       = "years.html",
    article     = "article.html",
    random      = "random.html",
    title_index = "title-index.html",
    rss         = RSS_Atom_XML,
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


def render_rss(all_articles, cfg, force):
    if cfg.blog_updated > cfg.rss_updated or force:
        rss_arts = get_rss_articles(all_articles)
        really_render_rss(rss_arts, cfg, force)


def really_render_rss(articles, blog_cfg, force):
    """如果不强制渲染，则只在已经存在 RSS (atom.xml) 时才渲染。"""
    if not force and not RSS_Path.exists():
        return
    tmpl = jinja_env.get_template(tmplfile["rss"])
    xml = tmpl.render(dict(blog=blog_cfg, entries=articles))
    print(f"render and write {RSS_Path}")
    RSS_Path.write_text(xml, encoding="utf-8")
    blog_cfg.rss_updated = model.now()
    render_blog_config(blog_cfg)


def get_rss_articles(all_articles):
    """
    按文章的修改时间排列。
    all_articles 是一个 dict, 已经有 id, 详见 get_all_articles()
    """
    sorted_articles = sort_articles(all_articles, key="mtime")
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
    return arts


def ignore_articles(articles):
    return [art for art in articles if not art["ignored"]]


def sort_articles(articles, key):
    return sorted(articles, key=itemgetter(key), reverse=True)

def get_all_html_filenames(all_articles):
    return [art["id"]+HTML_Suffix for art in all_articles]


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


def get_title_indexes(sorted_articles):
    """
    :return: dict(index, articles)
    """
    indexes = {}
    for art in sorted_articles:
        index = art["title"][:Title_Index_Length]
        if index in indexes:
            indexes[index].articles.append(art)
        else:
            index_id = index.encode().hex()
            indexes[index] = TitleIndex(
                name=index,
                id=f"i{index_id}",
                articles=[art]
            )
    return indexes


def sort_by_title_index(indexes: dict) -> list:
    keys = sorted(indexes.keys())
    result = []
    for key in keys:
        item = indexes[key]
        item.articles = sorted(item.articles, key=itemgetter("title"))
        result.append(item)
    return result


def render_write_html(page_name: str, data: dict, output_path: Path = None):
    if output_path is None:
        output_path = Output_Folder_Path.joinpath(tmplfile[page_name])
    tmpl = jinja_env.get_template(tmplfile[page_name])
    html = tmpl.render(data)
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


def render_title_index(all_articles, blog_cfg):
    indexes = get_title_indexes(all_articles)
    render_write_html("title_index", dict(
        indexes=sort_by_title_index(indexes),
        blog=blog_cfg,
        parent_dir=""
    ))


def render_index_html(recent_articles, html_filenames, blog_cfg):
    render_write_html("index", dict(
        blog=blog_cfg,
        articles=recent_articles,
        files=html_filenames,
        parent_dir=""
    ))
    render_write_html("random", dict(blog=blog_cfg, files=html_filenames))


def render_years_html(year_articles, blog_cfg):
    render_write_html("years", dict(
        year_articles=year_articles,
        blog=blog_cfg,
        parent_dir=""
    ))


def replace_or_not(art_cfg : ArticleConfig, blog_cfg: BlogConfig):
    match art_cfg.replace:
        case 0:
            return blog_cfg.auto_replace
        case -1:
            return False
        case 1:
            return True


def render_article_html(
        html_path : Path,
        md_text : str,
        blog_cfg: BlogConfig,
        art_cfg : ArticleConfig,
):
    if replace_or_not(art_cfg, blog_cfg):
        for pair in art_cfg.pairs:
            md_text = md_text.replace(pair[0], pair[1], 1)

    art = asdict(art_cfg)
    index_id = art["title"][:Title_Index_Length].encode().hex()
    art["index_id"] = f"i{index_id}"
    art["content"] = mistune.html(md_text)
    render_write_html(
        "article", dict(blog=blog_cfg, art=art, parent_dir=""), html_path)


def delete_articles(all_md_files):
    """
    :return: 删除的文件的数量 len(to_be_delete)
    """
    all_id = [file.stem for file in all_md_files]
    all_metadata = Metadata_Folder_Path.glob(f"*{TOML_Suffix}")
    to_be_delete = [file for file in all_metadata if file.stem not in all_id]
    result = len(to_be_delete)
    if result == 0:
        return 0

    for file in to_be_delete:
        print(f"DELETE {file}")
        file.unlink()
        html_path = html_path_from_md_path(file)
        print(f"DELETE {html_path}")
        html_path.unlink()

    return result


def update_index_rss(blog_cfg):
    all_arts = get_all_articles()
    render_rss(all_arts, blog_cfg, force=False)

    all_arts = ignore_articles(all_arts)
    all_arts = sort_articles(all_arts, key="ctime")

    recent_arts = get_recent_articles(all_arts, blog_cfg.home_recent_max)
    html_filenames = get_all_html_filenames(all_arts)
    render_index_html(recent_arts, html_filenames, blog_cfg)
    arts_in_years = get_articles_in_years(all_arts)
    render_years_html(arts_in_years, blog_cfg)
    render_title_index(all_arts, blog_cfg)


def render_all_articles(blog_cfg: BlogConfig, force: bool):
    """
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    all_md_files = Articles_Folder_Path.glob(f"*{MD_Suffix}")
    all_md_files = list(all_md_files)
    deleted_count = delete_articles(all_md_files)

    updated_articles = 0
    for md_file in all_md_files:
        err, need_to_render = add_or_update_article(md_file, blog_cfg, force)
        if err:
            return err
        if need_to_render:
            updated_articles += 1

    if force or deleted_count + updated_articles > 0:
        blog_updated_at_now(blog_cfg)
        update_index_rss(blog_cfg)

    return False


def delete_article(md_path, toml_path, blog_cfg):
    print(f"DELETE {md_path}")
    md_path.unlink()
    print(f"DELETE {toml_path}")
    toml_path.unlink()
    html_path = html_path_from_md_path(md_path)
    print(f"DELETE {html_path}")
    html_path.unlink()
    blog_updated_at_now(blog_cfg)
    update_index_rss(blog_cfg)


def render_article(md_file: Path, blog_cfg: BlogConfig, force: bool):
    """
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    err, need_to_render = add_or_update_article(md_file, blog_cfg, force)

    if err:
        return err

    if need_to_render:
        blog_updated_at_now(blog_cfg)
        update_index_rss(blog_cfg)

    return False


def preview_article(md_file: Path, blog_cfg: BlogConfig):
    """只渲染一个文件，不执行 update_index_rss() """
    md_data = md_file.read_bytes()
    art_toml_path = art_cfg_path_from_md_path(md_file)
    if art_toml_path.exists():
        art_cfg = ArticleConfig.loads(art_toml_path)
    else:
        art_cfg, err = ArticleConfig.from_md_file(md_file, md_data, blog_cfg.title_length_max)
        if err:
            return err

    art_cfg.mtime = model.now()
    render_article_html(Temp_HTML_Path, md_data.decode(), blog_cfg, art_cfg)


def add_or_update_article(md_file: Path, blog_cfg: BlogConfig, force: bool):
    """
    在渲染全部文章时，本函数处理其中一个文件。

    :return: 发生错误时返回 (str, None), 否则反回 (None, need_to_render)
    """
    md_file_data = md_file.read_bytes()
    art_cfg_new, err = ArticleConfig.from_md_file(
        md_file, md_file_data, blog_cfg.title_length_max)
    if err:
        return err, False

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
            print(f"更新: {art_cfg_new.title}")
            art_cfg.title = art_cfg_new.title
            art_cfg.checksum = art_cfg_new.checksum
            art_cfg.mtime = model.now()
            need_to_render = True

    # 文章内容有变化，需要渲染 toml
    if need_to_render:
        tmpl = jinja_env.get_template(tmplfile["art_cfg"])
        art_toml_data = tmpl.render(dict(art=art_cfg))
        print(f"render and write {art_toml_path}")
        art_toml_path.write_text(art_toml_data, encoding="utf-8")

    # 需要渲染 html
    if need_to_render or force:
        html_path = html_path_from_md_path(md_file)
        render_article_html(html_path, md_file_data.decode(), blog_cfg, art_cfg)

    return None, need_to_render


def art_cfg_path_from_md_path(md_path):
    """根据 markdown 文件的路径得出 toml 文件的路径"""
    name = md_path.with_suffix(TOML_Suffix).name
    return Metadata_Folder_Path.joinpath(name)


def html_path_from_md_path(article_path):
    """根据文章 (markdown 或 toml) 的路径得出 html 文件的路径"""
    name = article_path.with_suffix(HTML_Suffix).name
    return Output_Folder_Path.joinpath(name)
