#!/bin/bash

# Build and push admin Docker image

# Configuration
IMAGE_NAME="budstudio/budconnect-admin"
TAG="${1:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Building admin frontend Docker image...${NC}"

# Build the Docker image
docker build -t ${IMAGE_NAME}:${TAG} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Successfully built ${IMAGE_NAME}:${TAG}${NC}"
else
    echo -e "${RED}Failed to build Docker image${NC}"
    exit 1
fi

# Push to registry (uncomment when ready)
# echo -e "${YELLOW}Pushing image to registry...${NC}"
# docker push ${IMAGE_NAME}:${TAG}
# 
# if [ $? -eq 0 ]; then
#     echo -e "${GREEN}Successfully pushed ${IMAGE_NAME}:${TAG}${NC}"
# else
#     echo -e "${RED}Failed to push Docker image${NC}"
#     exit 1
# fi

echo -e "${GREEN}Build complete!${NC}"