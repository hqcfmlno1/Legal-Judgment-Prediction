import docx
import os  
import re 

base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docx_file_path = os.path.join(base_directory,'data','luat.docx')

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
for article in articles:
    raw_title = re.findall(r"Điều\s+\d+\..*?(?=\n)", article)
    if len(raw_title)>0:
        raw_title_old = re.findall(r"Điều\s+\d+\..*?(?=\n)", article)[0]
        processed_title = re.sub(r"\s*\[.*?\]", '', raw_title_old)        
        print(processed_title)
    else: 
        print("null")

print (len(articles))