class Instance:

    def __init__(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as f:
            lines = f.read().split('\n')

        header = lines[0].strip().split()
        self.m = int(header[0])
        self.n = int(header[1])
        self.ne = int(header[2])
        self.B = int(header[3])

        self.profits = list(map(int, lines[1].strip().split()))

        self.weights = list(map(int, lines[2].strip().split()))

        self.alt_resources = [set() for _ in range(self.m)]
        for k in range(self.ne):
            parts = lines[3 + k].strip().split()
            self.alt_resources[int(parts[0])].add(int(parts[1]))

    def __repr__(self):
        return f"Instance({self.filepath}: m={self.m}, n={self.n}, ne={self.ne}, B={self.B})"
