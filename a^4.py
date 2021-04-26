# -*- coding: utf-8 -*-
"""
@author: Akash Dasgupta
THIS IS THE BACKEND FOR THE 'AKASH'S AMAZING ANALYSIS AUTOMATOR (A^4)'. 

You have to run this using Origin's embeded python, as the 'originpro' module 
lives inside it. You can run this using the command 
"""

import os
import csv
from scipy.interpolate import interp1d
import numpy as np 


try:
    import originpro as op
    # Copies the template we are using to the user files (thanks Robbie!): 
    if not os.path.isfile(op.path('u')+r"/a^4/a4_template.otpu"):
        # %@A is were the app lives, %Y is the user folder
        op.lt_exec(r'file -c "%@Aa^4\a4_template.otpu" "%Ya4_template.otpu"')
except ModuleNotFoundError:
    print("I couldn't find Origin! I guess you are debuging, which is cool." +
          "\nJust remember, if you have not commented out all the Origin garbage, I will crash...")

class PixelData:
    """
    Class holds, for each pixel on a solar cell tested, the parameters recorded, as well as all the I/V data taken.
    Simply a set of getters and setters, just makes it easier to spool together a bunch of files into one object

    """

    def __init__(self, sys_label=None, user_label=None, substrate=None,
                 layout=None, area=None, dark_area=None, mux_index=None,
                 weather=None):
        """
        Initial class constructor. On creation can populate the id dict with all the parameters in the csv file. Data
        not initially added, but empty lists where they would go are created.
        :param sys_label: Label the solar sim software made (A, B, etc)
        :param user_label: User's label of the whole cell
        :param substrate: Substrate name
        :param layout: Layout id
        :param area: Area of pixel
        :param dark_area: Unsure
        :param mux_index: Index of pixel on device
        :param weather: Weather config
        """
        self.__id = {"sys_label": sys_label,
                     "user_label": user_label,
                     "substrate": substrate,
                     "layout": layout,
                     "area": area,
                     "dark_area": dark_area,
                     "mux_index": mux_index,
                     "weather": weather}  # This will hold all the parameters

        # Format: V,I,time, stat
        self.__dark_iv_1 = [None, None, None, None]
        self.__dark_iv_2 = [None, None, None, None]
        self.__light_iv_1 = [None, None, None, None]
        self.__light_iv_2 = [None, None, None, None]
        self.__vt = [None, None, None, None]
        self.__it = [None, None, None, None]
        self.__mppt = [None, None, None, None]

    def set_dark_iv(self, I=None, V=None, t=None, stat=None, index=1):
        if index == 1:  # there's 2 because of hysteresis testing
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
        return (self.__dark_iv_1, self.__dark_iv_2)

    def get_light_iv(self):
        return (self.__light_iv_1, self.__light_iv_2)

    def get_vt(self):
        return self.__vt

    def get_it(self):
        return self.__it

    def get_mppt(self):
        return self.__mppt


def find_ext(ext, path):
    """Returns list of files ending with some extention"""
    file_paths = []
    # Loops over files, adds them to blank:
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(ext):  # Only interested in tiffs
                file_paths.append(os.path.join(root, file))
        break  # toggles recursive and non recurcive
    return file_paths


def find_starts_with(starts_with, path):
    """Returns list of files ending with some extention"""
    file_paths = []
    # Loops over files, adds them to blank:
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.startswith(starts_with):  # Only interested in tiffs
                file_paths.append(os.path.join(root, file))
        break  # toggles recursive and non recurcive
    return file_paths


def print_logo():
    """ pretty unnecessary but also cool"""
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


