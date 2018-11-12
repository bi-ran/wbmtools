from collections import defaultdict

urlbase = "http://cmswbm.cern.ch/cmsdb/servlet"

def rm_hlt_path_version(name):
    ver_pos = name.rfind("_v")
    if ver_pos != -1:
        return str(name[:ver_pos])
    return str(name)


def get_hlt_prescales(mode, parser):
    url = "{}/TriggerMode?KEY={}".format(urlbase, mode)
    tables = parser.parse_url_tables(url)

    for _ in range(10):
        tables = parser.parse_url_tables(url)
        if len(tables) > 1:
            break

    try:
        return tables[2]
    except IndexError:
        print("get_hlt_prescales failed for mode", mode)
        return None


def get_hlt_summary(run, parser):
    url = "{}/HLTSummary?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    for _ in range(10):
        tables = parser.parse_url_tables(url)
        if len(tables) > 1:
            break

    try:
        return tables[1]
    except IndexError:
        print("get_hlt_summary failed for run", run)
        return None


def get_hlt_rates(run, parser):
    blacklist = ["Name", "HLTriggerFinalPath", "HLTTriggerFirstPath"]
    summary = get_hlt_summary(run, parser)

    hlt_rates = {}
    for entry in summary:
        # print(run, entry)
        try:
            path = rm_hlt_path_version(entry[1].split()[0])

            if path not in blacklist:
                hlt_rates[path] = str(entry[6])
        except IndexError:
            pass

    return hlt_rates


# def get_hlt_rates(run, minls, maxls, parser):
#     url = "{}/HLTSummary?fromLS={}&toLS={}&RUN={}".format(
#         urlbase, minls, maxls, run)
#     tables = parser.parse_url_tables(url)

#     hlt_rates = {}
#     for line in tables[1][2:]:
#         # print(line)
#         rates = [float(entry.replace(", ", "")) for entry in line[3:7]]
#         hlt_rates[line[1].split("_v")[0]] = rates

#     return hlt_rates


def get_run_info(run, parser):
    url = "{}/RunSummary?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    for _ in range(10):
        tables = parser.parse_url_tables(url)
        if len(tables) > 1:
            break

    try:
        tables[1]
    except IndexError:
        print("get_run_info failed for run", run)
        return None

    run_info = {}
    run_data = tables[1][1]

    run_info["run"] = run_data[0]
    run_info["lumi"] = run_data[1]
    run_info["key"] = run_data[3]
    run_info["l1"] = run_data[4]
    run_info["hlt"] = run_data[5]
    run_info["start"] = run_data[6]
    run_info["end"] = run_data[7]
    run_info["counts"] = run_data[8]
    run_info["bfield"] = run_data[9]
    run_info["tier0"] = run_data[10]
    run_info["components"] = run_data[11]

    # this may not be filled for some runs
    try:
        run_data_more = tables[3]
        run_info["l1menu"] = run_data_more[5][1]
        run_info["cmssw"] = run_data_more[7][1]
        run_info["fill"] = run_data_more[14][1]
    except IndexError:
        run_info["l1menu"] = "null"
        run_info["cmssw"] = "null"
        run_info["fill"] = "-1"

    return run_info


def get_lumi_summary(run, parser):
    url = "{}/LumiSections?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    for _ in range(10):
        tables = parser.parse_url_tables(url)
        if len(tables) > 1:
            break

    try:
        # fixing up the summary
        tables[1].insert(1, tables[1][0][41:])
        tables[1][0] = tables[1][0][:41]
        return tables[1]
    except IndexError:
        print("get_lumi_summary failed for run", run)
        return None


def get_pscol_for_lumis(run, parser):
    url = "{}/LumiSections?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    pscols = {}
    for line in tables[1]:
        offset = 41 if line[0] == "L S" else 0
        lumi = int(line[0+offset])
        pscol = int(line[1+offset])
        # instlumi = float(line[3+offset])
        pscols[lumi] = pscol

    return pscols


def get_lumis_for_pscol(run, parser):
    url = "{}/LumiSections?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    lumis = defaultdict(list)
    for line in tables[1]:
        offset = 41 if line[0] == "L S" else 0
        lumi = int(line[0+offset])
        pscol = int(line[1+offset])
        # instlumi = float(line[3+offset])
        lumis[pscol].append(lumi)

    return lumis


def get_ave_inst_lumi(instlumis, minls, maxls):
    if maxls == -1:
        maxls = max(instlumis.keys())

    nlumis = sum(1 for lumi in range(minls, maxls+1))
    if nlumis == 0:
        return 0

    return sum(instlumis[lumi] for lumi in range(minls, maxls+1)) / nlumis


def get_runs_for_time_period(start_date, end_date, parser):
    url = ("{}/FillSummary?runtimeTypeID=&fromTime={}&toTime={}"
           "&nameExp=LHCFILL&debug=0&showSection=0").format(
               urlbase, start_date, end_date)
    tables = parser.parse_url_tables(url)

    runs = []
    for table in tables:
        if table[0][0] != "Name":
            continue

        # print(table)
        for line in table[1:]:
            fill_runs = line[13]
            # print(line)
            for run in fill_runs.split():
                runs.append(run)

    return runs


def get_runs_for_fill(fill, parser):
    url = "{}/FillRuntimeChart?lhcFillID={}".format(urlbase, fill)
    tables = parser.parse_url_tables(url)

    for table in tables:
        if table[0][0] == "LHC Fill":
            return table[1][1].split()
    return None


def get_prescale_columns(key, parser):
    url = "{}/TriggerMode?KEY={}".format(urlbase, key)
    tables = parser.parse_url_tables(url)

    pscols = {}
    paths = tables[2]
    for line in paths:
        name = rm_hlt_path_version(line[1].split()[0])
        pscols[name] = line[2:-1]

    return pscols


def get_prescale_set(run, parser):
    url = "{}/PrescaleSets?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    for _ in range(10):
        tables = parser.parse_url_tables(url)
        if len(tables) > 1:
            break

    try:
        return tables[1]
    except IndexError:
        # print(parser.read_url(url)
        print("get_prescale_set failed for run", run)
        return []


def get_prescale_set_with_mask(run, parser):
    url = "{}/PrescaleSets?RUN={}".format(urlbase, run)
    tables, tblfmt = parser.parse_url_tables_format(url)

    for _ in range(10):
        tables, tblfmt = parser.parse_url_tables_format(url)
        if len(tables) > 1:
            break

    try:
        return map(lambda x, y: (x, y[0]), tables[1], tblfmt[1])
    except IndexError:
        # print(parser.read_url(url))
        print("get_prescale_set_with_mask failed for run", run)
        return []


def get_dcs_by_lumi(run, parser):
    url = "{}/LumiSections?RUN={}".format(urlbase, run)
    tables, tblfmt = parser.parse_url_tables_format(url)

    for index, entry in enumerate(tables[1]):
        print(entry, tblfmt[1][index])
