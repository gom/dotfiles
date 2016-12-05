if [ -z "$GCP_SDK_PATH" ]; then
  GCP_SDK_PATH="$HOME/src/google-cloud-sdk"
fi

if [ -e "$GCP_SDK_PATH" ]; then
  # The next line updates PATH for the Google Cloud SDK.
  source "$GCP_SDK_PATH/path.zsh.inc"

  # The next line enables shell command completion for gcloud.
  source "$GCP_SDK_PATH/completion.zsh.inc"

  alias gc='gcloud'
  alias gce='gcloud compute'
  alias gcei='gcloud compute instances'
  alias gke='gcloud container'
fi
