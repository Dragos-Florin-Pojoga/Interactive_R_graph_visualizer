{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.R
    pkgs.rPackages.shiny
  ];

  shellHook = ''
  '';
}
