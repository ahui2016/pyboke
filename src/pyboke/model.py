from dataclasses import dataclass
from pathlib import Path

import arrow

RFC3339 = "YYYY-MM-DD HH:mm:ssZZ"
Blog_Config_Filename = "blog.toml"
Articles_Folder_Name = "articles"
Output_Folder_Name = "output"
Templates_Folder_Name = "templates"
HTML_Suffix = ".html"
MD_Suffix = ".md"
RSS_Atom_XML = "atom.xml"

CWD = Path.cwd().resolve()
Blog_Paths = dict(
    Blog_Config_Filename=CWD.joinpath(Blog_Config_Filename),
    Articles_Folder_Name=CWD.joinpath(Articles_Folder_Name),
    Output_Folder_Name=CWD.joinpath(Output_Folder_Name),
    Templates_Folder_Name=CWD.joinpath(Templates_Folder_Name),
)


def now():
    return arrow.now().format(RFC3339)


@dataclass
class BlogConfig:
    name = ""  # 博客名称
    author = ""  # 默认作者（每篇文章也可独立设定作者）
    uuid = ""  # 用于 RSS feed 的 uuid
    website = ""  # 博客网址，用于 RSS feed
    rss_link = ""  # RSS feed 的网址，根据 website 生成
    home_recent_maxint = 20  # 首页 "最近更新" 列表中的项目上限
    rss_updated = ""  # 上次生成 RSS feed 的时间
    blog_updated = now()  # 博客更新日期，如果大于 rss_updated 就要重新生成 RSS


@dataclass
class ArticleConfig:
    author = ""  # 文章作者，留空则采用 BlogConfig.author
    ctime = ""  # 文章创建时间
    mtime = ""  # 文章修改时间
    checksum = ""  # 用来判断文章内容有无变更
