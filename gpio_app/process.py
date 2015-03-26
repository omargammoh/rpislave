from mng.processing import MP, _get_conf

def main(pins_conf):
    pins_conf = _get_conf()['apps']['gpio_app']['pins_conf']

    gpio_list = []

    for label, pconf in pins_conf.iteritems():
        print "setup the pin {pin} as {iou} desc {desc}".format(**pconf)

    return None
