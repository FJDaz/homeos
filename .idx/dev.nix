{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.11"; # Updated for better compatibility

  # Use packages from nixpkgs.
  packages = [
    pkgs.python312 # Python 3.12 as required in requirements.txt
    pkgs.python312Packages.pip
    pkgs.python312Packages.virtualenv
    pkgs.playwright-driver
    pkgs.lsof
    pkgs.nodejs-20
  ];

  # Sets environment variables in the workspace
  env = {
    # Playwright driver path for Python
    PLAYWRIGHT_BROWSERS_PATH = "/home/user/.cache/ms-playwright";
  };

  # Search for relevant idx-defined options in the documentation.
  idx = {
    # Search for extensions you want to install
    extensions = [
      "ms-python.python"
      "ms-python.vscode-pylance"
      "humao.rest-client"
    ];

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Create virtual environment and install requirements
        install-deps = ''
          python -m venv venv
          source venv/bin/activate
          # Use requirements_updated.txt if it exists, otherwise requirements.txt
          if [ -f "requirements_updated.txt" ]; then
            pip install -r requirements_updated.txt
          else
            pip install -r requirements.txt
          fi
          # Install Playwright browser
          python -m playwright install chromium
        '';
      };
    };

    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          # Serve the API and preview it on port 8000
          command = ["./start_api.sh"];
          manager = "web";
        };
      };
    };
  };
}
