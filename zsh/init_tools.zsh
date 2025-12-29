eval "$(starship init zsh)"
eval "$(fzf --zsh)"
eval "$(atuin init zsh)"

# zoxide init make completions
export _ZO_DOCTOR=0
eval "$(zoxide init zsh --cmd cd)"

# Generate completions if missing
zsh_generate_completions() {
  local comp_dir="${XDG_CACHE_HOME}/zsh/completions"
  [[ ! -f "$comp_dir/_mise" ]]     && mise completion zsh > "$comp_dir/_mise"
  [[ ! -f "$comp_dir/_sheldon" ]]  && sheldon completions --shell zsh > "$comp_dir/_sheldon"
  [[ ! -f "$comp_dir/_atuin" ]]    && atuin gen-completions --shell zsh > "$comp_dir/_atuin"
  [[ ! -f "$comp_dir/_starship" ]] && starship completions zsh > "$comp_dir/_starship"
}
zsh_generate_completions
