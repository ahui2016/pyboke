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
    Articles_Folder_Path

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
    years="years.html",
    title_index="title-index.html",
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
        really_render_rss(rss_arts, cfg, force=True)


def really_render_rss(articles, blog_cfg, force=False):
    """如果不强制渲染，则只在已经存在 RSS (atom.xml) 时才渲染。"""
    if not force and not RSS_Path.exists():
        return
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
        del art["photos"]
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


def get_title_indexes(sorted_articles):
    """
    :return: dict(index, articles)
    """
    i = 0
    indexes = {}
    for art in sorted_articles:
        index = art["title"][:Title_Index_Length]
        if index in indexes:
            indexes[index].articles.append(art)
        else:
            i += 1
            indexes[index] = TitleIndex(
                name=index,
                id=f"i{i}",
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


def render_title_index(all_articles, blog_cfg):
    indexes = get_title_indexes(all_articles)
    tmpl = jinja_env.get_template(tmplfile["title_index"])
    html = tmpl.render(dict(
        indexes=sort_by_title_index(indexes),
        blog=blog_cfg,
        parent_dir=""
    ))
    output_path = Output_Folder_Path.joinpath(tmplfile["title_index"])
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


def render_index_html(recent_articles, blog_cfg):
    tmpl = jinja_env.get_template(tmplfile["index"])
    html = tmpl.render(dict(
        blog=blog_cfg,
        articles=recent_articles,
        parent_dir=""
    ))
    output_path = Output_Folder_Path.joinpath(tmplfile["index"])
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


def render_years_html(year_articles, blog_cfg):
    tmpl = jinja_env.get_template(tmplfile["years"])
    html = tmpl.render(dict(
        year_articles=year_articles,
        blog=blog_cfg,
        parent_dir=""
    ))
    output_path = Output_Folder_Path.joinpath(tmplfile["years"])
    print(f"render and write {output_path}")
    output_path.write_text(html, encoding="utf-8")


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
    html_path = html_path_from_md_path(md_file)
    print(f"render and write {html_path}")
    html_path.write_text(html, encoding="utf-8")


def delete_articles(all_md_files):
    """
    :return: 需要删除的文件的数量 len(to_be_delete)
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


def render_all_articles(blog_cfg: BlogConfig, force: bool):
    """
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    all_md_files = Articles_Folder_Path.glob(f"*{MD_Suffix}")
    all_md_files = list(all_md_files)
    deleted_count = delete_articles(all_md_files)

    updated_articles = []
    for md_file in all_md_files:
        err, art_cfg = add_or_update_article(md_file, blog_cfg, force)
        if err:
            return err
        if art_cfg:
            updated_articles.append(asdict(art_cfg))

    if deleted_count + len(updated_articles) == 0:
        return False

    update_index_rss(blog_cfg)
    return False


def update_index_rss(blog_cfg):
    all_arts = get_all_articles()
    recent_arts = get_recent_articles(all_arts, blog_cfg.home_recent_max)
    render_index_html(recent_arts, blog_cfg)
    arts_in_years = get_articles_in_years(all_arts)
    render_years_html(arts_in_years, blog_cfg)
    render_title_index(all_arts, blog_cfg)
    rss_arts = get_rss_articles(all_arts)
    really_render_rss(rss_arts, blog_cfg)


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
    err, art_cfg = add_or_update_article(md_file, blog_cfg, force)

    if err:
        return err

    if art_cfg:
        update_index_rss(blog_cfg)

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
            photo_n = get_photo_n(art_cfg, blog_cfg.photo_n)
            art_cfg.photos, err = get_md_images(art_cfg, art_cfg_new, photo_n, art_toml_path)
            if err:
                return err, None
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


def get_photo_n(art_cfg, blog_photo_n):
    """如果 blog_photo_n 超过 len(photo_urls), 则自动改为指定最后一张图片"""
    if len(art_cfg.photos) == 0:
        return 1

    photo = art_cfg.photos[0]  # photo = [name, url1, url2...]
    photo_urls = photo[1:]
    urls_len = len(photo_urls)
    return urls_len if blog_photo_n > urls_len else blog_photo_n


def md_images_to_dict(images):
    d = {}
    for image in images:
        d[image[0]] = image[1:]
    return d


def get_md_images(art_cfg_old, art_cfg_new, photo_n, art_cfg_path):
    """图片地址用 JSON 描述如下：
    "photos": [
        [ "Photo1", "./articles/pics/abc.jpg", "https://example.com/abc.jpg" ],
        [ "Photo2", "./articles/pics/def.jpg", "https://example.com/def.jpg" ],
    ]
    photos 中的每一个 photo, photo[0] 是图片名称, photo[1] 是第一张图，以此类推。
    """

    # 如果图片只有一个地址，则以 art_cfg_new 为准。
    if len(art_cfg_old.photos) == 0 or len(art_cfg_old.photos[0]) == 2:
        return art_cfg_new.photos, None

    images_old = md_images_to_dict(art_cfg_old.photos)
    images = []

    for item in art_cfg_new.photos:
        name, img_url = item[0].strip(), item[1]
        if not name:
            return None
        if name in images_old:
            image = images_old.pop(name)
            image[photo_n] = img_url
            images.append(image)
        else:
            images.append(item)

    if len(images_old) > 0:
        return None, f"图片设置需要手动处理: {art_cfg_path}"

    return images, None


def art_cfg_path_from_md_path(md_path):
    """根据 markdown 文件的路径得出 toml 文件的路径"""
    name = md_path.with_suffix(TOML_Suffix).name
    return Metadata_Folder_Path.joinpath(name)


def html_path_from_md_path(article_path):
    """根据文章 (markdown 或 toml) 的路径得出 html 文件的路径"""
    name = article_path.with_suffix(HTML_Suffix).name
    return Output_Folder_Path.joinpath(name)
