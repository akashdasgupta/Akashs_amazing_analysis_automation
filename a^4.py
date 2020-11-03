# -*- coding: utf-8 -*-
"""
@author: Akash Dasgupta
THIS IS THE BACKEND FOR THE 'AKASH'S AMAZING ANALYSIS AUTOMATOR (A^4)'. 

You have to run this using Origin's embeded python, as the 'originpro' module 
lives inside it. You can run this using the command 
"""

import os
import csv
try:
    import originpro as op
except ModuleNotFoundError:
    print("I couldn't find Origin! I guess you are debuging, which is cool."+
          "\nJust remember, if you have not commented out all the Origin garbage, I will crash...")


class Pixel_Data():
    def __init__(self, sys_label=None, user_label=None, substrate=None, 
                  layout=None, area=None, dark_area=None, mux_index=None, 
                  weather=None):
        self.__id = {}
        self.__id["sys_label"] = sys_label
        self.__id["user_label"] = user_label
        self.__id["substrate"] = substrate
        self.__id["layout"] = layout
        self.__id["area"] = area
        self.__id["dark_area"] = dark_area
        self.__id["mux_index"]  = mux_index
        self.__id["weather"] = weather

        # Format: V,I,time, stat
        self.__dark_iv_1 = [None, None, None, None]
        self.__dark_iv_2 = [None, None, None, None]
        self.__light_iv_1 = [None, None, None, None]
        self.__light_iv_2 = [None, None, None, None]
        self.__vt = [None, None, None, None]
        self.__it = [None, None, None, None]
        self.__mppt = [None, None, None, None]
    
   
    def set_dark_iv(self, I=None, V=None, t=None, stat=None, index=1):
        if index == 1:
            self.__dark_iv_1 = [V, I, t, stat]
        elif index == 2:
            self.__dark_iv_2 = [V, I, t, stat]
        else:
            raise IndexError("Out of range: index only between 1 and 2")
    
    def set_light_iv(self, I=None, V=None, t=None, stat=None, index=1):
        if index == 1:
            self.__light_iv_1 = [V, I, t, stat]
        elif index == 2:
            self.__light_iv_2 = [V, I, t, stat]
        else:
            raise IndexError("Out of range: index only between 1 and 2")
    
    def set_vt(self, I=None, V=None, t=None, stat=None):
        self.__vt = [V, I, t, stat]
    
    def set_it(self, I=None, V=None, t=None, stat=None):
        self.__it = [V, I, t, stat]
    
    def set_mppt(self, I=None, V=None, t=None, stat=None):
        self.__mppt = [V, I, t, stat]
    
    def get_id(self):
        return self.__id
    def get_dark_iv(self):
        return (self.__dark_iv_1 , self.__dark_iv_2)
    def get_light_iv(self):
        return (self.__light_iv_1 , self.__light_iv_2)
    def get_vt(self):
        return self.__vt
    def get_it(self):
        return self.__it
    def get_mppt(self):
        return self.__mppt

# Just some funcs to make life a bit easier:
    
def find_extention(ext, path):
    "Returns list of files ending with some extention"
    file_paths = []
    # Loops over files, adds them to blank:
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(ext): # Only interested in tiffs
                file_paths.append(os.path.join(root, file))
        break # toggles recursive and non recurcive
    return file_paths

def find_starts_with(starts_with, path):
    "Returns list of files ending with some extention"
    file_paths = []
    # Loops over files, adds them to blank:
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.startswith(starts_with): # Only interested in tiffs
                file_paths.append(os.path.join(root, file))
        break # toggles recursive and non recurcive
    return file_paths

def print_logo():
    print("""
##############################################################################
   _____     /\     _____  
  /  _  \   /  \   /  |  | 
 /  /_\  \  \/\/  /   |  |_
/    |    \      /    ^   /
\____|__  /      \____   | 
        \/            |__| 
        
(AKASH'S AMAZING ANALYSIS AUTOMATOR')

Thanks for running my software. For help: akash.dasgupta@physics.ox.ac.uk
##############################################################################
          """)
          


# Ask user for where the data lives: 
datapath = input("Please enter the path to your data: ")
#datapath = r"C:\Users\akashdasgupta\Documents\temp"
print_logo()

database = {} # This dude will hold all the PixelData instances

csv_file_path = find_extention('.csv', datapath)[0] # Assuming only 1 csv
# Opens CSV and extracts the parameters for each run:
with open(csv_file_path, 'r') as file:
    reader = csv.reader(file)
    skip = True
    for row in reader:
        if  skip:
            skip = False
            continue
        # The key is actually also how the filename starts:
        database[row[1]+'_'+row[2]+'_'+"device"+row[7]] = Pixel_Data(row[1],
                                                                      row[2],
                                                                      row[3],
                                                                      row[4],
                                                                      row[5],
                                                                      row[6],
                                                                      row[7],
                                                                      row[8],)
