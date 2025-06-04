from OCR import OCRreader
from csvOut import CSVout
from company_list_setter import CompanyListSetter, OCRCorrector
import os

def main():
    print("포트폴리오 정리 OCR 프로그램입니다.")
    print("made by An Chaewoong, cwan0419@postech.ac.kr")

    # 1. OCR을 수행할 이미지 파일의 이름을 입력받습니다.
    img_name = input("이미지 파일의 이름을 입력하세요.(확장자 포함): ")
    #image_path = "images/" + img_name  # Path to the image file
    current_path = os.getcwd()
    image_path = os.path.join(current_path, "inputs/images", img_name)  # Path to the image file

    #2. OCR을 수행할 인스턴스를 생성합니다.
    screenshotOCR = OCRreader(lang_list=['en','ko'])

    #3. 출력될 csv 파일의 경로를 지정하고 CSV파일을 출력할할 인스턴스를 생성합니다.
    output_path = os.path.join(current_path, "output/output.csv")
    csvMaker = CSVout("output/output.csv")

    #4. OCR을 수행합니다.
    screenshotOCR.read_image(image_path)  # Load the image
    screenshotOCR.perform_ocr()  # Perform OCR on the image
    final_result = screenshotOCR.process_result()  # Process the OCR results

    print("[DEBUG] OCR 결과:", final_result)  # Print the OCR results for debugging

    #5. OCR 결과를 CSV 파일로 저장합니다.
    OCR_result_df = csvMaker.write(final_result)  # Write the results to a CSV file

    #6. OCR의 오류를 교정하기 위해 회사명 데이터프레임을 생성합니다.
    # 회사명 데이터프레임에는 유사도 점수 비교를 쉽게 하기 위해 유니코드 인덱스가 저장되어 있습니다.
    current_path = os.getcwd()
    csv_path = os.path.join(current_path, "inputs/company_info.csv")

    # company_list_setter = CompanyListSetter()
    # company_list_setter.set_company_dataframe(csv_path)  # Set the company names from the CSV file
    # company_names_df = company_list_setter.get_company_dataframe()  # Get the company names DataFrame
    # company_names_df.to_csv(os.path.join(current_path, "output/company_names.csv"), index=False, encoding='utf-8-sig')  # Save the company names to a CSV file

    OCR_Corrector = OCRCorrector()
    OCR_Corrector.set_company_dataframe(csv_path)
    OCR_Corrector.get_company_dataframe()  # Get the company names DataFrame
    OCR_Corrector.correct_ocr_result(OCR_result_df)
    OCR_result_df.to_csv(os.path.join(current_path, "output/corrected.csv"), index=False, encoding='utf-8-sig')  # Save the corrected OCR results to a CSV file

    #7. OCR 결과의 회사명을 교정합니다.
    
    
    print("OCR이 완료되었습니다.\noutput 폴더의 output.csv 파일을 확인하세요.")
    
if __name__=="__main__":
    main()