{ pkgs ? import <nixpkgs> {} }:

let
  python_pack = pkgs.python3.withPackages (ps: [
    ps.fastapi
    ps.pydantic
    ps.sqlalchemy
  ]);
in
pkgs.mkShell {
  packages = [ python_pack ];

  shellHook = ''
    export PYTHONPATH="${pkgs.python3.sitePackages}:$PYTHONPATH"
  '';
}
