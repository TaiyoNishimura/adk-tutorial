FROM mcr.microsoft.com/devcontainers/python:2-3.12-bullseye

USER vscode

WORKDIR /home/vscode


# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.local/bin:${PATH}"

# install gcloud CLI
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz \
&& tar -xvf google-cloud-cli-linux-x86_64.tar.gz \
&& rm google-cloud-cli-linux-x86_64.tar.gz \
&& ./google-cloud-sdk/install.sh
ENV PATH="/home/vscode/google-cloud-sdk/bin:${PATH}"

# install google-adk
RUN uv tool install google-adk

# install zsh-autusuggestions
RUN git clone https://github.com/zsh-users/zsh-autosuggestions /home/vscode/.zsh/zsh-autosuggestions
RUN echo "source /home/vscode/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh" >> /home/vscode/.zshrc