-- lua/plugins/fzf.lua
return {
  {
    "ibhagwan/fzf-lua",
    -- zsh で設定した fzf の外観に寄せる設定
    opts = {
      winopts = {
        height = 0.4,
        width = 0.9,
        preview = { layout = "horizontal", horizontal = "right:50%" },
      },
    },
  },
}