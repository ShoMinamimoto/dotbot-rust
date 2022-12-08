# Dotbot-rust

This is a plugin for [dotbot](https://github.com/anishathalye/dotbot) that adds `cargo`,
`cargo-update`, `install-rustup` directives. It's a quick and dirty hack of
wren's excellent [dotbot-brew](https://github.com/wren/dotbot-brew).

## Features

Similar to [dotbot-brew](https://github.com/wren/dotbot-brew), this plugin lets you
install cargo binaries after a quick check for already installed packages. The
`cargo-update` directive installs the
[install-update subcommand for cargo](https://github.com/nabijaczleweli/cargo-update)
and lets you quickly update only outdated packages.

## Installation

Add it as submodule of your dotfiles repository (per the [dotbot plugin installation
guidelines](https://github.com/anishathalye/dotbot#plugins)).

```shell
git submodule add https://github.com/shominamimoto/dotbot-rust.git
```

Modify your `install` script, so it automatically enables `rust` plugin.

```shell
"${BASEDIR}/${DOTBOT_DIR}/${DOTBOT_BIN}" -d "${BASEDIR}" --plugin-dir dotbot-rust -c "${CONFIG}" "${@}"
```

## Usage

In your `install.conf.yaml` use the `cargo` directive to list all packages to be installed
using `cargo`.

Also, if you plan on having multiple directives, you should consider using defaults to
set your preferred settings.

For example, your config might look something like:

```yaml
# Sets default config for certain directives
- defaults:
    - cargo-update:
        - stdout: False,
    - cargo:
        - stderr: True,
        - stdout: True,

# Installs rustup (and cargo) if missing
- install-rustup: true

# Updates any outdated crates
- cargo-update: true

# Installs certain cargo binaries
- cargo:
    - ripgrep
    - bottom
    - fd-find
```
