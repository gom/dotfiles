" <encoding>
set encoding=utf-8
set fileencodings=ucs-bom,iso-2022-jp-3,iso-2022-jp,utf-8,eucjp-ms,euc-jisx0213,euc-jp,sjis,cp932,default,latin
set fileformats=unix,mac,dos
set termencoding=utf-8

" <indent>
"set tabstop=4 "displayed tab width
set expandtab "tab to space
set shiftwidth=2 "space for autoindent
set autoindent

" <status line>
set laststatus=2 "always show status line
set statusline=[%n%{bufnr('$')>1?'/'.bufnr('$'):''}%{winnr('$')>1?':'.winnr().'/'.winnr('$'):''}]%<%f%m%r%h%w%{'['.(&fenc!=''?&fenc:&enc).']['.&ff.']'}%=%l/%L,%c%V%8P

" <basic>
let mapleader = ","
set nobackup
set hidden
set formatoptions+=mM "text format options
set visualbell "noerrorbells
set backspace=indent,eol,start
set whichwrap=b,s,h,l,<,>,[,]
"set wrap "wrap at end of line
set autoread
set scrolloff=5
set hid " enable switch buffer to keep editing current file

set nocompatible "vi compatible
syntax on
filetype indent plugin on

" <display>
set number "show line numbers
set showmatch "show needed parenthness
set ruler "show line number & char number
set notitle "display title
set showcmd "display command at status line
set nolist "show tab and CR/LF
set cursorline

" <search>
set ignorecase " ignore case for search
set wrapscan "when searching, end to begin of the file
set hlsearch " highlight search result
set smartcase "if start with upper case, not ignore case

" <completion>
set wildmenu "set filelist
set wildmode=list:full
set history=1000


" <Tab>
set showtabline=2
nnoremap <Space>t t
nnoremap <Space>T T
nnoremap t <Nop>
nnoremap <silent> tc :<C-u>tabnew<CR>:tabmove<CR>
nnoremap <silent> tk :<C-u>tabclose<CR>
nnoremap <silent> tn :<C-u>tabnext<CR>
nnoremap <silent> tp :<C-u>tabprevious<CR>

" <folding>
nnoremap <expr> h foldlevel(getpos('.')[1])>0 &&
      \(getpos('.')[2]==1 \|\|
      \getline('.')[: getpos('.')[2]-2] =~ "^[\<TAB> ]*$" )?"zch":"h"

" via http://nanabit.net/blog/2007/11/06/vim-wincmd/
" <keybinds>
nnoremap j gj
nnoremap k gk

map! <C-a> <Home>
map! <C-e> <End>
map <silent> <F2> :bp<cr>
map <silent> <F3> :bn<cr>
map <silent> <C-xb> :ls<CR>:buf 

nnoremap <Space>. :<C-u>edit $MYVIMRC<CR>
nnoremap <Space>s. :<C-u>source $MYVIMRC<CR> :<C-u>source $MYGVIMRC<CR>
nnoremap <Space>w :write<CR>
nnoremap <Space>d :bd<CR>
nnoremap <Space>q :q<CR>
nnoremap <C-h> :<C-u>help<Space>
nnoremap <C-h><C-h> :<C-u>help<Space><C-r><C-w><CR>

" yank, paste with os clipboard
" http://relaxedcolumn.blog8.fc2.com/blog-entry-125.html
noremap <Space>y "+y
noremap <Space>p "+p

inoremap <C-d> <Delete>
inoremap <C-f> <Right>
inoremap <C-b> <Left>
inoremap <C-j> <Down>
inoremap <C-k> <Up>

nmap sj <C-W>j<C-w>_
nmap sk <C-W>k<C-w>_
nmap sh <C-w>h<C-w>_
nmap sl <C-w>l<C-w>_

" <emacs keybinds>
nnoremap <C-n> gj
nnoremap <C-p> gk

" <MacVim>
if has('mac')
 source $VIMRUNTIME/delmenu.vim
 set langmenu=ja_jp.utf-8
 source $VIMRUNTIME/menu.vim
endif


" <Plugins>

" <Plugins:neobundle>
set nocompatible
filetype off

if has('vim_starting')
  set runtimepath+=~/.vim/bundle/neobundle.vim/
endif

