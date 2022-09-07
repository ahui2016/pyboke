import os

from pyboke.model import Blog_Paths, default_blog_cfg, Blog_Config_Path
from pyboke.tmpl_render import render_blog_config


def dir_not_empty(path):
    return True if os.listdir(path) else False


def make_folders(paths):
    for path in paths:
        path.mkdir()


def init_blog(path):
    """
    在一个空文件夹中初始化一个博客。
    :param path: 通常是当前目录 (current working directory).
    :return: 发生错误时返回 err_msg: str, 没有错误则返回 False 或空字符串。
    """
    if dir_not_empty(path):
        return f"Error. Folder Not Empty: {path}"

    make_folders(Blog_Paths)
    render_blog_config(default_blog_cfg())
    print(f"请用文本编辑器打开 {Blog_Config_Path} 填写博客名称、作者名称等。")
