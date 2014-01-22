(prefer-coding-system 'euc-jp-unix)

;;; Setting Tab width
(setq c-tab-always-indent t)
(setq indent-line-function 'indent-relative-maybe)

;;; Tab to Hard tab
(setq-default tab-width 4)
(setq-default c-basic-offset 4)
(setq-default indent-tabs-mode t)

(provide 'mywork)