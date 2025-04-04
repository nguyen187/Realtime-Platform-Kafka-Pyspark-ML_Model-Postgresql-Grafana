from collections import OrderedDict
from tabulate import tabulate

class JobContext(object):
    def __init__(self, sc):
        self.counters = OrderedDict()
        self._init_accumulators(sc)
        self._init_shared_data(sc)

    def _init_accumulators(self, sc):
        pass

    def _init_shared_data(self, sc):
        pass

    def initalize_counter(self, sc, name):
        # Assuming you're using PySpark's `SparkContext` for accumulators
        self.counters[name] = sc.accumulator(0)

    def inc_counter(self, name, value=1):
        if name not in self.counters:
            raise ValueError(f"{name} counter was not initialized. ({list(self.counters.keys())})")
        self.counters[name] += value

    def print_accumulators(self):
        print(tabulate(self.counters.items(), headers=["Counter", "Value"], tablefmt="simple"))
