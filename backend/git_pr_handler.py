"""
Git PR Handler module
Creates pull requests with changes and handles user confirmation
"""
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from utils.logger import setup_logger
from error_parser import Error

logger = setup_logger(__name__)

class GitPRHandler:
    """Handle git operations and PR creation"""
    
    def __init__(self, repo_path: Path = None):
        """Initialize git handler"""
        self.repo_path = repo_path or Path.cwd()
        logger.info(f"GitPRHandler initialized with repo: {self.repo_path}")
    
    def check_git_available(self) -> bool:
        """Check if git is available"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Git not available: {e}")
            return False
    
    def create_fix_branch(self, language: str, file_name: str) -> str:
        """Create a new git branch for the fix"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Normalize path separators to forward slashes and extract filename
            normalized_path = file_name.replace('\\', '/')
            clean_name = normalized_path.split('/')[-1].replace('.', '_')
            branch_name = f"fix/{language}/{clean_name}_{timestamp}"
            
            # Create and checkout new branch
            subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=self.repo_path,
                capture_output=True,
                check=False
            )
            
            logger.info(f"Created branch: {branch_name}")
            return branch_name
        except Exception as e:
            logger.error(f"Failed to create branch: {e}")
            return None
    
    def get_file_diff(self, file_path: Path) -> str:
        """Get git diff for a file"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--no-index', '--color=never', str(file_path) + '.orig', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            return result.stdout if result.stdout else "No changes detected"
        except Exception as e:
            logger.error(f"Failed to get diff: {e}")
            return ""
    
    def stage_and_commit(self, file_path: Path, errors: List[Error], branch_name: str) -> bool:
        """Stage file and create commit"""
        try:
            # Normalize path to use forward slashes for git commands
            normalized_path = str(file_path).replace('\\', '/')
            
            # Stage file
            result = subprocess.run(
                ['git', 'add', normalized_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.warning(f"git add failed: {result.stderr}")
                return False
            
            # Check if there are changes to commit
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                logger.warning("No changes detected to commit")
                return False
            
            # Create commit message with error details
            error_summary = "\n".join([f"- {e.type}: {e.message}" for e in errors])
            commit_message = f"""Fix errors in {file_path.name}

Errors fixed:
{error_summary}

Auto-fixed by AI Bug Fixer
Branch: {branch_name}"""
            
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.warning(f"git commit failed: {result.stderr}")
                return False
            
            logger.info(f"Committed changes to {file_path.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to commit: {e}")
            return False
    
    def create_pr_info(self, file_path: Path, errors: List[Error], fixed_code: str, original_code: str) -> Dict:
        """Create PR information dictionary"""
        return {
            'file': str(file_path),
            'errors_found': len(errors),
            'errors': [{'type': e.type, 'message': e.message} for e in errors],
            'original_code_snippet': original_code[:200] + ("..." if len(original_code) > 200 else ""),
            'fixed_code_snippet': fixed_code[:200] + ("..." if len(fixed_code) > 200 else ""),
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_to_main(self) -> bool:
        """Reset to main/master branch"""
        try:
            # Try main first, then master
            for branch in ['main', 'master']:
                result = subprocess.run(
                    ['git', 'checkout', branch],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    logger.info(f"Switched back to {branch}")
                    return True
            
            logger.warning("Could not reset to main/master branch")
            return False
        except Exception as e:
            logger.error(f"Failed to reset branch: {e}")
            return False
