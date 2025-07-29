# Docker Setup for Crawler Project

This Docker setup provides a Linux environment with Python, crawl4ai, and Jupyter notebooks to solve playwright compatibility issues on Windows.

## Project Structure
```
.docker/
├── Dockerfile          # Container image definition
├── .dockerignore       # Files to exclude from build
└── README-Docker.md    # This documentation
docker-compose.yml      # Container orchestration
```

## Quick Start

1. **Build and run the container:**
   ```bash
   docker-compose up --build
   ```

2. **Access Jupyter Lab:**
   Open your browser and go to: `http://localhost:8888`

3. **Stop the container:**
   ```bash
   docker-compose down
   ```

## What's Included

- **Linux environment** (Ubuntu-based)
- **Python 3.11**
- **crawl4ai** with playwright support
- **Jupyter Lab** for interactive development
- **All project dependencies** from requirements_scraper.txt
- **Data science libraries** (pandas, numpy, matplotlib, seaborn)

## Container Features

- **Persistent data:** Your project files are mounted as a volume
- **Auto-restart:** Container restarts unless manually stopped
- **No authentication:** Jupyter runs without token/password for development
- **Full playwright support:** All browsers installed and configured

## Usage Tips

- Your project files are automatically synced between host and container
- Use the `notebooks/` directory for your Jupyter notebooks
- All existing scrapers and tools are available within the container
- Install additional packages with `!pip install package_name` in notebooks

## Troubleshooting

- If port 8888 is busy, change it in docker-compose.yml
- For playwright issues, the container includes all required dependencies
- Logs are available with: `docker-compose logs`