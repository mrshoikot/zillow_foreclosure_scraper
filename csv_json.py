import json 
import csv
import glob
import tqdm

folder = input("Enter county: ")+" County"
  
properties = []


  

def flattenjson(b, delim):
    val = {}
    for i in b.keys():
        if isinstance(b[i], dict):
            get = flattenjson(b[i], delim)
            for j in get.keys():
                val[i + delim + j] = get[j]
        else:
            val[i] = b[i]
            
    return val

for file in tqdm.tqdm(list(glob.glob(folder+'/*.json'))):
    properties.append(flattenjson(json.loads(open(file).read())['data']['property'], '__'))



 
  
# now we will open a file for writing 
data_file = open('csvs/'+folder+'_Foreclosure.csv', 'w') 
  
# create the csv writer object 
csv_writer = csv.writer(data_file) 
  
# Counter variable used for writing  
# headers to the CSV file 
count = 0
  
for emp in properties: 
    if count == 0: 
  
        # Writing headers of CSV file 
        header = emp.keys() 
        csv_writer.writerow(header) 
        count += 1
  
    # Writing data of CSV file 
    csv_writer.writerow(emp.values()) 
  
data_file.close() 