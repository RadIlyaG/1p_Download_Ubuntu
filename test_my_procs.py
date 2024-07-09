import json
import lib_gen_1pDownload as lib_gen
import lib_radapps_1pDownload as radapps

def test_retrive_dut_family(mainapp):
    mainapp.gaSet['log'] = '/home/ilya/temp/11.txt'
    ws = radapps.WebServices()
    ws.print_rtext = False
    gen = lib_gen.Gen()

    for id_number in ['DC1002309464', 'DC1002281177', 'DC1002325736', 'DC10023011897']:
        res, dicti = ws.retrieve_oi4barcode(id_number)
        dbr_name = dicti['item']
        print(f'bind_uutId_entry res:{res} dbr_name:{dbr_name}')
        if res:
            mainapp.title(str(mainapp.gaSet['gui_num']) + ': ' + dbr_name)
            mainapp.gaSet['dbr_name'] = dbr_name
        else:
            db_dict={'title': "Get DBR Name fail", 'type': ['OK'], 'message': dbr_name,
                                        'icon': '::tk::icons::error'}
            print(db_dict)
            return False

        ret = gen.retrive_dut_fam(mainapp)
        print(f'bind_uutId_entry ret_retrive_dut_fam:{ret} mainapp.gaSet:{mainapp.gaSet}')
        # gen.add_to_log(mainapp, mainapp.gaSet)
        try:
            with open(mainapp.gaSet['log'], 'a+') as fi:
                json.dump(mainapp.gaSet, fi, indent=2, sort_keys=True)
        except Exception as e:
            print(e)
            #raise (e)


