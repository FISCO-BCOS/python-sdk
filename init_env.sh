#!/bin/bash
shell_env=""
shell_rc=""
ZSH="/bin/sh"
REALZSH="/bin/zsh"
BASH="/bin/bash"

ZSHRC="${HOME}/.zshrc"
BASHRC="${HOME}/.bashrc"


LOG_WARN()
{
    local content=${1}
    echo -e "\033[31m[WARN] ${content}\033[0m"
}

LOG_ERROR()
{
    local content=${1}
    echo -e "\033[31m[ERROR] ${content}\033[0m"
    exit 1
}

execute_cmd()
{
    command="${1}"
    #LOG_INFO "RUN: ${command}"
    eval ${command}
    ret=$?
    if [ $ret -ne 0 ];then
        LOG_ERROR "FAILED execution of command: ${command}"
        exit 1
    fi
}

LOG_INFO()
{
    local content=${1}
    echo -e "\033[32m[INFO] ${content}\033[0m"
}


# check python
check_python()
{
    version_f1=$(execute_cmd "python -V 2>&1|awk '{print \$2}'|awk -F '.' '{print \$1}'")
    # must be python 3
    if [ $(($version_f1)) -lt 3 ];then
        echo "1"
        return
    fi
    # must be >= python 3.6
    version_f2=$(execute_cmd "python -V 2>&1|awk '{print \$2}'|awk -F '.' '{print \$2}'")
    #`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $2}'`
    if [ $(($version_f2)) -lt 6 ];then
        echo "1"
        return
    fi
    echo "0"
}

install_pyenv()
{
    local pyenv_str=$(grep "pyenv" ${shell_rc})
    local pydir="${HOME}/.pyenv"
    local pydir_virtual="${HOME}/.pyenv/plugins/pyenv-virtualenv"
    if [ ! -z "${pyenv_str}" ] && [ -d "${pydir}" ] && [ -d "${pydir_virtual}" ];then
        LOG_INFO "pyenv has already been inited!"
        return
    fi
    LOG_INFO "clone and init pyenv to install python 3.7.3 !"
    # clone pyenv
    
    if [ ! -d "${pydir}" ];then
        execute_cmd "git clone https://github.com/yyuu/pyenv.git ~/.pyenv"
    fi
    
    if [ ! -d "${pydir_virtual}" ];then
		execute_cmd "git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv"
    fi
    # export env
    execute_cmd "echo 'export PATH=~/.pyenv/bin:\$PATH' >> ${shell_rc}"
    execute_cmd "echo 'export PYENV_ROOT=~/.pyenv' >> ${shell_rc}"
    execute_cmd "echo 'eval \"\$(pyenv init -)\"' >> ${shell_rc}"
	source ${shell_rc}
    execute_cmd "echo 'eval \"\$(pyenv virtualenv-init -)\"' >> ~/.bash_profile"
	
    LOG_INFO "init pyenv succeed!"
}

install_python3()
{
    version=3.7.3
	python_versions=$(pyenv versions | grep "${version}")
	if [ -z "${python_versions}" ];then
         execute_cmd "wget https://www.python.org/ftp/python/$version/Python-$version.tar.xz -P ~/.pyenv/cache/;pyenv install $version"
    fi
	python_versions=$(pyenv virtualenvs | grep "python-sdk")
	if [ -z "${python_versions}" ];then
	    execute_cmd "pyenv virtualenv ${version} python-sdk"
	fi
}

upgrade_pip()
{
    execute_cmd "pip install --upgrade pip"
}

init_config()
{
	if [ ! -f "client_config.py" ];then
        execute_cmd "cp client_config.py.template client_config.py"
	fi
}

main()
{
  shell_env=$(echo $SHELL)
  if [ "${shell_env}" = "${ZSH}" ] || [ "${shell_env}" = "${REALZSH}" ];then
	shell_rc="${ZSHRC}"
  # default is ~/.bashrc
  else
	shell_rc="${BASHRC}"
  fi
 
  local ret=$(check_python)
  # need to install python
  if [ ${ret} = "1" ];then
    install_pyenv
    source ${shell_rc}
    install_python3 
  fi
  source ${shell_rc}
  execute_cmd "pyenv shell 3.7.3"
  execute_cmd "pyenv rehash"
  upgrade_pip
  init_config
}
main
