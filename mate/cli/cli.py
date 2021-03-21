import logging
import os
import time
import traceback
from pprint import pprint

import click
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from click_repl import repl
from click_repl.exceptions import ExitReplException
from prompt_toolkit.history import FileHistory

from mate import logger, setup_logger
from mate.motors import set_motor, stop_all_motors
from mate.utils.version import get_version


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
HISTORY_FILE = os.environ["HOME"] + "/.mate-history"


# noinspection PyUnusedLocal
def exit_on_non_confirmation_callback(ctx, param, value):
    """Callback routine for click."""
    if not value:
        ctx.exit()


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option(
    "--debug", "-d", default=False, is_flag=True, help="Turn on debug messages."
)
@click.pass_context
def cli(ctx, debug):
    """CLI and Python module for testing SparkFun RASPBERRY PI Servo Hat."""
    setup_logger(debug)
    logger.debug("Logging enabled ....")
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w+") as file:
            file.write("")
    if ctx.invoked_subcommand is None:
        # noinspection PyBroadException
        try:
            ctx.invoke(command_repl)
        except ExitReplException:
            exit()
        except Exception:
            traceback.print_exc()


# noinspection PyUnusedLocal
@click.command(name="exit")
@click.pass_context
def command_exit(ctx):
    """Exit mate (aliases: exit, e, quit, q)"""
    raise ExitReplException


# noinspection PyUnusedLocal
@click.command(name="e", hidden=True)
@click.pass_context
def command_e(ctx):
    raise ExitReplException


# noinspection PyUnusedLocal
@click.command(name="quit", hidden=True)
@click.pass_context
def command_quit(ctx):
    raise ExitReplException


# noinspection PyUnusedLocal
@click.command(name="q", hidden=True)
@click.pass_context
def command_q(ctx):
    raise ExitReplException


@click.command(name="help")
@click.argument("topic", default=None, required=False, nargs=1)
@click.pass_context
def command_help(ctx, topic):
    """Help command"""
    if topic is None:
        click.echo(ctx.parent.get_help())
    else:
        if topic in cli.commands:
            click.echo(cli.commands[topic].get_help(ctx))
        else:
            click.echo("Unknown command: ", nl=False)
            click.secho("{}\n".format(topic), bold=True, fg="red")
            click.echo(ctx.parent.get_help())


# noinspection PyUnusedLocal
@click.command(name='go')
@click.argument('motor', type=int)
@click.argument('microseconds', type=int)
@click.option('--debug', '-d', default=False, is_flag=True, help='Turn on debug messages.')
def command_go(motor, microseconds, debug):
    """Set the pwm value for a motor."""
    try:
        set_motor(motor, microseconds)
    except RuntimeError as err:
        click.echo(str(err), color='red', err=True)
        logging.exception("Problem setting PWM value for motor {} to {}".format(motor, microseconds))


@click.command(name="repl", hidden=True)
def command_repl():
    """Start mate in a read-eval-print-loop (REPL) interactive shell."""
    print("mate v{}".format(get_version()))
    prompt_kwargs = {
        "message": u"mate> ",
        "history": FileHistory(HISTORY_FILE),
    }
    try:
        repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)
    except ExitReplException:
        exit()


@click.command(name="version")
def command_version():
    """Display mate version information."""
    logger.debug("In version .... DEBUG message")
    logger.info("In version ... INFO message")
    print("Mate v{}".format(get_version()))


# noinspection PyUnusedLocal
@click.command(name='stop')
@click.option('--debug', '-d', default=False, is_flag=True, help='Turn on debug messages.')
def command_stop(debug):
    """Stop all motors
    """
    try:
        stop_all_motors()
    except RuntimeError as err:
        click.echo(str(err), color='red', err=True)
        logging.exception("Problem stopping all motors.")


cli.add_command(command_e)
cli.add_command(command_exit)
cli.add_command(command_q)
cli.add_command(command_quit)
cli.add_command(command_help)
cli.add_command(command_go)
cli.add_command(command_repl)
cli.add_command(command_stop)
