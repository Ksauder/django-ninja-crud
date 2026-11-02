{ pkgs, config, ... }:
{
  languages.python = {
    enable = true;
    package = pkgs.python311;
    venv.enable = true;
    uv = {
      enable = true;
      sync.enable = true;
    };
  };

  # Keep .pre-commit-config.yaml intact for contributors not using devenv.
  git-hooks.configPath = ".pre-commit-config.devenv.yaml";

  git-hooks.hooks = {
    check-python.enable = true;
    check-merge-conflicts.enable = true;
    check-toml.enable = true;
    check-yaml.enable = true;
    end-of-file-fixer.enable = true;
    trim-trailing-whitespace.enable = true;

    ruff.enable = true;
    ruff-format.enable = true;

    # Use the venv's mypy so django-stubs and project dependencies resolve.
    mypy = {
      enable = true;
      files = "^src/ninja_crud/";
      # Parallel mypy runs corrupt the shared .mypy_cache.
      require_serial = true;
      settings.binPath = "${config.env.DEVENV_STATE}/venv/bin/mypy";
      args = [
        "--ignore-missing-imports"
        "--strict"
      ];
    };
  };

  scripts.run-tests.exec = ''
    coverage run -m django test --settings=tests.test_settings
    coverage report
  '';

  enterTest = ''
    run-tests
  '';

  tasks."dev:test" = {
    exec = ''uv run -m django test --settings=tests.test_settings'';
    before = [ "devenv:enterTest" ];
  };
}
