"""
GitHub Repository Analyzer for IELTS GenAI Prep
Analyzes the external repository to compare with current implementation
"""
import os
import json
import subprocess
import tempfile
import logging

logger = logging.getLogger(__name__)

def get_github_access_token():
    """Get GitHub access token from Replit connection"""
    try:
        hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        x_replit_token = None
        
        if os.environ.get('REPL_IDENTITY'):
            x_replit_token = 'repl ' + os.environ.get('REPL_IDENTITY')
        elif os.environ.get('WEB_REPL_RENEWAL'):
            x_replit_token = 'depl ' + os.environ.get('WEB_REPL_RENEWAL')
        
        if not x_replit_token:
            logger.error('X_REPLIT_TOKEN not found')
            return None
        
        import requests
        response = requests.get(
            f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=github',
            headers={
                'Accept': 'application/json',
                'X_REPLIT_TOKEN': x_replit_token
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if items:
                connection_settings = items[0]
                access_token = (connection_settings.get('settings', {}).get('access_token') or
                              connection_settings.get('settings', {}).get('oauth', {}).get('credentials', {}).get('access_token'))
                return access_token
        
        logger.error(f'Failed to get access token: {response.status_code}')
        return None
        
    except Exception as e:
        logger.error(f'Error getting access token: {e}')
        return None

def analyze_github_repository(repo_url='https://github.com/WWPCA/IeltsPrep'):
    """Analyze GitHub repository contents"""
    try:
        # Extract owner and repo from URL
        repo_path = repo_url.replace('https://github.com/', '')
        owner, repo = repo_path.split('/')
        
        access_token = get_github_access_token()
        if not access_token:
            logger.error("Could not get GitHub access token")
            return None
        
        import requests
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get repository information
        repo_response = requests.get(f'https://api.github.com/repos/{owner}/{repo}', headers=headers)
        if repo_response.status_code != 200:
            logger.error(f"Could not access repository: {repo_response.status_code}")
            return None
        
        repo_info = repo_response.json()
        
        # Get repository contents
        contents_response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/contents', headers=headers)
        if contents_response.status_code != 200:
            logger.error(f"Could not get repository contents: {contents_response.status_code}")
            return None
        
        contents = contents_response.json()
        
        analysis = {
            'repository_info': {
                'name': repo_info['name'],
                'description': repo_info.get('description', ''),
                'language': repo_info.get('language', 'Unknown'),
                'size': repo_info['size'],
                'stars': repo_info['stargazers_count'],
                'forks': repo_info['forks_count'],
                'created_at': repo_info['created_at'],
                'updated_at': repo_info['updated_at']
            },
            'files_and_directories': []
        }
        
        # Analyze top-level files and directories
        for item in contents:
            if item['type'] == 'file':
                analysis['files_and_directories'].append({
                    'name': item['name'],
                    'type': 'file',
                    'size': item['size'],
                    'download_url': item.get('download_url')
                })
            elif item['type'] == 'dir':
                # Get directory contents
                dir_response = requests.get(item['url'], headers=headers)
                if dir_response.status_code == 200:
                    dir_contents = dir_response.json()
                    analysis['files_and_directories'].append({
                        'name': item['name'],
                        'type': 'directory',
                        'files': [f['name'] for f in dir_contents if f['type'] == 'file']
                    })
        
        return analysis
        
    except Exception as e:
        logger.error(f'Error analyzing repository: {e}')
        return None

def compare_with_current_codebase(github_analysis):
    """Compare GitHub repository with current codebase"""
    if not github_analysis:
        return "Could not analyze GitHub repository"
    
    # Get current codebase files
    current_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and common non-essential directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]
        
        for file in files:
            if not file.startswith('.') and not file.endswith('.pyc'):
                rel_path = os.path.relpath(os.path.join(root, file), '.')
                current_files.append(rel_path)
    
    # Analyze differences
    github_files = set()
    github_dirs = set()
    
    for item in github_analysis['files_and_directories']:
        if item['type'] == 'file':
            github_files.add(item['name'])
        elif item['type'] == 'directory':
            github_dirs.add(item['name'])
            for subfile in item.get('files', []):
                github_files.add(f"{item['name']}/{subfile}")
    
    current_file_set = set(current_files)
    
    # Find differences
    only_in_github = github_files - current_file_set
    only_in_current = current_file_set - github_files
    common_files = github_files & current_file_set
    
    analysis_report = f"""
# GitHub Repository Analysis Report

## Repository Information
- **Name**: {github_analysis['repository_info']['name']}
- **Description**: {github_analysis['repository_info']['description']}
- **Primary Language**: {github_analysis['repository_info']['language']}
- **Size**: {github_analysis['repository_info']['size']} KB
- **Last Updated**: {github_analysis['repository_info']['updated_at']}

## File Comparison Analysis

### Files ONLY in GitHub Repository ({len(only_in_github)} files):
"""
    
    for file in sorted(only_in_github):
        analysis_report += f"- {file}\n"
    
    analysis_report += f"""
### Files ONLY in Current Codebase ({len(only_in_current)} files):
"""
    
    # Show only the most relevant files that are only in current codebase
    relevant_current_files = [f for f in only_in_current if 
                             f.endswith(('.py', '.html', '.js', '.yml', '.yaml', '.json')) and
                             not f.startswith(('test_', 'deploy_', 'fix_', 'backup_'))]
    
    for file in sorted(relevant_current_files)[:20]:  # Show first 20 most relevant
        analysis_report += f"- {file}\n"
    
    if len(relevant_current_files) > 20:
        analysis_report += f"- ... and {len(relevant_current_files) - 20} more files\n"
    
    analysis_report += f"""
### Common Files ({len(common_files)} files):
"""
    
    common_relevant = [f for f in common_files if f.endswith(('.py', '.html', '.js', '.yml', '.yaml'))]
    for file in sorted(common_relevant)[:10]:  # Show first 10
        analysis_report += f"- {file}\n"
    
    if len(common_relevant) > 10:
        analysis_report += f"- ... and {len(common_relevant) - 10} more common files\n"
    
    return analysis_report

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print("Analyzing GitHub repository: https://github.com/WWPCA/IeltsPrep")
    print("=" * 60)
    
    # Analyze the repository
    analysis = analyze_github_repository()
    
    if analysis:
        # Compare with current codebase
        comparison_report = compare_with_current_codebase(analysis)
        print(comparison_report)
        
        # Save detailed analysis to file
        with open('github_analysis_report.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print("\nDetailed analysis saved to: github_analysis_report.json")
    else:
        print("Failed to analyze GitHub repository. Check access permissions.")