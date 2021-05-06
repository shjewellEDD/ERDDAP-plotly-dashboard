import pandas as pd
import time

path = "C:\\Users\\jewell\\Documents\\ERRDAP Testing\\GoM 667nm Modis Reflectance.csv"


t = time.time()
data = pd.read_csv(path)
print("Read time: ", time.time()-t)

t = time.time()


drop_list = []

data.dropna()

# for n in range(1,len(data)):
#
#     if pd.isnull(data["r667"][n]):
#
#         drop_list.append(n)
#
# data.drop(labels=drop_list, inplace=True)

print("Process time: ", time.time()-t)

