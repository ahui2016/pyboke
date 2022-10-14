import shutil
from pathlib import Path

import click

from . import (
    __version__,
    __package_name__,
    util,
)
from .model import BlogConfig, Articles_Folder_Path, Drafts_Folder_Path, \
    Draft_TMPL_Path, ArticleConfig
from .tmpl_render import render_article, render_rss, render_all_articles, \
    art_cfg_path_from_md_path, delete_article, preview_article, update_index_rss, get_all_articles

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


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


def show_info(ctx, _, value):
    if not value or ctx.resilient_parsing:
        return
    cfg = check_initialization(ctx)
    website = cfg.website if cfg.rss_link else "(注意：未填写网址)"
    rss = cfg.rss_link if cfg.rss_link else "(注意：填写网址后才能生成RSS)"

    print()
    print(f"[boke]    {__file__}")
    print(f"[version] {__version__}")
    print(f"[repo]    https://github.com/ahui2016/pyboke")
    print()
    print(f"[Blog]    {cfg.name}")
    print(f"[Author]  {cfg.author}")
    print(f"[Website] {website}")
    print(f"[RSS]     {rss}")
    print(f"[Update]  {cfg.blog_updated}")
    print()
    print(f"[Themes]  {', '.join(util.get_themes())}")
    print(f"[Theme]   {cfg.current_theme}")
    print(f"[Total]   {util.articles_count()} articles")
    print()
    ctx.exit()


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
@click.option(
    "-i",
    "-info",
    is_flag=True,
    help="Show information about the blog.",
    expose_value=False,
    callback=show_info,
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
    "index",
    "-index",
    is_flag=True,
    default=False,
    help="只渲染索引、首页等，不渲染文章"
)
@click.option(
    "rss",
    "-rss",
    is_flag=True,
    default=False,
    help="渲染 RSS (atom.xml)"
)
@click.option(
    "theme",
    "-theme",
    default="",
    help="更改博客的主题(CSS)"
)
@click.option(
    "render_all",
    "-all",
    is_flag=True,
    default=False,
    help="渲染全部文章"
)
@click.option(
    "preview",
    "-preview",
    is_flag=True,
    default=False,
    help="预览"
)
@click.option(
    "force",
    "-force",
    is_flag=True,
    default=False,
    help="强制渲染"
)
@click.pass_context
def render(ctx, filename, index, rss, theme, render_all, preview, force):
    """Render TOML and HTML. (渲染文章的 toml 和 html)

    Examples:

    boke render articles/abc.md

    boke render -force articles/abcd.md

    boke render -all
    """

    if rss:
        cfg = check_initialization(ctx, check_website=True)
        render_rss(get_all_articles(), cfg, force=True)
        ctx.exit()

    cfg = check_initialization(ctx)

    if render_all:
        if err := render_all_articles(cfg, force):
            print(f"Error: {err}")
        ctx.exit()

    if theme:
        themes = util.get_themes()
        if theme not in themes:
            print(f"找不到主题: {theme}")
            print(f"可选主题: {themes}")
            ctx.exit()
        util.change_theme(theme, cfg)

    if index:
        update_index_rss(cfg)

    if index or theme:
        ctx.exit()

    if len(filename) != 1:
        print("请指定 articles 文件夹中的 1 个文件，更多用法: boke render -h")
        ctx.exit()

    file_path = Path(filename[0])

    if preview:
        if err := preview_article(file_path, cfg):
            print(f"Error: {err}")
        ctx.exit()

    if err := util.check_filename(file_path, Articles_Folder_Path):
        print(f"Error: {err}")
        ctx.exit()

    if err := render_article(file_path, cfg, force):
        print(f"Error: {err}")
        ctx.exit()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("filenames", nargs=2, type=click.Path())
@click.pass_context
def rename(ctx, filenames):
    """Rename a file. (更改一篇文章的文件名)

    Example:

    boke rename articles/old-name.md articles/new-name.md
    """
    cfg = check_initialization(ctx)
    old_path, new_path = Path(filenames[0]), Path(filenames[1])
    if err := util.rename(old_path, new_path):
        print(f"Error: {err}")
        ctx.exit()
    update_index_rss(cfg)


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
    delete_article(md_path, art_cfg_path, blog_cfg)
