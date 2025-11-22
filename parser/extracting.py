import docx
import os  
import re 

base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docx_file_path = os.path.join(base_directory,'data','processed','luat.docx')

luat = docx.Document(docx_file_path)

# exact all the articles
text = ''
for para in luat.paragraphs:
    text+=para.text
    text+='\n'
pattern_correct = r"(Điều\s+\d+\..*?)(?=\s*Điều\s+\d+\.|Bộ luật Hình sự hết hiệu lực thi hành kể từ ngày Bộ luật này có hiệu lực thi hành.)"
articles = re.findall(pattern_correct, text, flags=re.DOTALL)
articles[-1]+="Bộ luật Hình sự hết hiệu lực thi hành kể từ ngày Bộ luật này có hiệu lực thi hành."

# process article titles

metadata = []
for article in articles:
    law_and_content = {}
    article = re.sub(r"\nChương\s+[IVXLCDM]+.*?\Z",'', article, flags=re.DOTALL)
    raw_title = re.findall(r"Điều\s+\d+\..*?(?=\n)", article)
    if len(raw_title)>0:
        raw_title_old = re.findall(r"Điều\s+\d+\..*?(?=\n)", article)[0]
        processed_title = re.sub(r"\s*\[.*?\]", '', raw_title_old)        
    else: 
        processed_title = "null"
    if processed_title != "null":
        law_and_content['title'] = processed_title
        law_and_content['content'] = article.replace(raw_title_old, '')
        metadata.append(law_and_content)

# save metadata to a file
import json
output_file_path = os.path.join(base_directory,'data','processed','luat_hinh_su_metadata.json')
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=4)

