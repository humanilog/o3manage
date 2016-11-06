from pwd import getpwnam
from os import chdir, mkdir
import os.path
import multiprocessing
import configparser
import string
import random

import logging
logger = logging.getLogger(__name__)

from plumbum.cmd import adduser, git
git_checkout = git["checkout"]

import venv

from .su import sudef
from . import pkg

def genpasswd(length=20):
    """
    Generating a password string
    """
    choices = list(set(
        string.ascii_letters + string.digits + string.punctuation
    ) - set("%'") - set('"'))
    return "".join(random.choice(choices) for i in range(length))

@sudef
def _create_su(
    name, odoo_conf, repo="https://github.com/odoo/odoo.git", branch="9.0"
):
    """
    Does the steps to create an odoo instance under a specific user
    """
    passwd = getpwnam(name)
    home = passwd[5]

    git_clone = git["clone", "--depth", "1", "--branch", branch]

    logger.info("Creating directories")

    chdir(home)
    odoo_root_dir = os.path.join(home, "odoo")
    mkdir(odoo_root_dir)
    chdir(odoo_root_dir)

    autodirs = {
        "log": os.path.join(odoo_root_dir, "log"),
        "lib": os.path.join(odoo_root_dir, "lib"),
        "odoo_addons": os.path.join(odoo_root_dir, "odoo_addons")
    }

    for autodir in autodirs.values():
        mkdir(autodir)

    logger.info("Cloning repository")

    git_clone(repo, "odoo")
    git_dir = os.path.join(odoo_root_dir, "odoo")
    
    chdir(git_dir)
    git_checkout("9.0")
    chdir(odoo_root_dir)

    logger.info("Writing configuration")

    configfile = os.path.join(odoo_root_dir, "odoo.conf")
    config = configparser.ConfigParser()

    o3conf = dict(autodirs)
    o3conf.update({
        "root": odoo_root_dir,
        "conf": configfile,
        "git": git_dir
    })

    config["options"] = {k: v for k, v in odoo_conf.items() if v is not None}
    config["o3manage"] = o3conf
    
    return config


class OdooInstance():
    @classmethod
    def create(
        cls, user, port_base, pkg_manager=pkg.apt.AptPackageManager(),
        workers=multiprocessing.cpu_count(),
        db_user=None, db_password=None, db_host=None, db_port=None,
        **kwargs
    ):
        """
        Create an odoo instance
        """
        if len(str(port_base)) != 3:
            raise ValueError("Port base has to consist of three digits.")

        pkg_manager.ensure_dependencies() # TODO: check apt return codes
        adduser(user)

        # put all config vars into a dict
        # remove method arguments
        configdict = locals()
        del configdict["cls"]
        del configdict["user"]
        del configdict["port_base"]
        del configdict["pkg_manager"]
        del configdict["kwargs"]

        configdict["admin_passwd"] = genpasswd()

        configdict["xmlrpc_port"] = "{}1".format(port_base)
        configdict["longpolling_port"] = "{}2".format(port_base)
        configdict["workers"] = str(workers)

        configdict["log_level"] = "warn"

        # all other arguments are config variables
        configdict.update(kwargs)

        config = _create_su(user, configdict)
        
        config["options"]["logfile"] = os.path.join(
            config["o3manage"]["log"], "odoo.log")

        with open(config["o3manage"]["conf"], "w") as f:
            config.write(f)

        return cls(config)
    
    @property
    def root_dir(self):
        return self.config["o3manage"]["root"]
    
    @property
    def admin_passwd(self):
        return self.config["options"]["admin_passwd"]

    def __init__(self, config):
        if isinstance(config, str):
            filename = config
            config = configparser.ConfigParser()
            config.read(filename)
        self.config = config
