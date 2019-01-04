#!/usr/bin/env python3

import sys, requests, glob

usage = 'Usage: restore.py [ <user> <password> | <token> ] <url>'
if  len(sys.argv) == 2 and sys.argv[1] in ['-h', '-H', '--help']:
    sys.exit(usage)
elif len(sys.argv) == 3: # admin token and sonarqube url
    user_token, password, url = sys.argv[1], '', sys.argv[2]
elif len(sys.argv) == 4: # admin user, password and sonarqube url
    user_token, password, url = sys.argv[1], sys.argv[2], sys.argv[3]
else:
    sys.exit('Syntax error! ' + usage)

if url.endswith('/'):
    url = url[:-1]

ANALYTICS = 'Analytics'
KROTON = 'Kroton'
LEGACY = 'Legacy'
PRODUCTION = 'Production'

API_QP_RESTORE = '/api/qualityprofiles/restore'
API_QP_SET_DEFAULT = '/api/qualityprofiles/set_default'
API_UG_CREATE = '/api/user_groups/create'
API_PERM_ADD_GROUP = '/api/permissions/add_group'
API_QG_CREATE = '/api/qualitygates/create'
API_QG_CREATE_COND = '/api/qualitygates/create_condition'
API_QG_SET_DEFAULT = '/api/qualitygates/set_as_default'
API_QG_SELECT = '/api/qualitygates/select'
API_PROJECT_CREATE = '/api/projects/create'

def post(api, params=None, files=None):
    if files is not None:
        return requests.post(url + api, files=files, auth=(user_token, password))
    else:
        return requests.post(url + api, params=params, auth=(user_token, password))

# quality profiles
for file in glob.glob('quality-profiles-backup/*.xml'):
    post(API_QP_RESTORE, files={'backup': open(file, 'rb')})
post(API_QP_SET_DEFAULT, params={'language': 'cs', 'qualityProfile': 'Kroton Crypto'})
post(API_QP_SET_DEFAULT, params={'language': 'php', 'qualityProfile': 'Portal do Aluno'})

# security group and global permissions
post(API_UG_CREATE, params={'description': 'System architects', 'name': 'sonar-architects'})
post(API_PERM_ADD_GROUP, params={'groupName': 'sonar-architects', 'permission': 'profileadmin'})
post(API_PERM_ADD_GROUP, params={'groupName': 'sonar-architects', 'permission': 'gateadmin'})
post(API_PERM_ADD_GROUP, params={'groupName': 'sonar-architects', 'permission': 'provisioning'})

# quality gates
post(API_QG_CREATE, params={'name': ANALYTICS})
post(API_QG_CREATE, params={'name': KROTON})
post(API_QG_CREATE, params={'name': LEGACY})
post(API_QG_CREATE, params={'name': PRODUCTION})

response = requests.get(url + '/api/qualitygates/list', auth=(user_token, password))
qgs = dict(map(lambda qg: (qg['name'], qg['id']), response.json()['qualitygates']))

post(API_QG_CREATE_COND, params={'gateId': qgs[ANALYTICS], 'metric': 'new_security_rating', 'op': 'GT', 'error': 1, 'period': 1})
post(API_QG_CREATE_COND, params={'gateId': qgs[ANALYTICS], 'metric': 'new_reliability_rating', 'op': 'GT', 'error': 1, 'period': 1})
post(API_QG_CREATE_COND, params={'gateId': qgs[ANALYTICS], 'metric': 'new_maintainability_rating', 'op': 'GT', 'error': 1, 'period': 1})
post(API_QG_CREATE_COND, params={'gateId': qgs[ANALYTICS], 'metric': 'new_coverage', 'op': 'GT', 'error': 1, 'period': 1})
post(API_QG_CREATE_COND, params={'gateId': qgs[ANALYTICS], 'metric': 'new_duplicated_lines_density', 'op': 'GT', 'error': 10, 'warning': 3, 'period': 1})
post(API_QG_CREATE_COND, params={'gateId': qgs[ANALYTICS], 'metric': 'cognitive_complexity', 'op': 'GT', 'error': 6, 'warning': 4, 'period': 1})
post(API_QG_CREATE_COND, params={'gateId': qgs[ANALYTICS], 'metric': 'test_success_density', 'op': 'LT', 'error': 100, 'period': 1})

