# Init sheldon
if (( $+commands[sheldon] )); then
  eval "$(sheldon source)"
  rehash
fi
