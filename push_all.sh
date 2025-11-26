#!/bin/bash

# Push to All Remotes Script
# This script pushes the current branch to both GitLab (origin) and GitHub

set -e  # Exit on error

BRANCH=$(git branch --show-current)

echo "🚀 Pushing branch '$BRANCH' to all remotes..."
echo ""

echo "📤 Pushing to GitLab (origin)..."
git push origin "$BRANCH"
echo "✅ GitLab push complete!"
echo ""

echo "📤 Pushing to GitHub..."
git push github "$BRANCH"
echo "✅ GitHub push complete!"
echo ""

echo "🎉 Successfully pushed to all remotes!"
