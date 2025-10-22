#!/bin/bash
# Verify Repository Size - Run before git push

echo "=== Repository Size Verification ==="
echo ""

# Check for files over 50MB
echo "Checking for files over 50MB..."
LARGE_FILES=$(find . -type f -size +50M 2>/dev/null | grep -v "\.git/" | grep -v "\.cache/" | grep -v "\.pythonlibs/")

if [ -n "$LARGE_FILES" ]; then
    echo "❌ FAILED: Large files detected:"
    echo "$LARGE_FILES"
    echo ""
    echo "Add these to .gitignore before pushing!"
    exit 1
else
    echo "✓ No files over 50MB in working directory"
fi

# Check total repository size
echo ""
echo "Checking total repository size..."
REPO_SIZE=$(du -sh .git 2>/dev/null | cut -f1)
echo "Git repository size: $REPO_SIZE"

# Check what's staged
echo ""
echo "Files that will be pushed to GitHub:"
git ls-files | wc -l | xargs echo "Total files:"

# Check for common problem files
echo ""
echo "Checking for problematic patterns..."
PROBLEM_PATTERNS=(
    "*.zip"
    "*.tar.gz"
    "*lambda-with-deps*"
    "*awscliv2*"
    ".cache/*"
    ".pythonlibs/*"
    "node_modules/*"
    "*.pyc"
)

FOUND_PROBLEMS=0
for pattern in "${PROBLEM_PATTERNS[@]}"; do
    COUNT=$(git ls-files | grep -c "$pattern" 2>/dev/null || echo "0")
    if [ "$COUNT" -gt 0 ]; then
        echo "⚠️  Found $COUNT files matching: $pattern"
        FOUND_PROBLEMS=1
    fi
done

if [ "$FOUND_PROBLEMS" -eq 0 ]; then
    echo "✓ No problematic patterns found"
fi

echo ""
echo "=== Verification Complete ==="
echo ""
echo "If all checks passed, you can safely run:"
echo "  git push -u origin main --force"
