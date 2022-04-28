.. _configfile:

``smarker.conf``: Configuration File
====================================

Here is what it should look like. It needs to be in the same directory as the 
source code. Its a standard .ini format.

Once it's been created, you can safely forget about it since all of the options 
can be over-ridden in command line arguments.::
    
    [mysql]
    host = vps.eda.gay
    port = 3307
    user = root
    passwd = ************

    [tex]
    columns = 1
    show_full_docs = True
    show_source = True
    show_all_regex_occurrences = True
    show_all_run_output = True

    [md]
    show_full_docs = False
    show_source = False
    show_all_regex_occurrences = True
    show_all_run_output = False

    [txt]
    show_full_docs = False
    show_source = False
    show_all_regex_occurrences = True
    show_all_run_output = False

The first block configures where your SQL server is. The other options are
the default options when generating reports. ``[tex]`` options are inherited
for rendering to PDF.