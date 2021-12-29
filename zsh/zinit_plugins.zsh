zinit light-mode for \
    zdharma-continuum/zinit-annex-bin-gem-node

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
    mollifier/anyframe \
    @asdf-vm/asdf

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
zinit as"null" wait"1" lucid from"gh-r" light-mode for \
    sbin"fzf" junegunn/fzf-bin \
    mv"jq-* -> jq" sbin stedolan/jq \
    sbin"**/exa" ogham/exa \
    sbin"**/fd" @sharkdp/fd \
    sbin"**/bat" @sharkdp/bat \
    sbin"**/rg" BurntSushi/ripgrep \
    bpick"*lnx*" sbin"**/procs" dalance/procs \
    sbin"**/delta" dandavison/delta \
    bpick"*linux-gnu*" sbin"**/tokei" XAMPPRocky/tokei

zinit from"gh-r" as"program" mv"direnv* -> direnv" \
    atclone'./direnv hook zsh > zhook.zsh' atpull'%atclone' \
    pick"direnv" src="zhook.zsh" for \
        direnv/direnv

# Theme
zinit depth"1" lucid nocd for romkatv/powerlevel10k
#zinit pick"async.zsh" src"pure.zsh" light-mode for sindresorhus/pure

zinit snippet $_ZDOTDIR/functions/ssh-start.zsh
