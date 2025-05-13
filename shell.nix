{ pkgs ? import <nixpkgs> {} }:

let
  python_pack = pkgs.python3.withPackages (ps: [
    ps.pip
    ps.fastapi
    ps.pydantic
    ps.sqlalchemy
  ]);
in
pkgs.mkShell {
  packages = [ python_pack ];

  shellHook = ''
    if [ ! -d "venv" ]; then
      python -m venv venv
    fi
      source venv/bin/activate

    export PYTHONPATH="${pkgs.python3.sitePackages}:$PYTHONPATH"
  '';
}