def create_db(path):
    db = {}  # This dude will hold all the PixelData instances

    csv_file_path = find_ext('.csv', path)[0]  # Assuming only 1 csv
    # Opens CSV and extracts the parameters for each run:
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        skip = True
        for row in reader:
            if skip:
                skip = False
                continue
            # The key is actually also how the filename starts:
            if row[2] == '':
                key_str = row[1] + '_' + "device" + row[7]
            else:
                key_str = row[1] + '_' + row[2] + '_' + "device" + row[7]
            db[key_str] = PixelData(row[1],
                                    row[2],
                                    row[3],
                                    row[4],
                                    row[5],
                                    row[6],
                                    row[7],
                                    row[8], )  # Populates ID
    # Loops over each pixel, sweep through and mines the data:
    for key in db.keys():
        files_in_class = find_starts_with(key, path)
        for filename in files_in_class:

            # They have same rows/cols, so every file will fill these lists:
            I, V, t, stat = [[], [], [], []]
            with open(filename, 'r') as file:
                reader = csv.reader(file, delimiter='\t')
                skip = True
                for row in reader:
                    if skip:
                        skip = False
                        continue
                    V.append(float(row[0]))
                    I.append(float(row[1]))
                    t.append(float(row[2]))
                    stat.append(float(row[3]))

            # Add it to the appropriate member var:
            if filename.endswith(".div1.tsv"):
                db[key].set_dark_iv(I, V, t, stat, 1)

            elif filename.endswith(".div2.tsv"):
                db[key].set_dark_iv(I, V, t, stat, 2)

            elif filename.endswith(".liv1.tsv"):
                db[key].set_light_iv(I, V, t, stat, 1)

            elif filename.endswith(".liv2.tsv"):
                db[key].set_light_iv(I, V, t, stat, 2)

            elif filename.endswith(".it.tsv"):
                db[key].set_it(I, V, t, stat)

            elif filename.endswith(".vt.tsv"):
                db[key].set_vt(I, V, t, stat)

            elif filename.endswith(".mppt.tsv"):
                db[key].set_mppt(I, V, t, stat)
            # Maybe an else is safe?
    return db


