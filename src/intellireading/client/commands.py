import click
import logging
import sys
from intellireading.client.metaguiding import metaguide_epub_file, metaguide_dir, metaguide_xhtml_file
from typing import Any, cast
from collections.abc import Callable

_logger = logging.getLogger(__name__)

# TODO: somewhere in this file, logging should be configured. use the following snippet to do so:
# from monitoring.logutils import init_logging_from_file
# init_logging_from_file("logging.conf")


_output_file_option = click.option(
    "--output_file",
    type=click.Path(exists=False),
    prompt="The output file",
    prompt_required=False,
    help="The file to write",
)

_input_file_option = click.option(
    "--input_file",
    type=click.Path(exists=False),  # although it should exists, chaining commands will fail if it does not
    prompt="The input file",
    prompt_required=False,
    help="The file to read",
)

_output_dir_option = click.option(
    "--output_dir",
    type=click.Path(exists=False),
    prompt="The output directory",
    prompt_required=False,
    help="The directory to write to",
)

_input_dir_option = click.option(
    "--input_dir",
    type=click.Path(exists=False),  # although it should exists, chaining commands will fail if it does not
    prompt="The input directory",
    prompt_required=False,
    help="The directory to read from",
)

_remove_metaguiding_option = click.option(
    "--remove_metaguiding",
    is_flag=True,
    show_default=True,
    default=False,
    help="Remove metaguiding from the files (EXPERIMENTAL)",
)


def _exit_with_exception(exception: Exception, exit_code: int = 1, fg: str = "red") -> None:
    """Exit the program with an exception and exit code"""
    try:
        _logger.exception(exception)
        click.secho(
            "An error occurred. See the log for more details. (--log_level ERROR). Exiting... "
            f"(Exception Type: {type(exception).__name__}); (Exception: {exception})",
            fg=fg,
        )
    finally:
        sys.exit(exit_code)


def _get_from_ctx_if_none(
    ctx: click.Context,
    ctx_key: str,
    value: str | None,
    invoke_func: Callable[..., str] = lambda: "",
    **kwargs: Any,
) -> str:
    """Get a value from the context if it is None,
    otherwise invoke a function to get the value."""
    ctx.ensure_object(dict)
    if value:
        return value
    elif ctx.obj.get(ctx_key):
        return cast(str, ctx.obj[ctx_key])
    else:
        result: str = ctx.invoke(invoke_func, **kwargs)
        return result


@click.command(
    "metaguide-epub",
    help="Applies or removes metaguiding to the provided epub/kepub file",
)
@click.pass_context
@_input_file_option
@_output_file_option
@_remove_metaguiding_option
def metaguide_epub_cmd(ctx: click.Context, input_file: str, output_file: str, *, remove_metaguiding: bool) -> None:
    """Applies or removes metaguiding to the provided epub/kepub file"""

    try:
        ctx.ensure_object(dict)
        if remove_metaguiding:
            click.secho("Removing metaguiding from epub...", fg="yellow")
        else:
            click.secho("Metaguiding epub...", fg="yellow")

        input_file = _get_from_ctx_if_none(ctx, "output_file", input_file, lambda: click.prompt("The input file"))
        click.echo(f"Input file: {input_file}")
        output_file = _get_from_ctx_if_none(ctx, "output_file", output_file, lambda: click.prompt("The output file"))
        click.echo(f"Output file: {output_file}")

        metaguide_epub_file(input_file, output_file, remove_metaguiding=remove_metaguiding)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        _exit_with_exception(e)


@click.command(
    "metaguide-dir",
    help="Applies or removes metaguiding to the provided directory, recursively, for all epubs and xhtml files",
)
@click.pass_context
@_input_dir_option
@_output_dir_option
@_remove_metaguiding_option
def metaguide_dir_cmd(ctx: click.Context, input_dir: str, output_dir: str, *, remove_metaguiding: bool) -> None:
    """Applies metaguiding to the provided directory, recursively, for all epubs and xhtml files found in the directory
    input_dir: str
        The input directory
    output_dir: str
        The output directory
    remove_metaguiding: bool
        If True, removes metaguiding from the files
    """

    try:
        ctx.ensure_object(dict)
        if remove_metaguiding:
            click.secho("Removing metaguiding from directory...", fg="yellow")
        else:
            click.secho("Metaguiding directory...", fg="yellow")
        input_dir = _get_from_ctx_if_none(ctx, "input_dir", input_dir, lambda: click.prompt("The input directory"))
        click.echo(f"Input directory: {input_dir}")
        output_dir = _get_from_ctx_if_none(ctx, "output_dir", output_dir, lambda: click.prompt("The output directory"))
        click.echo(f"Output directory: {output_dir}")

        # check if we have the same input and output directories
        if input_dir == output_dir:
            _exit_with_exception(ValueError("Input and output directories cannot be the same. Exiting..."), fg="red")

        metaguide_dir(input_dir, output_dir, remove_metaguiding=remove_metaguiding)
    except Exception as e:
        _exit_with_exception(e)


@click.command(
    "metaguide-xhtml",
    help="Applies or removes metaguiding to the provided xhtml file",
)
@click.pass_context
@_input_file_option
@_output_file_option
@_remove_metaguiding_option
def metaguide_xhtml_cmd(ctx: click.Context, input_file: str, output_file: str, *, remove_metaguiding: bool) -> None:
    """Applies or removes metaguiding to the provided xhtml file"""

    try:
        ctx.ensure_object(dict)
        if remove_metaguiding:
            click.secho("Removing metaguiding from xhtml...", fg="yellow")
        else:
            click.secho("Metaguiding xhtml...", fg="yellow")

        input_file = _get_from_ctx_if_none(ctx, "output_file", input_file, lambda: click.prompt("The input file"))
        click.echo(f"Input file: {input_file}")
        output_file = _get_from_ctx_if_none(ctx, "output_file", output_file, lambda: click.prompt("The output file"))
        click.echo(f"Output file: {output_file}")

        metaguide_xhtml_file(input_file, output_file, remove_metaguiding=remove_metaguiding)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        _exit_with_exception(e)
