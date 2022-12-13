import os
import re
import subprocess
from typing import Any, Callable, Iterable, Mapping

import dotbot


class Rust(dotbot.Plugin):
    _directives: Mapping[str, Callable] = {}
    _defaults: Mapping[str, Any] = {}

    def __init__(self, *args, **kwargs) -> None:
        self._directives = {
            'install-rustup': self._install_rustup,
            'cargo': self._cargo,
            'cargo-update': self._cargo_update,
        }
        self._defaults = {
            'cargo': {
                'stdin': False,
                'stderr': True,
                'stdout': False,
                'force_intel': False,
            },
            'cargo-update': {
                'stdin': False,
                'stderr': False,
                'stdout': True,
                'force_intel': False,
            },
        }
        super().__init__(*args, **kwargs)

    def can_handle(self, directive: str) -> bool:
        return directive in list(self._directives.keys())

    def handle(self, directive: str, data: Iterable) -> bool:
        user_defaults = self._context.defaults().get(directive, {})
        local_defaults = self._defaults.get(directive, {})
        defaults = {**local_defaults, **user_defaults}
        return self._directives[directive](data, defaults)

    def _invoke_shell_command(
        self, cmd: str, defaults: Mapping[str, Any]
    ) -> int:
        with open(os.devnull, 'w') as devnull:
            if defaults['force_intel']:
                cmd = 'arch --x86_64 ' + cmd

            return subprocess.call(
                cmd,
                shell=True,
                cwd=self._context.base_directory(),
                stdin=devnull if defaults['stdin'] else None,
                stdout=devnull if defaults['stdout'] else None,
                stderr=devnull if defaults['stderr'] else None,
            )

    def _cargo(self, packages: list, defaults: Mapping[str, Any]) -> bool:
        result: bool = True

        for pkg in packages:
            run = self._install(
                'cargo install {pkg}',
                'cargo install --list | grep "^{pkg_name} "',
                pkg,
                defaults,
            )
            if not run:
                self._log.error('Some packages were not installed')
                result = False

        if result:
            self._log.info('All cargo packages have been installed')

        return result

    def _install(self, install_format, check_installed_format, pkg, defaults):
        cwd = self._context.base_directory()

        if not pkg:
            self._log.error('Cannot process blank package name')
            return False

        # Take out tap names (before slashes), and flags (after spaces), to get
        # just the package name (the part in between)
        pkg_parse = re.search(r'^(?:.+/)?(.+?)(?: .+)?$', pkg)
        if not pkg_parse:
            # ¯\_(ツ)_/¯
            self._log.error(f"Package name {pkg} doesn't work for some reason")
            return False

        pkg_name = pkg_parse[1]

        with open(os.devnull, 'w') as devnull:
            isInstalled = subprocess.call(
                check_installed_format.format(pkg_name=pkg_name),
                shell=True,
                stdin=devnull,
                stdout=devnull,
                stderr=devnull,
                cwd=cwd,
            )

            if isInstalled == 0:
                self._log.debug(f'{pkg} already installed')
                return True

            self._log.info(f'Installing {pkg}')
            result = self._invoke_shell_command(
                install_format.format(pkg=pkg), defaults
            )
            if 0 != result:
                self._log.warning(f'Failed to install [{pkg}]')

            return 0 == result

    def _install_rustup(self, val: bool, defaults: Mapping[str, Any]) -> bool:
        if not val:
            self._log.error(
                'Why would you even put `install-rustup: false` in there?'
            )
            return False

        link = 'https://sh.rustup.rs'
        cmd = f'curl --proto "=https" --tlsv1.2 -sSf {link} | sh -s -- -y --no-modify-path'
        return self._install(cmd, 'command -v rustup', 'rustup', defaults)

    def _cargo_update(self, val: bool, defaults: Mapping[str, Any]) -> bool:
        if not val:
            self._log.error("Okay, guess I'm not updating.")
            return False

        cargoupdate = self._install(
            'cargo install cargo-update',
            'cargo install-update -V',
            'cargo-update',
            defaults,
        )
        if not cargoupdate:
            return False

        result = self._invoke_shell_command(
            'cargo install-update --all', defaults
        )

        if 0 == result:
            self._log.info('All cargo packages up to date.')
        return 0 == result
