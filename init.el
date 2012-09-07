;;-*- coding: utf-8 -*-
;; User Info
;; set Load-Path
(setq site-lisp-root "~/.emacs.d/elisp")
(add-to-list 'load-path site-lisp-root)
(defun add-to-load-path (added-path)
  (add-to-list 'load-path (concat site-lisp-root "/" added-path)))

(add-to-load-path "init")
(add-to-load-path "anything")
(add-to-load-path "ruby")

;; set environment for Japanese
(set-language-environment "Japanese")



(if (eq (getenv "LANG") "ja_JP.eucJP")
    (require 'mywork)
  (progn
    (prefer-coding-system 'utf-8-unix)
    (set-terminal-coding-system 'utf-8-unix)
    (set-keyboard-coding-system 'utf-8-unix)))

; set language environment
(defun setlang (type)
  "Set Language Environment"
  (interactive "MLang type: ")
  (let ((langtype (cond ((string= type "utf-8") 'utf-8-unix)
			((string= type "euc")  'euc-jp-unix))))
        (prefer-coding-system langtype)
        (set-terminal-coding-system langtype)
        (set-keyboard-coding-system 'utf-8-unix)))

;; set env path
(setq mypath '("/opt/local/bin"
                "/opt/local/sbin"
                "/usr/local/bin"
                "~/bin"))
(setq exec-path (append exec-path mypath))
(setenv "PATH" (mapconcat (lambda(p)p) 
                          (cons (getenv "PATH") mypath)
                          ":"))

;; No-Startup Message
(setq inhibit-startup-message t)

;; Create Backup Directory
(setq make-backup-files t)
(setq backup-directory-alist
      (cons (cons "\\.*$" (expand-file-name "~/.backup"))
            backup-directory-alist))

;; Add Key-bind
(global-set-key "\C-h" 'backward-delete-char)
(global-set-key "\C-x\C-g" 'magit-status)

;; Add no killing copy Key-bind
(defun copy-line (&optional arg)
  (interactive "P")
  (toggle-read-only 1)
  (kill-line arg)
  (toggle-read-only 0))
(setq-default kill-read-only-ok t)
(global-set-key "\C-c\C-k" 'copy-line)

;; mini buffer setting
(setq resize-mini-windows nil)

;;; display line number
(line-number-mode t)

;;; display column number
(column-number-mode t)

;;; display time
(setq display-time-24hr-format t)
(display-time)

;;; hl-line-mode
(global-hl-line-mode)

;;; Highlight parent brackets
(show-paren-mode t)

;;; Highlight Region
(transient-mark-mode t)

;;; Setting Tab width
(setq c-tab-always-indent t)
(setq default-tab-width 2)
(setq indent-line-function 'indent-relative-maybe)

;;; Tab to Space
(setq-default tab-width 2 indent-tabs-mode nil)

;; comment
(global-set-key (kbd "C-c ;") 'comment-or-uncomment-region)
(setq comment-style 'multi-line)

;; "yes or no" => "y or n"
(fset 'yes-or-no-p 'y-or-n-p)

;; delete beep
(defun my-bell-function ()
  (unless (memq this-command
        '(isearch-abort abort-recursive-edit exit-minibuffer
              keyboard-quit mwheel-scroll down up next-line previous-line
              backward-char forward-char))
    (ding)))
(setq ring-bell-function 'my-bell-function)

;; use terminfo in Emacs
(setq system-uses-terminfo nil)

;; display escape chars in shell
(autoload 'ansi-color-for-comint-mode-on "ansi-color" nil t)
(add-hook 'shell-mode-hook 'ansi-color-for-comint-mode-on)

;; start emacs server
(require 'server)
(if (fboundp 'server-running-p)
    (unless (server-running-p)
      (server-start)))


;; Cocoa Emacs23  Setting
(when (>= emacs-major-version 23)
  ;; replace META key
  (setq ns-command-modifier (quote meta))
  (setq ns-alternate-modifier (quote super))
  ;; open new buffer when Drag & Drop
  (define-key global-map [ns-drag-file] 'ns-find-file))

;;;
;;; For Mac GUI
;;;
(when window-system
  (setq-default line-spacing
                (if (featurep 'mac-carbon) nil 2))
  ;; no display toolbar
  (tool-bar-mode 0)

  ;; Display Color
  (setq default-frame-alist
        (append (list
                 '(width . 162)
                 '(height . 50)
                 '(foreground-color . "floral white")
                 '(background-color . "black")
                 '(cursor-color . "LightSeaGreen")
                 '(border-color . "floral white")
                 '(alpha . (0.90 0.90))
;;                 '(line-spacing . 3)
                 )
                default-frame-alist))
  ;; toggle frame width change
  (defun toggle-frame-width ()
    (interactive)
    (let* ((wide-frame-width 162)
          (narrow-frame-width (/ wide-frame-width 2))
          (changed-width
           (lambda ()
             (if (= (frame-width) wide-frame-width)
                 narrow-frame-width
               wide-frame-width))))
      (set-frame-width (selected-frame) (funcall changed-width))))
  (global-set-key [(meta return)] 'toggle-frame-width)
  ;; Fullscreen
  ;;(setq initial-frame-alist
  ;;      (append
  ;;       '((fullscreen . fullboth))
  ;;       default-frame-alist))

  ;; Display Battery Mode
  (display-battery-mode t)

  ;; http://groups.google.com/group/carbon-emacs/msg/287876a967948923
  (defun toggle-fullscreen ()
    (interactive)
    (set-frame-parameter nil
                         'fullscreen
                         (if (frame-parameter nil
                                              'fullscreen)
                             nil 'fullboth)))
  (global-set-key [(meta return)] 'toggle-fullscreen)
)

(when (eq system-type 'gnu/linux)
  (when (>= emacs-major-version 23)
    (set-default-font "Ricty:spacing=0")
    ))

(when (eq system-type 'darwin)
  ;; Font
  (when (>= emacs-major-version 23)
    (set-face-attribute 'default nil
                        :family "menlo"
                        :height 130)
    (set-fontset-font
     (frame-parameter nil 'font)
     'japanese-jisx0208
     '("Hiragino Maru Gothic Pro" . "iso10646-1"))
    (set-fontset-font
     (frame-parameter nil 'font)
     'japanese-jisx0212
     '("Hiragino Maru Gothic Pro" . "iso10646-1"))
    (set-fontset-font
     (frame-parameter nil 'font)
     'mule-unicode-0100-24ff
     '("menlo" . "iso10646-1"))
    (setq face-font-rescale-alist
          '(("^-apple-hiragino.*" . 1.2)
            (".*osaka-bold.*" . 1.2)
            (".*osaka-medium.*" . 1.2)
            (".*courier-bold-.*-mac-roman" . 1.0)
            (".*monaco cy-bold-.*-mac-cyrillic" . 0.9)
            (".*monaco-bold-.*-mac-roman" . 0.9)
            ("-cdac$" . 1.3))))

  (when (= emacs-major-version 22)
    (require 'carbon-font)
    (fixed-width-set-fontset "hiramaru" 12)
    ) 
)

;;;
;; site-lisp
;;;

;; color-theme
(require 'color-theme)
(eval-after-load "color-theme"
  '(progn
     (color-theme-initialize)
     (color-theme-railscasts)))


;; drill-instructor.el
(load "drill-instructor")
(drill-instructor t)

;; ruby-mode.el
(autoload 'ruby-mode "ruby-mode"
  "Mode for editing ruby source files" t)
(setq auto-mode-alist
      (append '(("\\.rb$" . ruby-mode)) auto-mode-alist))
(setq interpreter-mode-alist (append '(("ruby" . ruby-mode))
                                     interpreter-mode-alist))
(autoload 'run-ruby "inf-ruby"
  "Run an inferior Ruby process")
(autoload 'inf-ruby-keys "inf-ruby"
  "Set local key defs for inf-ruby in ruby-mode")
(add-hook 'ruby-mode-hook
          '(lambda ()
             (inf-ruby-keys)))

;; ruby-dbNx.el
(autoload 'rubydb "rubydb3x"
  "run rubydb on program file in buffer *gud-file*.
the directory containing file becomes the initial working directory and source-file directory for your debugger." t)
(require 'inf-ruby)

;; ruby-block.el
(require 'ruby-block)
(ruby-block-mode t)
(setq ruby-block-highlight-toggle t)

;; ruby-electric.el
(require 'ruby-electric)
(add-hook 'ruby-mode-hook '(lambda () (ruby-electric-mode t)))
(setq ruby-electric-expand-delimiters-list nil)

;;  flymake for ruby settings
;; http://d.hatena.ne.jp/khiker/20070630/emacs_ruby_flymake
(require 'flymake)
;; I don't like the default colors :)
(set-face-background 'flymake-errline "red4")
(set-face-background 'flymake-warnline "dark slate blue")
;; Invoke ruby with '-c' to get syntax checking
(defun flymake-ruby-init ()
  (let* ((temp-file   (flymake-init-create-temp-buffer-copy
                       'flymake-create-temp-inplace))
         (local-file  (file-relative-name
                       temp-file
                       (file-name-directory buffer-file-name))))
    (list "ruby" (list "-c" local-file))))
(push '(".+\\.rb$" flymake-ruby-init) flymake-allowed-file-name-masks)
(push '("Rakefile$" flymake-ruby-init) flymake-allowed-file-name-masks)
(push '("^\\(.*\\):\\([0-9]+\\): \\(.*\\)$" 1 2 nil 3) flymake-err-line-patterns)
(add-hook
 'ruby-mode-hook
 '(lambda ()
    ;; Don't want flymake mode for ruby regions in rhtml files
    (if (not (null buffer-file-name)) (flymake-mode))))

(defun flymake-display-err-minibuf () 
  "Displays the error/warning for the current line in the minibuffer"
  (interactive)
  (let* ((line-no (flymake-current-line-no))
         (line-err-info-list
          (nth 0 (flymake-find-err-info flymake-err-info line-no)))
         (count (length line-err-info-list))
         )
    (while (> count 0)
      (when line-err-info-list
        (let* ((file (flymake-ler-file (nth (1- count) line-err-info-list)))
               (full-file  (flymake-ler-full-file
                            (nth (1- count) line-err-info-list)))
               (text (flymake-ler-text (nth (1- count) line-err-info-list)))
               (line (flymake-ler-line (nth (1- count) line-err-info-list))))
          (message "[%s] %s" line text)
          )
        )
      (setq count (1- count)))))

(add-hook
'ruby-mode-hook
'(lambda ()
   (define-key ruby-mode-map "\C-cd" 'flymake-display-err-minibuf)))


;; anything.el
(require 'anything)
(require 'anything-config)
(require 'anything-etags)
(require 'anything-match-plugin)
(require 'recentf)
(require 'recentf-ext)
(setq recentf-max-saved-items 1000)
(recentf-mode t)
(setq anything-sources (list anything-c-source-buffers
                             anything-c-source-bookmarks
                             anything-c-source-etags-select
                             anything-c-source-recentf
                             anything-c-source-buffer-not-found
                             anything-c-source-imenu
                             anything-c-source-file-name-history
                             anything-c-source-files-in-current-dir
                             anything-c-source-locate
                             anything-c-source-emacs-commands))
(setq imenu-auto-rescan t)
(define-key anything-map (kbd "C-p") 'anything-previous-line)
(define-key anything-map (kbd "C-n") 'anything-next-line)
(define-key anything-map (kbd "C-v") 'anything-next-source)
(define-key anything-map (kbd "M-v") 'anything-previous-source)
(global-set-key (kbd "C-x ;") 'anything)
(setq visit-tags-table "~/.etags")

(defun anything-kill-buffers ()
 (interactive)
 (anything
 '(((name . "Kill Buffers")
  (candidates . anything-c-buffer-list)
  (action
   ("Kill Buffer" . (lambda (candidate)
                      (kill-buffer candidate)
                      (anything-kill-buffers)
                      )))))
 nil nil))
(global-set-key (kbd "C-x :") 'anything-kill-buffers)
                 
;; rcodetools.el
(require 'rcodetools)
(setq rct-find-tag-if-available nil)
(defun ruby-mode-hook-rcodetools ()
  (define-key ruby-mode-map "\M-\C-i" 'rct-complete-symbol)
  (define-key ruby-mode-map "\C-c\C-t" 'ruby-toggle-buffer)
  (define-key ruby-mode-map "\C-c\C-d" 'xmp)
  (define-key ruby-mode-map "\C-c\C-f" 'rct-ri))
(add-hook 'ruby-mode-hook 'ruby-mode-hook-rcodetools)

(require 'anything-rcodetools)
(setq rct-get-all-methods-command "PAGER=cat fri -l")
;; See docs
(define-key anything-map "\C-c\C-z" 'anything-execute-persistent-action)

;; org-mode
(require 'org-install)
(setq org-startup-truncated nil)
(setq org-return-follows-link t)
(add-to-list 'auto-mode-alist '("\\.org$" . org-mode))
(define-key global-map "\C-cl" 'org-store-link)
(define-key global-map "\C-ca" 'org-agenda)
(global-font-lock-mode 1)
(add-hook 'org-mode-hook 'turn-on-font-lock)
(setq org-todo-keywords '("TODO" "DOING" "WAIT" "DONE")
      org-todo-interpretation 'sequence)
(setq org-hide-leading-stars 'hidestars)

;; org-remember
(org-remember-insinuate)
(setq org-directory "~/memo/")
(setq org-default-notes-file (concat org-directory "task.org"))
(setq org-remember-templates
	  '(("Todo" ?t "** TODO %?\n  %i\n  %a\n  %t" nil "Inbox")
		("Bug" ?b "** TODO %?\n  :bug:\n  %i\n  %a\n  %t" nil "Inbox")
		("Idea" ?i "** %?\n  %i\n  %a\n  %t" nil "New Ideas")))
(global-set-key (kbd "C-x /") 'org-remember) 

;; org-code-reading
(defvar org-code-reading-software-name nil)
;; ~/memo/code-reading.org に記録する
(defvar org-code-reading-file "code-reading.org")
(defun org-code-reading-read-software-name ()
  (set (make-local-variable 'org-code-reading-software-name)
       (read-string "Code Reading Software: " 
                    (or org-code-reading-software-name
                        (file-name-nondirectory
                         (buffer-file-name))))))

(defun org-code-reading-get-prefix (lang)
  (concat "[" lang "]"
          "[" (org-code-reading-read-software-name) "]"))
(defun org-remember-code-reading ()
  (interactive)
  (let* ((prefix (org-code-reading-get-prefix (substring (symbol-name major-mode) 0 -5)))
         (org-remember-templates
          `(("CodeReading" ?r "** %(identity prefix)%?\n   \n   %a\n   %t"
             ,org-code-reading-file "Memo"))))
    (org-remember)))
(global-set-key (kbd "C-x ,") 'org-remember-code-reading) 

;; install-elisp.el
(require 'install-elisp)
(setq install-elisp-repository-directory site-lisp-root)

;; text-adjust & mell
;; http://web.archive.org/web/20070208231732/http://taiyaki.org/elisp/mell/src/mell.el
;; http://web.archive.org/web/20070220213120/http://www.taiyaki.org/elisp/text-adjust/src/text-adjust.el
;;(require 'text-adjust)
;;(defun text-adjust-space-before-save-if-needed ()
;;  (when (memq major-mode
;;              '(org-mode text-mode mew-draft-mode myhatena-mode))
;;    (text-adjust-space-buffer)))
;;(defalias 'spacer 'text-adjust-space-buffer)
;;(add-hook 'before-save-hook 'text-adjust-space-before-save-if-needed)

;; nxhtml
(defun load-nxhtml ()
  (load "nxhtml/autostart.elc"))
(global-set-key (kbd "C-:") 'load-nxhtml)
(custom-set-variables
  ;; custom-set-variables was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
 '(ecb-options-version "2.32")
 '(indent-region-mode t)
 '(nxhtml-global-minor-mode t)
 '(nxhtml-global-validation-header-mode t)
 '(nxhtml-skip-welcome t)
 '(safe-local-variable-values (quote ((encoding . utf-8) (ruby-compilation-executable . "ruby") (ruby-compilation-executable . "ruby1.8") (ruby-compilation-executable . "ruby1.9") (ruby-compilation-executable . "rbx") (ruby-compilation-executable . "jruby"))))
 '(weblogger-config-alist (quote (("default" ("user" . "admin") ("server-url" . "http://gomlog.com/xmlrpc.php") ("weblog" . "1"))))))
(custom-set-faces
  ;; custom-set-faces was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
 '(mumamo-background-chunk-major ((((class color) (min-colors 8)) (:background "*"))))
 '(mumamo-background-chunk-submode ((((class color) (min-colors 8)) (:background "*")))))
(add-hook 'nxml-mode-hook
          (lambda ()
            (setq auto-fill-mode -1)
            (setq nxml-slash-auto-complete-flag t)
            (setq nxml-child-indent 2)
            (setq indent-tabs-mode t)
            (setq tab-width 2)))



;; Rinari
(add-to-load-path "rinari")
(require 'rinari)
;; Interactively Do Things (highly recommended, but not strictly required)
;;(require 'ido)
;;(ido-mode t)
(setq rinari-tags-file-name "TAGS")

;; rhtml-mode
(add-to-load-path "rhtml")
(require 'rhtml-mode)
(add-hook 'rhtml-mode-hook
  (lambda () (rinari-launch)))

;; rinari-extend-by-emacs.el
(setq rails-tags-dirs '("app" "lib" "test" "db" "vendor"))
(require 'rinari-extend-by-emacs-rails)
(defun ruby-mode-hooks-rinari-extend ()
  (define-key ruby-mode-map (kbd "<C-f1>") 'rails-search-doc)
  (define-key ruby-mode-map [f1] 'rails-search-doc-at-point))
(defun rinari-mode-hooks-rinari-extend ()
  (define-key rinari-minor-mode-map "\C-c\C-t" 'rails-create-tags))
(add-hook 'ruby-mode-hook 'ruby-mode-hooks-rinari-extend)
(add-hook 'rinari-mode-hook 'rinari-mode-hooks-rinari-extend)


;;ysnippet
(add-to-load-path "yasnippet")
(require 'yasnippet)
(yas/initialize)
(yas/load-directory (concat site-lisp-root "/yasnippet/snippets"))
(yas/load-directory (concat site-lisp-root "/yasnippets-rails/rails-snippets"))

;; js2.el
(add-to-load-path "js2-mode")
(autoload 'js2-mode "js2-mode" nil t)
(add-to-list 'auto-mode-alist (cons  "\\.\\(js\\|json\\|jsn\\|htc\\)\\'" 'js2-mode))

(add-hook 'js2-mode-hook
          (function
           (lambda ()
	     (setq js2-cleanup-whitespace nil
		   js2-mirror-mode nil)
		   ;;js2-bounce-indent-flag nil)

	     (defun indent-and-back-to-indentation ()
	       (interactive)
	       (indent-for-tab-command)
	       (let ((point-of-indentation
		      (save-excursion
            (back-to-indentation)
            (point))))
           (skip-chars-forward "\s " point-of-indentation)))
	     (define-key js2-mode-map "\C-i" 'indent-and-back-to-indentation)

	     (define-key js2-mode-map "\C-m" nil)
       (setq tab-width 2)
       (setq js2-basic-offset 2)
       (setq javascript-indent-level 2)
       (setq javascript-basic-offset tab-width)
       )))

;; apache-mode.el
(autoload 'apache-mode "apache-mode" nil t)
(add-to-list 'auto-mode-alist '("\\.htaccess\\'"   . apache-mode))
(add-to-list 'auto-mode-alist '("httpd\\.conf\\'"  . apache-mode))
(add-to-list 'auto-mode-alist '("srm\\.conf\\'"    . apache-mode))
(add-to-list 'auto-mode-alist '("access\\.conf\\'" . apache-mode))
(add-to-list 'auto-mode-alist '("sites-\\(available\\|enabled\\)/" . apache-mode))


;; pos-tip
(require 'pos-tip)

;; auto-complete.el
(add-to-load-path "auto-complete")
(require 'auto-complete-config)
(add-to-list 'ac-dictionary-directories (concat site-lisp-root "/auto-complete/ac-dict"))
(ac-config-default)

;; mic-paren.el
(require 'mic-paren)
(paren-activate)
(setq paren-match-face 'bold)
(setq paren-sexp-mode t)

;; linum.el
(when (= emacs-major-version 22)
  (require 'linum))
(global-set-key [f5] 'linum-mode)

;; magit.el
(add-to-load-path "magit/share/emacs/site-lisp")
(require 'magit)

;; apel.el
(add-to-load-path "apel")
(add-to-load-path "emu")

;; elscreen.el
(add-to-load-path "elscreen")
(require 'elscreen)
(require 'elscreen-gf)
(require 'elscreen-dired)
(require 'elscreen-w3m)
(require 'elscreen-dnd)
(require 'elscreen-server)
(global-set-key [(control tab)] 'elscreen-next)
(global-set-key [(control shift tab)] 'elscreen-previous)

;;haml-mode
(require 'haml-mode nil 't)
(add-to-list 'auto-mode-alist '("\\.haml$" . haml-mode))
;;sass-mode
(require 'sass-mode nil 't)
(add-to-list 'auto-mode-alist '("\\.sass$" . sass-mode))

;; wdired & dired customize
(autoload 'wdired-change-to-wdired-mode "wdired")
(add-hook 'dired-load-hook
          '(lambda ()
             (load-library "ls-lisp")
             (setq ls-lisp-dirs-first t)
             (setq dired-listing-switches "-AFl")
             (setq find-ls-option '("-exec ls -AFGl {} \\;" . "-AFGl"))
             (setq grep-find-command "find . -type f -print0 | xargs -0 -e grep -ns ")
             (define-key dired-mode-map "r" 'wdired-change-to-wdired-mode)
             (define-key dired-mode-map
               [menu-bar immediate wdired-change-to-wdired-mode]
               '("Edit File Names" . wdired-change-to-wdired-mode))))

;; wp-emacs
(add-to-load-path "wp-emacs")
(require 'weblogger)
(global-set-key "\C-cbs" 'weblogger-start-entry)
(define-key weblogger-entry-mode-map "\C-x\C-s" 'weblogger-send-entry)

(require 'textile-minor-mode)

(add-hook 'weblogger-entry-mode-hook 'textile-minor-mode)
(add-hook 'weblogger-entry-mode-hook 'flyspell-mode)

(defun publish-post ()
  (interactive)
  (textile-to-html-buffer-respect-weblogger)
  (weblogger-publish-entry)
 )

;; scala-mode
(add-to-load-path "scala-mode")
(add-hook 'scala-mode-hook
          '(lambda ()
             (yas/minor-mode-on)))
(setq yas/scala (concat site-lisp-root "/scala-mode/contrib/yasnippet/snippets"))
(yas/load-directory yas/scala)
(require 'scala-mode-auto)
(setq scala-interpreter "/opt/local/bin/scala")

;; color-moccur
(require 'color-moccur)
(require 'moccur-edit)
(setq moccur-split-word t)

;; anything-c-moccur
(require 'anything-c-moccur)
;; setting for customizeble variants (M-x customize-group anything-c-moccur でも設定可能)
(setq anything-c-moccur-anything-idle-delay 0.2
      anything-c-moccur-higligt-info-line-flag t
      anything-c-moccur-enable-auto-look-flag t
      anything-c-moccur-enable-initial-pattern t)
(global-set-key (kbd "M-o") 'anything-c-moccur-occur-by-moccur) ;serach in buf
(global-set-key (kbd "C-M-o") 'anything-c-moccur-dmoccur) ;dir

(add-hook 'dired-mode-hook
          '(lambda ()
             (local-set-key (kbd "O") 'anything-c-moccur-dired-do-moccur-by-moccur)))

;; auto-save-buffers.el
;;(require 'auto-save-buffers)
;;(run-with-idle-timer 0.5 t 'auto-save-buffers)

;; dmacro.el
(defconst *dmacro-key* "\C-ct" "repeat key")
(global-set-key *dmacro-key* 'dmacro-exec)
(autoload 'dmacro-exec "dmacro" nil t)

;; perltidy-region
(defun perltidy-region ()
  "Run perltidy on the current region."
  (interactive)
  (save-excursion
    (shell-command-on-region (point) (mark) "perltidy -q" nil t)))
(global-set-key "\C-t" 'perltidy-region)

;; exec etags recursive file search
(defun etags-find (dir pattern)
 " find DIR -name 'PATTERN' |etags -"
 (interactive
  "DFind-name (directory): \nsFind-name (filename wildcard): ")
 (shell-command
  (concat "find " dir " -type f -name \"" pattern "\" | etags -")))

;; redo.el
(require 'redo)
(global-set-key "\C-]" 'redo)

;; my Gauche.el
(require 'mygauche)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; git-grep
;; via: http://d.hatena.ne.jp/authorNari/20091225/1261667956
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; find a specify file upper from current buffer
(defun find-file-upward (name &optional dir)
  (setq dir (file-name-as-directory (or dir default-directory)))
  (cond
   ((string= dir (directory-file-name dir))
    nil)
   ((file-exists-p (expand-file-name name dir))
    (expand-file-name name dir))
   (t
    (find-file-upward name (expand-file-name ".." dir)))))

;; exec git-grep from git managed root dir
(defun git-root-grep ()
  (interactive)
  (let (
        (git-dir (concat (find-file-upward ".git") "/../"))
        (cmd "git --no-pager grep -n ")
        (origin-default-directory default-directory)
        )
    (setq default-directory git-dir)
    (setq cmd
          (read-string "run git root grep (like this) : " cmd))
    (compilation-start cmd 'grep-mode
                       `(lambda (name)
                          (format "*git-root-grep@%s*" ,git-dir)))
    (setq default-directory origin-default-directory)))
(global-set-key "\C-cg" 'git-root-grep)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; move other buffer
;; via: http://d.hatena.ne.jp/authorNari/20091225/1261667956
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(setq windmove-wrap-around t)
(define-key global-map [(C shift n)] 'windmove-down)
(define-key global-map [(C shift p)] 'windmove-up)
(define-key global-map [(C shift b)] 'windmove-left)
(define-key global-map [(C shift f)] 'windmove-right)

;; markdown-mode.el
(autoload 'markdown-mode "markdown-mode.el"
   "Major mode for editing Markdown files" t)
(setq auto-mode-alist
   (cons '("\\.markdown" . markdown-mode) auto-mode-alist))
(setq markdown-command "bluefeather")
;; conversion to MarkdownExtra in a selected region
(defun markdown-region (from to)
  (interactive "r")
  (if (> from to)
      (rotatef from to))
  (let ((buffer-output (get-buffer-create "*markdown*")))
    (with-current-buffer buffer-output
      (erase-buffer))
    (call-process-region from
                         to
                         markdown-command
                         nil
                         buffer-output
                         nil)
    (switch-to-buffer-other-window buffer-output)))

;; textile-mode.el
(require 'textile-mode)
(add-to-list 'auto-mode-alist '("\\.textile\\'" . textile-mode))


;; other window
;; via: http://d.hatena.ne.jp/rubikitch/20100210/emacs
(defun other-window-or-split ()
  (interactive)
  (when (one-window-p)
    (split-window-horizontally))
  (other-window 1))

(global-set-key (kbd "C-t") 'other-window-or-split)

;; text-translator
(add-to-list 'load-path (concat site-lisp-root "/text-translator"))
(require 'text-translator-load)
(global-set-key "\C-x\M-T" 'text-translator)
(setq text-translator-auto-selection-func
      'text-translator-translate-by-auto-selection-enja)
(global-set-key "\C-x\M-t" 'text-translator-all-by-auto-selection)

;; doc-view
;; http://www.tsdh.de/cgi-bin/wiki.pl/doc-view.el
(require 'doc-view)

;; html-helper-mode
(autoload 'html-helper-mode "html-helper-mode" "Yay HTML" t)
;; simple-hatena-mode
(add-to-load-path "simple-hatena-mode")
(require 'simple-hatena-mode)
(setq simple-hatena-default-group "sicp")

;; hatenahelper-mode
(require 'hatenahelper-mode)
(global-set-key "\C-xH" 'hatenahelper-mode)
(add-hook 'simple-hatena-mode-hook
          '(lambda ()
             (hatenahelper-mode 1)))

;; w3m-emacs
(when (executable-find "w3m")
  (add-to-load-path "w3m-emacs/share/emacs/site-lisp/w3m")
  (require 'w3m-load)
  (require 'w3m)
  (setq w3m-use-cookies t)
  (setq w3m-home-page "http://www.google.com")
  (global-set-key "\C-xm" 'browse-url-at-point))

;; tramp
(add-to-load-path "tramp/share/emacs/site-lisp")
(require 'tramp)
(setq tramp-default-method "sshx")

;; multi-term
(require 'multi-term)
(setq multi-term-program shell-file-name)
(add-hook 'term-mode-hook
          '(lambda ()
             ;; delete char with C-h
             (define-key term-raw-map (kbd "C-h") 'term-send-backspace)
             ;; paste with C-y
             (define-key term-raw-map (kbd "C-y") 'term-paste)
      			 ))

;; php-mode
(require 'php-mode)
(add-to-list 'auto-mode-alist (cons "\\.\\(php\\|php5\\)\\'" 'php-mode))
;; php-completion
(add-hook  'php-mode-hook
           (lambda ()
             (require 'php-completion)
             (php-completion-mode t)
             (define-key php-mode-map (kbd "C-o") 'phpcmp-complete)
	     (c-set-offset 'arglist-intro '+)
	     (c-set-offset 'arglist-close 0)
             (when (require 'auto-complete nil t)
               (make-variable-buffer-local 'ac-sources)
               (add-to-list 'ac-sources 'ac-source-php-completion)
               (auto-complete-mode t))))

;; smarty-mode
(add-to-list 'auto-mode-alist (cons "\\.tpl\\'" 'smarty-mode))
(require 'smarty-mode)

;; howm for org-mode
;; http://howm.sourceforge.jp/cgi-bin/hiki/hiki.cgi?OrgMode
;;(add-hook 'org-mode 'howm-mode)
;;(add-to-list 'auto-mode-alist '("\\.howm$" . org-mode))
;;(setq howm-view-title-header "*") ;; eval before loading howm

;; howm
(add-to-load-path "howm")
(setq howm-menu-lang 'ja)
(global-set-key "\C-c,," 'howm-menu)
(mapc
 (lambda (f)
   (autoload f
	 "howm" "Hitori Otegaru Wiki Modoki" t))
 '(howm-menu howm-list-all howm-list-recent
			 howm-list-grep howm-create
			 howm-keyword-to-kill-ring))


;; http://www.bookshelf.jp/soft/meadow_38.html#SEC560
;; リンクを TAB で辿る
(eval-after-load "howm-mode"
  '(progn
     (define-key howm-mode-map [tab] 'action-lock-goto-next-link)
     (define-key howm-mode-map [(meta tab)] 'action-lock-goto-previous-link)))
;; 「最近のメモ」一覧時にタイトル表示
(setq howm-list-recent-title t)
;; 全メモ一覧時にタイトル表示
(setq howm-list-all-title t)
;; メニューを 2 時間キャッシュ
(setq howm-menu-expiry-hours 2)

;; howm の時は auto-fill で
;;(add-hook 'howm-mode-on-hook 'auto-fill-mode)

;; RET でファイルを開く際, 一覧バッファを消す
;; C-u RET なら残る
(setq howm-view-summary-persistent nil)

;; メニューの予定表の表示範囲
;; 10 日前から
(setq howm-menu-schedule-days-before 10)
;; 3 日後まで
(setq howm-menu-schedule-days 3)

;; howm のファイル名
;; 以下のスタイルのうちどれかを選んでください
;; で，不要な行は削除してください
;; 1 メモ 1 ファイル (デフォルト)
(setq howm-file-name-format "%Y/%m/%Y-%m-%d-%H%M%S.howm")

(setq howm-view-grep-parse-line
      "^\\(\\([a-zA-Z]:/\\)?[^:]*\\.howm\\):\\([0-9]*\\):\\(.*\\)$")
;; 検索しないファイルの正規表現
(setq
 howm-excluded-file-regexp
 "/\\.#\\|[~#]$\\|\\.bak$\\|/CVS/\\|\\.doc$\\|\\.pdf$\\|\\.ppt$\\|\\.xls$")

;; いちいち消すのも面倒なので
;; 内容が 0 ならファイルごと削除する
(if (not (memq 'delete-file-if-no-contents after-save-hook))
    (setq after-save-hook
          (cons 'delete-file-if-no-contents after-save-hook)))
(defun delete-file-if-no-contents ()
  (when (and
         (buffer-file-name (current-buffer))
         (string-match "\\.howm" (buffer-file-name (current-buffer)))
         (= (point-min) (point-max)))
    (delete-file
     (buffer-file-name (current-buffer)))))

;; http://howm.sourceforge.jp/cgi-bin/hiki/hiki.cgi?SaveAndKillBuffer
;; C-cC-c で保存してバッファをキルする
(defun my-save-and-kill-buffer ()
  (interactive)
  (when (and
         (buffer-file-name)
         (string-match "\\.howm"
                       (buffer-file-name)))
    (save-buffer)
    (kill-buffer nil)))
(eval-after-load "howm"
  '(progn
     (define-key howm-mode-map
       "\C-c\C-c" 'my-save-and-kill-buffer)))

;; select date by calender
;; http://www.bookshelf.jp/soft/meadow_38.html#SEC560
(eval-after-load "calendar"
  '(progn
     (define-key calendar-mode-map
       "\C-m" 'my-insert-day)
     (defun my-insert-day ()
       (interactive)
       (let ((day nil)
             (calendar-date-display-form
         '("[" year "-" (format "%02d" (string-to-int month))
           "-" (format "%02d" (string-to-int day)) "]")))
         (setq day (calendar-date-string
                    (calendar-cursor-to-date t)))
         (exit-calendar)
         (insert day)))))

;; howm for outline mode
;; http://www.bookshelf.jp/soft/meadow_38.html#SEC560
(autoload 'howm-mode
  "howm-mode" "Hitori Otegaru Wiki Modoki" t)
(defadvice howm-mode
  (before outline-minor activate)
  (outline-minor-mode t))
(require 'outline)
(defun my-outline-flip-subtree (&optional dummy)
  (interactive)
  (if (save-excursion
        (forward-line 1)
        (let ((p (overlays-at (line-beginning-position)))
              (ol nil))
          (while (and p (not ol))
            (setq ol (overlay-get (car p) 'invisible))
            (setq p (cdr p)))
          ol))
      (show-subtree)
    (hide-subtree)))
(defun add-my-action-lock-rule ()
  (let ((rule
         (action-lock-general
          'my-outline-flip-subtree
          (if (and
               buffer-file-name
               (string-match "\\.howm$" buffer-file-name))
              "^ *\\(\\*\\**\\)"
            (concat "\\(" outline-regexp "\\)"))
          1 1)))
    (if (not (member rule action-lock-default-rules))
        (progn (setq action-lock-default-rules
                     (cons rule action-lock-default-rules))
               (action-lock-set-rules action-lock-default-rules)))))
(add-hook 'action-lock-mode-on-hook 'add-my-action-lock-rule)

;; skk
(add-to-load-path "skk")
(require 'skk-autoloads)
(setq skk-preload)
(global-set-key "\C-\\" 'skk-mode)
(global-set-key "\C-xj" 'skk-auto-fill-mode)
(global-set-key "\C-xt" 'skk-tutorial)
(setq skk-cdb-large-jisyo (concat site-lisp-root "/skk/data/SKK-JISYO.L.cdb"))
(setq skk-kakutei-key "\C-o")
(add-hook 'isearch-mode-hook
          #'(lambda ()
              (when (and (boundp 'skk-mode)
                         skk-mode
                         skk-isearch-mode-enable)
                (skk-isearch-mode-setup))))
(add-hook 'isearch-mode-end-hook
          #'(lambda ()
              (when (and (featurep 'skk-isearch)
                         skk-isearch-mode-enable)
                (skk-isearch-mode-cleanup))))

;; gtags-mode
(when (locate-library "gtags")
  (require 'gtags))
;;(autoload 'gtags-mode "gtags" "" t)
(global-set-key "\M-," 'gtags-find-tag)
(global-set-key "\M-r" 'gtags-find-rtag)
(global-set-key "\M-s" 'gtags-find-symbol)
(global-set-key "\M-p" 'gtags-find-pattern)
(global-set-key "\M-P" 'gtags-find-file)
(global-set-key "\M-*" 'gtags-pop-stack)

(add-hook 'php-mode-hook
          (lambda ()
            (gtags-mode 1)
            (gtags-make-complete-list)
            (setq tab-width 4)
            (setq c-basic-offset 4)
            (setq gtags-libpath `((,(expand-file-name "~/.gtags/php") . "/usr/local/lib/php")))
            ))

;; sudoedit
;; http://d.hatena.ne.jp/rubikitch/20101018/sudoext
;; require (server-start)
(require 'sudo-ext)


;; jdee
(add-to-load-path "elib")
(add-to-load-path "jdee/lisp")
(autoload 'jde-mode "jde" "Java Development Environment for Emacs" t)
(setq auto-mode-alist (cons '("\.java$" . jde-mode) auto-mode-alist))

;; cedet
(add-to-load-path "cedet/cogre")
(add-to-load-path "cedet/common")
(add-to-load-path "cedet/contrib")
(add-to-load-path "cedet/ede")
(add-to-load-path "cedet/eieio")
(add-to-load-path "cedet/semantic")
(add-to-load-path "cedet/speedbar")
(add-to-load-path "cedet/srecode")

(setq semantic-load-turn-useful-things-on t)
(load "cedet")
;;(semantic-load-enable-code-helpers)

;; jde-mode-config
(custom-set-variables
 '(jde-jdk-registry (quote (("1.6.0.24" . "/usr/lib/jvm/java-6-sun/"))))
 '(jde-global-classpath (quote (
                                "~/lib/android-sdk/platforms/android-4/android.jar"
                                "~/lib/android-sdk/platforms/android-7/android.jar"
                                "~/lib/android-sdk/platforms/android-8/android.jar"
                                "~/lib/android-sdk/platforms/android-10/android.jar"
                                "~/lib/android-sdk/platforms/android-11/android.jar"
                                ))))

(add-hook 'jde-mode-hook
          '(lambda ()
             (c-set-offset 'arglist-intro '+)
             (c-set-offset 'arglist-close 0)
             (c-set-offset 'topmost-intro-cont 0) ;; new line on annotation
             (c-set-offset 'func-decl-cont 0)
             (setq indent-tabs-mode nil)
             (setq c-basic-offset 4)
             (setq c-set-style "java")
             ))

;; custom variables
(setq compilation-window-height 8)
(setq bsh-vm-args '("-Duser.language=en"))
(setq jde-import-auto-sort t)

;;; ant on jdee
(setq jde-build-function '(jde-ant-build))
(setq jde-ant-enabled-find t)
(setq jde-ant-program "/usr/bin/ant")
(setq jde-ant-read-target t)

;;; check style on jdee
(setq jde-checkstyle-option-rcurly (list "alone"))

(let ((elem (assq 'encoded-kbd-mode minor-mode-alist)))
  (when elem
    (setcar (cdr elem) "")))

;; view-mode
(require 'view-support)

;; key-chord.el
(require 'key-chord)
(setq key-chord-two-keys-delay 0.04)
(key-chord-mode 1)
(key-chord-define-global "jk" 'view-mode)
