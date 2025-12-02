"""utility to update markdown files from source to target directory.
respects the 'modified' tag in frontmatter to avoid overwriting manually edited files.
"""

import os
import sys
import shutil
import frontmatter
from datetime import datetime


def files_are_identical(path1, path2):
    """return true if two files have identical text content."""
    try:
        with open(path1, 'r', encoding='utf-8') as f1, \
             open(path2, 'r', encoding='utf-8') as f2:
            return f1.read() == f2.read()
    except Exception:
        return False


def update_files(target_dir, updated_dir):
    """update files in target directory from updated directory, respecting modifications."""
    log_file = 'update_log.txt'
    
    replaced_files = []
    skipped_modified_files = []
    unchanged_files = []
    new_files = []
    error_files = []
    
    updated_files = [f for f in os.listdir(updated_dir) if f.endswith('.md')]
    
    for filename in updated_files:
        updated_file_path = os.path.join(updated_dir, filename)
        target_file_path = os.path.join(target_dir, filename)
        
        try:
            if os.path.exists(target_file_path):
                # check if manually modified
                with open(target_file_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    metadata_tags = post.get('tags', [])
                
                if 'modified' in metadata_tags:
                    skipped_modified_files.append(filename)
                    continue

                # check if identical
                if files_are_identical(updated_file_path, target_file_path):
                    unchanged_files.append(filename)
                    continue

                # replace if not modified and content differs
                shutil.copy2(updated_file_path, target_file_path)
                replaced_files.append(filename)

            else:
                # does not exist — new file
                shutil.copy2(updated_file_path, target_file_path)
                new_files.append(filename)
        
        except Exception as e:
            error_files.append((filename, str(e)))
    
    # write log
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"# File Update Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if replaced_files:
            log.write(f"## Files Replaced ({len(replaced_files)}):\n")
            for file in sorted(replaced_files):
                log.write(f"  - {file}\n")
            log.write("\n")

        if unchanged_files:
            log.write(f"## Files Unchanged ({len(unchanged_files)}):\n")
            for file in sorted(unchanged_files):
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
        log.write(f"  - Unchanged: {len(unchanged_files)}\n")
        log.write(f"  - Skipped (modified): {len(skipped_modified_files)}\n")
        log.write(f"  - New files: {len(new_files)}\n")
        log.write(f"  - Errors: {len(error_files)}\n")
    
    # console summary
    print(f"file update completed!")
    print(f"  - replaced: {len(replaced_files)}")
    print(f"  - unchanged: {len(unchanged_files)}")
    print(f"  - skipped (modified): {len(skipped_modified_files)}")
    print(f"  - new files: {len(new_files)}")
    print(f"  - errors: {len(error_files)}")
    print(f"\ndetailed log written to: {log_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python update.py <target_directory> <updated_directory>")
        sys.exit(1)
    
    target_directory = sys.argv[1]
    updated_directory = sys.argv[2]
    
    if not os.path.exists(target_directory) or not os.path.isdir(target_directory):
        print(f"error: target directory '{target_directory}' is invalid.")
        sys.exit(1)
    
    if not os.path.exists(updated_directory) or not os.path.isdir(updated_directory):
        print(f"error: updated directory '{updated_directory}' is invalid.")
        sys.exit(1)
    
    update_files(target_directory, updated_directory)
