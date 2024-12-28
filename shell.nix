{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.opencv4
    python3Packages.numpy
    python3Packages.pyqt5
    gtk3
    gtk3-x11
    glib
    pkg-config
    gst_all_1.gstreamer
    gst_all_1.gst-plugins-base
    gst_all_1.gst-plugins-good
    gst_all_1.gst-plugins-bad
    libGL
    libGLU
    xorg.libX11
    xorg.libXext
    xorg.libXrender
    xorg.libXi
    xorg.libXfixes
    qt5.qtbase
    qt5.qtwayland
    wayland
  ];

  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
      pkgs.gtk3
      pkgs.glib
      pkgs.gst_all_1.gstreamer
      pkgs.gst_all_1.gst-plugins-base
      pkgs.libGL
      pkgs.qt5.qtbase
      pkgs.qt5.qtwayland
    ]}:$LD_LIBRARY_PATH
    export QT_QPA_PLATFORM=xcb  # Mudando para xcb ao invés de wayland
    export XDG_RUNTIME_DIR=/run/user/$(id -u)
    export QT_PLUGIN_PATH=${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins
    export QT_PLUGIN_PATH=${pkgs.qt5.qtbase}/lib/qt-${pkgs.qt5.qtbase.version}/plugins:$QT_PLUGIN_PATH
  '';
}