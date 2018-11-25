from collections import defaultdict

urlbase = "http://cmswbm.cern.ch/cmsdb/servlet"

def get_prescale_sets(parser, run):
    url = "{}/PrescaleSets?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    try:
        return tables[1]
    except IndexError:
        print("get_prescale_set failed for run", run)
        return None


def get_prescale_columns(parser, key):
    url = "{}/TriggerMode?KEY={}".format(urlbase, key)
    tables = parser.parse_url_tables(url)

    try:
        tables[2]
    except IndexError:
        print("get_prescale_columns failed for key", key)
        return None

    prescales = {}
    for row in tables[2]:
        path = row[1].split()[0]
        prescales[path] = row[2:]

    return prescales


def get_l1_summary(parser, run, minls=1, maxls=-1):
    url = "{}/L1Summary?fromLS={}&toLS={}&RUN={}".format(
        urlbase, minls, maxls, run)
    tables = parser.parse_url_tables(url)

    try:
        tables[7]
    except IndexError:
        print("get_hlt_summary failed for run", run)
        return None

    summary = {}
    for row in tables[7][2:]:
        if not row[1]:
            continue

        line = [cell.replace(',', '') for cell in row]
        summary[line[1].split()[0]] = line

    return summary


def get_hlt_summary(parser, run, minls=1, maxls=-1):
    url = "{}/HLTSummary?fromLS={}&toLS={}&RUN={}".format(
        urlbase, minls, maxls, run)
    tables = parser.parse_url_tables(url)

    try:
        tables[1]
    except IndexError:
        print("get_hlt_summary failed for run", run)
        return None

    summary = {}
    for row in tables[1][2:]:
        line = [cell.replace(',', '') for cell in row]
        summary[line[1].split()[0]] = line

    return summary


def get_run_summary(parser, run):
    url = "{}/RunSummary?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    try:
        table = tables[1][1]
    except IndexError:
        print("get_run_info failed for run", run)
        return None

    summary = {}
    summary['run'] = table[0]
    summary['lumi'] = table[1]
    summary['key'] = table[3]
    summary['l1key'] = table[4]
    summary['hltkey'] = table[5]
    summary['start'] = table[6]
    summary['stop'] = table[7]
    summary['counts'] = table[8]
    summary['bfield'] = table[9]
    summary['components'] = table[11]

    # this may not be filled for some runs
    try:
        table = tables[3]
        summary["cmssw"] = table[7][1]
        summary["fill"] = table[14][1]
    except IndexError:
        summary["cmssw"] = "null"
        summary["fill"] = "-1"

    return summary


def get_lumis_summary(parser, run):
    url = "{}/LumiSections?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    try:
        # fixing up the summary
        tables[1].insert(1, tables[1][0][41:])
        tables[1][0] = [s.replace(' ', '') for s in tables[1][0][:41]]
        return tables[1]
    except IndexError:
        print("get_lumi_summary failed for run", run)
        return None


def get_pscol_for_lumis(parser, run):
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


def get_lumis_for_pscol(parser, run):
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


def get_dcs_by_lumi(parser, run):
    url = "{}/LumiSections?RUN={}".format(urlbase, run)
    tables = parser.parse_url_tables(url)

    for index, entry in enumerate(tables[1]):
        print(entry)


def get_runs_for_fill(parser, fill):
    url = "{}/FillRuntimeChart?lhcFillID={}".format(urlbase, fill)
    tables = parser.parse_url_tables(url)

    for table in tables:
        if table[0][0] == "LHC Fill":
            return table[1][1].split()
    return None


def get_runs_for_time_period(parser, start_date, end_date):
    url = ("{}/FillSummary?runtimeTypeID=&fromTime={}&toTime={}"
           "&nameExp=LHCFILL&debug=0&showSection=0").format(
               urlbase, start_date, end_date)
    tables = parser.parse_url_tables(url)

    runs = []
    for table in tables:
        if table[0][0] != "Name":
            continue

        for line in table[1:]:
            for run in line[13].split():
                runs.append(run)

    return runs
