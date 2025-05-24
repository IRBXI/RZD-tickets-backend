{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [ pkgs.sqlite ];
  shellHook = ''
    echo "SQLite $(sqlite3 --version) is available"
    echo "Database files will be created in: $(pwd)"
  '';
}
