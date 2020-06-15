#!/bin/bash
shell_env=""
shell_rc=""
ZSH="/bin/sh"
REALZSH="/bin/zsh"
BASH="/bin/bash"

ZSHRC="${HOME}/.zshrc"
BASHRC="${HOME}/.bashrc"

SOLC_LINUX_URL="https://github.com/FISCO-BCOS/solidity/releases/download/v0.4.25/solc-linux.tar.gz"
SOLC_MAC_URL="https://github.com/FISCO-BCOS/solidity/releases/download/v0.4.25/solc-mac.tar.gz"
SOLC_LINUX_GM_URL="https://github.com/FISCO-BCOS/solidity/releases/download/v0.4.25/solc-linux-gm.tar.gz"
SOLC_MAC_GM_URL="https://github.com/FISCO-BCOS/solidity/releases/download/v0.4.25/solc-mac-gm.tar.gz"
SOLC_DIR="bin/solc/v0.4.25"
SOLC_PATH="${SOLC_DIR}/solc"
SOLC_GM_PATH="${SOLC_DIR}/solc-gm"
OS_TYPE="Linux"

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
    LOG_INFO "clone and init pyenv to install python 3.7.3 !"
    # clone pyenv
    if [ ! -d "${pydir}" ];then
        execute_cmd "git clone https://github.com/pyenv/pyenv.git ~/.pyenv"
    fi

    if [ ! -d "${pydir_virtual}" ];then
		execute_cmd "git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv"
    fi
    if [ ! -z "${pyenv_str}" ] && [ -d "${pydir}" ] && [ -d "${pydir_virtual}" ];then
        LOG_INFO "pyenv has already been inited!"
        return
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
        execute_cmd "wget https://www.python.org/ftp/python/$version/Python-$version.tar.xz -P ~/.pyenv/cache/ && pyenv install $version"
    fi
	python_versions=$(pyenv virtualenvs | grep "python-sdk")
	if [ -z "${python_versions}" ];then
	    execute_cmd "pyenv virtualenv ${version} python-sdk"
	fi
}

install_linux_solc()
{
    mkdir -p ${SOLC_DIR}
    if [ ! -f ${SOLC_PATH} ];then
        LOG_INFO "Download and install solc into ${SOLC_PATH}..."
        curl -LO ${SOLC_LINUX_URL}
        tar -xvf solc-linux.tar.gz
        mv solc ${SOLC_DIR}
    else
        LOG_INFO "solc is already installed into ${SOLC_PATH}"
    fi
    if [ ! -f ${SOLC_GM_PATH} ];then
        LOG_INFO "Download and install solc-gm into ${SOLC_GM_PATH}..."
        curl -LO ${SOLC_LINUX_GM_URL}
        tar -xvf solc-linux-gm.tar.gz
        mv solc ${SOLC_GM_PATH}
    else
        LOG_INFO "solc-gm is already installed into ${SOLC_GM_PATH}"
    fi
}

install_mac_solc()
{
    mkdir -p ${SOLC_DIR}
    if [ ! -f ${SOLC_PATH} ];then
        LOG_INFO "Download and install solc into ${SOLC_PATH}..."
        curl -LO ${SOLC_MAC_URL}
        tar -xvf solc-mac.tar.gz
        mv solc ${SOLC_DIR}
    else
        LOG_INFO "solc is already installed into ${SOLC_PATH}"
    fi
    if [ ! -f ${SOLC_GM_PATH} ];then
        LOG_INFO "Download and install solc-gm into ${SOLC_GM_PATH}..."
        curl -LO ${SOLC_MAC_GM_URL}
        tar -xvf solc-mac-gm.tar.gz
        mv solc ${SOLC_GM_PATH}
    else
        LOG_INFO "solc-gm is already installed into ${SOLC_GM_PATH}"
    fi
}

init_config()
{
	if [ ! -f "client_config.py" ];then
        LOG_INFO "copy config file..."
        execute_cmd "cp client_config.py.template client_config.py"
	fi
    solc_path="bin/solc/v0.4.25"
    LOG_INFO "install solc v0.4.25..."
    if [ "${OS_TYPE}" == "Linux" ];then
        install_linux_solc
    elif [ "${OS_TYPE}" == "Darwin" ];then
        install_mac_solc
    fi
}

python_init()
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
    version="3.7.3"
    which pyenv
    # already install pyenv, then check the versions
    if [ $? -eq 0 ];then
        python_versions=$(pyenv versions | grep python-sdk)
        if [ ! -z "${python_versions}" ];then
            LOG_INFO "already install python ${version}, please activate the version with command: pyenv activate python-sdk"
            return
        fi
    fi
    
    install_pyenv
    source ${shell_rc}
    install_python3
    LOG_INFO "install python ${version} success, please activate with command: pyenv activate python-sdk"
  else
    python_version=$(execute_cmd "python -V 2>&1")
    LOG_INFO "python version already ${python_version} already meet requirement~"
  fi
}

function help()
{
    echo $1
    cat << EOF
    Usage:
        -p <Optional>   init python environment, install python-3.7.3 if current python version is lower than python-3.6
        -i <Required>   init the basic environment
EOF
}

main()
{
    OS_TYPE=$(uname)
    while getopts "pih" option; do
        case ${option} in
        p) python_init
        ;;
        i) init_config
        ;;
        h) help
        esac
    done
}
main $@
