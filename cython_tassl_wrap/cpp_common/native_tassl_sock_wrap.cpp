/*
  FISCO BCOS/Python-SDK is a python client for FISCO BCOS2.0 (https://github.com/FISCO-BCOS/)
  FISCO BCOS/Python-SDK is free software: you can redistribute it and/or modify it under the
  terms of the MIT License as published by the Free Software Foundation. This project is
  distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
  @author: kentzhang
  @date: 2021-03
*/
#include <stdlib.h>
#include "tassl_sock_wrap.h"
#include "native_tassl_sock_wrap.h"
using namespace fisco_tassl_sock_wrap;
//将tassl_sock_wrap.cpp里的TasslSockWrap类，桥接为native c代码接口
//基本逻辑就是new一个TasslSockWrap对象，把指针返回给上层，后续拿这个指针调用接口
//在mingw编译时，如果有namespace，则输出的def符号带上了其他特殊符号，所以不用namespace
//using namespace native_fisco_tassl_sock_wrap;

	void * ssock_create(){
		TasslSockWrap *pssock = new TasslSockWrap();
		return (void *)pssock;
	}
	void   ssock_release(void * p_void_ssock){
		TasslSockWrap *pssock = (TasslSockWrap *)p_void_ssock;
		if(pssock==NULL){return;}
	}
	

	int  ssock_init(
					void * p_void_ssock,
					const char *ca_crt_file_,
					const char * sign_crt_file_,
					const char * sign_key_file_,
					const char * en_crt_file_,
					const char * en_key_file_
						){
		TasslSockWrap *pssock = (TasslSockWrap *)p_void_ssock;
		if(pssock==NULL){return -1;}
		return pssock->init(ca_crt_file_,
					 sign_crt_file_,
					 sign_key_file_,
					 en_crt_file_,
					 en_key_file_);

	}

	int  ssock_try_connect(void * p_void_ssock,const char *host_,const int port_){
		TasslSockWrap *pssock = (TasslSockWrap *)p_void_ssock;
		if(pssock==NULL){return -1;}
		return pssock->try_connect(host_,port_);

	}
	int  ssock_finish(void * p_void_ssock){
		TasslSockWrap *pssock = (TasslSockWrap *)p_void_ssock;
		if(pssock==NULL){return -1;}
		return pssock->finish();
	}
	
	void  ssock_set_echo_mode(void * p_void_ssock,int mode){
		TasslSockWrap *pssock = (TasslSockWrap *)p_void_ssock;
		if(pssock==NULL){return;}
		return pssock->set_echo_mode(mode);
	}

	
	int  ssock_send(void * p_void_ssock,const char * buffer,const int len){
		TasslSockWrap *pssock = (TasslSockWrap *)p_void_ssock;
		if(pssock==NULL){return -1;}
		return pssock->send(buffer,len);

	}
	int  ssock_recv(void * p_void_ssock,char *buffer,const int buffersize){
		TasslSockWrap *pssock = (TasslSockWrap *)p_void_ssock;
		if(pssock==NULL){return -1;}
		
		int retval =  pssock->recv(buffer,buffersize);
		/*for(int i=0;i<retval;i++)
		{
			printf("%x",buffer[i]);
		}
		printf("\n");
		fflush(stdout);
		*/
		return retval;
	}



