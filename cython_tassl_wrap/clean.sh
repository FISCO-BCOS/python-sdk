rm -f libtassl_sock_wrap.so
rm -f cython_tassl_sock_wrap.*.so 
rm -f cython_tassl_sock_wrap*.dll
rm -f cython_tassl_sock_wrap.cpp
rm -rf build
rm -rf dist
rm -rf __pycache__ 
cd cpp_linux
make clean
cd ..
cd cpp_win
make clean
cd ..
