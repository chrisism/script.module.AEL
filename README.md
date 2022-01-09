# Advanced Kodi Launcher Module

| Release | Status | 
|----|----|
| Stable | [![Build Status](https://dev.azure.com/jnpro/AKL/_apis/build/status/script.module.akl?branchName=main)](https://dev.azure.com/jnpro/AKL/_build/latest?definitionId=4&branchName=main)|
| Beta | [![Build Status](https://dev.azure.com/jnpro/AKL/_apis/build/status/script.module.akl?branchName=release/1.0.1)](https://dev.azure.com/jnpro/AKL/_build/latest?definitionId=4&branchName=release/1.0.1)|
| Unstable | [![Build Status](https://dev.azure.com/jnpro/AKL/_apis/build/status/script.module.akl?branchName=dev)](https://dev.azure.com/jnpro/AKL/_build/latest?definitionId=4&branchName=dev)|

Main module to be used by all AKL plugins. Contains utility code and shared classes and API's. Also contains the base classes for building Launchers, Scanners or Scrapers for AKL.  
For more information about how to build your own custom plugins, read the [wiki](https://github.com/chrisism/plugin.program.akl/wiki/Extend-AKL) pages.

## script.module.akl
Python package can also be installed through pip from this [feed](https://dev.azure.com/jnpro/AKL/_packaging?_a=feed&feed=akl_libs): https://dev.azure.com/jnpro/AKL/_packaging?_a=feed&feed=akl_libs

**Install custom pip feed**  
Follow the instructions here: https://dev.azure.com/jnpro/AKL/_packaging?_a=connect&feed=akl_libs
  
**Install module**  
``
pip install script.module.akl
``