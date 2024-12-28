{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python311;
  pythonPackages = python.pkgs;

  ultralyticsOverride = pythonPackages.buildPythonPackage rec {
    pname = "ultralytics";
    version = "8.3.55";
    format = "pyproject";

    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-BN3OteJOfiLpfH33UJVp8retnWnAzo0xUgLAlmJjv4A=";
    };

    nativeBuildInputs = with pythonPackages; [
      setuptools
      pip
      wheel
      hatchling
      hatch-requirements-txt
      hatch-vcs
    ];

    propagatedBuildInputs = with pythonPackages; [
      numpy
      opencv4
      pillow
      pyyaml
      requests
      scipy
      torch
      torchvision
      tqdm
      matplotlib
      pandas
      seaborn
      setuptools
      packaging
      psutil
      py-cpuinfo
    ];

    doCheck = false;
    SETUPTOOLS_SCM_PRETEND_VERSION = version;
    pythonRemoveDeps = [
      "opencv-python"
      "ultralytics-thop"
    ];
    dontCheckRuntimeDeps = true;
    PYTHONPATH = "";
    ULTRALYTICS_CONFIG_SKIP = "1";
    pipInstallFlags = ["--no-deps"];
  };
  
  pythonWithPackages = python.withPackages (ps: with ps; [
    numpy
    pillow
    matplotlib
    pyyaml
    requests
    scipy
    tqdm
    pygobject3
    pycairo
    typing-extensions
    setuptools
    pip
    torch
    torchvision
    opencv4
    pandas
    seaborn
    ultralyticsOverride
  ]);

in
pkgs.mkShell {
  buildInputs = with pkgs; [
    pythonWithPackages
    gtk3
    gtk-layer-shell
    gobject-introspection
    glib
    librsvg
    pkg-config
    cairo
    pango
    gdk-pixbuf
    atk
    gsettings-desktop-schemas
    libGL
    libGLU
    stdenv.cc.cc.lib
    zlib
    harfbuzz
    shared-mime-info
    wayland
    wayland-protocols
    libxkbcommon
  ];

  nativeBuildInputs = with pkgs; [
    pkg-config
    gobject-introspection.dev
    harfbuzz.dev
    wrapGAppsHook
    wayland-scanner
  ];

  shellHook = ''
    # Wayland and GTK environment setup
    export XDG_SESSION_TYPE="wayland"
    export GDK_BACKEND="wayland"
    export NIXOS_OZONE_WL="1"
    export MOZ_ENABLE_WAYLAND="1"
    export QT_QPA_PLATFORM="wayland"
    export SDL_VIDEODRIVER="wayland"
    export _JAVA_AWT_WM_NONREPARENTING="1"
    export XDG_CURRENT_DESKTOP="Hyprland"
    export XDG_SESSION_DESKTOP="Hyprland"
    
    # GObject introspection setup
    export GI_TYPELIB_PATH="${pkgs.lib.concatStringsSep ":" [
      "${pkgs.gobject-introspection}/lib/girepository-1.0"
      "${pkgs.glib.out}/lib/girepository-1.0"
      "${pkgs.gtk3}/lib/girepository-1.0"
      "${pkgs.pango.out}/lib/girepository-1.0"
      "${pkgs.gdk-pixbuf}/lib/girepository-1.0"
      "${pkgs.atk}/lib/girepository-1.0"
      "${pkgs.harfbuzz}/lib/girepository-1.0"
    ]}"

    # Library paths
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath ([
      pkgs.gtk3
      pkgs.glib.out
      pkgs.pango.out
      pkgs.cairo
      pkgs.gdk-pixbuf
      pkgs.atk
      pkgs.libGL
      pkgs.libGLU
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.harfbuzz
      pkgs.wayland
      pkgs.libxkbcommon
      pythonWithPackages
    ])}"

    # XDG paths
    export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}:${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:${pkgs.shared-mime-info}/share:$XDG_DATA_DIRS"

    # Development paths
    export PKG_CONFIG_PATH="${pkgs.lib.makeSearchPath "lib/pkgconfig" [
      pkgs.glib.dev
      pkgs.gtk3.dev
      pkgs.pango.dev
      pkgs.cairo.dev
      pkgs.gdk-pixbuf.dev
      pkgs.atk.dev
      pkgs.harfbuzz.dev
      pkgs.wayland.dev
    ]}"

    # Skip ultralytics version check
    export ULTRALYTICS_CONFIG_SKIP=1

    echo "Environment initialized with Wayland support"
    
    # Verify the environment
    python -c "
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
print('GTK Version:', Gtk._version)
try:
    display = Gtk.gdk.Display.get_default()
    print('Display:', display.get_name() if display else 'No display')
except:
    print('Display: Could not get display information')
"
  '';

  inherit (pkgs) stdenv;
}