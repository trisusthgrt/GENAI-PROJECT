# Advanced Directory Compression and Archive Management System
"""
High-performance directory compression utilities for creating organized
archives of generated code and documentation artifacts.
"""

import os
import zipfile
from pathlib import Path
from typing import Optional, List
import asyncio
from processors.exceptions import CompressionException

class DirectoryCompressor:
    """
    Sophisticated directory compression engine that creates optimized archives
    with intelligent file filtering and compression algorithms.
    """
    
    # Default exclusion patterns for cleaner archives
    DEFAULT_EXCLUSIONS = {
        '__pycache__',
        '.git',
        '.gitignore',
        'node_modules',
        '.env',
        '*.pyc',
        '*.log',
        '.DS_Store',
        'Thumbs.db'
    }
    
    @classmethod
    async def compress_directory_async(
        cls, 
        source_directory: str, 
        output_archive: str,
        exclusions: Optional[List[str]] = None
    ) -> None:
        """
        Asynchronous directory compression interface for non-blocking operations.
        
        Args:
            source_directory: Path to directory to be compressed
            output_archive: Path for the resulting ZIP archive
            exclusions: Optional list of patterns to exclude from compression
        """
        await asyncio.to_thread(cls.compress_directory_structure, source_directory, output_archive, exclusions)
    
    @classmethod
    def compress_directory_structure(
        cls, 
        source_path: str, 
        archive_path: str,
        exclusions: Optional[List[str]] = None
    ) -> None:
        """
        Comprehensive directory compression with intelligent file filtering.
        Creates optimized ZIP archives with proper directory structure preservation.
        
        Args:
            source_path: Source directory to compress
            archive_path: Destination path for the archive file
            exclusions: Custom exclusion patterns (extends default exclusions)
        """
        try:
            source_directory = Path(source_path)
            
            # Validate source directory existence
            if not source_directory.exists():
                raise CompressionException(f"Source directory does not exist: {source_path}")
            
            if not source_directory.is_dir():
                raise CompressionException(f"Source path is not a directory: {source_path}")
            
            # Combine default and custom exclusions
            active_exclusions = cls.DEFAULT_EXCLUSIONS.copy()
            if exclusions:
                active_exclusions.update(exclusions)
            
            # Create the archive with optimized compression
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zip_archive:
                
                # Walk through directory structure
                for root, directories, files in os.walk(source_directory):
                    # Filter directories based on exclusion patterns
                    directories[:] = [d for d in directories if not cls._should_exclude(d, active_exclusions)]
                    
                    for file_name in files:
                        if cls._should_exclude(file_name, active_exclusions):
                            continue
                        
                        file_path = os.path.join(root, file_name)
                        relative_path = os.path.relpath(file_path, source_directory)
                        
                        # Add file to archive with preserved structure
                        zip_archive.write(file_path, relative_path)
                        
        except Exception as compression_error:
            raise CompressionException(f"Directory compression failed: {compression_error}")
    
    @classmethod
    def _should_exclude(cls, item_name: str, exclusion_patterns: set) -> bool:
        """
        Determine if a file or directory should be excluded from compression
        based on configured exclusion patterns.
        """
        # Check exact name matches
        if item_name in exclusion_patterns:
            return True
        
        # Check pattern matches (simple wildcard support)
        for pattern in exclusion_patterns:
            if '*' in pattern:
                # Simple wildcard matching
                if pattern.startswith('*') and item_name.endswith(pattern[1:]):
                    return True
                if pattern.endswith('*') and item_name.startswith(pattern[:-1]):
                    return True
        
        return False
    
    @classmethod
    def get_archive_info(cls, archive_path: str) -> dict:
        """
        Extract comprehensive metadata from an existing ZIP archive.
        Provides insights into archive contents and structure.
        """
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_archive:
                file_list = zip_archive.filelist
                
                return {
                    "archive_path": archive_path,
                    "total_files": len(file_list),
                    "compressed_size": sum(info.compress_size for info in file_list),
                    "uncompressed_size": sum(info.file_size for info in file_list),
                    "compression_ratio": cls._calculate_compression_ratio(file_list),
                    "file_types": cls._analyze_file_types(file_list),
                    "directory_structure": cls._extract_directory_structure(file_list)
                }
        except Exception as analysis_error:
            raise CompressionException(f"Archive analysis failed: {analysis_error}")
    
    @classmethod
    def _calculate_compression_ratio(cls, file_info_list: List) -> float:
        """Calculate the compression ratio for the archive."""
        total_compressed = sum(info.compress_size for info in file_info_list)
        total_uncompressed = sum(info.file_size for info in file_info_list)
        
        if total_uncompressed == 0:
            return 0.0
        
        return round((total_compressed / total_uncompressed) * 100, 2)
    
    @classmethod
    def _analyze_file_types(cls, file_info_list: List) -> dict:
        """Analyze file type distribution within the archive."""
        file_types = {}
        
        for file_info in file_info_list:
            if file_info.is_dir():
                continue
                
            file_extension = Path(file_info.filename).suffix.lower()
            file_extension = file_extension if file_extension else 'no_extension'
            
            file_types[file_extension] = file_types.get(file_extension, 0) + 1
        
        return file_types
    
    @classmethod
    def _extract_directory_structure(cls, file_info_list: List) -> List[str]:
        """Extract the directory structure from the archive."""
        directories = set()
        
        for file_info in file_info_list:
            if file_info.is_dir():
                directories.add(file_info.filename)
            else:
                # Add parent directories
                parent_path = str(Path(file_info.filename).parent)
                if parent_path != '.':
                    directories.add(parent_path)
        
        return sorted(list(directories))

# Backward compatibility function
def zip_folder(source_folder: str, destination_zip: str) -> None:
    """
    Legacy compatibility wrapper for directory compression.
    Maintains compatibility with original function signature.
    """
    DirectoryCompressor.compress_directory_structure(source_folder, destination_zip)

# Alternative interface for async operations
def compress_directory_structure(source_path: str, archive_path: str) -> None:
    """Direct interface to directory compression functionality."""
    DirectoryCompressor.compress_directory_structure(source_path, archive_path)
