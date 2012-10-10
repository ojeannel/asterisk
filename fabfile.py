from fabric.api import *
from cuisine import *

# http://devblog.seomoz.org/2011/08/launching-and-deploying-instances-with-boto-and-fabric/
# https://github.com/sebastien/cuisine/blob/master/src/cuisine.py

env.hosts = ['vagrant@33.33.33.11']
env.password = 'vagrant'
#env.abort_on_prompts = True
env.roledefs = {
    'provisioning': ['vagrant@33.33.33.11'], 
    'asterisk': ['asteriskpbx@33.33.33.11'], 
    }

@task
def full_asterisk_install():
  asterisk_greenfield()
  setup_asterisk()


@roles('provisioning')
def asterisk_greenfield():
  update_system()
  install_system_packages()
  configure_packages()
  setup_users_groups()

@task 
def update_system():
  sudo('cp /etc/apt/sources.list /etc/apt/sources.list.backup')
  #sudo("sed -i.bak 's/us.archive.ubuntu.com/fr.archive.ubuntu.com/g' /etc/apt/sources.list")
  conf = file_local_read('grubpc.debconf')
  file_write('/tmp/grubpc.debconf', conf)
  sudo('cat /tmp/grubpc.debconf | debconf-set-selections')
  sudo("sed -i.bak 's/http:\/\/us\.archive\.ubuntu\.com\/ubuntu\//http:\/\/bouyguestelecom\.ubuntu\.lafibre\.info\/ubuntu\//g' /etc/apt/sources.list")
  sudo('grub-install /dev/sda')
  sudo('update-grub')
  sudo("DEBIAN_FRONTEND=noninteractive  aptitude update -f -y && aptitude upgrade -f -y")
  fabric.operations.reboot()

@task
def install_system_packages():
  list = 'ntp build-essential subversion libncurses5-dev libssl-dev libxml2-dev \
      vim-nox git-core curl wget sudo autoconf automake binutils-doc bison \
      build-essential flex help2man libtool patch zlib1g zlib1g-dev zlibc libc6 libevent-dev \
      libbz2-dev libpcre3 libpcre3-dev libpcrecpp0 libssl0.9.8 libreadline5 \
      libreadline5-dev libxml2 libxml2-dev libxslt1.1 libxslt1-dev libmcrypt-dev \
      ssl-cert libssl-dev screen unzip unrar coreutils zsh debconf-utils'
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
  sudo("echo '%asteriskpbx ALL=(ALL) ALL' > /etc/sudoers.d/asteriskpbx")
  sudo("chmod 0440 /etc/sudoers.d/asteriskpbx")





@task
@roles('asterisk')
def setup_asterisk(): 
  env.password = 'password'
  install_asterisk_module_dependencies()
  install_libpri()
  install_dadhi()
  install_asterisk()

def install_asterisk_module_dependencies():
  # Needed temporarily due to https://bugs.launchpad.net/ubuntu/+source/aptitude/+bug/831768 
  sudo("echo '# foreign-architecture i386' > /etc/dpkg/dpkg.cfg.d/multiarch")
  list = 'libgmime-2.6-dev libgmime-2.6-0 libsrtp0 libsrtp0-dev' 
  sudo("aptitude install %s -f -y" % list)

  run('mkdir -p ~/src/asterisk-complete/asterisk')
  with cd('~/src/asterisk-complete/asterisk'):
    run('svn checkout http://svn.asterisk.org/svn/asterisk/tags/10.9.0-rc3/')
  with cd('~/src/asterisk-complete/asterisk/10.9.0-rc3'):
    sudo('./contrib/scripts/install_prereq install')  # Has prompt - phone code
    #libvpb0 ITU-T telephone code:
    sudo('./contrib/scripts/install_prereq install-unpackaged')

def install_libpri():
  run('mkdir -p ~/src/asterisk-complete/libpri')
  with cd('~/src/asterisk-complete/libpri'):
    run('svn checkout http://svn.asterisk.org/svn/libpri/tags/1.4.12/')
  with cd('~/src/asterisk-complete/libpri/1.4.12'):
    run('make')
    sudo('make install')

def install_dadhi():
  # Make sure kernel sources are installed first
  sudo("aptitude install linux-headers-`uname -r` -f -y")

  run('mkdir -p ~/src/asterisk-complete/dahdi')
  with cd('~/src/asterisk-complete/dahdi'):
    run('svn checkout http://svn.asterisk.org/svn/dahdi/linux-complete/tags/2.6.1+2.6.1/')
  with cd('~/src/asterisk-complete/dahdi/2.6.1+2.6.1'):
    run('make')
    sudo('make install')
    sudo('make config')

def install_asterisk():
  with cd('~/src/asterisk-complete/asterisk/10.9.0-rc3'):
    run('./configure')
    run('make')
    sudo('make install')
    set_asterisk_directory_permissions()
    sudo('make config')
    #sudo('make menuselect')
    sudo('make install')
    sudo('make OVERWRITE=n samples')
  sudo('mkdir -p /etc/asterisk/samples')
  sudo('mv /etc/asterisk/*.conf /etc/asterisk/samples')
  sudo("sed -i.bak 's/asterisk/asteriskpbx/g' /etc/udev/rules.d/dahdi.rules")

def set_asterisk_directory_permissions():
  sudo('chown -R asteriskpbx:asteriskpbx /usr/lib/asterisk/')
  sudo('chown -R asteriskpbx:asteriskpbx /var/lib/asterisk/')
  sudo('chown -R asteriskpbx:asteriskpbx /var/spool/asterisk/')
  sudo('chown -R asteriskpbx:asteriskpbx /var/log/asterisk/')
  sudo('chown -R asteriskpbx:asteriskpbx /var/run/asterisk')
  sudo('chown asteriskpbx:asteriskpbx   /usr/sbin/asterisk')
