from time import sleep, time
import spidev
import numpy as np
def __read_spi(spi, channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

def _read_spi(spi, channel):
    t0 = time()
    lis_v = []
    while True:
        v = __read_spi(spi, channel)
        lis_v.append(v)
        if time() - t0 > 0.1:
            break
    data = np.average(lis_v)
    return data
    
spi_client = spidev.SpiDev()
spi_client.close()#this is important, otherwise too many files exception is raised after a whime
spi_client.open(0, 0)
i=0
while True:
    spi_client.close()#this is important, otherwise too many files exception is raised after a whime
    spi_client.open(0, 0)
    r = _read_spi(spi=spi_client, channel=0)
    v = r/1023.0 * 5
    psi = (v - 0.5) * 5.0/4.0
    mh2o = psi* 0.703
    print "spi=%s volts=%s psi=%s mh2o=%s" %(round(r,2),round(v,4), round(psi,4), round(mh2o,4))
    sleep (1)
    if i%10==0:
        print ""
    i+=1