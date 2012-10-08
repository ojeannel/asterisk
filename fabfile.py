from fabric.api import *
from cuisine import *

env.hosts = ['vagrant@33.33.33.11']
env.password = 'vagrant'
env.abort_on_prompts = True

@task()
def asterisk_greenfield():
  update_system()
  install_system_packages()
  configure_packages()
  setup_users_groups()

@task 
def update_system():
  sudo("aptitude update -f -y && aptitude upgrade -f -y")

@task
def install_system_packages():
  list = 'ntp build-essential subversion libncurses5-dev libssl-dev libxml2-dev \
    vim-nox git-core curl wget sudo autoconf automake binutils-doc bison \
    build-essential flex help2man libtool patch zlib1g zlib1g-dev zlibc libc6 libevent-dev \
    libbz2-dev libpcre3 libpcre3-dev libpcrecpp0 libssl0.9.8 libreadline5 \
    libreadline5-dev libxml2 libxml2-dev libxslt1.1 libxslt1-dev libmcrypt-dev \
    ssl-cert libssl-dev screen unzip unrar coreutils zsh'
  sudo("aptitude install %s -f -y" % list)

@task
def configure_packages():
  configure_ntp()

def configure_ntp():
  sudo('/etc/init.d/ntp restart')

@task
def setup_users_groups():
  group_ensure("asteriskpbx")
  user_ensure("asteriskpbx", "password", None, None, None, '/bin/zsh')
  group_user_ensure("asteriskpbx", "asteriskpbx")
  sudo("echo '%asteriskpbx ALL=(root) ALL' > /etc/sudoers.d/asteriskpbx")
  sudo("chmod 0440 /etc/sudoers.d/asteriskpbx")
  

def setup_asterisk()
  install_asterisk_module_dependencies()
  install_libpri()
  install_dadhi()
  install_asterisk()
