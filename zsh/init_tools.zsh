# Helper for caching tool initializations
zsh_cache_init() {
  local name="$1"
  shift
  local cache_file="${XDG_CACHE_HOME}/zsh/init/${name}.zsh"
  local bin_file="$(mise where ${name} 2> /dev/null)/${name}"
  
  if [[ ! -f "$cache_file" || "$bin_file" -nt "$cache_file" ]]; then
    echo "Update an init cache: ${bin_file}"
    mkdir -p "$(dirname "$cache_file")"
    eval "$@" > "$cache_file"
  fi
  source "$cache_file"
}

zsh_cache_init starship starship init zsh
zsh_cache_init fzf fzf --zsh
zsh_cache_init atuin atuin init zsh

# zoxide init make completions
export _ZO_DOCTOR=0
zsh_cache_init zoxide zoxide init zsh --cmd cd

# Generate completions if missing
zsh_generate_completions() {
  local comp_dir="${XDG_CACHE_HOME}/zsh/completions"
  [[ ! -d "$comp_dir" ]] && mkdir -p "$comp_dir"
  
  [[ ! -f "$comp_dir/_mise" ]]     && mise completion zsh > "$comp_dir/_mise"
  [[ ! -f "$comp_dir/_sheldon" ]]  && sheldon completions --shell zsh > "$comp_dir/_sheldon"
  [[ ! -f "$comp_dir/_atuin" ]]    && atuin gen-completions --shell zsh > "$comp_dir/_atuin"
  [[ ! -f "$comp_dir/_starship" ]] && starship completions zsh > "$comp_dir/_starship"
}
zsh_generate_completions
