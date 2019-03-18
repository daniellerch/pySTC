
SRC = stc_interface.cpp stc_embed_c.cpp stc_extract_c.cpp common.cpp stc_ml_c.cpp 
OBJ= stc_interface.o stc_embed_c.o stc_extract_c.o common.o stc_ml_c.o 
default:
	g++ -std=c++98 -fPIC -O3 -c $(SRC)
	g++ -shared -o lib/stc.so $(OBJ) 
	rm -f *.o
clean:
	rm -f *.o *.pyc 
