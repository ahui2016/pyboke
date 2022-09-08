import click

from . import (
    __version__,
    __package_name__,
    util,
)

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

def check_initialization(ctx):
    if not util.blog_file_folders_exist():
        print("请先进入博客根目录，或使用 'boke init' 命令新建博客")
        ctx.exit()
    if err := util.ensure_blog_config():
        print(err)
        ctx.exit()


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
    check_initialization(ctx)
    if not util.article_in_articles(filename):
        print(f"不在 articles 文件夹内: {filename}")
        ctx.exit()
    print(filename)

