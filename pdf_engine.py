import os

def generate_pdf(tex_path):
    output_dir = os.path.dirname(tex_path)
    os.system(f'pdflatex -interaction=nonstopmode -output-directory="{output_dir}" "{tex_path}"')
    
    # Cleanup auxiliary files created by pdflatex
    base_name = os.path.splitext(tex_path)[0]
    for ext in ['.aux', '.log', '.out', '.fls', '.fdb_latexmk', '.synctex.gz']:
        file_to_remove = base_name + ext
        if os.path.exists(file_to_remove):
            try:
                os.remove(file_to_remove)
            except:
                pass