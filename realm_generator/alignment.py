import random


def get_alignment(data, bias=None, stdev=1):
    align = None
    align_print = 'none'

    if data['alignment']['id'] != 'none':
        align = []
        if bias is None:
            for axis in data['alignment']['axes']:
                align.append(random.choice(axis['list']))
        else:
            num_axes = len(data['alignment']['axes'])
            for axis, i in zip(data['alignment']['axes'], range(0,num_axes)):
                axis_max = len(axis['list']) - 1
                bias_index = axis['list'].index(bias[i])
                align_index = min(axis_max,(max(0,round(random.gauss(bias_index, stdev)))))
                align.append(axis['list'][align_index])
        align_print = ' '.join(align)

    return (align, align_print)
