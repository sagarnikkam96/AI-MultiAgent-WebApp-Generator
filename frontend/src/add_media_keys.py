with open('i18n.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# Add media-related keys after buildError in each language section
media_keys = """    addMedia: '➕ Add Media',
    addMediaHint: 'Upload images, videos, or files to include in your website.',
    mediaGallery: 'Media Gallery',
    noMedia: 'No media uploaded yet. Click "Add Media" to upload files.',
    uploadPrompt: 'Choose files to upload',
    imageLabel: 'Image',
    videoLabel: 'Video',
    fileLabel: 'File',"""

# Find all occurrences of buildError and add media keys after each
import re

# Pattern to find buildError lines followed by closing brace
pattern = r"(    buildError: '[^']+',\n)(  \},)"

def replacement(match):
    return match.group(1) + media_keys + "\n" + match.group(2)

content = re.sub(pattern, replacement, content)

with open('i18n.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print('Added media keys to all languages')
