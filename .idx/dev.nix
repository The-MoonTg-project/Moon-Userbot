{ pkgs, ... }: {

  # Which nixpkgs channel to use.
  channel = "stable-23.11"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.docker
    pkgs.python3
    pkgs.ffmpeg
  ];

  # Sets environment variables in the workspace
  env = {
    SOME_ENV_VAR = "hello";
  };

  # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
  idx.extensions = [
    "ms-azuretools.vscode-docker"
    "ms-python.debugpy"
    "ms-python.python"
    "esbenp.prettier-vscode"
    "ms-python.pylint"
  ];

  services.docker.enable = true;

  # Enable previews and customize configuration
  idx.previews = {
    enable = false;
    previews = [
      {
        command = [
          "npm"
          "run"
          "start"
          "--"
          "--port"
          "$PORT"
          "--host"
          "0.0.0.0"
          "--disable-host-check"
        ];
        manager = "web";
        id = "web";
      }
    ];
  };
}