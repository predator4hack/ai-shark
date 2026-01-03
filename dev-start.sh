#!/bin/bash

# AI-Shark Development Environment Starter
# This script uses 'docker compose' (plugin) instead of 'docker-compose'

echo "🚀 Starting AI-Shark Development Environment..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your GOOGLE_API_KEY"
    echo ""
fi

# Use docker compose (plugin) instead of docker-compose
echo "Starting services with docker compose..."
docker compose -f docker-compose.dev.yml up --build

# Note: This uses the modern 'docker compose' command (with space)
# instead of the legacy 'docker-compose' (with hyphen)
