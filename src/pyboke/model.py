import hashlib
import re
from dataclasses import dataclass, asdict
from pathlib import Path

import arrow
import tomli

# 注意: model.py 在最底层，不能 import util.py, tmpl_render.py, 更不能 import main.py

RFC3339 = "YYYY-MM-DD HH:mm:ssZZ"
Blog_Config_Filename = "blog.toml"
Drafts_Folder_Name = "drafts"
Draft_TMPL_Name = "draft.md"
Articles_Folder_Name = "articles"
Pics_Folder_Name = "pics"
Metadata_Folder_Name = "metadata"
Output_Folder_Name = "output"
Templates_Folder_Name = "templates"
Themes_Folder_Name = "themes"
HTML_Suffix = ".html"
TOML_Suffix = ".toml"
MD_Suffix = ".md"
RSS_Atom_XML = "atom.xml"
Theme_CSS_Name = "theme.css"
Default_Theme_Name = "simple"

CWD = Path.cwd().resolve()
Drafts_Folder_Path = CWD.joinpath(Drafts_Folder_Name)
Articles_Folder_Path = CWD.joinpath(Articles_Folder_Name)
Pics_Folder_Path = Articles_Folder_Path.joinpath(Pics_Folder_Name)
Metadata_Folder_Path = Articles_Folder_Path.joinpath(Metadata_Folder_Name)
Output_Folder_Path = CWD.joinpath(Output_Folder_Name)
Theme_CSS_Path = Output_Folder_Path.joinpath(Theme_CSS_Name)
Templates_Folder_Path = CWD.joinpath(Templates_Folder_Name)
Themes_Folder_Path = Templates_Folder_Path.joinpath(Themes_Folder_Name)
Draft_TMPL_Path = Templates_Folder_Path.joinpath(Draft_TMPL_Name)
Blog_Config_Path = CWD.joinpath(Blog_Config_Filename)

# 文件名只能使用 0-9, a-z, A-Z, _(下划线), -(短横线)。
Filename_Forbid_Pattern = re.compile(r"[^._0-9a-zA-Z\-]")
Markdown_Title_Pattern = re.compile(r"^(#{1,6}|>|1.|-|\*) (.+)")


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
    title_length_max: int  # 文章标题长度上限，单位: byte
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
            title_length_max=192,
            rss_updated="",
            blog_updated=now(),
        )

    @classmethod
    def loads(cls):
        """Loads BlogConfig from Blog_Config_Path"""
        data = tomli_loads(Blog_Config_Path)
        return BlogConfig(**data)


@dataclass
class ArticleConfig:
    title: str  # 文章标题 [不需要手动填写，会自动获取]
    author: str  # 文章作者 [通常留空，自动等同于博客作者]
    ctime: str  # 文章创建时间
    mtime: str  # 文章修改时间
    checksum: str  # sha1, 用来判断文章内容有无变更

    @classmethod
    def from_md_file(cls, md_file, title_length):
        with open(md_file, "rb") as f:
            data = f.read()
            first_line = get_first_line(data)
            title = get_md_title(first_line, title_length)
            checksum = hashlib.sha1(data).hexdigest()
            ctime = now()
            return ArticleConfig(
                title=title,
                author="",
                ctime=ctime,
                mtime=ctime,
                checksum=checksum
            )

    @classmethod
    def loads(cls, file):
        """Loads ArticleConfig from an article.toml file."""
        data = tomli_loads(file)
        return ArticleConfig(**data)

    def copy(self):
        """Make a copy."""
        return ArticleConfig(**asdict(self))


def tomli_loads(file) -> dict:
    """正确处理 utf-16"""
    with open(file, "rb") as f:
        text = f.read()
        try:
            text = text.decode()  # Default encoding is 'utf-8'.
        except UnicodeDecodeError:
            text = text.decode("utf-16").encode().decode()
        return tomli.loads(text)


def get_first_line(file):
    """
    :param file: bytes
    :return: str, 注意有可能返回空字符串。
    """
    lines = file.decode()
    for line in lines.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def byte_len(s: str) -> int:
    return len(s.encode("utf8"))


def utf8_lead_byte(b):
    """A UTF-8 intermediate byte starts with the bits 10xxxxxx."""
    return (b & 0xC0) != 0x80


# https://stackoverflow.com/questions/13727977/truncating-string-to-byte-length-in-python
def utf8_byte_truncate(text: str, max_bytes: int) -> str:
    """If text[max_bytes] is not a lead byte, back up until a lead byte is
    found and truncate before that character."""
    utf8 = text.encode("utf8")
    if len(utf8) <= max_bytes:
        return text
    i = max_bytes
    while i > 0 and not utf8_lead_byte(utf8[i]):
        i -= 1
    return utf8[:i].decode("utf8")


def check_filename(name: str):
    """
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    if Filename_Forbid_Pattern.search(name) is None:
        return False
    else:
        return "文件名只能使用 0-9, a-z, A-Z, _(下划线), -(短横线), .(点)" \
               "\n注意：不能使用空格，请用下划线或短横线代替空格。"


def get_md_title(md_first_line: str, max_bytes: int) -> str:
    """
    :param md_first_line: 应已去除首尾空白字符。
    :param max_bytes: 标题长度上限，单位: bytes
    :return: 注意有可能返回空字符串。
    """
    md_title = Markdown_Title_Pattern.findall(md_first_line)
    if not md_title:
        title = md_first_line
    else:
        # 此时 md_title 大概像这样: [('#', ' abcd')]
        title = md_title[0][1].strip()

    return utf8_byte_truncate(title, max_bytes).strip()
