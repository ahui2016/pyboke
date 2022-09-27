import shutil
from pathlib import Path

import click

from . import (
    __version__,
    __package_name__,
    util,
    tmpl_render,
)
from .model import BlogConfig, Articles_Folder_Path, Drafts_Folder_Path, Draft_TMPL_Path, ArticleConfig
from .tmpl_render import render_article, render_all_title_indexes, render_rss, render_index_html, \
    render_all_articles, art_cfg_path_from_md_path, delete_article, render_years_html

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

def check_initialization(ctx, check_website=False) -> BlogConfig:
    """
    :return: 没有错误时返回 BlogConfig, 出错时直接退出程序。
    """
    if not util.blog_file_folders_exist():
        print("请先进入博客根目录，或使用 'boke init' 命令新建博客")
        ctx.exit()
    err, cfg = util.ensure_blog_config(check_website)
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
    file_path = Path(filename)
    if err := util.check_filename(file_path, Drafts_Folder_Path):
        print(f"Error: {err}")
        ctx.exit()

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
    file_path = Path(filename)
    if err := util.check_filename(file_path, Drafts_Folder_Path):
        print(f"Error: {err}")
        ctx.exit()

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
    help="渲染标题索引"
)
@click.option(
    "years",
    "-years",
    is_flag=True,
    default=False,
    help="渲染年份列表"
)
@click.option(
    "rss",
    "-rss",
    is_flag=True,
    default=False,
    help="渲染 RSS (atom.xml)"
)
@click.option(
    "render_all",
    "-all",
    is_flag=True,
    default=False,
    help="渲染全部文章"
)
@click.option(
    "force",
    "-force",
    is_flag=True,
    default=False,
    help="强制渲染"
)
@click.pass_context
def render(ctx, filename, indexes, years, rss, render_all, force):
    """Render TOML and HTML. (渲染文章的 toml 和 html)

    Examples:

    boke render articles/abc.md

    boke render -force articles/abcd.md

    boke render -all
    """

    if rss:
        cfg = check_initialization(ctx, check_website=True)
        render_rss(cfg, force=True)
        ctx.exit()

    cfg = check_initialization(ctx)

    if indexes:
        all_articles = tmpl_render.get_all_articles()
        render_all_title_indexes(all_articles, cfg)

    if years:
        all_articles = tmpl_render.get_all_articles()
        arts_in_years = tmpl_render.get_articles_in_years(all_articles)
        render_years_html(arts_in_years, cfg)

    if render_all:
        if err := render_all_articles(cfg, force):
            print(f"Error: {err}")

    if indexes or years or render_all:
        ctx.exit()

    if len(filename) != 1:
        print("请指定 articles 文件夹中的 1 个文件，更多用法: boke render -h")
        ctx.exit()

    file_path = Path(filename[0])

    if err := util.check_filename(file_path, Articles_Folder_Path):
        print(f"Error: {err}")
        ctx.exit()

    if err := render_article(file_path, cfg, force):
        print(f"Error: {err}")
        ctx.exit()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("filename", nargs=1, type=click.Path(exists=True))
@click.pass_context
def delete(ctx, filename):
    """Delete an article. (删除文章)

    Examples:

    boke delete articles/abc.md
    """
    blog_cfg = check_initialization(ctx)
    md_path = Path(filename)
    if err := util.check_filename(md_path, Articles_Folder_Path):
        print(f"Error: {err}")
        ctx.exit()

    art_cfg_path = art_cfg_path_from_md_path(md_path)
    art_cfg = ArticleConfig.loads(art_cfg_path)
    print(f"Title: {art_cfg.title}")
    click.confirm("Confirm deletion (确认删除，不可恢复)", abort=True)
    delete_article(md_path, art_cfg_path, art_cfg, blog_cfg)
