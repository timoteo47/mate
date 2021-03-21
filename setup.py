import os
from setuptools import setup, find_packages, Command
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
from subprocess import STDOUT


def run_command(cmd):
    """tests shell command in subprocess and return results

    Arg:
        cmd (str): Shell command
        timeout (int): Time in seconds to wait for command to complete.

    Returns:
        (str) results from shell command

    """
    try:
        response = subprocess.check_output(cmd, shell=True, stderr=STDOUT).decode()
        return response, 0
    except subprocess.CalledProcessError as error:
        return error.output.decode(), error.returncode


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        install.run(self)


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        os.system("rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info *~")


setup(
    name="mate",
    version="0.1",
    author="Tim Sylvester",
    author_email="tsylvester@netflix.com",
    url="http://www.xacademy.org",
    license="LICENSE",
    description="Run bundled TTR tests.",
    long_description=open("README.md").read(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["mate=mate.cli.cli:cli"]},
    cmdclass={
        "clean": CleanCommand,
        "develop": PostDevelopCommand,
        "install": PostInstallCommand,
    },
)
