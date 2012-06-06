" <encoding>
set encoding=utf-8
set fileencodings=ucs-bom,iso-2022-jp-3,iso-2022-jp,utf-8,eucjp-ms,euc-jisx0213,euc-jp,sjis,cp932,default,latin
set fileformats=unix,mac,dos

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
filetype on
filetype indent on
filetype plugin on

" <display>
set number "show line numbers
set showmatch "show needed parenthness
set ruler "show line number & char number
set notitle "display title
set showcmd "display command at status line
set nolist "show tab and CR/LF

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



" <Plugins>
" <Fuf>
nnoremap <Space>f f
nnoremap <Space>F F
nnoremap f <Nop>
nnoremap <silent> fb :<C-u>FufBuffer!<CR>
nnoremap <silent> ff :<C-u>FufFile! <C-r>=expand('%:~:.')[:-1-len(expand('%:~:.:t'))]<CR><CR>
nnoremap <silent> fm :<C-u>FufMruFile!<CR>
nnoremap <silent> tb :<C-u>tabnew<CR>:tabmove<CR>:FufBuffer!<CR>
nnoremap <silent> tf :<C-u>tabnew<CR>:tabmove<CR>:FufFile! <C-r>=expand('#:~:.')[:-1-len(expand('#:~:.:t'))]<CR><CR>
nnoremap <silent> tm :<C-u>tabnew<CR>:tabmove<CR>:FufMruFile!<CR>
let g:fuf_patternSeparator = ' '
let g:fuf_modesDisable = ['mrucmd']
let g:fuf_mrufile_exclude = '\v\.DS_Store|\.git|\.swp|\.svn'
let g:fuf_mrufile_maxItem = 100
let g:fuf_enumeratingLimit = 20
let g:fuf_file_exclude = '\v\.DS_Store|\.git|\.swp|\.svn'

" <autocomplpop>
" {{{ Autocompletion using the TAB key
" " This function determines, wether we are on the start of the line text
" (then tab indents) or
" " if we want to try autocompletion
function! InsertTabWrapper()
	let col = col('.') - 1
	if !col || getline('.')[col - 1] !~ '\k'
		return "\<TAB>"
	else
		if pumvisible()
			return "\<C-N>"
		else
			return "\<C-N>\<C-P>"
		end
	endif
endfunction
" Remap the tab key to select action with InsertTabWrapper
inoremap <tab> <c-r>=InsertTabWrapper()<cr>
" }}} Autocompletion using the TAB key
inoremap <expr> <CR> pumvisible() ? "\<C-Y>\<CR>" : "\<CR>"

" <MacVim>
if has('mac')
 source $VIMRUNTIME/delmenu.vim
 set langmenu=ja_jp.utf-8
 source $VIMRUNTIME/menu.vim
endif

