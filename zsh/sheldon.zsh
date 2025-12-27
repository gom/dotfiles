# This script is responsible for setting up Sheldon, the plugin manager.
# It ensures that Sheldon is installed, and that plugins are installed and sourced.

# Install Sheldon if it's not already installed.
if ! [ -x "$(command -v sheldon)" ]; then
    echo "Sheldon not found. Installing..."
    # Download and install Sheldon to ~/.local/bin
    curl --proto '=https' -fLsS https://rossmacarthur.github.io/install/crate.sh \
        | bash -s -- --repo rossmacarthur/sheldon --to ~/.local/bin

    # After installing Sheldon for the first time, lock the plugins.
    # This will download and install all the plugins defined in plugins.toml.
    if [ -x "$(command -v sheldon)" ]; then
        echo "Running 'sheldon lock' to install plugins..."
        sheldon lock
    else
        echo "Sheldon installation failed." >&2
    fi
fi

# Source Sheldon plugins
if (( $+commands[sheldon] )); then
  eval "$(sheldon source)"
  rehash
fi
