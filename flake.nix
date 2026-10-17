{
  description = "qutebrowser with tmux/vim-style split panes (fork)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        qutebrowser-panes = pkgs.qutebrowser.overrideAttrs (old: {
          pname = "qutebrowser-panes";
          version = "3.7.0-panes-dev";
          src = ./.;
          doCheck = false;
          doInstallCheck = false;
        });
      in {
        packages = {
          default = qutebrowser-panes;
          qutebrowser-panes = qutebrowser-panes;
        };

        apps.default = {
          type = "app";
          program = "${qutebrowser-panes}/bin/qutebrowser";
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ qutebrowser-panes ];
          packages = [ pkgs.git ];
          shellHook = ''
            echo "== qutebrowser-panes dev shell =="
            echo "Build+run:  nix run .# -- --basedir ./dev-profile"
            echo "Rebuild:    nix build .# --print-out-paths"
            echo "Profile is isolated at ./dev-profile — safe to delete anytime."
          '';
        };
      });
}
