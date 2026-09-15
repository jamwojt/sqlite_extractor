FROM python:3.14-slim AS builder

# Copy uv binary from official image (or use installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 2. Install Dependencies First (for caching)
COPY pyproject.toml uv.lock ./

# Use cache mounts for faster subsequent builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# 3. Copy Application Code
COPY . .

# 4. Install Project Code
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# 5. Runtime Stage
FROM python:3.14-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app /app

# Set environment to use venv binaries
ENV PATH="/app/.venv/bin:$PATH"

# Run application
ENTRYPOINT ["python", "src/main.py"]
