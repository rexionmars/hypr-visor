{
  description = "Hypr Camera Application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = import ./shell.nix { inherit pkgs; };
        
        # Adicionar um pacote construível
        packages.default = pkgs.python3Packages.buildPythonPackage {
          pname = "hypr-camera";
          version = "0.1.0";
          src = ./.;
          propagatedBuildInputs = with pkgs.python3Packages; [
            numpy
            opencv4
            pyqt5
          ];
        };

        # Adicionar um app executável
        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/hypr-camera";
        };
      }
    );
}