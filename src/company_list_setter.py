import pandas as pd
from difflib import SequenceMatcher
import jellyfish
import os
from dotenv import load_dotenv
import google.generativeai as genai

class CompanyListSetter:
    def set_company_dataframe(self, file_path):
        company_df = pd.read_csv(file_path, encoding='utf-8-sig')
        self.company_df = company_df

        names_df = company_df["Korean Name"].drop_duplicates().reset_index(drop=True)
        names_df = names_df.sort_values().reset_index(drop=True) # Sort the names alphabetically
        
        self.ETF_df = company_df[company_df["ETF"] == "Y"]

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
    def __init__(self):
        load_dotenv()
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

        genai.configure(api_key = GOOGLE_API_KEY)
        self.LLM_corrector = genai.GenerativeModel(model_name="gemini-1.5-flash")

        response = self.LLM_corrector.generate_content("안녕, 반가워.")
        print(response.text)

    def correct_ocr_typo(self, OCR_result_df):
        """
        OCR 결과가 담긴 DataFrame을 쉘로우 카피해서 원본 회사명과 비교한 뒤,
        가장 유사한 회사명으로 고칩니다. 이 과정에서 원본 OCR_result_df에 수정을 가합니다.
        """
        # DEBUG
        # self.company_names_df.to_csv(os.path.join(os.getcwd(), "output/company_names.csv"), index=False, encoding='utf-8-sig')  # Save the company names to a CSV file
        # print("회사명 데이터프레임 저장됨\n")

        for ocr_index, ocr_row in OCR_result_df.iterrows():
            matched = self.ETF_df[self.ETF_df["Symbol"] == ocr_row["종목명"]]
            if not matched.empty:
                # print(matched) # DEBUG
                OCR_result_df.at[ocr_index, "종목명"] = matched.iloc[0]["Korean Name"]
                continue
            
            # 앞 철자 기준으로 유사도 점수 비교를 지원하는 부분
            # 전체 리스트와 비교하는 것과 속도가 큰 차이 없는데 정확도는 떨어져서 삭제제
            # ocr_fw = ocr_row["종목명"][0] # ocr_first_word
            # if '가' <= ocr_fw <= '힣': ocr_fl = self.divide_to_chosung(ocr_fw) # 한글일 경우 자모까지 슬라이싱
            # else: ocr_fl = ocr_fw # 숫자, 영문일 경우 그대로 사용

            # for company_index, company_row in self.company_names_df.iterrows():
            #     # print(f"[DEBUG] OCR Index: {ocr_index}, Company Index: {company_index}, OCR First Word: {ocr_fl}, Company First Letter: {company_row['First Letter']}")
            #     if ocr_fl == company_row["First Letter"]:
            #         scoring_lower_bound = company_row["FL Index"] # 유사도 점수를 평가할 최소 인덱스 위치
            #         scoring_upper_bound = self.company_names_df.loc[company_index + 1, "FL Index"] # 유사도 점수를 평가할 최대 인덱스 위치 + 1
            #         break
            
            # 전체체 범위에 대해 유사도 점수를 계산
            max_similarity = 0
            corrected_name = ocr_row["종목명"]

            scoring_lower_bound = 0
            scoring_upper_bound = len(self.company_names_df["Korean Name"])

            candidates = []

            for i in range(scoring_lower_bound, scoring_upper_bound):
                # current_similarity = SequenceMatcher(None, ocr_row["종목명"], self.company_names_df.loc[i, "Korean Name"]).ratio()
                name_on_dataframe = self.company_names_df.loc[i, "Korean Name"]
                current_similarity = jellyfish.jaro_winkler_similarity(ocr_row["종목명"], name_on_dataframe)
                if current_similarity > 0.6: 
                    candidates.append(name_on_dataframe)
                
                # 최종적으로 similarity가 가장 높은 회사명이 저장됨
                # if max_similarity < current_similarity:
                #     max_similarity = current_similarity
                #     corrected_name = name_on_dataframe
            
            candidates_str = ", ".join(candidates)
            
            LLM_prompt = """You must correct the typo of OCR Result. You are going to get one OCR result and candidates for the correct answer.
            Your answer must be consisted with only corrected company's name. Do not include other things.

            User: OCR result is 언비디아. Candidates are 메타비아, 아우디아, 엔비디아, 젠비아
            Answer: 엔비디아
            
            User: OCR result is 애플. Candidates are 심플, 애즈, 애플, 애플랙
            Answer: 애플
            
            User: OCR result is 프록터 앤드 검블. Candidates are P&G(프록터 & 갬블), 랜즈 엔드
            Answer: P&G(프록터 & 갬블)"""
            
            user_input = f"User: OCR result is {ocr_row['종목명']}. Candidates are {candidates_str}"
            LLM_input = f"{LLM_prompt}\n\n{user_input}\nAnswer:"

            response = self.LLM_corrector.generate_content(LLM_input)
            # print(response.text.strip()) # For Debug

            OCR_result_df.at[ocr_index, "종목명"] = response.text.strip()
    
    def correct_ocr_figures(self, OCR_result_df):
        """ This method corrects unnecessary characters in OCR results.
        This method does shallow copy from the original dataframe, so corrects the original dataframe directly."""

        for ocr_idx, ocr_row in OCR_result_df.iterrows():
            ocr_price = ocr_row["평가금액"]
            ocr_shares = ocr_row["보유량"]

            if ocr_price is not None:
                ocr_price = ocr_price.replace("원", "")
                ocr_price = ocr_price.replace(",", "")

            if ocr_shares is not None:
                ocr_shares = ocr_shares.replace("주", "")

            OCR_result_df.at[ocr_idx, "평가금액"] = ocr_price
            OCR_result_df.at[ocr_idx, "보유량"] = ocr_shares