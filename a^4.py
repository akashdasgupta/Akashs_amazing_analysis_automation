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
            db[row[1] + '_' + row[2] + '_' + "device" + row[7]] = PixelData(row[1],
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
        # Calculate the parameters:
        voc = float(db[key].get_vt()[0][0])  # Open circuit voltage, from stability file
        isc = float(db[key].get_it()[1][0])  # Short circuit current, from stability file

        # Fill factor: Finds max power, and vm, im in the process, takes ratio of that to voc*isc:
        mpp_i = db[key].get_mppt()[1]
        mpp_v = db[key].get_mppt()[0]
        mpp = max([mpp_i[i] * mpp_v[i] for i in range(len(mpp_v))])
        for i in range(len(mpp_i)):
            if mpp_i[i] * mpp_v[i] == mpp:
                vm = mpp_v[i]
                im = mpp_i[i]
        ff = mpp / (voc * isc)

        voc_list.append(voc)
        isc_list.append(isc)
        ff_list.append(ff)
        vm_list.append(vm)
        im_list.append(im)
        ids.append(db[key].get_id())
        ######################################################################

        # Extract data from PixelData class for convenience:
        dx1 = db[key].get_dark_iv()[0][0]
        dy1 = db[key].get_dark_iv()[0][1]
        dx2 = db[key].get_dark_iv()[1][0]
        dy2 = db[key].get_dark_iv()[1][1]

        lx1 = db[key].get_light_iv()[0][0]
        ly1 = db[key].get_light_iv()[0][1]
        lx2 = db[key].get_light_iv()[1][0]
        ly2 = db[key].get_light_iv()[1][1]

        # Push lists into the cols on sheet, labels and type as appropriate:
        wks.from_list('A', lx1, 'Voltage', 'V', axis='X')
        wks.from_list('B', ly1, 'Current', 'A', "Illuminated, 1", axis='Y')
        wks.from_list('C', lx2, 'Voltage', 'V', axis='X')
        wks.from_list('D', ly2, 'Current', 'A', "Illuminated, 2", axis='Y')

        wks.from_list('E', dx1, 'Voltage', 'V', axis='X')
        wks.from_list('F', dy1, 'Current', 'A', "Dark, 1", axis='Y')
        wks.from_list('G', dx2, 'Voltage', 'V', axis='X')
        wks.from_list('H', dy2, 'Current', 'A', "Dark, 2", axis='Y')

        # Create graph to plot into:
        graph = op.new_graph(lname="IV: " + key, template=op.path('u') + 'a4_template.otpu')
        # !!! a custom template is used in line above, change it to "line" if this is missing!!!

        # First 2 (solid line) plots on base layer:
        plot1 = graph[0].add_plot(wks, coly="F", colx="E", type='line')
        plot2 = graph[0].add_plot(wks, coly="B", colx="A", type='line')
        # Rescales axis, sets linewidth up, sets up autocolour:        
        op.lt_exec("Rescale; set %C -w 2000; layer -g; layer.X.showAxes=3; layer.Y.showAxes=3;")

        # op.lt_exec("RECT1.DX={};RECT1.DY={};RECT1.X={};RECT1.Y={};RECT1.COLOR=4;RECT1.FILLCOLOR=7;RECT1.SHOW=1;".format(mpp_v/2,mpp_i/2,mpp_v/2,mpp_i/2))
        layer2 = graph.add_layer(type="noxy")  # new layer, noax allows us to use the same axis as before
        plot3 = graph[1].add_plot(wks, coly="H", colx="G", type='line')
        plot4 = graph[1].add_plot(wks, coly="D", colx="C", type='line')
        # Rescales axis, sets linewidth up, Changes linestyle to dash, sets up autocolour:
        op.lt_exec("Rescale; set %C -w 2000; layer -g; set %C -d 1")

        ######################################################################
        # Fill factor rectangles: 

        # Ideal:
        voc_sweep = [voc * (i + 1) / 50 for i in range(50)]
        isc_sweep = [isc * (i + 1) / 50 for i in range(50)]
        v_ideal = []
        i_ideal = []

        for voc_step in voc_sweep:
            v_ideal.append(voc_step)
            i_ideal.append(isc)
        for isc_step in isc_sweep:
            v_ideal.append(voc)
            i_ideal.append(isc_step)

        # Max power: 
        v_mppt_sweep = [vm * (i + 1) / 50 for i in range(50)]
        i_mppt_sweep = [im * (i + 1) / 50 for i in range(50)]
        v_mppt_rect = []
        i_mppt_rect = []

        for voc_step in v_mppt_sweep:
            v_mppt_rect.append(voc_step)
            i_mppt_rect.append(mpp_i)
        for isc_step in i_mppt_sweep:
            v_mppt_rect.append(mpp_v)
            i_mppt_rect.append(isc_step)

        # Push to hidden worksheet:           
        wks2 = op.new_sheet(lname="hacky_way_of_making_boxes(max_power)", hidden=True)
        wks2.from_list('A', v_mppt_rect, axis='X')
        wks2.from_list('B', i_mppt_rect, "Max power rectangle", axis='Y')
        # Add to plot:
        layer3 = graph.add_layer(type="noxy")  # new layer, noax allows us to use the same axis as before
        plot5 = graph[2].add_plot(wks2, colx="A", coly="B", type='line')
        op.lt_exec('Rescale; set %C -w 2000; set %C -d 5; set %c -cl color("Blue");')

        wks3 = op.new_sheet(lname="hacky_way_of_making_boxes(ideal)", hidden=True)
        wks3.from_list('A', v_ideal, axis='X')
        wks3.from_list('B', i_ideal, "ideal power rectangle", axis='Y')

        layer4 = graph.add_layer(type="noxy")  # new layer, noax allows us to use the same axis as before
        plot6 = graph[3].add_plot(wks3, colx="A", coly="B", type='line')
        op.lt_exec('Rescale; set %C -w 2000; set %C -d 1; set %c -cl color("#008800");')

        # Add labels for Voc, Isc, ff
        # Format: label -a "x" "y" "label";
        op.lt_exec('label -a "' + str(voc + voc / 100) + '" "' + str(0) + '" "' + str(round(voc * 1000)) + ' mV";')
        op.lt_exec('label -a "' + str(0) + '" "' + str(isc) + '" "' + str(round(isc * 1000)) + ' mA";')
        op.lt_exec('label -a "' + str(vm / 2) + '" "' + str(im / 2) + '" "Fill Factor: \n ' + str(round(ff, 3)) + '";')

        ######################################################################

        op.wait()  # wait until operation is done
        op.wait('s', 0.05)  # wait further for graph to update

        graph_num = op.graph_list()[0].get_str("name")
        graph_strs.append("graph://" + graph_num + " - " + "IV: " + key)  # creates hyperlink
        Graph_index += 1

    op.lt_exec('pe_cd /; pe_cd "SUMMARY";')  # moves to summary dir
    wks_sum = op.new_sheet(lname="DATA SUMMARY ")  # Creates sheet for summary
    # super hacky way to get more cols but like leave me alone
    for i in range(10):
        op.lt_exec('wks.addCol()')  # more hackyness, just forgive me

    # Info cols:
    wks_sum.from_list('A', [i['sys_label'] for i in ids], 'Cell', axis='X')
    wks_sum.from_list('B', [i['user_label'] for i in ids], 'Name', axis='X')
    wks_sum.from_list('C', [i['mux_index'] for i in ids], 'Device number', axis='X')
    # Data cols:
    wks_sum.from_list('D', ff_list, 'Fill Factor', 'W', axis='Y')
    wks_sum.from_list('E', vm_list, 'V_mp', 'V', axis='Y')
    wks_sum.from_list('F', im_list, 'I_mp', 'A', axis='Y')
    wks_sum.from_list('G', voc_list, 'V_oc', 'V', axis='Y')
    wks_sum.from_list('H', isc_list, 'I_sc', 'A', axis='Y')
    # Hyperlinks to graphs:
    wks_sum.from_list('I', graph_strs, 'IV curve', comments='CLICK the cell', axis='Z')

    return True


if __name__ == '__main__':
    # Ask user for where the data lives:
    datapath = input("Please enter the path to your data: ")
    print_logo()  # most important part of the code, without a doubt

    database = create_db(datapath)
    err = origin_create_plots(database)
    print("\n\nALL DONE!! You can close this window now")
