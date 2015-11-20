import output
import settings
import image
import itertools

def compare_campaign(cid):
    pb = output.PathBuilder(cid=cid)
    compare_output(pathbuilder=pb, configs=settings.DEFAULT.configs)

# TODO: Refactor to new module
def compare_configs(pathbuilder, configs):
    sizes = settings.DEFAULT.tagsizes

    # Compare all combinations of configs
    for a, b in itertools.combinations(configs, 2):
        for s in sizes:
            pba = output.PathBuilder(config=a, size=s, cid=pathbuilder.cid)
            pbb = output.PathBuilder(config=b, size=s, cid=pathbuilder.cid)
            if not pba.validate():
                "Path not found for {}, skipping compare...".format(pba.path)
                continue
            if not pbb.validate():
                "Path not found for {}, skipping compare...".format(pbb.path)
                continue
            image.compare(pba.tagimage, pbb.tagimage)


# TODO: Refactor to new module
def compare_output(pathbuilder, configs):
    print ""
    print "_--==== COMPARING RESULTS ====--_"
    print ""

    # TODO: Need to do n-way compare for configs - hardcoding to 2 for now
    assert pathbuilder, "No pathbuilder object!"
    assert configs, "No configs!"
    compare_configs(pathbuilder, configs)

if __name__ == '__main__':
    for cid in settings.DEFAULT.campaigns:
        compare_campaign(cid=cid)
