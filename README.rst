Place-price calculator for toydb
--------------------------------


How to use:


::

    # assuming you have virtualenv installed

    make develop

    .env/bin/python prices.py mysql://scott:tiger@localhost/foo

    # it will print out csv with a header to stdout