call neobundle#rc(expand('~/.vim/bundle/'))
NeoBundle 'Shougo/neobundle.vim'
NeoBundle 'Shougo/vimproc'

NeoBundle 'Shougo/unite.vim'
NeoBundle 'h1mesuke/unite-outline'
NeoBundle 'ujihisa/unite-colorscheme'
NeoBundle 'Shougo/neocomplcache'
NeoBundle 'Shougo/neocomplcache-snippets-complete'
NeoBundle 'Shougo/neocomplcache-clang_complete'
NeoBundle 'Shougo/vim-vcs'
NeoBundle 'Shougo/vimfiler'
NeoBundle 'Shougo/vimshell'
NeoBundle 'Shougo/vinarise'
NeoBundle 'thinca/vim-quickrun'
NeoBundle 'thinca/vim-ref'
NeoBundle 'mattn/zencoding-vim'
NeoBundle 'Shougo/echodoc'
NeoBundle 'teramako/jscomplete-vim'

NeoBundle 'gtags.vim'
"NeoBundle 'taglist.vim'
NeoBundle 'Gist.vim'
NeoBundle 'Lokaltog/vim-powerline'

" colorschemes
NeoBundle 'Zenburn'
NeoBundle 'Wombat'

filetype plugin indent on
"
" Brief help
" :NeoBundleList          - list configured bundles
" :NeoBundleInstall(!)    - install(update) bundles
" :NeoBundleClean(!)      - confirm(or auto-approve) removal of unused bundles
 
