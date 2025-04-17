zinit light-mode for \
    zdharma-continuum/zinit-annex-bin-gem-node \
    zdharma-continuum/zinit-annex-binary-symlink

zinit wait"0" lucid light-mode for \
    atload"_zsh_autosuggest_start" \
        zsh-users/zsh-autosuggestions \
    zsh-users/zsh-history-substring-search \
    atinit"ZINIT[COMPINIT_OPTS]=-C; zicompinit; zicdreplay" \
        zdharma-continuum/fast-syntax-highlighting \
    atpull'zinit creinstall -q .' blockf \
        zsh-users/zsh-completions \
    zdharma-continuum/history-search-multi-word \
    chrissicool/zsh-256color \
    reegnz/jq-zsh-plugin \
    mollifier/cd-gitroot \
    mollifier/anyframe

# Extending Git
# https://github.com/zdharma-continuum/zinit#customizing-paths
zinit as"null" wait"1" lucid light-mode for \
    sbin    Fakerr/git-recall \
    sbin    cloneopts paulirish/git-open \
    sbin    paulirish/git-recent \
    sbin    davidosomething/git-my \
    sbin atload"export _MENU_THEME=legacy" \
            arzzen/git-quick-stats \
    sbin    iwata/git-now \
    make"PREFIX=$ZPFX install" \
            tj/git-extras \
    sbin"git-url;git-guclone" make"GITURL_NO_CGITURL=1" \
            zdharma-continuum/git-url

# Tools
zinit wait"1" lucid from"gh-r" light-mode for \
    sbin"fzf" junegunn/fzf-bin \
    sbin"* -> jq" nocompile @jqlang/jq \
    sbin"**/rg" BurntSushi/ripgrep \
    sbin"**/delta" dandavison/delta \
    sbin"**/procs -> procs" dalance/procs \
    atclone"cp -vf completions/exa.zsh _exa" sbin"**/exa -> exa" ogham/exa \
    sbin"**/tokei -> tokei" XAMPPRocky/tokei \
    lbin"!" id-as null @sharkdp/fd \
    lbin"!" id-as null @sharkdp/bat \
    lbin"!" id-as null @bootandy/dust \
    sbin"**/asdf" @asdf-vm/asdf

zinit light-mode from"gh-r" as"program" for \
      mv"direnv* -> direnv" \
      atclone'./direnv hook zsh > zhook.zsh' \
      src"zhook.zsh" \
    direnv/direnv

# Theme
zinit depth"1" lucid nocd for romkatv/powerlevel10k
#zinit pick"async.zsh" src"pure.zsh" light-mode for sindresorhus/pure

zinit snippet $_ZDOTDIR/functions/ssh-start.zsh
