import easyocr
import cv2
import os

class ImageManager:
    def image_path_creater(self, input_str):
        image_names = input_str.split(",")
        image_paths = []
        current_path = os.getcwd()
        for name in image_names:
            name = name.strip()
            image_paths.append(os.path.join(os.getcwd(), "inputs/images", name))
        
        return image_paths

class OCRreader:
    def __init__(self, lang_list):
        self.reader = easyocr.Reader(lang_list, gpu=False)
        self.img = None
        self.result = None
        self.stockDict = {} # dictionary of stock names and shares
    
    def read_image(self, image_path):
        # Load the image using OpenCV
        # self.img = None
        # self.result = None
        # self.stockDict = {} # initialize stockDict as an empty dictionary

        self.img = cv2.imread(image_path)
        self.img_height, self.img_width = self.img.shape[:2]
        if self.img is None:
            print(f"Error: Unable to read image at {image_path}")
    
    def perform_ocr(self):
        if self.img is None:
            print("Error: No image loaded. Please load an image first.")
            return
        
        # Perform OCR on the loaded image
        # Save text's list to self.result
        self.result = self.reader.readtext(self.img)

        return self.result

    def return_image(self):
        return self.img
    
    def return_stockDict(self):
        return self.stockDict
    
    def process_result(self):
        """ Process the OCR results to extract stock names, shares, and prices."""

        if self.result is None:
            print("Error: No OCR result available. Please perform OCR first.")
            return
        
        for (bbox, text, prob) in self.result:
            """ stockDict의 key는 종목명, value는 [평가금액, 보유량]의 리스트입니다. """
            lh_x_ratio = bbox[0][0] / self.img_width
            rh_x_ratio = bbox[1][0] / self.img_width

            # print(f"[DEBUG] {self.img_width}")
            # print(lh_x_ratio, text)

            if 250/1440 < lh_x_ratio < 270/1440 :
                # print(lh_x_ratio, text)
                if('주' not in text):
                    self.stockDict[text] = [] # name of stock
                else: # shares of stock
                    last_key = list(self.stockDict.keys())[-1]
                    self.stockDict[last_key].append(text)
            
            elif 1300/1440 < rh_x_ratio < 1340/1440 :
                # print(rh_x_ratio, text)
                if ('(' not in text) and (')' not in text): # price of stock
                    # print(f"Detected text: {text}, Probability: {prob:.2f}")
                    # print(f"Bounding box: ", bbox, "\n")
                    last_key = list(self.stockDict.keys())[-1]
                    self.stockDict[last_key].append(text)
        
        # print(f"\n[DEBUG]: {self.stockDict}")
        df = self.dict_to_dataframe(self.stockDict)
        return df
    
    def show_result(self):
        if self.result is None:
            print("Error: No OCR result available. Please perform OCR first.")
            return
        
        # Show the OCR results
        for (bbox, text, prob) in self.result:
            top_left = tuple(map(int, bbox[0]))
            bottom_right = tuple(map(int, bbox[2]))

            cv2.rectangle(self.img, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(self.img, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("OCR Result", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def dict_to_dataframe(self, data):
        import pandas as pd

        rows = []
        for key, values in data.items():
            print(f"[DEBUG] {key}: {values}")
            if len(values) == 0:
                rows.append([key])
            elif len(values) < 2:
                price = values[0]
                rows.append([key, price])
            else:
                # price, shares = values
                price = values[0]
                shares = values[1]
                rows.append([key, price, shares])
        
        df = pd.DataFrame(rows, columns=['종목명', '평가금액', '보유량'])

        return df