import shutil
from pathlib import Path

import click

from . import (
    __version__,
    __package_name__,
    util,
)
from .model import BlogConfig, Articles_Folder_Path, Drafts_Folder_Path, Draft_TMPL_Path, Draft_TMPL_Name
from .tmpl_render import render_article, render_all_title_indexes, render_all_years, render_rss

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.version_option(
    __version__,
    "-v",
    "-V",
    "--version",
    package_name=__package_name__,
    message="pyboke version: %(version)s",
)
@click.pass_context
def cli(ctx):
    """PyBoke: Static Blog Generator (极简博客生成器)

    https://pypi.org/project/pyboke/
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


# 以上是主命令
############
# 以下是子命令

def check_initialization(ctx) -> BlogConfig:
    """
    :return: 没有错误时返回 BlogConfig, 出错时直接退出程序。
    """
    if not util.blog_file_folders_exist():
        print("请先进入博客根目录，或使用 'boke init' 命令新建博客")
        ctx.exit()
    err, cfg = util.ensure_blog_config()
    if err:
        print(err)
        ctx.exit()
    return cfg


@cli.command(context_settings=CONTEXT_SETTINGS, name="init")
@click.pass_context
def init_command(ctx):
    """Initialize your blog.

    初始化博客。请在一个空文件夹内执行 'boke init'。
    """
    if err := util.init_blog():
        print(err)
        ctx.exit()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("filename", nargs=1)
@click.pass_context
def new(ctx, filename):
    """Create a new draft. (新建一个草稿文件)

    Example: boke new drafts/abc.md
    """
    check_initialization(ctx)
    if err := util.check_filename(filename, Drafts_Folder_Path):
        print(f"Error: {err}")
        ctx.exit()

    file_path = Path(filename)
    if file_path.exists():
        print(f"Error: 文件已存在: {filename}")
        ctx.exit()

    dst = Drafts_Folder_Path.joinpath(file_path.name)
    shutil.copyfile(Draft_TMPL_Path, dst)
    print("OK")


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("filename", nargs=1, type=click.Path(exists=True))
@click.pass_context
def post(ctx, filename):
    """Post an article in drafts. (发布 drafts 文件夹内的文章)

    Example: boke post drafts/abc.md
    """
    cfg = check_initialization(ctx)
    if err := util.check_filename(filename, Drafts_Folder_Path):
        print(f"Error: {err}")
        ctx.exit()

    file_path = Path(filename)
    article = Articles_Folder_Path.joinpath(file_path.name)
    if article.exists():
        print(f"Error: 文件已存在: {article}")
        ctx.exit()

    shutil.move(file_path, article)
    print(f"Move {filename} to {article}")

    if err := render_article(article, cfg, force=False):
        print(f"Error: {err}")
        ctx.exit()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("filename", nargs=-1, type=click.Path(exists=True))
@click.option(
    "indexes",
    "--title-index",
    is_flag=True,
    default=False,
    help="强制渲染全部标题索引"
)
@click.option(
    "years",
    "--years-only",
    is_flag=True,
    default=False,
    help="强制渲染全部年份列表"
)
@click.option(
    "rss",
    "--rss-only",
    is_flag=True,
    default=False,
    help="强制渲染 RSS (atom.xml)"
)
@click.option(
    "force",
    "-force",
    is_flag=True,
    default=False,
    help="强制渲染HTML"
)
@click.pass_context
def render(ctx, filename, indexes, years, rss, force):
    """Render TOML and HTML. (渲染文章的 toml 和 html)

    Examples:

    boke render articles/abc.md

    boke render -force articles/abcd.md

    boke render -all
    """
    cfg = check_initialization(ctx)

    if indexes:
        render_all_title_indexes(cfg)

    if years:
        render_all_years(cfg)

    if rss:
        render_rss(cfg, force=True)

    if indexes or years or rss:
        ctx.exit()

    if len(filename) != 1:
        print("请指定 articles 文件夹中的 1 个文件")
        ctx.exit()

    filename = filename[0]

    if err := util.check_filename(filename, Articles_Folder_Path):
        print(f"Error: {err}")
        ctx.exit()

    file_path = Path(filename)

    if err := render_article(file_path, cfg, force):
        print(f"Error: {err}")
        ctx.exit()
