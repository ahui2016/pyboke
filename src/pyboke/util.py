import os
import shutil
from pathlib import Path

import tomli

from .model import Blog_Config_Path, CWD, Templates_Folder_Name, Articles_Folder_Path, \
    Templates_Folder_Path, Output_Folder_Path, BlogConfig, Pics_Folder_Path
from .tmpl_render import render_blog_config


def dir_not_empty(path):
    return True if os.listdir(path) else False


def copy_templates():
    src_folder = Path(__file__).parent.parent.joinpath(Templates_Folder_Name)
    shutil.copytree(src_folder, Templates_Folder_Path)


def init_blog():
    """
    在一个空文件夹中初始化一个博客。
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    if dir_not_empty(CWD):
        return f"Error. Folder Not Empty: {CWD}"

    Articles_Folder_Path.mkdir()
    Pics_Folder_Path.mkdir()
    Output_Folder_Path.mkdir()
    copy_templates()
    render_blog_config(BlogConfig.default())
    print(f"请用文本编辑器打开 {Blog_Config_Path} 填写博客名称、作者名称等。")


def tomli_loads(file) -> dict:
    """正确处理 utf-16"""
    with open(file, "rb") as f:
        text = f.read()
        try:
            text = text.decode()  # Default encoding is 'utf-8'.
        except UnicodeDecodeError:
            text = text.decode("utf-16").encode().decode()
        return tomli.loads(text)


def blog_file_folders_exist():
    return Articles_Folder_Path.exists()\
        and Pics_Folder_Path.exists()\
        and Output_Folder_Path.exists()\
        and Blog_Config_Path.exists()


def ensure_blog_config():
    """
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    data = tomli_loads(Blog_Config_Path)
    cfg = BlogConfig(**data)
    default_cfg = BlogConfig.default()
    if cfg.name == default_cfg.name:
        return f"请用文本编辑器打开 {Blog_Config_Path} 填写博客名称"
    if cfg.author == default_cfg.author:
        return f"请用文本编辑器打开 {Blog_Config_Path} 填写作者名称"
    if cfg.home_recent_max <= 0:
        return f"请用文本编辑器打开 {Blog_Config_Path} 填写 home_recent_max, 必须大于零"
    return False


def article_in_articles(filename):
    return Path(filename).parent.samefile(Articles_Folder_Path)
