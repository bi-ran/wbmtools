# wbmtools
A collection of python scripts to parse information from CMS web based monitoring. Anything availible in wbm can in theory be parsed. 

This uses kerberos based authenication, therefore you must have a kerberos ticket active. Additionally you will the cern certificate CA bundle to allow the WBM certificate to be validated. This is most easily obtained from lxplus, lxplus.cern.ch:/etc/ssl/certs/ca-bundle.crt

The external requirements can easily be installed with pip

      pip install -r requirements.txt
Note that with pip you can either install to a virtualenv or your user area if you dont wish to/have permission to install to the central packages location. 
The virtualenv way:
      
      python3 -m venv <dir>
      source <dir>/bin/activate #for bash
      pip install -r requirements.txt
when you are done, type "deactivate" to return to your normal python env
