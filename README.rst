Electrum Raven Wallet (RVN)
=====================================

::

  Licence: MIT Licence
  Language: Python (>= 3.6)


.. image:: https://travis-ci.org/spesmilo/electrum.svg?branch=master
    :target: https://travis-ci.org/spesmilo/electrum
    :alt: Build Status
.. image:: https://coveralls.io/repos/github/spesmilo/electrum/badge.svg?branch=master
    :target: https://coveralls.io/github/spesmilo/electrum?branch=master
    :alt: Test coverage statistics
.. image:: https://d322cqt584bo4o.cloudfront.net/electrum/localized.svg
    :target: https://crowdin.com/project/electrum
    :alt: Help translate Electrum online



**Electrum Raven (RVN)** is a lightweight wallet for Raven (RVN), designed for fast and secure transactions with low fees.  

Features  
=============
- **Fast Transactions**: Raven’s blockchain ensures fast and efficient transactions.  
- **Secure**: Multi-signature support and hardware wallet integration.  
- **Lightweight**: Efficient and fast synchronization with the network.  
- **Cross-Platform Support**: Available for Windows, macOS, and Linux. 

Downloads
---------

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Platform
     - Download Link
   * - Windows
     - `program-windows.exe <https://github.com/Electrum-Raven/electrum-rvn/releases/download/v.1.2.4/electrum-ravencoin-v1.2.4-setup.exe>`_
   * - Linux
     - `program-linux.AppImage <https://github.com/Electrum-Raven/electrum-rvn/releases/download/v.1.2.4/electrum-ravencoin-v1.2.4-x86_64.AppImage>`_
   * - macOS
     - `program-macos.dmg <https://github.com/Electrum-Raven/electrum-rvn/releases/download/v.1.2.4/electrum-ravencoin-v1.2.4.dmg>`_




License  
=============

This project is licensed under the MIT License. See the `LICENSE`_ for details.

.. _LICENSE: https://github.com/Electrum-Raven/electrum-rvn/blob/master/LICENCE


Getting started
===============

(*If you've come here looking to simply run Electrum RVN*)

Electrum itself is pure Python, and so are most of the required dependencies,
but not everything. The following sections describe how to run from source, but here
is a TL;DR::

    sudo apt-get install libsecp256k1-0
    python3 -m pip install --user .[gui,crypto]


Not pure-python dependencies
----------------------------

If you want to use the Qt interface, install the Qt dependencies::

    sudo apt-get install python3-pyqt5

For elliptic curve operations, `libsecp256k1`_ is a required dependency::

    sudo apt-get install libsecp256k1-0

Alternatively, when running from a cloned repository, a script is provided to build
libsecp256k1 yourself::

    sudo apt-get install automake libtool
    ./contrib/make_libsecp256k1.sh

Due to the need for fast symmetric ciphers, `cryptography`_ is required.
Install from your package manager (or from pip)::

    sudo apt-get install python3-cryptography


If you would like hardware wallet support, see `this`_.

.. _libsecp256k1: https://github.com/bitcoin-core/secp256k1
.. _pycryptodomex: https://github.com/Legrandin/pycryptodome
.. _cryptography: https://github.com/pyca/cryptography
.. _this: https://github.com/spesmilo/electrum-docs/blob/master/hardware-linux.rst

Running from tar.gz
-------------------

If you downloaded the official package (tar.gz), you can run
Electrum from its root directory without installing it on your
system; all the pure python dependencies are included in the 'packages'
directory. To run Electrum from its root directory, just do::

    ./run_electrum

You can also install Electrum on your system, by running this command::

    sudo apt-get install python3-setuptools python3-pip
    python3 -m pip install --user .

This will download and install the Python dependencies used by
Electrum instead of using the 'packages' directory.
It will also place an executable named :code:`electrum` in :code:`~/.local/bin`,
so make sure that is on your :code:`PATH` variable.


Development version (git clone)
-------------------------------

Check out the code from GitHub::

    git clone git://github.com/spesmilo/electrum.git
    cd electrum
    git submodule update --init

Run install (this should install dependencies)::

    python3 -m pip install --user -e .


Create translations (optional)::

    sudo apt-get install python-requests gettext
    ./contrib/pull_locale

Finally, to start Electrum::

    ./run_electrum



Creating Binaries
=================

Linux (tarball)
---------------

See :code:`contrib/build-linux/sdist/README.md`.


Linux (AppImage)
----------------

See :code:`contrib/build-linux/appimage/README.md`.


Mac OS X / macOS
----------------

See :code:`contrib/osx/README.md`.


Windows
-------

See :code:`contrib/build-wine/README.md`.


Android
-------

See :code:`contrib/android/Readme.md`.
