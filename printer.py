# Updateable stdout printing.
import sys

class Printer():
    def __init__(self,data):
        sys.stdout.write("\r\x1b[K"+data.__str__())
        sys.stdout.flush()