# Loops over each pixel, sweep through and mines the data:
for key in database.keys():
    files_in_class = find_starts_with(key, datapath)
    for filename in files_in_class:
        
        # They have same rows/cols, so every file will fill these lists:
        I,V,t,stat = [[],[],[],[]]
        with open(filename, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            skip = True
            for row in reader:
                if  skip:
                    skip = False
                    continue
                V.append(float(row[0]))
                I.append(float(row[1]))
                t.append(float(row[2]))
                stat.append(float(row[3]))
        
        # Add it to the approriate member var:
        if filename.endswith(".div1.tsv"):
            database[key].set_dark_iv(I,V,t,stat,1)
            
        elif filename.endswith(".div2.tsv"):
            database[key].set_dark_iv(I,V,t,stat,2)
            
        elif filename.endswith(".liv1.tsv"):
            database[key].set_light_iv(I,V,t,stat,1)
            
        elif filename.endswith(".liv2.tsv"):
            database[key].set_light_iv(I,V,t,stat,2)
            
        elif filename.endswith(".it.tsv"):
            database[key].set_it(I,V,t,stat)
            
        elif filename.endswith(".vt.tsv"):
            database[key].set_vt(I,V,t,stat)
            
        elif filename.endswith(".mppt.tsv"):
            database[key].set_mppt(I,V,t,stat)
        # Maybe an else is safe?
        
##############################################################################
#Origin Nonsense
##############################################################################

op.lt_exec('pe_cd /; pe_mkdir "SUMMARY"; pe_cd /;pe_mkdir "FULL_IV_CURVES";')

voc_list = []
isc_list = []
ff_list = []
vm_list = []
im_list = []


ids = []
graph_strs = []

Graph_index = 1
for key in database.keys():
    op.lt_exec('pe_cd /; pe_cd "FULL_IV_CURVES"; pe_mkdir "'+key+'"; pe_cd "'+key+'"')
    print("NOW PLOTING: Graph"+str(Graph_index)+" - "+key)
    wks=op.new_sheet(lname="DATA for " + key)
    
    #super hacky way to get more cols but like leave me alone
    for i in range(10):
        op.lt_exec('wks.addCol()')
    
    dx1 = database[key].get_dark_iv()[0][0]
    dy1 = database[key].get_dark_iv()[0][1]
    dx2 = database[key].get_dark_iv()[1][0]
    dy2 = database[key].get_dark_iv()[1][1]
    
    lx1 = database[key].get_light_iv()[0][0]
    ly1 = database[key].get_light_iv()[0][1]
    lx2 = database[key].get_light_iv()[1][0]
    ly2 = database[key].get_light_iv()[1][1]
    
    wks.from_list('A', lx1, 'Voltage', 'V', axis='X')
    wks.from_list('B', ly1, 'Current', 'A', "Illuminated, 1",axis='Y')
    wks.from_list('C', lx2, 'Voltage', 'V', axis='X')
    wks.from_list('D', ly2, 'Current', 'A', "Illuminated, 2",axis='Y')
    
    wks.from_list('E', dx1, 'Voltage', 'V', axis='X')
    wks.from_list('F', dy1, 'Current', 'A', "Dark, 1",axis='Y')
    wks.from_list('G', dx2, 'Voltage', 'V', axis='X')
    wks.from_list('H', dy2, 'Current', 'A', "Dark, 2",axis='Y')

    graph = op.new_graph(lname="IV: " + key, template='line')


    plot3 = graph[0].add_plot(wks, coly="F", colx="E", type='line')
    plot1 = graph[0].add_plot(wks, coly="B", colx="A", type='line')
    op.lt_exec("Rescale; set %C -w 2000; layer -g;")

    layer2 = graph.add_layer(type="noxy")
    plot4 = graph[1].add_plot(wks, coly="H", colx="G", type='line')
    plot2 = graph[1].add_plot(wks, coly="D", colx="C", type='line')
    op.lt_exec("Rescale; set %C -w 2000; layer -g; set %C -d 1")
    
    op.lt_exec("legendupdate update:=reconstruct legend:=combine;")

    op.wait() # wait until operation is done
    op.wait('s', 0.05)#wait further for graph to update
   
    voc = float(database[key].get_vt()[0][0])
    isc = float(database[key].get_it()[1][0])
    
    mpp_i = database[key].get_mppt()[1]
    mpp_v =  database[key].get_mppt()[0]
    mpp = max([mpp_i[i]*mpp_v[i] for i in range(len(mpp_v))])
    for i in range(len(mpp_i)):
        if mpp_i[i]*mpp_v[i] == mpp:
            vm = mpp_v[i]
            im = mpp_i[i]
    ff = mpp/(voc*isc)
    
    voc_list.append(voc)
    isc_list.append(isc)
    ff_list.append(ff)
    vm_list.append(vm)
    im_list.append(im)
    
    
    ids.append(database[key].get_id())
    graph_strs.append("graph://Graph"+str(Graph_index)+" - "+"IV: " +key)
    Graph_index+=1

op.lt_exec('pe_cd /; pe_cd "SUMMARY";') 
wks_sum = op.new_sheet(lname="DATA SUMMARY ")
#super hacky way to get more cols but like leave me alone
for i in range(10):
    op.lt_exec('wks.addCol()')

wks_sum.from_list('A', [i['sys_label'] for i in ids], 'Cell', axis='X')
wks_sum.from_list('B', [i['user_label'] for i in ids], 'Name', axis='X')
wks_sum.from_list('C', [i['mux_index'] for i in ids], 'Device number', axis='X')

wks_sum.from_list('D', ff_list, 'Fill Factor', 'W', axis='Y')
wks_sum.from_list('E', vm_list, 'V_mp', 'V', axis='Y')
wks_sum.from_list('F', im_list, 'I_mp', 'A', axis='Y')
wks_sum.from_list('G', voc_list, 'V_oc', 'V', axis='Y')
wks_sum.from_list('H', isc_list, 'I_sc', 'A', axis='Y')

wks_sum.from_list('I', graph_strs, 'IV curve', comments = 'CLICK the cell', axis='Z')
        
print("ALL DONE!! You can close this window now")
        
        

        
        
        
        
        
        
        
        
        