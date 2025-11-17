import os
import re
from tqdm import tqdm

def fix_setext_headers(text):
    """
    convert setext-style headers (underlined with dashes) to ATX-style headers.
    skips YAML frontmatter.
    
    example:
        header?
        ------
        
        becomes:
        
        ### header?
    """
    lines = text.split('\n')
    result = []
    i = 0
    
    # check if file starts with yaml frontmatter and skip it
    if lines and lines[0].strip() == '---':
        result.append(lines[0])
        i = 1
        # find the closing ---
        while i < len(lines):
            result.append(lines[i])
            if lines[i].strip() == '---':
                i += 1
                break
            i += 1
    
    while i < len(lines):
        # check if next line exists and is an underline
        if i + 1 < len(lines):
            current_line = lines[i]
            next_line = lines[i + 1]
            
            # check if next line is all dashes (at least 3)
            if re.match(r'^-{3,}$', next_line.strip()) and current_line.strip():
                # convert to ATX header (level 3)
                result.append(f'### {current_line.strip()}')
                i += 2  # skip both the header line and underline
                continue
        
        result.append(lines[i])
        i += 1
    
    return '\n'.join(result)

def fix_code_blocks(text):
    """
    convert standalone inline code blocks into fenced code blocks with 'gse' language.
    combines consecutive code blocks or code blocks separated only by blank lines.
    
    example:
        `ABS(-2)`
        `ABS(A2)`
        
        becomes:
        
        ```gse
        ABS(-2)
        ABS(A2)
        ```
    """
    lines = text.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # check if this line is a standalone inline code block
        if stripped.startswith('`') and stripped.endswith('`') and stripped.count('`') == 2:
            # collect consecutive code blocks (with possible blank lines between)
            code_lines = [stripped[1:-1]]  # remove the backticks
            j = i + 1
            
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith('`') and next_line.endswith('`') and next_line.count('`') == 2:
                    code_lines.append(next_line[1:-1])
                    j += 1
                elif next_line == '':
                    # blank line - peek ahead to see if there's another code block
                    k = j + 1
                    while k < len(lines) and lines[k].strip() == '':
                        k += 1
                    if k < len(lines):
                        next_non_blank = lines[k].strip()
                        if next_non_blank.startswith('`') and next_non_blank.endswith('`') and next_non_blank.count('`') == 2:
                            j = k
                            continue
                    break
                else:
                    break
            
            # create a fenced code block
            result.append('```gse')
            result.extend(code_lines)
            result.append('```')
            i = j
        else:
            result.append(line)
            i += 1
    
    return '\n'.join(result)

def fix_google_sheets_errors(text):
    """
    wrap Google Sheets error codes in inline code blocks.
    only affects errors that are not already in code blocks.
    
    errors: #NULL!, #DIV/0!, #VALUE!, #REF!, #NAME?, #NUM!, #N/A, #ERROR
    """
    # pattern to split text into inline code and normal text
    pattern = r'(`[^`]+`)|([^`]+)'
    
    # regex to match Google Sheets errors (not in code blocks)
    error_regex = re.compile(r'(#NULL!|#DIV/0!|#VALUE!|#REF!|#NAME\?|#NUM!|#N/A|#ERROR)')
    
    new_text = ''
    parts = re.findall(pattern, text)
    
    for code, normal in parts:
        if code:
            # already in code block, keep as is
            new_text += code
        elif normal:
            # wrap errors in backticks
            fixed = error_regex.sub(r'`\1`', normal)
            new_text += fixed
    
    return new_text

def fix_dollar_signs(text):
    """
    escape literal $ so they are not interpreted as LaTeX delimiters.
    does not modify:
    - inline code (`...`)
    - fenced code blocks (```...```)
    - already-escaped $
    """
    # split into fenced code, inline code, or normal text
    # group 1: fenced code block
    # group 2: inline code
    # group 3: normal text
    pattern = re.compile(
        r'(```[\s\S]*?```)|'     # fenced code
        r'(`[^`]+`)|'            # inline code
        r'([^`]+)',              # normal text
        re.MULTILINE
    )

    def escape_dollars(segment):
        # replace unescaped $ with \$
        return re.sub(r'(?<!\\)\$', r'\$', segment)

    parts = pattern.findall(text)
    result = []

    for fenced, inline, normal in parts:
        if fenced:
            result.append(fenced)
        elif inline:
            result.append(inline)
        elif normal:
            result.append(escape_dollars(normal))

    return ''.join(result)

