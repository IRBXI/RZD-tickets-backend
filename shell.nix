{ pkgs ? import <nixpkgs> {} }:

let
  python_pack = pkgs.python3.withPackages (ps: [
    ps.pip
  ]);

  python = pkgs.python;


  lib-path = with pkgs; lib.makeLibraryPath [
    libffi
    openssl
    stdenv.cc.cc
  ];
in
pkgs.mkShell {
  packages = [ python_pack ];

  shellHook = ''
    SOURCE_DATE_EPOCH=$(date +%s)
    export "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${lib-path}"
    VENV=.venv

    if test ! -d $VENV; then
      python3.12 -m venv $VENV
    fi

    source ./$VENV/bin/activate
    export PYTHONPATH=$(pwd)/$VENV/${python.sitePackages}/:$PYTHONPATH
    pip install -r requirements.txt
  '';

  postShellHook = ''
    ln -sf ${python.sitePackages}/* ./.venv/lib/python3.12/site-packages
  '';
}
