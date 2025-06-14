from OCR import OCRreader, ImageManager
from csvOut import CSVout
from company_list_setter import CompanyListSetter, OCRCorrector
import os
import pandas as pd

def main():
    print("포트폴리오 정리 OCR 프로그램입니다.")
    print("made by An Chaewoong, cwan0419@postech.ac.kr")

    current_path = os.getcwd()

    # 1. OCR을 수행할 이미지 파일의 이름을 입력받습니다.
    user_input = input("이미지 파일의 이름을 입력하세요.(확장자 포함): ")
    #image_path = "images/" + img_name  # Path to the image file
    image_manager = ImageManager()
    image_paths = image_manager.image_path_creater(user_input)  # Create the image path from the input string
    print(f"[DEBUG] {image_paths}")  # Print the image paths for debugging

    #2. OCR을 수행할 인스턴스를 생성합니다.
    screenshotOCR = OCRreader(lang_list=['en','ko'])

    #3. 출력될 csv 파일의 경로를 지정하고 CSV파일을 출력할할 인스턴스를 생성합니다.
    output_path = os.path.join(current_path, "output/output.csv")
    csvMaker = CSVout("output/output.csv")

    #4. OCR을 수행합니다.
    final_results_df = []  # Initialize a list to store final results, Dictionaries' list.
    for image_path in image_paths:
        screenshotOCR.read_image(image_path)  # Load the image
        screenshotOCR.perform_ocr()  # Perform OCR on the image
        # screenshotOCR.show_result()
        result_in_df = screenshotOCR.process_result()  # Process the OCR results
        final_results_df.append(result_in_df)  # Append the result DataFrame to the list
    
    print("[DEBUG] DataFrame 리스트:\n", final_results_df)  # Print the list of DataFrames for debugging
    concatenated_df = pd.concat(final_results_df, ignore_index=True)  # Concatenate all DataFrames
    concatenated_df.drop_duplicates(subset='종목명', keep='first', inplace=True)  # Remove duplicates based on '종목명'
    print("[DEBUG] 최종 DataFrame:\n", concatenated_df)  # Print the concatenated DataFrame for debugging

    # print("[DEBUG] OCR 결과:", final_result)  # Print the OCR results for debugging

    #5. OCR 결과를 CSV 파일로 저장합니다.
    OCR_result_df = csvMaker.write(concatenated_df)  # Write the results to a CSV file
    concatenated_df.to_csv("output/output.csv", index=False, encoding='utf-8-sig')

    #6. OCR의 오류를 교정합니다. 교정 과정에는 jaro_winkler_similarity 계산과 LLM의 판단이 들어갑니다.
    # 회사명 데이터프레임에는 유사도 점수 비교를 쉽게 하기 위해 유니코드 인덱스가 저장되어 있습니다.
    current_path = os.getcwd()
    csv_path = os.path.join(current_path, "inputs/company_info.csv")

    # company_list_setter = CompanyListSetter()
    # company_list_setter.set_company_dataframe(csv_path)  # Set the company names from the CSV file
    # company_names_df = company_list_setter.get_company_dataframe()  # Get the company names DataFrame
    # company_names_df.to_csv(os.path.join(current_path, "output/company_names.csv"), index=False, encoding='utf-8-sig')  # Save the company names to a CSV file

    OCR_Corrector = OCRCorrector()
    OCR_Corrector.set_company_dataframe(csv_path)
    company_names_df = OCR_Corrector.get_company_dataframe()  # Get the company names DataFrame
    company_names_df.to_csv(os.path.join(current_path, "output/company_names.csv"), index=False, encoding='utf-8-sig')
    OCR_Corrector.correct_ocr_typo(concatenated_df)
    OCR_Corrector.correct_ocr_figures(concatenated_df)
    concatenated_df.to_csv(os.path.join(current_path, "output/LLM_corrected.csv"), index=False, encoding='utf-8-sig')  # Save the corrected OCR results to a CSV file    
    
    print("OCR이 완료되었습니다.\noutput 폴더의 output.csv 파일을 확인하세요.")
    
if __name__=="__main__":
    main()