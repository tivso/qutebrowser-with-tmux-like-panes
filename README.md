# qutebrowser-panes

Fork of [qutebrowser](https://github.com/qutebrowser/qutebrowser) adding
tmux/vim-style split panes within tabs. Multiple WebViews live inside a single
tab, share the same profile (cookies, logins, config), and are navigated with
a backtick (`` ` ``) prefix.

Based on upstream v3.7.0.

## Download / install

### With Nix (any OS — Linux, macOS, NixOS)

If you already have Nix (with flakes enabled):

```
git clone https://github.com/tivso/qutebrowser-with-tmux-like-panes ~/qutebrowser-panes
cd ~/qutebrowser-panes
nix profile install .#
```

That puts the fork's `qutebrowser` in `~/.nix-profile/bin`, shadowing the
system install. Launch with `qutebrowser` — your real profile is used
(bookmarks, cookies, config.py).

Upgrade after a `git pull`: `nix profile upgrade qutebrowser-panes`
Uninstall: `nix profile remove qutebrowser-panes`

Don't have Nix? Install from https://nixos.org/download then enable flakes
by adding `experimental-features = nix-command flakes` to
`~/.config/nix/nix.conf`.

Try without installing:
```
nix run github:tivso/qutebrowser-with-tmux-like-panes -- --temp-basedir
```

### From source without Nix (Linux / macOS / Windows)

You need the same runtime deps upstream qutebrowser needs: Python 3.9+,
PyQt6, PyQt6-WebEngine, plus a handful of Python packages. See upstream's
[INSTALL.asciidoc](https://github.com/qutebrowser/qutebrowser/blob/main/doc/install.asciidoc)
for the per-OS instructions.

Then, instead of cloning upstream, clone this fork and run it directly:

```
git clone https://github.com/tivso/qutebrowser-with-tmux-like-panes ~/qutebrowser-panes
cd ~/qutebrowser-panes
pip install -r requirements.txt
python3 qutebrowser.py
```

(Use a virtualenv if you don't want to install globally.)

On Debian/Ubuntu the quick path is:
```
sudo apt install python3-pyqt6 python3-pyqt6.qtwebengine python3-jinja2 \
                 python3-yaml python3-pygments python3-colorama
git clone https://github.com/tivso/qutebrowser-with-tmux-like-panes
cd qutebrowser-with-tmux-like-panes
python3 qutebrowser.py
```

On Arch:
```
sudo pacman -S python-pyqt6 python-pyqt6-webengine python-jinja \
               python-yaml python-pygments python-colorama python-adblock
```

On macOS with Homebrew:
```
brew install python-pyqt6 pyqt-builder
pip3 install adblock jinja2 pyyaml pygments colorama
```

## Usage

Open qutebrowser normally. In any tab, you now have panes.

1. Open a page in a tab: `o example.com` (same as upstream)
2. Split the current tab so a second page is on the right: `` `v `` (or `:vsplit [url]`)
3. Split below: `` `s `` (or `:split [url]`)
4. Move focus between panes: `` `h `` / `` `j `` / `` `k `` / `` `l ``
   — or just click the pane you want
5. Close the focused pane: `` `c `` (or `:pane-close`). If it was the only
   pane in the tab, the tab closes.

Each browser tab keeps its own pane layout. Panes share the profile, so you
stay logged into sites across all of them.

## Commands

| Command         | Does                                                        |
|-----------------|-------------------------------------------------------------|
| `:vsplit [url]` | New pane to the right                                       |
| `:split  [url]` | New pane below                                              |
| `:pane-close`   | Close focused pane; closes the tab if it was the last pane  |
| `:pane-left`    | Focus pane to the left                                      |
| `:pane-right`   | Focus pane to the right                                     |
| `:pane-up`      | Focus pane above                                            |
| `:pane-down`    | Focus pane below                                            |

If `url` is omitted, the new pane loads your configured `url.default_page`.

## Default bindings (normal mode)

Backtick (`` ` ``) is the pane prefix. It replaces the upstream mark-set
binding — rebind that in `config.py` if you want marks back.

```
`h   pane-left        `v   vsplit
`j   pane-down        `s   split
`k   pane-up          `c   pane-close
`l   pane-right
```

The status bar and URL bar follow whichever pane you click into.

## Known limitations

- **Hints (`f`) target the wrong pane after focus moves.** The hint system
  caches the "current tab" when hint mode starts; in a multi-pane tab it may
  overlay hints on a pane you didn't focus. Workaround: click back into the
  pane you want, then press `f`.
- **Splits don't nest.** A `:split` after a `:vsplit` reorients the whole
  top-level splitter — all panes end up on the new axis.
- **Scroll %, caret selection, and search match** in the status bar still
  track the pane that was active when the tab was first created, not the
  currently focused one. URL / title / icon update correctly.
- `:pane-close` picks the next pane to focus by position (right/below first,
  else left/above). No MRU history.
- Pane layouts aren't saved in sessions.
