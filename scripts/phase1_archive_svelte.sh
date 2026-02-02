#!/bin/bash

# Check if frontend-svelte directory exists
if [ -d "frontend-svelte" ]; then
  # Move frontend-svelte to archive_svelte
  echo "Moving frontend-svelte to archive_svelte..."
  mv frontend-svelte archive_svelte
  echo "Moved frontend-svelte to archive_svelte successfully."
else
  echo "frontend-svelte directory does not exist. No action taken."
fi