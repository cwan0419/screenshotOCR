import pandas as pd
from difflib import SequenceMatcher
import os

class CompanyListSetter:
    def set_company_dataframe(self, file_path):
        company_df = pd.read_csv(file_path, encoding='utf-8-sig')
        names_df = company_df["Korean Name"].drop_duplicates().reset_index(drop=True)
        names_df = names_df.sort_values().reset_index(drop=True) # Sort the names alphabetically

        names_df = names_df.to_frame(name='Korean Name')  # Convert Series to DataFrame
        names_df["Dict"] = pd.NA
        names_df["Dict Index"] = pd.NA
        names_df["First Letter"] = pd.NA
        names_df["FL Index"] = pd.NA

        unicode_flag = 0
        unicode_flag_divided = 0
        dict_index = 0
        letter_index = 0
        for name_index, row in names_df.iterrows():
            first_word = row["Korean Name"][0]
            if '가' <= first_word <= '힣': first_letter = self.divide_to_chosung(first_word) # 한글일 경우 자모까지 슬라이싱
            else: first_letter = first_word # 숫자, 영문일 경우 그대로 사용

            # 첫 번째 글자 기반 인덱싱
            if ord(first_word) > unicode_flag:
                unicode_flag = ord(first_word)
                names_df.loc[dict_index, "Dict"] = first_word
                names_df.loc[dict_index, "Dict Index"] = name_index
                dict_index += 1

            # 첫 번째 자모 기반 인덱싱. 예를 들어 '가'는 'ㄱ'으로, '나'는 'ㄴ'으로 인식
            if ord(first_letter) > unicode_flag_divided:
                unicode_flag_divided = ord(first_letter)
                names_df.loc[letter_index, "First Letter"] = first_letter
                names_df.loc[letter_index, "FL Index"] = name_index
                letter_index += 1
        
        total_data_length = len(names_df["Korean Name"])
        names_df.loc[dict_index, "Dict"] = names_df.loc[letter_index, "First Letter"] = "END"
        names_df.loc[dict_index, "Dict Index"] = names_df.loc[letter_index, "FL Index"] = total_data_length

        self.company_names_df = names_df
    
    def get_company_dataframe(self):
        return self.company_names_df

    def divide_to_chosung(self, char):
        list_chosung = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        char_code = ord(char) - ord('가')
        chosung_index = char_code // 588
        return list_chosung[chosung_index]

class OCRCorrector(CompanyListSetter):
    def correct_ocr_result(self, OCR_result_df):
        """
        OCR 결과가 담긴 DataFrame을 쉘로우 카피해서 원본 회사명과 비교한 뒤,
        가장 유사한 회사명으로 고칩니다. 이 과정에서 원본 OCR_result_df에 수정을 가합니다.
        """
        # DEBUG
        self.company_names_df.to_csv(os.path.join(os.getcwd(), "output/company_names.csv"), index=False, encoding='utf-8-sig')  # Save the company names to a CSV file
        print("회사명 데이터프레임 저장됨\n")

        for ocr_index, ocr_row in OCR_result_df.iterrows():
            ocr_fw = ocr_row["종목명"][0] # ocr_first_word
            if '가' <= ocr_fw <= '힣': ocr_fl = self.divide_to_chosung(ocr_fw) # 한글일 경우 자모까지 슬라이싱
            else: ocr_fl = ocr_fw # 숫자, 영문일 경우 그대로 사용

            for company_index, company_row in self.company_names_df.iterrows():
                # print(f"[DEBUG] OCR Index: {ocr_index}, Company Index: {company_index}, OCR First Word: {ocr_fl}, Company First Letter: {company_row['First Letter']}")
                if ocr_fl == company_row["First Letter"]:
                    scoring_lower_bound = company_row["FL Index"] # 유사도 점수를 평가할 최소 인덱스 위치
                    scoring_upper_bound = self.company_names_df.loc[company_index + 1, "FL Index"] # 유사도 점수를 평가할 최대 인덱스 위치 + 1
                    break
            
            # 해당 범위에 대해 유사도 점수를 계산
            max_similarity = 0
            corrected_name = ocr_row["종목명"]

            for i in range(scoring_lower_bound, scoring_upper_bound):
                current_similarity = SequenceMatcher(None, ocr_row["종목명"], self.company_names_df.loc[i, "Korean Name"]).ratio()
                print(f"[DEBUG] Comparing OCR Name: {ocr_row['종목명']} with Company Name: {self.company_names_df.loc[i, 'Korean Name']}, Similarity: {current_similarity}")
                if max_similarity < current_similarity:
                    max_similarity = current_similarity
                    corrected_name = self.company_names_df.loc[i, "Korean Name"] # 최종적으로 similarity가 가장 높은 회사명이 저장됨
            
            OCR_result_df.at[ocr_index, "종목명"] = corrected_name