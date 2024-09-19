from .. import global_vars, resources_loader


def test_GlobalVar():
    cfg = resources_loader.ConfigLoader()
    lb = global_vars.VarArmorLabels(
        cfg['image_folder'],
        cfg['label_folder'],
        cfg['deserted_image_folder']
    )
    for i in lb.pairs:
        print(i)
    print(lb.deserted_folder, end='\n\n')

    lb.delete(2)
    for i in lb.pairs:
        print(i)
    print()

    lb.restore(0)
    for i in lb.pairs:
        print(i)