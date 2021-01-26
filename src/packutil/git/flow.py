class Branch:
    def __init__(self, ref):
        self.name = "/".join(ref.split("/")[2:])
        self.category = self.name.split("/")[0]

    def __repr__(self):
        return self.name
