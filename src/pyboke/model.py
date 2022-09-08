from dataclasses import dataclass
from pathlib import Path

import arrow

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
Articles_Folder_Path = CWD.joinpath(Articles_Folder_Name)
Output_Folder_Path = CWD.joinpath(Output_Folder_Name)
Templates_Folder_Path = CWD.joinpath(Templates_Folder_Name)
Pics_Folder_Path = Articles_Folder_Path.joinpath(Pics_Folder_Name)
Blog_Config_Path = CWD.joinpath(Blog_Config_Filename)


def now():
    return arrow.now().format(RFC3339)


@dataclass
class BlogConfig:
    name: str  # 博客名称
    author: str  # 默认作者（每篇文章也可独立设定作者）
    uuid: str  # 用于 RSS feed 的 uuid
    website: str  # 博客网址，用于 RSS feed
    rss_link: str  # RSS feed 的网址，根据 website 生成
    home_recent_max: int  # 首页 "最近更新" 列表中的项目上限
    rss_updated: str  # 上次生成 RSS feed 的时间
    blog_updated: str  # 博客更新日期，如果大于 rss_updated 就要重新生成 RSS

    @classmethod
    def default(cls):
        return BlogConfig(
            name="在此填写博客名称",
            author="在此填写作者名称",
            uuid="",  # 在第一次填写博客名称时生成
            website="在此填写博客网址",
            rss_link="",  # 在博客名称变更时生成
            home_recent_max=20,
            rss_updated="",
            blog_updated=now(),
        )


@dataclass
class ArticleConfig:
    author: str  # 文章作者，留空则采用 BlogConfig.author
    ctime: str  # 文章创建时间
    mtime: str  # 文章修改时间
    checksum: str  # sha1, 用来判断文章内容有无变更
