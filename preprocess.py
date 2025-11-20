import os
import win32com.client as win32

base_directory = os.path.dirname(os.path.abspath(__file__))
doc_file_path = os.path.join(base_directory,'luat.doc')

def doc_to_docx(doc_file_path):
    word = win32.Dispatch('Word.Application')
    word.Visible = False
    doc = word.Documents.Open(doc_file_path)
    doc_file_path = doc_file_path + 'x'
    doc.SaveAs(doc_file_path, FileFormat=16)  
    doc.Close()
    word.Quit()
    return doc_file_path

doc_to_docx(doc_file_path)