" Installation check.
if neobundle#exists_not_installed_bundles()
  echomsg 'Not installed bundles : ' .
        \ string(neobundle#get_not_installed_bundle_names())
  echomsg 'Please execute ":NeoBundleInstall" command.'
  "finish
endif

" <Plugins:colors-soralized>
"set background=dark
colorscheme desert
highlight CursorLine cterm=none ctermbg=black

" <Plugins:Gtags>
nnoremap <C-q> <C-w><C-w><C-w>q
map <C-g> :Gtags 
map <C-i> :Gtags -f %<CR>
map <C-j> :GtagsCursor<CR>
"map <C-n> :cn<CR>
"map <C-p> :cp<CR>


" <Plugins:neocomplcache>
" Disable AutoComplPop.
let g:acp_enableAtStartup = 0
" Use neocomplcache.
let g:neocomplcache_enable_at_startup = 1
" Use smartcase.
let g:neocomplcache_enable_smart_case = 1
" Use camel case completion.
let g:neocomplcache_enable_camel_case_completion = 1
" Use underbar completion.
let g:neocomplcache_enable_underbar_completion = 1
" Set minimum syntax keyword length.
let g:neocomplcache_min_syntax_length = 3
let g:neocomplcache_lock_buffer_name_pattern = '\*ku\*'

" Define dictionary.
let g:neocomplcache_dictionary_filetype_lists = {
    \ 'default' : '',
    \ 'vimshell' : $HOME.'/.vimshell_hist',
    \ 'scheme' : $HOME.'/.gosh_completions'
    \ }

" Define keyword.
if !exists('g:neocomplcache_keyword_patterns')
  let g:neocomplcache_keyword_patterns = {}
endif
let g:neocomplcache_keyword_patterns['default'] = '\h\w*'

" Plugin key-mappings.
imap <C-k>     <Plug>(neocomplcache_snippets_expand)
smap <C-k>     <Plug>(neocomplcache_snippets_expand)
inoremap <expr><C-g>     neocomplcache#undo_completion()
inoremap <expr><C-l>     neocomplcache#complete_common_string()

" SuperTab like snippets behavior.
"imap <expr><TAB> neocomplcache#sources#snippets_complete#expandable() ? "\<Plug>(neocomplcache_snippets_expand)" : pumvisible() ? "\<C-n>" : "\<TAB>"

" Recommended key-mappings.
" <CR>: close popup and save indent.
inoremap <expr><CR>  neocomplcache#smart_close_popup() . "\<CR>"
" <TAB>: completion.
inoremap <expr><TAB>  pumvisible() ? "\<C-n>" : "\<TAB>"
" <C-h>, <BS>: close popup and delete backword char.
inoremap <expr><C-h> neocomplcache#smart_close_popup()."\<C-h>"
inoremap <expr><BS> neocomplcache#smart_close_popup()."\<C-h>"
inoremap <expr><C-y>  neocomplcache#close_popup()
inoremap <expr><C-e>  neocomplcache#cancel_popup()

" AutoComplPop like behavior.
"let g:neocomplcache_enable_auto_select = 1

" Shell like behavior(not recommended).
"set completeopt+=longest
"let g:neocomplcache_enable_auto_select = 1
"let g:neocomplcache_disable_auto_complete = 1
"inoremap <expr><TAB>  pumvisible() ? "\<Down>" : "\<TAB>"
"inoremap <expr><CR>  neocomplcache#smart_close_popup() . "\<CR>"

" Enable omni completion.
autocmd FileType css setlocal omnifunc=csscomplete#CompleteCSS
autocmd FileType html,markdown setlocal omnifunc=htmlcomplete#CompleteTags
autocmd FileType javascript setlocal omnifunc=javascriptcomplete#CompleteJS
autocmd FileType python setlocal omnifunc=pythoncomplete#Complete
autocmd FileType xml setlocal omnifunc=xmlcomplete#CompleteTags

" Enable heavy omni completion.
if !exists('g:neocomplcache_omni_patterns')
  let g:neocomplcache_omni_patterns = {}
endif
let g:neocomplcache_omni_patterns.ruby = '[^. *\t]\.\w*\|\h\w*::'
"autocmd FileType ruby setlocal omnifunc=rubycomplete#Complete
let g:neocomplcache_omni_patterns.php = '[^. \t]->\h\w*\|\h\w*::'
let g:neocomplcache_omni_patterns.c = '\%(\.\|->\)\h\w*'
let g:neocomplcache_omni_patterns.cpp = '\h\w*\%(\.\|->\)\h\w*\|\h\w*::'

" <Plugins:vim-ref>
let g:ref_source_webdict_sites = {
      \   'wiki': 'http://ja.wikipedia.org/wiki/%s',
      \   'alc': 'http://eow.alc.co.jp/%s/UTF-8',
      \   'phpnet': 'http://jp.php.net/search.php?pattern=%s&show=quickref',
      \   'ruby': 'http://doc.ruby-lang.org/ja/search/query:%s',
      \ }
let g:ref_source_webdict_sites.default = 'alc'

" <Plugins:unite>
noremap <silent> ub :Unite buffer<CR>
noremap <silent> uf :UniteWithBufferDir -buffer-name=files file<CR>
noremap <silent> ur :Unite -buffer-name=register register<CR>
noremap <silent> um :Unite file_mru<CR>
noremap <silent> ui :Unite buffer file_mru<CR>
nnoremap <silent> ua :<C-u>UniteWithBufferDir -buffer-name=files buffer file_mru bookmark file<CR>

" split window
au FileType unite nnoremap <silent> <buffer> <expr> <C-j> unite#do_action('split')
au FileType unite inoremap <silent> <buffer> <expr> <C-j> unite#do_action('split')
au FileType unite nnoremap <silent> <buffer> <expr> <C-l> unite#do_action('vsplit')
au FileType unite inoremap <silent> <buffer> <expr> <C-l> unite#do_action('vsplit')
" finish with ESC * 2
au FileType unite nnoremap <silent> <buffer> <ESC><ESC> :q<CR>
au FileType unite inoremap <silent> <buffer> <ESC><ESC> <ESC>:q<CR>
au FileType unite nnoremap <silent> <buffer> <expr> <C-k> unite#do_action('delete')
au FileType unite inoremap <silent> <buffer> <expr> <C-k> unite#do_action('delete')

" new tab
nnoremap <silent> tb :<C-u>tabnew<CR>:tabmove<CR>:Unite buffer<CR>
nnoremap <silent> tf :<C-u>tabnew<CR>:tabmove<CR>:UniteWithBufferDir -buffer-name=files file<CR>
nnoremap <silent> tm :<C-u>tabnew<CR>:tabmove<CR>:Unite file_mru<CR>
nnoremap <silent> ti :<C-u>tabnew<CR>:tabmove<CR>:Unite buffer file_mru<CR>
nnoremap <silent> ta :<C-u>tabnew<CR>:tabmove<CR>:UniteWithBufferDir -buffer-name=files buffer file_mru bookmark file<CR>

