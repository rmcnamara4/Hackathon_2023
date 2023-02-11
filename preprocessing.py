import pandas as pd


def date_difference(date_yyyymmdd, date_yyyymm):
    month_diff = (int(date_yyyymmdd[:4]) - int(date_yyyymm[:4])) * 12
    if len(date_yyyymm) == 4:
        return month_diff
    return month_diff + (int(date_yyyymm[4:]) - int(date_yyyymmdd[4:6]))


def preprocess_data(json_file: dict):
    rows = []
    drug_infos = []
    for result in json_file['results']:
        rows.append(
            {'SourceCountry': result['primarysourcecountry'] if 'primarysourcecountry' in result.keys() else None,
             'Qualification': result['primarysource']['qualification'] if 'qualification' in result[
                 'primarysource'].keys() else None,
             'SetAge': result['patient']['patientonsetage'] if 'patientonsetage' in result['patient'].keys() else None,
             'Sex': result['patient']['patientsex'] if 'patientsex' in result['patient'].keys() else None,
             'Serious': result['serious']
             })
        for drug in result['patient']['drug']:
            if 'activesubstance' not in drug.keys():
                continue
            rows[-1][drug['activesubstance']['activesubstancename']] = 1
            if 'DrugChar' + str(drug['drugcharacterization']) in rows[-1].keys():
                rows[-1]['DrugChar' + str(drug['drugcharacterization'])] += 1
            else:
                rows[-1]['DrugChar' + str(drug['drugcharacterization'])] = 1
            if 'drugstructuredosagenumb' in drug.keys():
                rows[-1][drug['activesubstance']['activesubstancename'] + 'Dosage'] = drug['drugstructuredosagenumb']
            else:
                rows[-1][drug['activesubstance']['activesubstancename'] + 'Dosage'] = 'Missing'
            if 'drugstartdate' in drug.keys():
                if 'MostRecentDrug' in rows[-1].keys():
                    rows[-1]['MostRecentDrug'] = min(rows[-1]['MostRecentDrug'],
                                                     date_difference(result['receivedate'], drug['drugstartdate']))
                else:
                    rows[-1]['MostRecentDrug'] = date_difference(result['receivedate'], drug['drugstartdate'])
    df = pd.DataFrame(rows)

    #removing the drugs that only occur once
    a = pd.DataFrame(df.sum()).reset_index()
    a = a.drop(0, axis=0)
    df = df.drop(list(a[a[0] == 1]['index']), axis=1)
    
    df = pd.concat([df.drop('SourceCountry',axis=1),pd.get_dummies(df['SourceCountry']).drop(['ZA'],axis=1)],axis=1)

    return df
