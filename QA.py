def do_lines_overlap(line1, line2):
    x1, x2 = line1
    x3, x4 = line2

    return (x1 <= x4 and x2 >= x3) or (x3 <= x2 and x4 >= x1)
