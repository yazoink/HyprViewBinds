# HyprViewBinds
A simple GTK3 GUI for quickly viewing all of your current Hyprland keybinds.
![20241124_00:52:29_screenshot](https://github.com/user-attachments/assets/b7b22fa2-42d9-4431-896f-cb13690bb178)

## Dependencies
- `GTK3`
- `gobject-introspection`
- `pygobject3`

## Installation
### Most distros
- Copy `hyprviewbinds.py` to `/usr/bin`
- Copy `hyprviewbinds.desktop` to `/usr/share/applications`

### NixOS (home-manager)
I don't know the proper way to do this but this is how I installed it

#### Module Directory Structure
```
hyprviewbinds
├── default.nix
├── hyprviewbinds
│   ├── hyprviewbinds.py
│   └── setup.py
├── hyprviewbinds.desktop
└── hyprviewbinds.nix
```

#### default.nix
```nix
{ pkgs, ... }:
let
  hyprviewbinds = pkgs.callPackage ./hyprviewbinds.nix {};
in
{
  home.file.".local/share/applications/hyprviewbinds.desktop".source = ./hyprviewbinds.desktop;
  home.packages = [
    hyprviewbinds
  ];
}
```

#### hyprviewbinds.nix
```nix
{ pkgs, ... }:
pkgs.python312Packages.buildPythonApplication rec {
  pname = "hyprviewbinds";
  version = "1.0";

  src = ./hyprviewbinds;
    nativeBuildInputs = [
    pkgs.gobject-introspection
    pkgs.wrapGAppsHook
  ];

  propagatedBuildInputs = with pkgs.python312Packages; [
    pygobject3
    sh
  ] ++ [
    pkgs.gtk3
  ];

  makeWrapperArgs = [
    "--prefix GI_TYPELIB_PATH : ${pkgs.gtk3}/lib/girepository-1.0"
    "--prefix LD_LIBRARY_PATH : ${pkgs.gtk3}/lib"
  ];

  doCheck = false;
}

```
