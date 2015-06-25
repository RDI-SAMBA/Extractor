# Extractor
===================================
# Installation
To run the Extractor you need the following programs installed on your system:

* Python >= 3.4
* git
* neo4j == 2.2
* mongodb 

Before running the program you also need the following Python 3 packages installed:
 
* pymongo
* py2neo
* twitter
* twython
* facebook

These packages can be easily installed using  'pip', the package management tool
which comes with any Python >= 3.4. Open a Terminal in Linux or cmd in Windows and type
the following commands:

$ pip install pymongo py2neo twitter twython
$ pip install git+https://github.com/pythonforfacebook/facebook-sdk.git

Note that if you are running Linux you may need to add 'sudo' at the start of these 
commands. (You need root access to install the packages if the Python interpreter you're
working with is not installed in your Home directory.)

=====================================

# Running Extractor

To run Extractor, make sure that your mongodb or neo4j database servers are running then 
cd into the directory where main.py is located and type:

$ python main.py

