# Advanced File Operations and Code Artifact Management System
"""
Sophisticated file management utilities for organized code artifact storage
and intelligent directory structure management during code generation processes.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

class CodeArtifactManager:
    """
    Advanced code artifact management system that provides intelligent
    file organization and storage capabilities for generated code assets.
    """
    
    # Default base directory for all generated artifacts
    BASE_ARTIFACTS_DIRECTORY = "artifacts"
    
    # File type categorization for intelligent organization
    FILE_TYPE_MAPPINGS = {
        '.py': 'python',
        '.ts': 'typescript',
        '.js': 'javascript',
        '.html': 'templates',
        '.css': 'styles',
        '.scss': 'styles',
        '.json': 'configuration',
        '.md': 'documentation',
        '.txt': 'documentation',
        '.yml': 'configuration',
        '.yaml': 'configuration'
    }
    
    @classmethod
    def save_code_artifact(
        cls, 
        relative_directory: str, 
        filename: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Intelligent code artifact storage with automatic directory creation and metadata tracking.
        
        Args:
            relative_directory: Directory path relative to artifacts base (e.g., 'backend', 'frontend')
            filename: Name of the file to be created
            content: File content to be written
            metadata: Optional metadata dictionary for tracking file information
        """
        # Construct full directory path within artifacts structure
        target_directory = Path(cls.BASE_ARTIFACTS_DIRECTORY) / relative_directory
        target_directory.mkdir(parents=True, exist_ok=True)
        
        # Create complete file path
        target_file_path = target_directory / filename
        
        # Write content to file with UTF-8 encoding
        with open(target_file_path, 'w', encoding='utf-8') as artifact_file:
            artifact_file.write(content)
        
        # Generate and store metadata if provided or auto-generated
        if metadata or cls._should_generate_metadata(filename):
            cls._store_artifact_metadata(target_file_path, content, metadata)
    
    @classmethod
    def ensure_directory_structure(cls, base_path: str, structure: Dict[str, Any]) -> None:
        """
        Create a complete directory structure based on a nested dictionary specification.
        
        Args:
            base_path: Base path where the structure should be created
            structure: Nested dictionary representing directory/file structure
        """
        base_directory = Path(base_path)
        base_directory.mkdir(parents=True, exist_ok=True)
        
        for item_name, item_content in structure.items():
            item_path = base_directory / item_name
            
            if isinstance(item_content, dict):
                # Create subdirectory and recurse
                cls.ensure_directory_structure(str(item_path), item_content)
            elif isinstance(item_content, str):
                # Create file with content
                item_path.parent.mkdir(parents=True, exist_ok=True)
                with open(item_path, 'w', encoding='utf-8') as file:
                    file.write(item_content)
    
    @classmethod
    def get_artifact_inventory(cls, directory_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive inventory of all artifacts in the specified directory.
        
        Args:
            directory_path: Optional specific directory to inventory (defaults to base artifacts)
            
        Returns:
            Dictionary containing detailed artifact inventory and statistics
        """
        search_directory = Path(directory_path or cls.BASE_ARTIFACTS_DIRECTORY)
        
        if not search_directory.exists():
            return {"error": "Artifacts directory does not exist", "path": str(search_directory)}
        
        inventory = {
            "directory_path": str(search_directory),
            "generated_at": datetime.now().isoformat(),
            "total_files": 0,
            "total_directories": 0,
            "file_types": {},
            "size_statistics": {},
            "file_listing": []
        }
        
        for item_path in search_directory.rglob("*"):
            if item_path.is_file():
                inventory["total_files"] += 1
                
                # Analyze file type
                file_extension = item_path.suffix.lower()
                file_type = cls.FILE_TYPE_MAPPINGS.get(file_extension, 'other')
                inventory["file_types"][file_type] = inventory["file_types"].get(file_type, 0) + 1
                
                # Calculate file size
                file_size = item_path.stat().st_size
                
                # Add to file listing
                relative_path = item_path.relative_to(search_directory)
                inventory["file_listing"].append({
                    "path": str(relative_path),
                    "size_bytes": file_size,
                    "type": file_type,
                    "modified": datetime.fromtimestamp(item_path.stat().st_mtime).isoformat()
                })
                
            elif item_path.is_dir():
                inventory["total_directories"] += 1
        
        # Calculate size statistics
        total_size = sum(file_info["size_bytes"] for file_info in inventory["file_listing"])
        inventory["size_statistics"] = {
            "total_bytes": total_size,
            "total_kb": round(total_size / 1024, 2),
            "total_mb": round(total_size / (1024 * 1024), 2),
            "average_file_size": round(total_size / max(inventory["total_files"], 1), 2)
        }
        
        return inventory
    
    @classmethod
    def cleanup_artifacts(cls, directory_path: Optional[str] = None, keep_metadata: bool = True) -> Dict[str, Any]:
        """
        Clean up artifacts directory with optional metadata preservation.
        
        Args:
            directory_path: Optional specific directory to clean (defaults to base artifacts)
            keep_metadata: Whether to preserve metadata files during cleanup
            
        Returns:
            Dictionary containing cleanup statistics and results
        """
        import shutil
        
        target_directory = Path(directory_path or cls.BASE_ARTIFACTS_DIRECTORY)
        
        if not target_directory.exists():
            return {"status": "no_action", "message": "Directory does not exist"}
        
        # Generate pre-cleanup inventory
        pre_cleanup_stats = cls.get_artifact_inventory(str(target_directory))
        
        if keep_metadata:
            # Selectively remove non-metadata files
            removed_count = 0
            for item_path in target_directory.rglob("*"):
                if item_path.is_file() and not item_path.name.startswith("_metadata"):
                    item_path.unlink()
                    removed_count += 1
            
            cleanup_stats = {
                "status": "selective_cleanup",
                "files_removed": removed_count,
                "metadata_preserved": True
            }
        else:
            # Complete directory removal and recreation
            shutil.rmtree(target_directory)
            target_directory.mkdir(parents=True, exist_ok=True)
            
            cleanup_stats = {
                "status": "complete_cleanup",
                "files_removed": pre_cleanup_stats["total_files"],
                "metadata_preserved": False
            }
        
        cleanup_stats.update({
            "pre_cleanup_stats": pre_cleanup_stats,
            "cleanup_timestamp": datetime.now().isoformat()
        })
        
        return cleanup_stats
    
    @classmethod
    def _should_generate_metadata(cls, filename: str) -> bool:
        """
        Determine if metadata should be automatically generated for a file based on its type.
        """
        file_extension = Path(filename).suffix.lower()
        # Generate metadata for code files but not for documentation or configuration
        return file_extension in ['.py', '.ts', '.js', '.html', '.css', '.scss']
    
    @classmethod
    def _store_artifact_metadata(
        cls, 
        file_path: Path, 
        content: str, 
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store comprehensive metadata for a code artifact including auto-generated insights.
        """
        metadata = {
            "file_info": {
                "filename": file_path.name,
                "path": str(file_path.relative_to(cls.BASE_ARTIFACTS_DIRECTORY)),
                "size_bytes": len(content.encode('utf-8')),
                "created_at": datetime.now().isoformat()
            },
            "content_analysis": {
                "line_count": len(content.splitlines()),
                "character_count": len(content),
                "estimated_complexity": cls._estimate_code_complexity(content),
                "file_type": cls.FILE_TYPE_MAPPINGS.get(file_path.suffix.lower(), 'unknown')
            }
        }
        
        # Merge custom metadata if provided
        if custom_metadata:
            metadata["custom_metadata"] = custom_metadata
        
        # Store metadata in a companion JSON file
        metadata_file_path = file_path.with_suffix(file_path.suffix + '.meta.json')
        with open(metadata_file_path, 'w', encoding='utf-8') as metadata_file:
            json.dump(metadata, metadata_file, indent=2)
    
    @classmethod
    def _estimate_code_complexity(cls, content: str) -> str:
        """
        Provide a basic estimation of code complexity based on content analysis.
        """
        lines = content.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) < 20:
            return "simple"
        elif len(non_empty_lines) < 100:
            return "moderate"
        elif len(non_empty_lines) < 300:
            return "complex"
        else:
            return "highly_complex"

# Legacy compatibility function for existing code
def saveFile(dirname: str, filename: str, content: str) -> None:
    """
    Legacy compatibility wrapper for the original saveFile function.
    Maintains backward compatibility while using the new artifact manager.
    """
    CodeArtifactManager.save_code_artifact(dirname, filename, content)
