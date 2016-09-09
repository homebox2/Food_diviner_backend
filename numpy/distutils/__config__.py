# This file is generated by C:\projects\windows-wheel-builder\numpy\setup.py
# It contains system_info results at the time of building this package.
__all__ = ["get_info","show"]

openblas_info={}
openblas_lapack_info={}
atlas_3_10_threads_info={'define_macros': [('NO_ATLAS_INFO', -1)], 'libraries': ['numpy-atlas', 'numpy-atlas'], 'library_dirs': ['C:\\projects\\windows-wheel-builder\\atlas-builds\\atlas-3.10.1-sse2-32\\lib'], 'language': 'f77'}
lapack_opt_info={'define_macros': [('NO_ATLAS_INFO', -1)], 'library_dirs': ['C:\\projects\\windows-wheel-builder\\atlas-builds\\atlas-3.10.1-sse2-32\\lib'], 'language': 'f77', 'libraries': ['numpy-atlas', 'numpy-atlas']}
blas_mkl_info={}
atlas_3_10_blas_threads_info={'libraries': ['numpy-atlas'], 'define_macros': [('HAVE_CBLAS', None), ('NO_ATLAS_INFO', -1)], 'library_dirs': ['C:\\projects\\windows-wheel-builder\\atlas-builds\\atlas-3.10.1-sse2-32\\lib'], 'language': 'c'}
blas_opt_info={'libraries': ['numpy-atlas'], 'library_dirs': ['C:\\projects\\windows-wheel-builder\\atlas-builds\\atlas-3.10.1-sse2-32\\lib'], 'language': 'c', 'define_macros': [('HAVE_CBLAS', None), ('NO_ATLAS_INFO', -1)]}
mkl_info={}
lapack_mkl_info={}

def get_info(name):
    g = globals()
    return g.get(name, g.get(name + "_info", {}))

def show():
    for name,info_dict in globals().items():
        if name[0] == "_" or type(info_dict) is not type({}): continue
        print(name + ":")
        if not info_dict:
            print("  NOT AVAILABLE")
        for k,v in info_dict.items():
            v = str(v)
            if k == "sources" and len(v) > 200:
                v = v[:60] + " ...\n... " + v[-60:]
            print("    %s = %s" % (k,v))
    