;;; skk-setup.el --- initial setup for SKK  -*- emacs-lisp -*-
;; This file was generated automatically by SKK-MK at Mon Sep 13 11:41:57 2010

;; Copyright (C) 2000 NAKAJIMA Mikio <minakaji@osaka.email.ne.jp>

;; Author: NAKAJIMA Mikio <minakaji@osaka.email.ne.jp>
;; Maintainer: SKK Development Team <skk@ring.gr.jp>
;; Version: $Id: skk-setup.el.in,v 1.30 2006/01/04 10:10:46 skk-cvs Exp $
;; Keywords: japanese, mule, input method
;; Last Modified: $Date: 2006/01/04 10:10:46 $

;; This file is part of Daredevil SKK.

;; Daredevil SKK is free software; you can redistribute it and/or
;; modify it under the terms of the GNU General Public License as
;; published by the Free Software Foundation; either version 2, or
;; (at your option) any later version.

;; Daredevil SKK is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
;; General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with Daredevil SKK, see the file COPYING.  If not, write to
;; the Free Software Foundation Inc., 51 Franklin St, Fifth Floor,
;; Boston, MA 02110-1301, USA.

;;; Commentary:

;;; Code:

;;; Autoloads.
(unless (featurep 'xemacs)
  (require 'skk-autoloads))

;;; Key bindings.
(global-set-key "\C-x\C-j" 'skk-mode)
(global-set-key "\C-xj" 'skk-auto-fill-mode)
(global-set-key "\C-xt" 'skk-tutorial)

;;; Dictionaries.
(defvar skk-large-jisyo "/Users/konuma/lisp/skk/data/SKK-JISYO.L")
(defvar skk-aux-large-jisyo "/Users/konuma/lisp/skk/data/SKK-JISYO.L")
(defvar skk-tut-file "/Users/konuma/lisp/skk/data/SKK.tut")

;;; Isearch setting.
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

(provide 'skk-setup)

;;; skk-setup.el ends here