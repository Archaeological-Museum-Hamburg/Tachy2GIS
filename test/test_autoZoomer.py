from plugin.T2G.autoZoomer import ExtentProvider


def test_init():
    ep = ExtentProvider()
    assert ep.features.maxlen == 0


