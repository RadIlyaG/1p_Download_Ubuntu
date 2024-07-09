import json
import lib_gen_1pDownload as lib_gen
import lib_radapps_1pDownload as radapps


def test_retrive_dut_family(mainapp):

    ws = radapps.WebServices()
    ws.print_rtext = False
    gen = lib_gen.Gen()
    log = f'/home/ilya/temp/{gen.my_time()}.txt'

    for id_number in ['DC1002309464', 'DC1002281177', 'DC1002325736', 'DC10023011897', 'DC1002309826', 'DC1002319735',
                      'DC1002300153', 'DC1002275246', 'DC1002275006', 'DC1002275325',
                      'DC1002306005', 'DC1002287083', 'DC1002284907', 'DC1002306120',
                      'DC1002326762', 'DC1002328380']:
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

        # print(json.dumps(mainapp.gaSet, indent=2, sort_keys=True))

        with open(log, 'a+') as fi:
            fi.write(f'{id_number} {dbr_name} \n')
            for k, v in mainapp.gaSet.items():
                fi.write(f'{k}: {v} \n')
            fi.write("\n")

        # gen.add_to_log(mainapp, f'{dbr_name}')
        # for k, v in mainapp.gaSet.items():
        #     gen.add_to_log(mainapp, f'{k}: {v}')
        # gen.add_to_log(mainapp, f' ')
        # try:
        #     with open(mainapp.gaSet['log'], 'a+') as fi:
        #         json.dump(mainapp.gaSet, fi, indent=2, sort_keys=True)
        # except Exception as e:
        #     print(e)
        #     raise (e)


