import easyocr
import cv2

class OCRreader:
    def __init__(self, lang_list):
        self.reader = easyocr.Reader(lang_list, gpu=False)
        self.img = None
        self.result = None
        self.stockNames = [] # list of stock names
        self.stockShares = [] # list of stock shares
        self.stockDict = {} # dictionary of stock names and shares
        self.criteria_x = 0 # x coordinate of the criteria line
    
    def read_image(self, image_path):
        # Load the image using OpenCV
        self.img = cv2.imread(image_path)
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
        if self.result is None:
            print("Error: No OCR result available. Please perform OCR first.")
            return
        
        # print(f"[DEBUG]:", type(self.result[7][0]))
        # This part saves the stock names, shares, and prices to a self.stockDict
        # This part distinguishes OCR results by the ratio of x coordinates and the text
        for (bbox, text, prob) in self.result:
            if ('평가금액' in text):
                self.criteria_x = bbox[0][0]
                
            elif self.criteria_x * 250 / 85 < bbox[0][0] < self.criteria_x * 270 / 85 :
                if('주' not in text):
                    self.stockDict[text] = [] # name of stock
                else: # shares of stock
                    last_key = list(self.stockDict.keys())[-1]
                    self.stockDict[last_key].append(text)
            
            elif self.criteria_x * 1310 / 85 < bbox[1][0] < self.criteria_x * 1330 / 85:
                if ('(' not in text) and (')' not in text): # price of stock
                    # print(f"Detected text: {text}, Probability: {prob:.2f}")
                    # print(f"Bounding box: ", bbox, "\n")
                    last_key = list(self.stockDict.keys())[-1]
                    self.stockDict[last_key].append(text)
        
        # print(f"\n[DEBUG]: {self.stockDict}")
        return self.stockDict
    
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