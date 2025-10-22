#!/bin/bash
# Repository Cleanup Script
# Safely moves old files to archive folder
# Created: October 19, 2025

echo "🧹 IELTS AI Prep Repository Cleanup"
echo "===================================="
echo ""

# Create archive folder with timestamp
ARCHIVE_DIR="archive/cleanup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

echo "📁 Created archive folder: $ARCHIVE_DIR"
echo ""

# Counter for moved files
MOVED_COUNT=0

# Function to move files
move_files() {
    local pattern="$1"
    local description="$2"
    local count=0
    
    for file in $pattern; do
        if [ -f "$file" ]; then
            mv "$file" "$ARCHIVE_DIR/"
            ((count++))
            ((MOVED_COUNT++))
        fi
    done
    
    if [ $count -gt 0 ]; then
        echo "✓ Moved $count $description"
    fi
}

# Move backup ZIP files
echo "📦 Moving backup files..."
move_files "*.zip" "ZIP backup files"
move_files "*.bak" "BAK backup files"

# Move old HTML backups (but keep approved and working templates)
echo ""
echo "📄 Moving old HTML backups..."
move_files "*backup*.html" "HTML backup files"
move_files "complete-*.html" "complete HTML files"
move_files "updated-*.html" "updated HTML files"
move_files "comprehensive_template.html" "old template files"
move_files "current_approved_template.html" "old template files"
move_files "dashboard.html" "old dashboard files"
move_files "database_schema_demo.html" "demo files"
move_files "login.html" "old login files"
move_files "public_home.html" "old home files"
move_files "template_part*.html" "template part files"

# Move old test scripts
echo ""
echo "🧪 Moving old test scripts..."
move_files "test_*.py" "Python test scripts"
move_files "test_*.html" "HTML test files"
move_files "test_*.js" "JavaScript test files"

# Move old deployment guides and summaries
echo ""
echo "📚 Moving old documentation..."
move_files "*DEPLOYMENT*.md" "deployment docs"
move_files "*GUIDE*.md" "guide docs"
move_files "*SUMMARY*.md" "summary docs"
move_files "*COMPLETE*.md" "completion docs"
move_files "*FIX*.md" "fix docs"
move_files "*ANALYSIS*.md" "analysis docs"
move_files "*MIGRATION*.md" "migration docs"
move_files "*STATUS*.md" "status docs"
move_files "*IMPLEMENTATION*.md" "implementation docs"

# Move old shell scripts
echo ""
echo "⚙️ Moving old shell scripts..."
move_files "deploy-*.sh" "deploy scripts"
move_files "setup-*.sh" "setup scripts"
move_files "update-*.sh" "update scripts"
move_files "configure-*.sh" "configure scripts"
move_files "monitor-*.sh" "monitor scripts"
move_files "check-*.sh" "check scripts"
move_files "complete-*.sh" "complete scripts"
move_files "aws-*.sh" "AWS scripts"
move_files "production-*.sh" "production scripts"

# Move old Python scripts (non-essential)
echo ""
echo "🐍 Moving old Python scripts..."
move_files "add_*.py" "add scripts"
move_files "backup_*.py" "backup scripts"
move_files "block_*.py" "block scripts"
move_files "clean_*.py" "clean scripts"
move_files "cleanup-*.py" "cleanup scripts"
move_files "deactivate_*.py" "deactivate scripts"
move_files "disable_*.py" "disable scripts"
move_files "final_*.py" "final scripts"
move_files "fix-*.py" "fix scripts"
move_files "force_*.py" "force scripts"
move_files "implement_*.py" "implement scripts"
move_files "load_*.py" "load scripts"
move_files "parse_*.py" "parse scripts"
move_files "populate-*.py" "populate scripts"
move_files "remove-*.py" "remove scripts"
move_files "restore_*.py" "restore scripts"
move_files "restrict_*.py" "restrict scripts"
move_files "run-*.py" "run scripts"
move_files "setup_*.py" "setup scripts"
move_files "simple-*.py" "simple scripts"
move_files "standardize-*.py" "standardize scripts"
move_files "store_*.py" "store scripts"
move_files "temporary_*.py" "temporary scripts"
move_files "transfer-*.py" "transfer scripts"
move_files "update_*.py" "update scripts"
move_files "updated_*.py" "updated scripts"
move_files "upload_*.py" "upload scripts"
move_files "use_*.py" "use scripts"
move_files "verify_*.py" "verify scripts"

# Move old YAML/JSON config files
echo ""
echo "⚙️ Moving old config files..."
move_files "cloud-run-config.yaml" "old config files"
move_files "production-config.yaml" "old config files"
move_files "enterprise-scaling-config.yaml" "old config files"
move_files "ielts-genai-prep-cloudformation.yaml" "old CloudFormation files"
move_files "cloudformation-*.yaml" "old CloudFormation files"
move_files "custom-domain-*.yaml" "old custom domain files"
move_files "import-template.yaml" "old import files"
move_files "minimal-template.yaml" "old template files"
move_files "iam-policy-*.json" "old IAM policy files"
move_files "app-store-assets.json" "old app store files"

# Move old config scripts
move_files "production-config.sh" "old config scripts"
move_files "*.txt" "old text files (except requirements)"

# Move old documentation images
echo ""
echo "🖼️ Moving old images..."
move_files "*.png" "PNG images (except app icons)"
move_files "footer.png" "footer images"
move_files "homepage_footer.png" "homepage images"

# Move old directories
echo ""
echo "📂 Moving old directories..."
if [ -d "github_backup" ]; then
    mv github_backup "$ARCHIVE_DIR/"
    echo "✓ Moved github_backup/ directory"
    ((MOVED_COUNT++))
fi

if [ -d "production-branch-code" ]; then
    mv production-branch-code "$ARCHIVE_DIR/"
    echo "✓ Moved production-branch-code/ directory"
    ((MOVED_COUNT++))
fi

if [ -d "production_deployment" ] && [ "$(ls -A production_deployment 2>/dev/null)" ]; then
    mv production_deployment "$ARCHIVE_DIR/"
    echo "✓ Moved production_deployment/ directory"
    ((MOVED_COUNT++))
fi

if [ -d "lambda_minimal" ]; then
    mv lambda_minimal "$ARCHIVE_DIR/"
    echo "✓ Moved lambda_minimal/ directory"
    ((MOVED_COUNT++))
fi

if [ -d "replit_agent" ]; then
    mv replit_agent "$ARCHIVE_DIR/"
    echo "✓ Moved replit_agent/ directory"
    ((MOVED_COUNT++))
fi

# Summary
echo ""
echo "=================================="
echo "✅ Cleanup Complete!"
echo "📊 Moved $MOVED_COUNT files/directories to: $ARCHIVE_DIR"
echo ""
echo "Next steps:"
echo "1. Test your application to ensure everything still works"
echo "2. If everything works, you can delete the archive folder"
echo "3. Commit the cleaned repository to GitHub"
echo ""
echo "To restore if needed: mv $ARCHIVE_DIR/* ."
echo "To delete archive: rm -rf $ARCHIVE_DIR"
