# A^4 (Akashs amazing analysis automation!)

An analysis automation programme, written to process J/V curves of solar cells from data obtained using the 'Wavelabs Solar Simulator, for the Henry J Snaith "Photovoltaic and Optoelectronic Device" Groups at Oxford university. The programme parses data files of the fromat outputed by custom software written by Grey Chhristoforo. Thanks to Grey, Suhas Mahesh, Tino Lukas and Robbie Oliver.

* **For regular users:** The programme comes packedged in an install file. See the installation and useage instructions below.

* **For Advanced users:** The Python file requires the OriginPro module, which lives inside the embedded python environment which gets installed alongside OriginPro. If you want to run the script on its own without install, or wish to edit it you will have to run it through there. There is a required style file (.optu) aswell to make everything look pretty, this is required in the script, but this part can be commented away if required.

## Installation 

* You MUST have Origin version 2021 or higher for this to work! For Oxford Physics users, this version is available on the physics Self Service:

![Latest Origin on self service](readme_images/self_service.png)

* Download the "install.opx" file. On github, you can download all the code in a zip file, and extract it, to get a folder with the install file:

![Download files](readme_images/download_and_extract.png)

* Open Origin
* Open the folder with the install file, and drag and drop the file into origin: 

![Drag and drop install](readme_images/dragndrop.png)

* The App is installed! It will appear on the app bar on the right:

![Where the app appears](readme_images/a4_exists.png)

* IMPORTANT: YOU MUST CLOSE AND OPEN THE APP ONCE AFTER INSTALL! Otherwise it dosen't properly update the python package lists.

## Usage

* Click on the app:  

![click the app](readme_images/click_me.png)

* Enter the path to the data files:  

![Enter path](readme_images/path_enter.png)

* There is a summary page with all the important parameters, and links to the J/V curves:

![Summary of params](readme_images/summary.png)

* Clicking on the J/V curves will open the page with the graph and the full data :

![One graph](readme_images/one_graph.png)

* You can return to the summary page from the project explorer: 

![Return to summary](readme_images/return_sum.png)


