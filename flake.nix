{
  description = "Blender Krita Link Plugin & C++ UV-Select Extension";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Krita unwrapped with uv-select injected into the source tree
        kritaUnwrappedWithPlugin = pkgs.krita-unwrapped.overrideAttrs (oldAttrs: {
          postPatch = (oldAttrs.postPatch or "") + ''
            # Copy cppPart/uv-select into Krita's plugins directory
            cp -r ${./cppPart/uv-select} plugins/uv-select
            echo "add_subdirectory(uv-select)" >> plugins/CMakeLists.txt
          '';
        });

        # Wrapped Krita with the plugin for running locally on NixOS
        kritaWithPlugin = pkgs.krita.override {
          krita-unwrapped = kritaUnwrappedWithPlugin;
        };

        # Portable standalone plugin package (sanitized RPATH for distribution)
        portablePlugin = pkgs.stdenv.mkDerivation {
          pname = "kritashapesselection-portable";
          version = "1.0";
          dontUnpack = true;

          nativeBuildInputs = [ pkgs.patchelf pkgs.zip ];

          installPhase = ''
            mkdir -p $out/lib/kritaplugins $out/share/krita/actions $out/dist
            
            SO_FILE=$(find ${kritaUnwrappedWithPlugin} -name "kritashapesselection.so" | head -n 1)
            
            if [ -n "$SO_FILE" ] && [ -f "$SO_FILE" ]; then
              cp "$SO_FILE" $out/lib/kritaplugins/kritashapesselection.so
              cp ${./cppPart/uv-select/kritashapesselection.action} $out/share/krita/actions/
              
              # Sanitize RPATH so it has no hardcoded /nix/store references
              chmod +w $out/lib/kritaplugins/kritashapesselection.so
              patchelf --set-rpath '$ORIGIN/..:$ORIGIN' $out/lib/kritaplugins/kritashapesselection.so
              
              # Create release zip archive
              cd $out && zip -r $out/dist/uv-select-linux.zip lib/ share/
            else
              echo "Error: kritashapesselection.so not found in ${kritaUnwrappedWithPlugin}"
              exit 1
            fi
          '';
        };
      in
      {
        packages = {
          default = kritaWithPlugin;
          krita = kritaWithPlugin;
          portable-plugin = portablePlugin;
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ pkgs.krita-unwrapped ];
          packages = with pkgs; [
            cmake
            ninja
            patchelf
            zip
          ];
        };

        apps = {
          default = flake-utils.lib.mkApp { drv = kritaWithPlugin; };
        };
      }
    );
}
