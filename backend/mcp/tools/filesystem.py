"""
File System Tools for MCP Server
Provides file operations for CrewAI agents
"""

import os
import stat
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class FileSystemTools:
    """File system operations for MCP tools"""
    
    def __init__(self, base_path: str = "/Users/marty/repos/terra-mystica/backend"):
        """
        Initialize file system tools
        
        Args:
            base_path: Base path for file operations (security constraint)
        """
        self.base_path = Path(base_path).resolve()
        logger.info("FileSystemTools initialized", base_path=str(self.base_path))
    
    def _validate_path(self, file_path: str) -> Path:
        """
        Validate and resolve file path within base directory
        
        Args:
            file_path: File path to validate
            
        Returns:
            Resolved Path object
            
        Raises:
            ValueError: If path is outside base directory
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                # Relative path - resolve relative to base_path
                resolved_path = (self.base_path / path).resolve()
            else:
                # Absolute path - check if within base_path
                resolved_path = path.resolve()
            
            # Security check - ensure path is within base directory
            try:
                resolved_path.relative_to(self.base_path)
            except ValueError:
                raise ValueError(f"Path {file_path} is outside allowed base directory {self.base_path}")
            
            return resolved_path
            
        except Exception as e:
            logger.error("Path validation failed", file_path=file_path, error=str(e))
            raise ValueError(f"Invalid path: {file_path} - {str(e)}")
    
    def read_file(self, file_path: str) -> str:
        """
        Read contents of a file
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File contents as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If no read permission
        """
        try:
            path = self._validate_path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            # Attempt to read as text first
            try:
                content = path.read_text(encoding='utf-8')
                logger.info("File read successfully", file_path=file_path, size=len(content))
                return content
            except UnicodeDecodeError:
                # If UTF-8 fails, try reading as binary and return hex representation
                content = path.read_bytes()
                logger.info("File read as binary", file_path=file_path, size=len(content))
                return f"[Binary file - {len(content)} bytes] Hex: {content[:100].hex()}..."
                
        except Exception as e:
            logger.error("Failed to read file", file_path=file_path, error=str(e))
            raise
    
    def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> str:
        """
        Write content to a file
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            create_dirs: Whether to create parent directories if they don't exist
            
        Returns:
            Success message
            
        Raises:
            PermissionError: If no write permission
        """
        try:
            path = self._validate_path(file_path)
            
            # Create parent directories if requested
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            path.write_text(content, encoding='utf-8')
            
            logger.info("File written successfully", 
                       file_path=file_path, size=len(content), created_dirs=create_dirs)
            return f"Successfully wrote {len(content)} characters to {file_path}"
            
        except Exception as e:
            logger.error("Failed to write file", file_path=file_path, error=str(e))
            raise
    
    def list_directory(self, directory_path: str, include_hidden: bool = False) -> Dict[str, Any]:
        """
        List contents of a directory
        
        Args:
            directory_path: Path to the directory to list
            include_hidden: Whether to include hidden files/directories
            
        Returns:
            Dictionary with directory contents information
        """
        try:
            path = self._validate_path(directory_path)
            
            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {directory_path}")
            
            items = []
            for item in path.iterdir():
                # Skip hidden files unless requested
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                try:
                    stat_info = item.stat()
                    items.append({
                        "name": item.name,
                        "path": str(item.relative_to(self.base_path)),
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat_info.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        "permissions": oct(stat_info.st_mode)[-3:],
                    })
                except (OSError, PermissionError) as e:
                    # Handle permission errors for individual files
                    items.append({
                        "name": item.name,
                        "path": str(item.relative_to(self.base_path)),
                        "type": "unknown",
                        "error": str(e)
                    })
            
            result = {
                "directory": directory_path,
                "total_items": len(items),
                "files": [item for item in items if item.get("type") == "file"],
                "directories": [item for item in items if item.get("type") == "directory"],
                "errors": [item for item in items if "error" in item]
            }
            
            logger.info("Directory listed successfully", 
                       directory_path=directory_path, total_items=len(items))
            return result
            
        except Exception as e:
            logger.error("Failed to list directory", directory_path=directory_path, error=str(e))
            raise
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file or directory exists
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file/directory exists, False otherwise
        """
        try:
            path = self._validate_path(file_path)
            exists = path.exists()
            logger.debug("File existence check", file_path=file_path, exists=exists)
            return exists
        except Exception as e:
            logger.error("Failed to check file existence", file_path=file_path, error=str(e))
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            path = self._validate_path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat_info = path.stat()
            
            info = {
                "path": file_path,
                "absolute_path": str(path),
                "name": path.name,
                "suffix": path.suffix,
                "type": "directory" if path.is_dir() else "file",
                "size": stat_info.st_size,
                "size_human": self._human_readable_size(stat_info.st_size),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                "permissions": {
                    "octal": oct(stat_info.st_mode)[-3:],
                    "readable": os.access(path, os.R_OK),
                    "writable": os.access(path, os.W_OK),
                    "executable": os.access(path, os.X_OK),
                },
                "owner": {
                    "uid": stat_info.st_uid,
                    "gid": stat_info.st_gid,
                }
            }
            
            # Add directory-specific info
            if path.is_dir():
                try:
                    item_count = len(list(path.iterdir()))
                    info["item_count"] = item_count
                except PermissionError:
                    info["item_count"] = "Permission denied"
            
            logger.info("File info retrieved successfully", file_path=file_path)
            return info
            
        except Exception as e:
            logger.error("Failed to get file info", file_path=file_path, error=str(e))
            raise
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def create_directory(self, directory_path: str, parents: bool = True) -> str:
        """
        Create a directory
        
        Args:
            directory_path: Path to the directory to create
            parents: Whether to create parent directories
            
        Returns:
            Success message
        """
        try:
            path = self._validate_path(directory_path)
            path.mkdir(parents=parents, exist_ok=True)
            
            logger.info("Directory created successfully", directory_path=directory_path)
            return f"Successfully created directory: {directory_path}"
            
        except Exception as e:
            logger.error("Failed to create directory", directory_path=directory_path, error=str(e))
            raise
    
    def delete_file(self, file_path: str) -> str:
        """
        Delete a file or empty directory
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            Success message
        """
        try:
            path = self._validate_path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if path.is_dir():
                path.rmdir()  # Only removes empty directories
            else:
                path.unlink()
            
            logger.info("File deleted successfully", file_path=file_path)
            return f"Successfully deleted: {file_path}"
            
        except Exception as e:
            logger.error("Failed to delete file", file_path=file_path, error=str(e))
            raise