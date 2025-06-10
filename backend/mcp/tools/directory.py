"""
Directory Tools for MCP Server
Provides directory operations for uploads, thumbnails, and temp files
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import structlog

logger = structlog.get_logger(__name__)


class DirectoryTools:
    """Directory operations for MCP server"""
    
    def __init__(self, base_path: str = "/Users/marty/repos/terra-mystica/backend"):
        """
        Initialize directory tools
        
        Args:
            base_path: Base path for the application
        """
        self.base_path = Path(base_path).resolve()
        self.uploads_path = self.base_path / "uploads"
        self.thumbnails_path = self.base_path / "thumbnails"
        self.temp_path = self.uploads_path / "temp"
        self.images_path = self.uploads_path / "images"
        
        # Ensure base directories exist
        self._ensure_base_directories()
        
        logger.info("DirectoryTools initialized", 
                   base_path=str(self.base_path),
                   uploads_path=str(self.uploads_path),
                   thumbnails_path=str(self.thumbnails_path))
    
    def _ensure_base_directories(self):
        """Ensure base directories exist"""
        directories = [
            self.uploads_path,
            self.thumbnails_path,
            self.temp_path,
            self.images_path,
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug("Directory ensured", path=str(directory))
            except Exception as e:
                logger.error("Failed to create directory", path=str(directory), error=str(e))
    
    def ensure_upload_directory(self, user_id: int) -> str:
        """
        Ensure user upload directory exists
        
        Args:
            user_id: User ID
            
        Returns:
            Path to user upload directory
        """
        try:
            user_dir = self.images_path / str(user_id)
            user_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("User upload directory ensured", user_id=user_id, path=str(user_dir))
            return str(user_dir)
            
        except Exception as e:
            logger.error("Failed to ensure upload directory", user_id=user_id, error=str(e))
            raise
    
    def get_upload_path(self, user_id: int, filename: str) -> str:
        """
        Get full path for uploaded file
        
        Args:
            user_id: User ID
            filename: Original filename
            
        Returns:
            Full path for uploaded file
        """
        try:
            user_dir = self.ensure_upload_directory(user_id)
            file_path = Path(user_dir) / filename
            
            logger.debug("Upload path generated", user_id=user_id, filename=filename, path=str(file_path))
            return str(file_path)
            
        except Exception as e:
            logger.error("Failed to get upload path", user_id=user_id, filename=filename, error=str(e))
            raise
    
    def get_thumbnail_path(self, image_filename: str, size: str = "medium") -> str:
        """
        Get thumbnail file path for an image
        
        Args:
            image_filename: Original image filename
            size: Thumbnail size (small, medium, large)
            
        Returns:
            Path to thumbnail file
        """
        try:
            # Validate size
            valid_sizes = ["small", "medium", "large"]
            if size not in valid_sizes:
                raise ValueError(f"Invalid thumbnail size: {size}. Valid sizes: {valid_sizes}")
            
            # Create thumbnail filename
            path = Path(image_filename)
            stem = path.stem
            suffix = path.suffix
            
            thumbnail_filename = f"{stem}_{size}{suffix}"
            thumbnail_path = self.thumbnails_path / thumbnail_filename
            
            logger.debug("Thumbnail path generated", 
                        image_filename=image_filename, size=size, path=str(thumbnail_path))
            return str(thumbnail_path)
            
        except Exception as e:
            logger.error("Failed to get thumbnail path", 
                        image_filename=image_filename, size=size, error=str(e))
            raise
    
    def ensure_thumbnail_directory(self) -> str:
        """
        Ensure thumbnail directory exists
        
        Returns:
            Path to thumbnail directory
        """
        try:
            self.thumbnails_path.mkdir(parents=True, exist_ok=True)
            logger.debug("Thumbnail directory ensured", path=str(self.thumbnails_path))
            return str(self.thumbnails_path)
            
        except Exception as e:
            logger.error("Failed to ensure thumbnail directory", error=str(e))
            raise
    
    def get_temp_file_path(self, filename: str) -> str:
        """
        Get temporary file path
        
        Args:
            filename: Temporary filename
            
        Returns:
            Path to temporary file
        """
        try:
            temp_file_path = self.temp_path / filename
            logger.debug("Temp file path generated", filename=filename, path=str(temp_file_path))
            return str(temp_file_path)
            
        except Exception as e:
            logger.error("Failed to get temp file path", filename=filename, error=str(e))
            raise
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Clean up temporary files older than specified age
        
        Args:
            max_age_hours: Maximum age in hours for temp files
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            cleaned_files = []
            total_size_freed = 0
            errors = []
            
            if not self.temp_path.exists():
                return {
                    "cleaned_files": 0,
                    "total_size_freed": 0,
                    "errors": [],
                    "cutoff_time": cutoff_time.isoformat()
                }
            
            for file_path in self.temp_path.iterdir():
                try:
                    if file_path.is_file():
                        # Check file age
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        if file_mtime < cutoff_time:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            
                            cleaned_files.append({
                                "filename": file_path.name,
                                "size": file_size,
                                "modified": file_mtime.isoformat()
                            })
                            total_size_freed += file_size
                            
                except Exception as e:
                    errors.append({
                        "filename": file_path.name if file_path else "unknown",
                        "error": str(e)
                    })
            
            result = {
                "cleaned_files": len(cleaned_files),
                "total_size_freed": total_size_freed,
                "total_size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
                "errors": errors,
                "cutoff_time": cutoff_time.isoformat(),
                "files": cleaned_files
            }
            
            logger.info("Temp files cleanup completed", 
                       cleaned_files=len(cleaned_files), 
                       total_size_freed_mb=result["total_size_freed_mb"],
                       errors=len(errors))
            
            return result
            
        except Exception as e:
            logger.error("Failed to cleanup temp files", error=str(e))
            return {
                "error": str(e),
                "cleaned_files": 0,
                "total_size_freed": 0
            }
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics for uploads and thumbnails
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            stats = {
                "uploads": self._get_directory_stats(self.uploads_path),
                "thumbnails": self._get_directory_stats(self.thumbnails_path),
                "temp": self._get_directory_stats(self.temp_path),
                "images": self._get_directory_stats(self.images_path),
            }
            
            # Calculate totals
            total_files = sum(s["file_count"] for s in stats.values() if s["exists"])
            total_size = sum(s["total_size"] for s in stats.values() if s["exists"])
            
            stats["totals"] = {
                "total_files": total_files,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
            }
            
            logger.info("Storage statistics retrieved", 
                       total_files=total_files, 
                       total_size_mb=stats["totals"]["total_size_mb"])
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get storage statistics", error=str(e))
            return {"error": str(e)}
    
    def _get_directory_stats(self, directory: Path) -> Dict[str, Any]:
        """Get statistics for a directory"""
        try:
            if not directory.exists():
                return {
                    "exists": False,
                    "path": str(directory),
                    "error": "Directory does not exist"
                }
            
            file_count = 0
            dir_count = 0
            total_size = 0
            file_types = {}
            
            for item in directory.rglob("*"):
                try:
                    if item.is_file():
                        file_count += 1
                        item_size = item.stat().st_size
                        total_size += item_size
                        
                        # Track file types
                        suffix = item.suffix.lower()
                        if suffix:
                            file_types[suffix] = file_types.get(suffix, 0) + 1
                        else:
                            file_types["no_extension"] = file_types.get("no_extension", 0) + 1
                            
                    elif item.is_dir():
                        dir_count += 1
                        
                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue
            
            return {
                "exists": True,
                "path": str(directory),
                "file_count": file_count,
                "directory_count": dir_count,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_types": file_types,
            }
            
        except Exception as e:
            return {
                "exists": False,
                "path": str(directory),
                "error": str(e)
            }
    
    def list_user_files(self, user_id: int) -> Dict[str, Any]:
        """
        List files for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user files information
        """
        try:
            user_dir = self.images_path / str(user_id)
            
            if not user_dir.exists():
                return {
                    "user_id": user_id,
                    "directory": str(user_dir),
                    "exists": False,
                    "files": []
                }
            
            files = []
            for file_path in user_dir.iterdir():
                if file_path.is_file():
                    try:
                        stat_info = file_path.stat()
                        files.append({
                            "filename": file_path.name,
                            "path": str(file_path),
                            "size": stat_info.st_size,
                            "size_mb": round(stat_info.st_size / (1024 * 1024), 2),
                            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                            "extension": file_path.suffix.lower(),
                        })
                    except (OSError, PermissionError) as e:
                        files.append({
                            "filename": file_path.name,
                            "error": str(e)
                        })
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x.get("modified", ""), reverse=True)
            
            result = {
                "user_id": user_id,
                "directory": str(user_dir),
                "exists": True,
                "file_count": len([f for f in files if "error" not in f]),
                "total_size": sum(f.get("size", 0) for f in files if "error" not in f),
                "files": files
            }
            
            result["total_size_mb"] = round(result["total_size"] / (1024 * 1024), 2)
            
            logger.info("User files listed", user_id=user_id, file_count=result["file_count"])
            return result
            
        except Exception as e:
            logger.error("Failed to list user files", user_id=user_id, error=str(e))
            return {
                "error": str(e),
                "user_id": user_id
            }
    
    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create backup of uploads and thumbnails
        
        Args:
            backup_name: Optional backup name
            
        Returns:
            Backup information
        """
        try:
            if backup_name is None:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_dir = self.base_path / "backups" / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup uploads
            if self.uploads_path.exists():
                uploads_backup = backup_dir / "uploads"
                shutil.copytree(self.uploads_path, uploads_backup)
            
            # Backup thumbnails
            if self.thumbnails_path.exists():
                thumbnails_backup = backup_dir / "thumbnails"
                shutil.copytree(self.thumbnails_path, thumbnails_backup)
            
            # Create backup info file
            backup_info = {
                "backup_name": backup_name,
                "created_at": datetime.now().isoformat(),
                "backup_path": str(backup_dir),
                "contents": {
                    "uploads": self.uploads_path.exists(),
                    "thumbnails": self.thumbnails_path.exists(),
                }
            }
            
            info_file = backup_dir / "backup_info.json"
            info_file.write_text(json.dumps(backup_info, indent=2))
            
            logger.info("Backup created successfully", backup_name=backup_name, path=str(backup_dir))
            return backup_info
            
        except Exception as e:
            logger.error("Failed to create backup", backup_name=backup_name, error=str(e))
            return {"error": str(e)}
    
    def validate_directories(self) -> Dict[str, Any]:
        """
        Validate all required directories exist and are accessible
        
        Returns:
            Validation results
        """
        try:
            directories = {
                "base": self.base_path,
                "uploads": self.uploads_path,
                "thumbnails": self.thumbnails_path,
                "temp": self.temp_path,
                "images": self.images_path,
            }
            
            results = {}
            all_valid = True
            
            for name, path in directories.items():
                try:
                    exists = path.exists()
                    is_dir = path.is_dir() if exists else False
                    readable = os.access(path, os.R_OK) if exists else False
                    writable = os.access(path, os.W_OK) if exists else False
                    
                    results[name] = {
                        "path": str(path),
                        "exists": exists,
                        "is_directory": is_dir,
                        "readable": readable,
                        "writable": writable,
                        "valid": exists and is_dir and readable and writable
                    }
                    
                    if not results[name]["valid"]:
                        all_valid = False
                        
                except Exception as e:
                    results[name] = {
                        "path": str(path),
                        "error": str(e),
                        "valid": False
                    }
                    all_valid = False
            
            validation_result = {
                "all_valid": all_valid,
                "directories": results,
                "checked_at": datetime.now().isoformat()
            }
            
            logger.info("Directory validation completed", all_valid=all_valid)
            return validation_result
            
        except Exception as e:
            logger.error("Failed to validate directories", error=str(e))
            return {"error": str(e)}