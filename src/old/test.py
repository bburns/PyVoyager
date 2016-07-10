

# prefer simpler testing in each file...


import step0download


def test_get_download_url():
    assert step0download.get_download_url(5201) == "http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5201.tar.gz"


test_get_download_url()



    
