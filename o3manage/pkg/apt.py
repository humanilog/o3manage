from .manager import PackageManager

try:
    from plumbum.cmd import apt
except ImportError:
    from plumbum.cmd import apt_get as apt

apt_install = apt["-y", "install"]

class AptPackageManager(PackageManager):
    _dependencies = [
        "postgresql-server-dev-all",
        "python-dev",
        "python-pip",
        "git",
        "nodejs",
        "nodejs-legacy",
        "node-less",
        "libldap2-dev",
        "libsasl2-dev",
        "libxml2-dev",
        "libxslt1-dev",
        "libjpeg-dev"
    ]

    def __init__(self):
        apt("update")

    def install(self, dependencies):
        apt_install(*list(dependencies))