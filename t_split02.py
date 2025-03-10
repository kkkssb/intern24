import pdfplumber
import PyPDF2
import re
import os

# 폴더 경로 지정하기
path = ' '

def split_pdf_on_keyword(file, directory_to_save, split_start_count):
    # 디렉터리가 없다면 생성
    if not os.path.exists(directory_to_save):
        os.makedirs(directory_to_save)

    split_count = split_start_count
    pdf_writer = PyPDF2.PdfWriter()
    keyword_found = False 
    original_filename = os.path.basename(file)

    # pdfplumber로 텍스트와 테이블 확인
    with pdfplumber.open(file) as pdf:
        for page_num in range(len(pdf.pages)):
            # page_text = pdf.pages[page_num].extract_text()
            tables = pdf.pages[page_num].extract_tables()

            # 테이블 내 특정 조건 확인 및 분할
            if len(tables) > 0:   
                for table_index, table in enumerate(tables, start=1):
                    if len(table) > 0 and len(table[0]) > 2:        
                        if table[0][2] == '소관':
                        # 조건이 만족되면 현재까지의 페이지를 하나의 파일로 저장
                            if keyword_found:
                                output_filename = f"{directory_to_save}/2022_02_{str(split_count).zfill(5)}.pdf"
                                with open(output_filename, "wb") as output_pdf:
                                    pdf_writer.write(output_pdf)
                                split_count += 1
                                pdf_writer = PyPDF2.PdfWriter()  # 새로운 PdfWriter 생성
                            keyword_found = True
            if keyword_found:                
                # 현재 페이지를 pdf_writer에 추가
                with open(file, "rb") as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    page = reader.pages[page_num]
                    pdf_writer.add_page(page)

    # 마지막 PDF 부분 저장
    if pdf_writer.pages:
        output_filename = f"{directory_to_save}/2022_02_{str(split_count).zfill(5)}.pdf"
        with open(output_filename, "wb") as output_pdf:
            pdf_writer.write(output_pdf)
    created_files = split_count - split_start_count +1
    # 완료 메시지 출력
    print(f"PDF 분할이 완료되었습니다. {split_count}개의 파일이 생성되었습니다. {created_files}개 {original_filename}")
    return split_count+1

# 사용 예시
# 해당 폴더 안에 있는 파일 리스트 불러오기
total_split_count = 1  # 총 분할 수 초기화
for file_name in os.listdir(path):
    file_path = os.path.join(path, file_name)
    # PDF 파일인지 확인
    if file_name.endswith('.pdf'):
        total_split_count = split_pdf_on_keyword(file_path, "output", total_split_count)