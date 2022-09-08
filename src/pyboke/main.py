import click

from . import (
    __version__,
    __package_name__,
    util,
)
from .model import BlogConfig, ArticleConfig
from .tmpl_render import render_article_config

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
@click.argument("filename", nargs=1, type=click.Path(exists=True))
@click.pass_context
def post(ctx, filename):
    """Post an article. (发表文章)

    Example: boke post ./articles/abc.md
    """
    if err := util.check_filename(filename):
        print(f"Error: {err}")
        ctx.exit()

    cfg = check_initialization(ctx)
    art = ArticleConfig.from_md_file(filename, cfg.title_length_max)
    if not art.title:
        print(f"Error: 无法获取文章标题，请修改文章的标题(文件的第一行内容)")
        ctx.exit()

    print(f"Article: {art}")
    render_article_config(filename, art, force=False)
