"""
Goal: implement code for processing PHI files
    used for validation (false positives and negatives calculation)

    Precision   = tp / (tp + fp)
    Recal       = tp / (tp + fn)

Note: this file was exportet drom a Jupyter Notebook

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import pandas as pd

pd.set_option('display.max_columns', 700)
pd.set_option('display.width', 3000)
pd.set_option('display.max_colwidth', 200)


groups = {
    '1': {
        'source_flm_both': 'linkage_related/flm_both.csv',
        'source_ufh_both': 'linkage_related/ufh_both.csv',
        'out_file_merged': 'merged_2000_sample.csv',
        'out_file': '_candidates_from_2000_sample.csv',
    },
    '2': {
        'source_flm_both': 'linkage_related/flm_rule2.csv',
        'source_ufh_both': 'linkage_related/ufh_rule2.csv',
        'out_file_merged': 'merged_500_sample.csv',
        'out_file': '_candidates_from_500_sample.csv',
    },
    '3': {
        'source_flm_both': 'linkage_related/flm_rule1.csv',
        'source_ufh_both': 'linkage_related/ufh_rule1.csv',
        'out_file_merged': 'merged_11_sample.csv',
        'out_file': '_candidates_from_11_sample.csv',
    },
}

JOIN_TYPE_UUID = 'uuid'
JOIN_TYPE_SSN = 'ssn'
JOIN_TYPE_MEDID = 'medid'
JOIN_TYPE_ADDRESS1 = 'address1'

# this is the main flag to change when doing different types of matching
join_by = JOIN_TYPE_ADDRESS1

group = '3'
source_flm_both = groups[group].get('source_flm_both')
source_ufh_both = groups[group].get('source_ufh_both')
out_file_merged = groups[group].get('out_file_merged')
out_file = groups[group].get('out_file')


def clean_address(x):
    return str(x).lower().strip().replace('.', '')


def clean(x):
    return str(x).strip()

df_flm = pd.read_csv(source_flm_both, sep=",",
                     skipinitialspace=True,
                     skip_blank_lines=True,
                     # escapechar='\\',
                     dtype=object,
                     # dtype={'PHI_addr1': str, 'PHI_city': str},
                     usecols=[
                         'MedicaidID', 'PHI_SSN', 'first', 'last',
                         'linkage_uuid', 'PHI_addr1', 'PHI_city', 'PHI_zip',
                         'dob', 'gender']
                     )
# df_flm.fillna('', inplace=True)
# df_flm = df_flm.applymap(str.strip)
df_flm['PHI_addr1'] = df_flm['PHI_addr1'].astype(str).apply(
    lambda x: clean_address(x))

df_flm.sample(3)


# In[ ]:

df_ufh = pd.read_csv(
    source_ufh_both, sep=",",
    skipinitialspace=True,
    skip_blank_lines=True,
    # escapechar='\\',
    dtype=object,
    # dtype={'PATNT_ADDR1': str, 'PATNT_CITY_NAME': str},
    usecols=[
        'FLM_PATID', 'LINKAGE_UUID', 'UFH_PATID',
        'PATNT_SSN',
        'PATNT_FIRST_NAME', 'PATNT_LAST_NAME',
        'MOST_RECENT_MEDICAID_POLICY_NUM',
        'PATNT_BIRTH_DATE', 'PCORNET_SEX', 'PATNT_ADDR1', 'PATNT_CITY_NAME',
        'PATNT_ZIP_CD']
)
df_ufh.rename(columns={
    'MOST_RECENT_MEDICAID_POLICY_NUM': 'UFH_MEDICAID_ID',
    'PATNT_FIRST_NAME': 'UFH_FIRST',
    'PATNT_LAST_NAME': 'UFH_LAST'}, inplace=True)

# df_ufh.fillna('', inplace=True)
df_ufh['UFH_MEDICAID_ID'] = df_ufh['UFH_MEDICAID_ID'].astype(str).apply(
    str.strip)
df_ufh['PATNT_ADDR1'] = df_ufh['PATNT_ADDR1'].astype(str).apply(
    lambda x: clean_address(x))

df_ufh.sample(3)


#

# In[ ]:

if join_by == JOIN_TYPE_UUID:
    # This is the line that changes the join condition in order to calculate FP
    df = pd.merge(df_flm, df_ufh, left_on='linkage_uuid',
                  right_on='LINKAGE_UUID', how='inner')

elif join_by == JOIN_TYPE_SSN:
    # extra step to filter rows with fake SSNs
    df_ufh = df_ufh.loc[~df_ufh['PATNT_SSN'].isin(
        ['111111111', '222222222', '333333333',
         '444444444', '555555555', '666666666',
         '777777777', '888888888', '999999999'])]
    # This is the line that changes the join condition in order to calculate TN
    df = pd.merge(df_flm, df_ufh, left_on='PHI_SSN', right_on='PATNT_SSN',
                  how='inner')

elif join_by == JOIN_TYPE_MEDID:
    df_ufh = df_ufh.loc[~df_ufh['UFH_MEDICAID_ID'].isnull()]
    df = pd.merge(df_flm, df_ufh, left_on='MedicaidID',
                  right_on='UFH_MEDICAID_ID',
                  how='inner')

elif join_by == JOIN_TYPE_ADDRESS1:
    # df_ufh = df_ufh.loc[~df_ufh['UFH_MEDICAID_ID'].isnull()]
    df = pd.merge(df_flm, df_ufh, left_on='PHI_addr1', right_on='PATNT_ADDR1',
                  how='inner')

print("UFH shape: {}".format(df_ufh.shape))
df.sample()


# In[ ]:

df['match_medid'] = df.apply(
    lambda x: 'yes'
    if clean(x['MedicaidID']) == clean(x['UFH_MEDICAID_ID']) else 'no', axis=1)
df['match_ssn'] = df.apply(
    lambda x: 'yes'
    if clean(x['PHI_SSN']) == clean(x['PATNT_SSN']) else 'no', axis=1)
df['match_uuid'] = df.apply(
    lambda x: 'yes'
    if clean(x['LINKAGE_UUID']) == clean(x['linkage_uuid']) else 'no', axis=1)


df['match_addr1'] = df.apply(
    lambda x: 'yes'
    if clean_address(x['PHI_addr1']) == clean_address(x['PATNT_ADDR1'])
    else 'no', axis=1)
df['match_city'] = df.apply(
    lambda x: 'yes'
    if clean_address(x['PHI_city']) == clean_address(x['PATNT_CITY_NAME'])
    else 'no', axis=1)
df['match_zip'] = df.apply(
    lambda x: 'yes'
    if clean(x['PHI_zip']) == clean(x['PATNT_ZIP_CD'])
    else 'no', axis=1)

df['match_medid_OR_ssn'] = df.apply(
    lambda x: 'yes'
    if x['match_medid'] == 'yes' or x['match_ssn'] == 'yes'
    else 'no', axis=1)

print("Merged df shape: {}".format(df.shape))
df.sample()


# In[ ]:

sorted_cols = [
    'LINKAGE_UUID', 'linkage_uuid',
    'match_uuid',
    'PHI_SSN', 'PATNT_SSN',
    'match_ssn',
    'MedicaidID', 'UFH_MEDICAID_ID',
    'match_medid',
    'dob', 'PATNT_BIRTH_DATE',
    'first', 'UFH_FIRST',
    'last', 'UFH_LAST',
    'PHI_addr1', 'PATNT_ADDR1',
    'PHI_city', 'PATNT_CITY_NAME',
    'PHI_zip', 'PATNT_ZIP_CD',
    'match_medid_OR_ssn',
    'match_addr1', 'match_city', 'match_zip',

]
df[sorted_cols].to_csv(out_file_merged, index=False)

df[['match_medid_OR_ssn']].groupby('match_medid_OR_ssn').size()
df[['match_uuid']].groupby('match_uuid').size()


# In[ ]:

# use this line to estimate False Positives (for precision)
# not_found = df.loc[df['match_medid_OR_ssn'] == 'no']

# use this line to estimate False Negatives (for recall)
not_found = df.loc[df['match_uuid'] == 'no']

not_found


# In[ ]:

print("Total unmatched rows: {}".format(len(not_found)))


# In[ ]:

# not_found.drop('LINKAGE_UUID', axis=1, inplace=True)
not_found = not_found[sorted_cols]
not_found['MANUAL_REVIEW'] = 'not reviewed'
not_found.to_csv(out_file, index=False)


# In[ ]:
