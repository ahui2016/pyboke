from dataclasses import dataclass
from pathlib import Path

import arrow
import tomli

RFC3339 = "YYYY-MM-DD HH:mm:ssZZ"
Blog_Config_Filename = "blog.toml"
Articles_Folder_Name = "articles"
Pics_Folder_Name = "pics"
Output_Folder_Name = "output"
Templates_Folder_Name = "templates"
HTML_Suffix = ".html"
MD_Suffix = ".md"
RSS_Atom_XML = "atom.xml"

CWD = Path.cwd().resolve()
Blog_Paths = dict(
    Articles_Folder_Name=CWD.joinpath(Articles_Folder_Name),
    Output_Folder_Name=CWD.joinpath(Output_Folder_Name),
    Templates_Folder_Name=CWD.joinpath(Templates_Folder_Name),
)
Blog_Paths[Pics_Folder_Name] = Blog_Paths[Articles_Folder_Name].joinpath(Pics_Folder_Name)
Blog_Config_Path = CWD.joinpath(Blog_Config_Filename)


def now():
    return arrow.now().format(RFC3339)


@dataclass
class BlogConfig:
    name = ""  # 博客名称
    author = ""  # 默认作者（每篇文章也可独立设定作者）
    uuid = ""  # 用于 RSS feed 的 uuid
    website = ""  # 博客网址，用于 RSS feed
    rss_link = ""  # RSS feed 的网址，根据 website 生成
    home_recent_maxint = 0  # 首页 "最近更新" 列表中的项目上限
    rss_updated = ""  # 上次生成 RSS feed 的时间
    blog_updated = ""  # 博客更新日期，如果大于 rss_updated 就要重新生成 RSS


def default_blog_cfg():
    cfg = BlogConfig()
    cfg.name = "在此填写博客名称"
    cfg.author = "在此填写作者名称"
    cfg.uuid = ""  # 在第一次填写博客名称时生成
    cfg.website = "在此填写博客网址"
    cfg.rss_link = ""  # 在博客名称变更时生成
    cfg.home_recent_maxint = 20
    cfg.rss_updated = ""
    cfg.blog_updated = now()
    return cfg


@dataclass
class ArticleConfig:
    author = ""  # 文章作者，留空则采用 BlogConfig.author
    ctime = ""  # 文章创建时间
    mtime = ""  # 文章修改时间
    checksum = ""  # 用来判断文章内容有无变更


def tomli_loads(file) -> dict:
    """正确处理 utf-16"""
    with open(file, "rb") as f:
        text = f.read()
        try:
            text = text.decode()  # Default encoding is 'utf-8'.
        except UnicodeDecodeError:
            text = text.decode("utf-16").encode().decode()
        return tomli.loads(text)
