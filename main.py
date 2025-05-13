from OCR import OCRreader
from csvOut import CSVout

def main():
    print("포트폴리오 정리 OCR 프로그램입니다.")
    print("made by An Chaewoong, cwan0419@postech.ac.kr")
    image_path = "images/screenshot.jpg"  # Path to the image file
    screenshotOCR = OCRreader(lang_list=['en','ko'])
    csvMaker = CSVout("output/output.csv")

    screenshotOCR.read_image(image_path)  # Load the image
    screenshotOCR.perform_ocr()  # Perform OCR on the image
    final_result = screenshotOCR.process_result()  # Process the OCR results
    csvMaker.write(final_result)  # Write the results to a CSV file
    print("OCR이 완료되었습니다.\n output 폴더의 output.csv 파일을 확인하세요.")

    # print(final_result)
    # screenshotOCR.show_result()  # Show the OCR results, for DEBUGGING
    
if __name__=="__main__":
    main()