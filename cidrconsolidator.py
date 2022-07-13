"""Consolidate CIDR ranges."""

import math


class IPRange:
    def __init__(self, range):
        """Expects strings."""
        self.range = range

    def __str__(self):
        return self.range

    def __repr__(self):
        return f'IPRange({self})'

    def __add__(self, other):
        if self.decimal > other.decimal:
            return other+self  # with our setup, impossible, but try anyway
        ip = None
        cidr = None
        if self.decimal == other.decimal:
            ip = self.ip
            cidr = self.cidr if int(self.cidr) < int(other.cidr) else other.cidr
        elif self.decimal < other.decimal and self.next >= other.next:
            ip = self.ip
            cidr = self.cidr
        elif self.next == other.decimal and self.cidr == other.cidr:
            ip = self.ip
            cidr = str(int(self.cidr)-1)
        else:
            raise ValueError(f'Cannot add {self} to {other}')
        return IPRange(ip + '/' + cidr)

    def __iadd__(self, other):
        return self + other

    @property
    def range(self):
        return self.ip + '/' + self.cidr

    @range.setter
    def range(self, new):
        try:
            self.ip, self.cidr = new.split('/')
            assert self.decimal % 2**(32-int(self.cidr)) == 0
        except (ValueError, AssertionError) as e:
            raise ValueError(f'Invalid CIDR range format! ({new})') from e

    @property
    def decimal(self):
        dots = self.ip.split('.')
        return (((((int(dots[0])*256) + int(dots[1]))*256) + int(dots[2]))*256) + int(dots[3])

    @decimal.setter
    def decimal(self, new):
        num4 = int(new % 256)
        new = (new-num4)/256
        num3 = int(new % 256)
        new = (new-num3)/256
        num2 = int(new % 256)
        new = (new-num2)/256
        num1 = int(new)
        self.ip = f'{num1}.{num2}.{num3}.{num4}'

    @property
    def next(self):
        """Decimal form."""
        jump = 2**(32-int(self.cidr))
        return self.decimal + jump


def sort_func(iprange):
    return iprange.decimal


def do_shit():
    ranges = []
    with open("list.txt",'r') as file:
        for line in file:
            ranges.append(IPRange(line.strip()))
    ranges.sort(key=sort_func)
    change = True
    while change:
        change = False
        cranges = []
        for range in ranges:
            try:
                cranges[-1] += range
                change = True
            except (IndexError, ValueError):
                cranges.append(range)
            while True:
                range = cranges.pop()
                try:
                    cranges[-1] += range
                except (IndexError, ValueError):
                    cranges.append(range)
                    break;
        ranges = cranges
    with open('consolidated.txt','w') as file:
        for range in ranges:
            file.write(f'{range}\n')


if __name__ == "__main__":
    do_shit()
