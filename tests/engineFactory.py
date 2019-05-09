# This file is part of dax_imgserv.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# The purpose of this is to read all the FITS files in a directory tree
# and insert their header information into the metadata database.
"""
This module exposes engine from SQLAlchemy.

@author  Jacek Becla, SLAC
"""

# standard library imports
try:
    from ConfigParser import ConfigParser, NoSectionError
except ImportError:
    from configparser import ConfigParser, NoSectionError

import logging as log
import os

# related third-package library imports
import sqlalchemy
from sqlalchemy.engine.url import URL, make_url

###############################################################################


def getEngineFromFile(fileName,
                      drivername=None,
                      username=None,
                      password=None,
                      host=None,
                      port=None,
                      database=None,
                      query=None):
    """
    Initializes and returns SQLAlchemy engine using values provided through the
    file. The file must contain "database" section with key "url" defined.
    Optionally it can contain **kwargs that can be passed to the SQLAlchemy
    create_engine(). For  details see
    http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html

    Optional parameters drivername, username, password, host, port, database,
    query can be used to overwrite values from the file. A typical usecase:
    one can use drivername, username, password, host, port from the file,
    and pass database name.

    Note, if mysql sees "localhost" it switches to using socket, even if port is
    specified. Commonly used way around it is to specify "127.0.0.1" as port for
    local access.

    Example file:

    [database]
    url = mysql+mysqldb://joe:myPassword@localhost:3306/?unix_socket=/tmp/mysql.sock
    echo = yes
    pool_size = 5

    Raises IOError if the file does not exists.
    Raises ConfigParser exceptions (such as NoSectionError)
    """
    fileName = os.path.expanduser(fileName)
    parser = ConfigParser()
    with open(fileName) as config:
        # readfp is deprecated in Python3.x, read_file is not in Python2
        read_file = getattr(parser, "read_file", None) or getattr(parser,
                                                                  "readfp")
        read_file(config, fileName)
    try:
        options = dict(parser.items("database"))
    except NoSectionError:
        log.error("File %s does not contain section 'database'", fileName)
        raise

    if drivername or username or password or host or port or database or query:
        url = make_url(options['url'])
        if drivername:
            url.drivername = drivername
        if username:
            url.username = username
        if password:
            url.password = password
        if host:
            url.host = host
        if port:
            url.port = port
        if database:
            url.database = database
        if query:
            url.query = query
        options['url'] = url

    return sqlalchemy.engine_from_config(options, "")

################################################################################


def getEngineFromArgs(drivername="mysql+mysqldb",
                      username=None,
                      password=None,
                      host=None,
                      port=None,
                      database=None,
                      query=None,
                      **engineKVArgs):
    """
    Initializes and returns SQLAlchemy engine using provided values.

    To specify socket, use query={"unix_socket": "/the/socket.file"}

    Note, if mysql sees "localhost" it switches to using socket, even if port is
    specified. Commonly used way around it is to specify "127.0.0.1" as port for
    local access.
    """
    url = URL(drivername=drivername,
              username=username,
              password=password,
              host=host,
              port=port,
              database=database,
              query=query)
    return sqlalchemy.create_engine(url, **engineKVArgs)
