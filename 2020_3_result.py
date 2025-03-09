import pdfplumber
import pandas as pd
import re

#전체 데이터
excel_data = [] 

number_data1 = []
number_data2 = []
text_part_data = []

start_row = 1  # 기본값: 1행부터
end_row = 20    # 최대 20행까지 출력
start_column = 1  # 1열부터
end_column = 10   # 10열까지


# PDF 파일 열기
with pdfplumber.open('2020_사업별 세부설명자료1.pdf') as pdf:
    pages = pdf.pages
    split_pages = []
    match1 = []

    # 페이지 순회
    for page_num, page in enumerate(pages, start=1):
        #print(page_num)
        text = page.extract_text()
        tables = page.extract_tables()

        #□기호와 함께있는 단어들 수집
        keyword = r'□\s*(.+?)\s*(?=\n)'
        matches = re.findall(keyword, text)
       
        for table_index, table in enumerate(tables, start=1):
            
            #초기화
            first_table = None

            if len(matches) == 0:
            # '□'기호와 함께 있는 단어가 없다면
            # (첫번째 장에 '□산출근거' 단어가 있고 두번째 페이지에는 산출근거표만 있다는 결과)
                first_table = tables[0] #해당페이지의 첫번째표 데이터수집

            elif len(matches) > 0:
                
                for i in range(0, len(matches)):
                   
                    if matches[i] == "산출근거":
                        
                        if len(matches) == len(tables)+1:
                          first_table=tables[i-1]
                        
                        elif len(matches) > len(tables)+1:
                          first_table=None
                        
                        elif len(matches) == len(tables):
                          first_table=tables[i]
                        
                        elif len(matches) < len(tables):
                          first_table=tables[i+1] 

        if first_table is not None :
        # 지정한 행 범위만 순회
            for row_num in range(start_row - 1, min(end_row, len(first_table))):  
                row = first_table[row_num]  # 행은 0부터 시작
                row_data = [
                    str(row[col_num - 1]).replace('[', '').replace(']', '').replace('None', '').strip()
                    for col_num in range(start_column, min(end_column + 1, len(row)+1))
                ]              
                # 빈 값(공백 또는 None)을 제외한 데이터만 새로운 행으로 추가
                cleaned_row = [cell for cell in row_data if cell != '']       
                print(cleaned_row)
                if row[0] == "편성목별" or row[0] == "계":
                    number_data1.append('000')
                    number_data2.append('000')
                    text_part_data.append(row[0])
                else:
                    # '123 abc'이런식으로 되어있는 단어들 찾기
                    match_0 = re.findall(r"(\d+)\s*(\D+)", row[0])
                    if match_0:
                        # 한 셀안에 '123 abc'형식으로 되어있는 단어가 1개 이상이 있는경우
                        if len(match_0) >1:
                            
                            for i in range(1, len(match_0)):
                                #print(cleaned_row)
                                excel_data.append(cleaned_row)
                        for num, text in match_0:
                            number_data1.append(num)  # 숫자 부분
                            number_data2.append('000')  # 기본값
                            text_part_data.append(text)
                
                if row[1] != "None" and row[1] is not None and not any(',' in str(item) for item in row[1]):

                    match_1 = re.findall(r"(\d+)\s*(\D+)", row[1])

                    if match_1:
                        if len(match_1) >1:
                            #'match_1 - 1' 길이만큼 행 추가
                            for i in range(1, len(match_1)):
                                # print(cleaned_row)
                                excel_data.append(cleaned_row)
                        #print(len(match_1))
                        for num, text in match_1:
                            number_data1.append('')  # 첫 번째 열은 빈값으로
                            number_data2.append(num)  # 숫자 부분
                            text_part_data.append(text)

                # 빈 값이 아닌 셀들만 excel_data에 추가
                if cleaned_row:  # 빈 행은 추가하지 않음
                    excel_data.append(cleaned_row)


# 수집한 데이터를 Pandas DataFrame으로 변환
df = pd.DataFrame(excel_data)

df.insert(0, '빈열', number_data1) 
df.insert(1, '빈열1', number_data2)
df.insert(2, '빈열2', text_part_data)  

# 엑셀 파일로 저장
df.to_excel('ex_table.xlsx', index=False, header=False)
print("엑셀 파일로 저장 완료!")