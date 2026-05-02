import os

def generate_pdf(tex_path):
    output_dir = os.path.dirname(tex_path)
    os.system(f"pdflatex -interaction=nonstopmode -output-directory={output_dir} {tex_path}")