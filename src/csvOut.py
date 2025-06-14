import pandas as pd

class CSVout:
    def __init__(self, filename):
        self.filename = filename

    def write(self, data):
        rows = []
        for key, values in data.items():
            if len(values) < 2:
                price = values[0]
                rows.append([key, price])
            else:
                price = values[0]
                shares = values[1]
                rows.append([key, price, shares])
        
        df = pd.DataFrame(rows, columns=['종목명', '평가금액', '보유량'])
        df.to_csv(self.filename, index=False, encoding='utf-8-sig')

        return df