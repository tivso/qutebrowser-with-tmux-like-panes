# qutebrowser-panes

Fork of [qutebrowser](https://github.com/qutebrowser/qutebrowser) adding
tmux/vim-style split panes within tabs. Multiple WebViews live inside a single
tab, share the same profile (cookies, logins, config), and are navigated with
a backtick (`` ` ``) prefix.

Based on upstream v3.7.0.

## Commands

| Command        | Does                                                   |
|----------------|--------------------------------------------------------|
| `:vsplit [url]`| Open a new pane to the right                           |
| `:split  [url]`| Open a new pane below                                  |
| `:pane-close`  | Close the focused pane (closes the tab if it's the last pane) |
| `:pane-left`   | Focus the pane to the left                             |
| `:pane-right`  | Focus the pane to the right                            |
| `:pane-up`     | Focus the pane above                                   |
| `:pane-down`   | Focus the pane below                                   |

If `url` is omitted, the new pane loads your configured `url.default_page`.

## Default bindings (normal mode)

Backtick (`` ` ``) is the pane prefix (overrides the upstream mark-set
binding; rebind in `config.py` if you want marks back).

```
`h   pane-left        `v   vsplit
`j   pane-down        `s   split
`k   pane-up          `c   pane-close
`l   pane-right
```

The status bar and URL bar follow whichever pane you click into.

## Install (NixOS, flakes)

```
git clone https://github.com/tivso/qutebrowser-with-tmux-like-panes ~/qutebrowser-panes
cd ~/qutebrowser-panes
nix profile install .#
```

This puts the fork's `qutebrowser` in `~/.nix-profile/bin`, shadowing the
system install. Launch with `qutebrowser` — your real profile is used.

Upgrade after pulling changes:

```
nix profile upgrade qutebrowser-panes
```

Uninstall:

```
nix profile remove qutebrowser-panes
```

## Try without installing

```
nix run github:tivso/qutebrowser-with-tmux-like-panes -- --temp-basedir
```

## Known limitations

- Splits don't nest yet — a `:split` after a `:vsplit` reorients the whole
  top-level splitter. All panes end up on the new axis.
- Sub-API signals (scroll %, caret selection, search match) still point at
  the original pane after focus moves. URL / title / icon update correctly.
- `:pane-close` picks the next pane to focus by position (right/below, falling
  back to left/above). No MRU history.
- No session-restore support for pane layouts.
