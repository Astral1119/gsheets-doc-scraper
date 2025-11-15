#!/usr/bin/env python3
"""
script to update markdown files from an updated directory to a target directory.
respects the 'modified' tag in frontmatter to avoid overwriting manually edited files.
"""
import os
import shutil
import frontmatter
import sys
from datetime import datetime


def update_files(target_dir, updated_dir):
    """
    update files in target_dir with files from updated_dir.
    
    args:
        target_dir: directory containing files to potentially update
        updated_dir: directory containing the updated files
    """
    log_file = 'update_log.txt'
    
    # track different categories of files
    replaced_files = []
    skipped_modified_files = []
    new_files = []
    error_files = []
    
    # get all files from the updated directory
    updated_files = [f for f in os.listdir(updated_dir) if f.endswith('.md')]
    
    for filename in updated_files:
        updated_file_path = os.path.join(updated_dir, filename)
        target_file_path = os.path.join(target_dir, filename)
        
        try:
            # check if file exists in target directory
            if os.path.exists(target_file_path):
                # read the target file's frontmatter
                with open(target_file_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    metadata_tags = post.get('tags', [])
                
                # check if the file has been modified
                if 'modified' in metadata_tags:
                    skipped_modified_files.append(filename)
                else:
                    # replace the file
                    shutil.copy2(updated_file_path, target_file_path)
                    replaced_files.append(filename)
            else:
                # file doesn't exist, copy it
                shutil.copy2(updated_file_path, target_file_path)
                new_files.append(filename)
        
        except Exception as e:
            error_files.append((filename, str(e)))
    
    # write the log file
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"# File Update Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if replaced_files:
            log.write(f"## Files Replaced ({len(replaced_files)}):\n")
            for file in sorted(replaced_files):
                log.write(f"  - {file}\n")
            log.write("\n")
        
        if skipped_modified_files:
            log.write(f"## Files Skipped (Modified) ({len(skipped_modified_files)}):\n")
            for file in sorted(skipped_modified_files):
                log.write(f"  - {file}\n")
            log.write("\n")
        
        if new_files:
            log.write(f"## New Files Copied ({len(new_files)}):\n")
            for file in sorted(new_files):
                log.write(f"  - {file}\n")
            log.write("\n")
        
        if error_files:
            log.write(f"## Errors ({len(error_files)}):\n")
            for file, error in error_files:
                log.write(f"  - {file}: {error}\n")
            log.write("\n")
        
        log.write("## Summary:\n")
        log.write(f"  - Total files processed: {len(updated_files)}\n")
        log.write(f"  - Replaced: {len(replaced_files)}\n")
        log.write(f"  - Skipped (modified): {len(skipped_modified_files)}\n")
        log.write(f"  - New files: {len(new_files)}\n")
        log.write(f"  - Errors: {len(error_files)}\n")
    
    # print summary to console
    print(f"File update completed!")
    print(f"  - Replaced: {len(replaced_files)}")
    print(f"  - Skipped (modified): {len(skipped_modified_files)}")
    print(f"  - New files: {len(new_files)}")
    print(f"  - Errors: {len(error_files)}")
    print(f"\nDetailed log written to: {log_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python update_files.py <target_directory> <updated_directory>")
        print("  target_directory: Directory containing files to update")
        print("  updated_directory: Directory containing the updated files")
        sys.exit(1)
    
    target_directory = sys.argv[1]
    updated_directory = sys.argv[2]
    
    # validate directories
    if not os.path.exists(target_directory):
        print(f"Error: Target directory '{target_directory}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(target_directory):
        print(f"Error: '{target_directory}' is not a directory.")
        sys.exit(1)
    
    if not os.path.exists(updated_directory):
        print(f"Error: Updated directory '{updated_directory}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(updated_directory):
        print(f"Error: '{updated_directory}' is not a directory.")
        sys.exit(1)
    
    update_files(target_directory, updated_directory)