def fix_links(text, valid_names):
    """
    convert markdown links to wikilinks where appropriate.
    
    rules:
    - links starting with '//' get 'https:' prepended
    - links starting with '/' are checked against valid_names for wikilink conversion
    - links starting with 'http' are checked against valid_names for wikilink conversion
    - function names are cleaned (remove backticks and ' function' suffix)
    """
    link_regex = re.compile(r'\[(.*?)\]\((.*?)\)')
    
    def replacer(match):
        name, url = match.groups()
        
        if url.startswith('//'):
            # add https: to the url
            url = 'https:' + url
            return f'[{name}]({url})'
        
        elif url.startswith('/'):
            cleaned_name = name.replace('`', '')
            cleaned_name = re.sub(r' function$', '', cleaned_name)
            
            if cleaned_name in valid_names:
                return f'[[{cleaned_name}]]'
            else:
                return f'[{name}](https://support.google.com{url})'
        
        elif url.startswith('http'):
            cleaned_name = name.replace('`', '')
            cleaned_name = re.sub(r' function$', '', cleaned_name)
            
            if cleaned_name in valid_names:
                return f'[[{cleaned_name}]]'
            else:
                return f'[{name}]({url})'
        
        return match.group(0)
    
    return link_regex.sub(replacer, text)

def fix_syntax_headers(text):
    """
    some files are missing a Syntax section
    but may have analogous. this function just
    replaces analogous sections with a Syntax header
    """
    # split into fenced code, inline code, or normal text
    # group 1: fenced code block
    # group 2: inline code
    # group 3: normal text
    pattern = re.compile(
        r'(```[\s\S]*?```)|'     # fenced code
        r'(`[^`]+`)|'            # inline code
        r'([^`]+)',              # normal text
        re.MULTILINE
    )

    def replace_header(segment):
        return re.sub(r'Parts of a.*\s', 'Syntax', segment)

    parts = pattern.findall(text)
    result = []

    for fenced, inline, normal in parts:
        if fenced:
            result.append(fenced)
        elif inline:
            result.append(inline)
        elif normal:
            result.append(replace_header(normal))

    return ''.join(result)


def convert_bullet_lists(text):
    """
    convert all * bullet lists to - bullet lists.
    """
    lines = text.split('\n')
    result = []
    
    for line in lines:
        # match lines that start with optional whitespace, then *, then a space
        if re.match(r'^(\s*)\*\s', line):
            # Replace the * with -
            line = re.sub(r'^(\s*)\*\s', r'\1- ', line)
        result.append(line)
    
    return '\n'.join(result)


def process_markdown_file(text, valid_names):
    """
    apply all markdown fixes to a text document.
    
    args:
        text: the markdown text to process
        valid_names: list of valid document names for wikilink conversion
        
    returns:
        the processed markdown text
    """
    text = fix_google_sheets_errors(text)
    text = fix_links(text, valid_names)
    text = fix_setext_headers(text)
    text = fix_dollar_signs(text)
    text = fix_code_blocks(text)
    text = fix_syntax_headers(text)
    text = convert_bullet_lists(text)
    return text


def process_directory(directory='parsed'):
    """
    process all markdown files in a directory with the markdown fixes.
    """
    files = os.listdir(directory)
    
    # get list of valid names for wikilink conversion
    valid_names = [file[:-3] for file in files if file.endswith('.md')]
    
    for file in tqdm(files, desc='Processing markdown files'):
        if file == ".obsidian" or not file.endswith('.md'):
            continue
        
        filepath = os.path.join(directory, file)
        
        # read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # process the content
        content = process_markdown_file(content, valid_names)
        
        # write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


if __name__ == '__main__':
    process_directory()
