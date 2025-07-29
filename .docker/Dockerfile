# Use Python 3.11 on Ubuntu as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for crawl4ai and playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (required for playwright)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements first for better caching
COPY requirements_scraper.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_scraper.txt

# Install crawl4ai and jupyter
RUN pip install --no-cache-dir \
    crawl4ai \
    jupyter \
    jupyterlab \
    notebook \
    pandas \
    numpy \
    matplotlib \
    seaborn

# Install JupyterLab Spanish language pack
# RUN jupyter labextension install @jupyterlab/translation-extension
RUN pip install jupyterlab-language-pack-es-ES

# Install playwright and browsers
RUN pip install playwright
RUN playwright install
RUN playwright install-deps

# configurar crawl4ai
RUN crawl4ai-setup
RUN crawl4ai-doctor


# Copy the entire project
COPY . .

# Create a directory for notebooks if it doesn't exist
RUN mkdir -p /app/notebooks

# Expose Jupyter port
EXPOSE 8888

# Set environment variables
ENV PYTHONPATH=/app
ENV JUPYTER_ENABLE_LAB=yes

# Copy and set up the startup script
COPY .docker/start-jupyter.sh /usr/local/bin/start-jupyter.sh
RUN chmod +x /usr/local/bin/start-jupyter.sh

# Default command
CMD ["/usr/local/bin/start-jupyter.sh"]