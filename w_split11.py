import PyPDF2
import re
import os

# 폴더 경로 지정하기
path = ' '


# PDF 분할 함수 정의
def split_pdf_on_keyword(file, directory_to_save, split_start_count, keyword, end_keyword_pattern):
    # 디렉터리가 없다면 생성
    if not os.path.exists(directory_to_save):
        os.makedirs(directory_to_save)

    # PDF 파일 열기
    pdf = PyPDF2.PdfReader(file)
    total_pages = len(pdf.pages)
    pdf_writer = PyPDF2.PdfWriter()
    split_count = split_start_count
    # 정규표현식 패턴 정의
    start_pattern = re.compile(re.escape(keyword))
    end_pattern = re.compile(end_keyword_pattern)
    keyword_found = False
    original_filename = os.path.basename(file)

    for page_num in range(total_pages):
        page = pdf.pages[page_num]
        text = page.extract_text()  # 텍스트 추출
        # print(text)

        # 시작 키워드가 발견된 페이지부터 저장 시작
        if start_pattern.search(text):
            keyword_found = True
            # 현재까지의 페이지를 하나의 파일로 저장
            if pdf_writer.pages:
                output_filename = f"{directory_to_save}/2023_02_{str(split_count).zfill(5)}.pdf"
                with open(output_filename, "wb") as output_pdf:
                    pdf_writer.write(output_pdf)
                split_count += 1
                pdf_writer = PyPDF2.PdfWriter()  # 새로운 PdfWriter 생성

        # 키워드가 발견된 이후의 페이지부터 pdf_writer에 추가
        if keyword_found:
            pdf_writer.add_page(page)

            # 종료 키워드가 발견되면 두 페이지 전까지 PDF 저장 후 중단
            if end_pattern.search(text) and pdf_writer.pages:
                if len(pdf_writer.pages) > 2:
                    # 두 페이지 전까지의 내용 저장
                    output_writer = PyPDF2.PdfWriter()
                    for p in pdf_writer.pages[:-3]:  # 마지막 두 페이지를 제외한 페이지 추가
                        output_writer.add_page(p)
                    
                    # 파일 저장
                    output_filename = f"{directory_to_save}/2023_02_{str(split_count).zfill(5)}.pdf"
                    with open(output_filename, "wb") as output_pdf:
                        output_writer.write(output_pdf)
                    split_count += 1
                    print(f"키워드분할됨{page_num}")
                # 새로운 PdfWriter 생성 및 키워드 플래그 리셋
                pdf_writer = PyPDF2.PdfWriter()
                keyword_found = False
                continue

    # 마지막 PDF 부분 저장
    if pdf_writer.pages and keyword_found:
        output_filename = f"{directory_to_save}/2023_02_{str(split_count).zfill(5)}.pdf"
        with open(output_filename, "wb") as output_pdf:
            pdf_writer.write(output_pdf)
    creat_count = split_count - split_start_count + 1

    # 완료 메시지 출력
    print(f"PDF 분할이 완료되었습니다. {split_count}개의 파일이 생성되었습니다. 총 {creat_count}개 {original_filename}")
    return split_count + 1

# 해당 폴더 안에 있는 파일 리스트 불러오기
total_split_count = 1  # 총 분할 수 초기화
for file_name in sorted(os.listdir(path)):
    file_path = os.path.join(path, file_name)
    # PDF 파일인지 확인
    if file_name.endswith('.pdf'):
        total_split_count = split_pdf_on_keyword(file_path, "2023세출1", total_split_count, keyword="사업 지원 형태", end_keyword_pattern=r"1.\s총\s괄")
