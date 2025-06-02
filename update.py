# this script takes a content directory as input
# and updates the markdown files therein with the latest content
# however, if the corresponding markdown file in the content directory
# has been modified, then it will *not* be updated
# and instead the name of the file will be logged to a file called log.txt
# to tell if a file has been modified, we will use the file's frontmatter
# which will lack the 'generated' tag if it has been modified

# in order to best use this script, you should run it periodically
# and manually check the files that have already been modified to make sure
# they are up to date with the latest content

# TODO:
# - combine with raw_scrape.py to automatically update the content directory
# - compare new and old raw html files to see if there are any changes and update the content directory accordingly

import os
import frontmatter
import sys

def update_content(content_dir):
    """
    Update the markdown files in the content directory with the latest content.
    If a file has been modified, it will not be updated and its name will be logged.
    """
    log_file = 'log.txt'

    # ensure the log file exists
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write("# Update Log\n")
    
    files = os.listdir(content_dir)

    already_modified = set()
    updated_files = set()
    error_files = set()


    for file in files:
        file_path = os.path.join(content_dir, file)
        
        # check if the file is a markdown file
        # shouldn't be necessary, but just in case
        if not file.endswith('.md'):
            continue
        
        # read the content of the file
        with open(file_path, 'r', encoding='utf-8') as f:
            metadata, content = frontmatter.parse(f.read())
            metadata_tags = metadata['tags'] if 'tags' in metadata else []

        # if there are no tags, then we assume the file has been modified
        if not metadata_tags or 'generated' not in metadata_tags:
            # log the file name
            already_modified.add(file)
            continue

        # otherwise, we update the file with the latest content
        # taken from the parsed directory
        parsed_file_path = os.path.join('parsed', file)
        if os.path.exists(parsed_file_path):
            with open(parsed_file_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
            
            # write the new content to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            updated_files.add(file)
        else:
            # if the parsed file does not exist, log the error
            error_files.add(file)

    # write the log file
    with open(log_file, 'a', encoding='utf-8') as log:
        if already_modified:
            log.write("# Files that were not updated (modified):\n")
            for file in already_modified:
                log.write(f"{file}\n")
        
        if updated_files:
            log.write("# Files that were updated:\n")
            for file in updated_files:
                log.write(f"{file}\n")
        
        if error_files:
            log.write("# Files that could not be updated (missing parsed content):\n")
            for file in error_files:
                log.write(f"{file}\n")

if __name__ == "__main__":
    # take the content directory as an argument
    if len(sys.argv) != 2:
        print("Usage: python update.py <content_directory>")
        sys.exit(1)
    content_directory = sys.argv[1]
    if not os.path.exists(content_directory):
        print(f"Content directory {content_directory} does not exist.")
        sys.exit(1)
    update_content(content_directory)
    print("Content update completed. Check log.txt for any modified files.")
