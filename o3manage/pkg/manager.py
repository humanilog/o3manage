class PackageManager(object):
    _dependencies = []

    def ensure_dependencies(self):
        self.install(self._dependencies)
    
    def install(self, dependencies):
        raise NotImplementedError()