post(API_QG_CREATE_COND, params={'gateId': qgs[KROTON], 'metric': 'new_duplicated_lines_density', 'op': 'GT', 'error': 5, 'period': 1})
post(API_QG_CREATE_COND, params={'gateId': qgs[KROTON], 'metric': 'sqale_rating', 'op': 'GT', 'error': 3})
post(API_QG_CREATE_COND, params={'gateId': qgs[KROTON], 'metric': 'security_rating', 'op': 'GT', 'error': 3})
post(API_QG_CREATE_COND, params={'gateId': qgs[KROTON], 'metric': 'reliability_rating', 'op': 'GT', 'error': 3})

post(API_QG_CREATE_COND, params={'gateId': qgs[LEGACY], 'metric': 'new_security_rating', 'op': 'GT', 'error': 3, 'period': 1})
post(API_QG_CREATE_COND, params={'gateId': qgs[LEGACY], 'metric': 'new_reliability_rating', 'op': 'GT', 'error': 3, 'period': 1})
post(API_QG_CREATE_COND, params={'gateId': qgs[LEGACY], 'metric': 'new_maintainability_rating', 'op': 'GT', 'error': 3, 'period': 1})

post(API_QG_CREATE_COND, params={'gateId': qgs[PRODUCTION], 'metric': 'bugs', 'op': 'GT', 'error': 550})
post(API_QG_CREATE_COND, params={'gateId': qgs[PRODUCTION], 'metric': 'code_smells', 'op': 'GT', 'error': 20000})
post(API_QG_CREATE_COND, params={'gateId': qgs[PRODUCTION], 'metric': 'duplicated_blocks', 'op': 'GT', 'error': 3100})
post(API_QG_CREATE_COND, params={'gateId': qgs[PRODUCTION], 'metric': 'duplicated_lines_density', 'op': 'GT', 'error': 13.9})
post(API_QG_CREATE_COND, params={'gateId': qgs[PRODUCTION], 'metric': 'vulnerabilities', 'op': 'GT', 'error': 0})

post(API_QG_SET_DEFAULT, params={'id': qgs[KROTON]})

# projects
post(API_PROJECT_CREATE, params={'project': 'ingestion-processor:development', 'name': 'Ingestion Processor development'})
post(API_PROJECT_CREATE, params={'project': 'ingestion-processor:master', 'name': 'Ingestion Processor master'})
post(API_PROJECT_CREATE, params={'project': 'last-mile:master', 'name': 'Last Mile master'})
post(API_QG_SELECT, params={'gateId': 1, 'projectKey': 'ingestion-processor:development'})
post(API_QG_SELECT, params={'gateId': 1, 'projectKey': 'ingestion-processor:master'})
post(API_QG_SELECT, params={'gateId': 1, 'projectKey': 'last-mile:master'})

post(API_PROJECT_CREATE, params={'project': 'trusted-transformation:development', 'name': 'Trusted Transformation development'})
post(API_PROJECT_CREATE, params={'project': 'trusted-transformation:master', 'name': 'Trusted Transformation master'})
post(API_QG_SELECT, params={'gateId': qgs[ANALYTICS], 'projectKey': 'trusted-transformation:development'})
post(API_QG_SELECT, params={'gateId': qgs[ANALYTICS], 'projectKey': 'trusted-transformation:master'})

with open('projects-backup/legacy-projects.txt') as file:
    for line in file:
        post(API_PROJECT_CREATE, params={'project': line, 'name': line})
        post(API_QG_SELECT, params={'gateId': qgs[LEGACY], 'projectKey': line})

with open('projects-backup/production-projects.txt') as file:
    for line in file:
        post(API_PROJECT_CREATE, params={'project': line, 'name': line})
        post(API_QG_SELECT, params={'gateId': qgs[PRODUCTION], 'projectKey': line})