def origin_create_plots(db):
    # Creates the folders needed:
    op.lt_exec('pe_cd /; pe_mkdir "SUMMARY"; pe_cd /;pe_mkdir "FULL_IV_CURVES";')

    # Lists that will populate summary pages:
    voc_list = []  # Open circuit voltage
    isc_list = []  # Short circuit current
    ff_list = []  # Fill factor
    vm_list = []  # Voltage at max power
    im_list = []  # Current at max power
    pce_list = []
    # stabalised values:
    voc_st_list = []  # Open circuit voltage
    isc_st_list = []  # Short circuit current
    ff_st_list = []  # Fill factor
    vm_st_list = []  # Voltage at max power
    im_st_list = []  # Current at max power
    pce_st_list = []

    ids = []  # The ID dict (for info cols)
    graph_strs = []  # Holds hyperlinks to plotted graphs

    Graph_index = 1  # Keep track of how many graphs, needed for the hyperlinking
    for key in db.keys():
        # move into the full iv curve dir, create new dir per pixel:
        op.lt_exec('pe_cd /; pe_cd "FULL_IV_CURVES"; pe_mkdir "' + key + '"; pe_cd "' + key + '"')
        print("NOW PLOTING: Graph" + str(Graph_index) + " - " + key)

        # Create worksheet:
        wks = op.new_sheet(lname="DATA for " + key)  # Long name is linked to key
        # super hacky way to get more cols but like leave me alone
        for i in range(10):
            op.lt_exec('wks.addCol()')
            
        ######################################################################  
        # Extract data from PixelData class for convenience:
        area = float(db[key].get_id()["area"])
        dark_area = float(db[key].get_id()["dark_area"])

        dx1 = db[key].get_dark_iv()[0][0]
        try:
            dy1 = [i *(1e3 / dark_area) for i in db[key].get_dark_iv()[0][1]]
        except:
            dy1 = None
        dx2 = db[key].get_dark_iv()[1][0]
        try:
            dy2 = [i *(1e3 / dark_area) for i in db[key].get_dark_iv()[1][1]]
        except:
            dy2 = None

        lx1 = db[key].get_light_iv()[0][0]

        try:
            ly1 = [i *(1e3 / area) for i in db[key].get_light_iv()[0][1]]
        except:
            raise ValueError("You need to have at least 1 light JV!!!")
        lx2 = db[key].get_light_iv()[1][0]
        try:
            ly2 = [i *(1e3 / area) for i in db[key].get_light_iv()[1][1]]
        except:
            ly2 = None

        ######################################################################
        # Calculate the parameters:

        
       # Stability file data: 

        try:
            voc_st = float(db[key].get_vt()[0][-1])  # Open circuit voltage, from stability file
        except:
            voc_st = None
        try:
            isc_st = float(db[key].get_it()[1][-1])* (1e3/area)  # Short circuit current, from stability file
        except:
            isc_st = None
        try:
            im_st = np.mean(db[key].get_mppt()[1][-5:])* (1e3/area)
            vm_st = np.mean(db[key].get_mppt()[0][-5:])
            mpp_st = vm_st * im_st 
        except:
            im_st, vm_st, mpp_st = (None, None, None)
        try:
            ff_st = mpp_st/ (voc_st * isc_st * 10)
        except:
            ff_st = None
  
        # Bound error is false, for really bad stuff it'll output NaN (Thanks Joel!)
        j_from_v = interp1d(lx1, ly1,bounds_error=False)
        v_from_j = interp1d(ly1, lx1, bounds_error=False)
        voc = v_from_j(0)
        isc = j_from_v(0)

        temp_v = np.arange(min(lx1), max(lx1), (max(lx1)-min(lx1)/10000))
        mpp_index = np.argmin(temp_v*j_from_v(temp_v))
        vm = temp_v[mpp_index]
        im = j_from_v(temp_v[mpp_index])

        # Check second curve in case it's better:

        try:
            j_from_v2 = interp1d(lx2, ly2)
            v_from_j2 = interp1d(ly2, lx2)
            voc2 = v_from_j2(0)
            isc2 = j_from_v2(0)

            temp_v2 = np.arange(min(lx2), max(lx2), (max(lx2)-min(lx2)/10000))
            mpp_index2 = np.argmin(temp_v2*j_from_v2(temp_v2))
            vm2 = temp_v2[mpp_index2]
            im2 = j_from_v2(temp_v2[mpp_index2])

            if im*vm > im2*vm2:
                voc = voc2
                isc = isc2
                im = im2
                vm = vm2
        except:
            pass
            
        ff = (vm*im)/(voc*isc)


        voc_st_list.append(voc_st)
        isc_st_list.append(isc_st)
        ff_st_list.append(ff_st)
        vm_st_list.append(vm_st)
        im_st_list.append(im_st)
        try:
            pce_st_list.append(abs(mpp_st))
        except TypeError:
            pce_st_list.append(mpp_st)

        voc_list.append(float(voc))
        isc_list.append(float(isc))
        ff_list.append(float(ff))
        vm_list.append(float(vm))
        im_list.append(float(im))
        pce_list.append(abs(float(vm*im)))
        ids.append(db[key].get_id())
        ######################################################################
        # Push lists into the cols on sheet, labels and type as appropriate:
        letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
        
        counter = 0
        if ly1:
            wks.from_list(letters[counter], lx1, 'Voltage', 'V', axis='X')
            counter += 1
            wks.from_list(letters[counter], ly1, 'Current', 'mA/cm^2', "Illuminated, 1", axis='Y')
            counter += 1
        if ly2:
            wks.from_list(letters[counter], lx2, 'Voltage', 'V', axis='X')
            counter += 1
            wks.from_list(letters[counter], ly2, 'Current', 'mA/cm^2', "Illuminated, 2", axis='Y')
            counter += 1

        if dy1:
            wks.from_list(letters[counter], dx1, 'Voltage', 'V', axis='X')
            counter += 1
            wks.from_list(letters[counter], dy1, 'Current', 'mA/cm^2', "Dark, 1", axis='Y')
            counter += 1
        if dy2:
            wks.from_list(letters[counter], dx2, 'Voltage', 'V', axis='X')
            counter += 1
            wks.from_list(letters[counter], dy2, 'Current', 'mA/cm^2', "Dark, 2", axis='Y')
            counter += 1

        # Create graph to plot into:
        #graph = op.new_graph(lname="IV: " + key, template=op.path('u') + 'a4_template.otpu')
        # !!! a custom template is used in line above, change it to "line" if this is missing!!!
        graph = op.new_graph(lname="IV: " + key, template='a4_template.otpu')

        # First 2 (solid line) plots on base layer:
        plot1 = graph[0].add_plot(wks, coly="F", colx="E", type='line')
        plot2 = graph[0].add_plot(wks, coly="B", colx="A", type='line')
        # Rescales axis, sets linewidth up, sets up autocolour:        
        op.lt_exec("Rescale; set %C -w 2000; layer -g; layer.X.showAxes=3; layer.Y.showAxes=3;")
        
        layer2 = graph.add_layer(type="noxy")  # new layer, noax allows us to use the same axis as before
        plot3 = graph[1].add_plot(wks, coly="H", colx="G", type='line')
        plot4 = graph[1].add_plot(wks, coly="D", colx="C", type='line')
        # Rescales axis, sets linewidth up, Changes linestyle to dash, sets up autocolour:
        op.lt_exec("Rescale; set %C -w 2000; layer -g; set %C -d 1")


        ######################################################################

        op.wait()  # wait until operation is done
        op.wait('s', 0.05)  # wait further for graph to update

        graph_num = op.graph_list()[0].get_str("name")
        graph_strs.append("graph://" + graph_num + " - " + "IV: " + key)  # creates hyperlink
        Graph_index += 1

    op.lt_exec('pe_cd /; pe_cd "SUMMARY";')  # moves to summary dir
    wks_sum = op.new_sheet(lname="DATA SUMMARY ")  # Creates sheet for summary
    # super hacky way to get more cols but like leave me alone
    for i in range(30):
        op.lt_exec('wks.addCol()')  # more hackyness, just forgive me
    # Info cols:
    wks_sum.from_list('A', [i['sys_label'] for i in ids], 'Cell', axis='X')
    wks_sum.from_list('B', [i['user_label'] for i in ids], 'Name', axis='X')
    wks_sum.from_list('C', [i['mux_index'] for i in ids], 'Device number', axis='X')
    # Data cols:
    wks_sum.from_list('D', voc_list, 'V_oc', 'V', axis='Y')
    wks_sum.from_list('E', isc_list, 'I_sc', 'mA/cm^-2', axis='Y')
    wks_sum.from_list('F', pce_list, 'Max power point', 'mWcm^-2', axis='Y')
    wks_sum.from_list('G', ff_list, 'Fill Factor', '', axis='Y')
    wks_sum.from_list('H', vm_list, 'V_mp', 'V', axis='Y')
    wks_sum.from_list('I', im_list, 'I_mp', 'mA/cm^-2', axis='Y')

    # Get ready....here comes...MORE HACKYNESS
    letters = ['J','K','L','M','N','O','P']
    letter_counter = 0
    
    if voc_st_list[0]:
        wks_sum.from_list(letters[letter_counter], voc_st_list, 'V_oc (STABALISED)', 'V', axis='Y')
        letter_counter += 1
    if isc_st_list[0]:
        wks_sum.from_list(letters[letter_counter], isc_st_list, 'I_sc (STABALISED)', 'A', axis='Y')
        letter_counter += 1
    if pce_list[0]:
        wks_sum.from_list(letters[letter_counter], pce_st_list, 'Max power point (STABALISED)', 'mWcm^-2', axis='Y')
        letter_counter += 1
    if ff_st_list[0]:
        wks_sum.from_list(letters[letter_counter], ff_st_list, 'Fill Factor (STABALISED)', 'W', axis='Y')
        letter_counter += 1
    if vm_st_list[0]:
        wks_sum.from_list(letters[letter_counter], vm_st_list, 'V_mp (STABALISED)', 'V', axis='Y')
        letter_counter += 1
    if im_st_list[0]:
        wks_sum.from_list(letters[letter_counter], im_st_list, 'I_mp (STABALISED)', 'A', axis='Y')
        letter_counter += 1
    # Hyperlinks to graphs:
    wks_sum.from_list(letters[letter_counter], graph_strs, 'IV curve', comments='CLICK the cell', axis='Z')

    return True


if __name__ == '__main__':
    # Ask user for where the data lives:
    datapath = input("Please enter the path to your data: ")
    print_logo()  # most important part of the code, without a doubt

    database = create_db(datapath)
    err = origin_create_plots(database)
    print("\n\nALL DONE!! You can close this window now")
