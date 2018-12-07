#!/bin/sh

if [ $# -ne 2 ]; then
	echo Please pass a admin token and SonarQube URL; exit 1
fi

token=$1; url=$2; folder=projects-backup; files=quality-profiles-backup/*

if [[ $url == */ ]]; then
	url=${url::-1}
fi

# quality profiles
for file in $files; do
	curl -X POST -u $token: -F backup=@$file $url/api/qualityprofiles/restore
done
curl -X POST -u $token: -F "language=cs" -F "qualityProfile=Kroton Crypto" $url/api/qualityprofiles/set_default
curl -X POST -u $token: -F "language=php" -F "qualityProfile=Portal do Aluno" $url/api/qualityprofiles/set_default

# security group and global permissions
curl -X POST -u $token: -F "description=System architects" -F "name=sonar-architects" $url/api/user_groups/create
curl -X POST -u $token: -F "groupName=sonar-architects" -F "permission=profileadmin" $url/api/permissions/add_group
curl -X POST -u $token: -F "groupName=sonar-architects" -F "permission=gateadmin" $url/api/permissions/add_group
curl -X POST -u $token: -F "groupName=sonar-architects" -F "permission=provisioning" $url/api/permissions/add_group

# quality gates
curl -X POST -u $token: -F "name=Analytics Trusted Transformation" $url/api/qualitygates/create
curl -X POST -u $token: -F "gateId=2" -F "metric=new_security_rating" -F "op=GT" -F "error=1" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=2" -F "metric=new_reliability_rating" -F "op=GT" -F "error=1" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=2" -F "metric=new_maintainability_rating" -F "op=GT" -F "error=1" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=2" -F "metric=new_coverage" -F "op=GT" -F "error=1" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=2" -F "metric=new_duplicated_lines_density" -F "op=GT" -F "error=10" -F "warning=3" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=2" -F "metric=cognitive_complexity" -F "op=GT" -F "error=6" -F "warning=4" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=2" -F "metric=test_success_density" -F "op=LT" -F "error=100" -F "period=1" $url/api/qualitygates/create_condition

curl -X POST -u $token: -F "name=Kroton" $url/api/qualitygates/create
curl -X POST -u $token: -F "gateId=3" -F "metric=new_duplicated_lines_density" -F "op=GT" -F "error=5" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=3" -F "metric=sqale_rating" -F "op=GT" -F "error=3" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=3" -F "metric=security_rating" -F "op=GT" -F "error=3" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=3" -F "metric=reliability_rating" -F "op=GT" -F "error=3" $url/api/qualitygates/create_condition

curl -X POST -u $token: -F "name=Legacy" $url/api/qualitygates/create
curl -X POST -u $token: -F "gateId=4" -F "metric=new_security_rating" -F "op=GT" -F "error=3" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=4" -F "metric=new_reliability_rating" -F "op=GT" -F "error=3" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=4" -F "metric=new_maintainability_rating" -F "op=GT" -F "error=3" -F "period=1" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=4" -F "metric=new_duplicated_lines_density" -F "op=GT" -F "error=35" -F "period=1" $url/api/qualitygates/create_condition

curl -X POST -u $token: -F "name=Production" $url/api/qualitygates/create
curl -X POST -u $token: -F "gateId=5" -F "metric=bugs" -F "op=GT" -F "error=550" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=5" -F "metric=code_smells" -F "op=GT" -F "error=20000" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=5" -F "metric=duplicated_blocks" -F "op=GT" -F "error=3100" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=5" -F "metric=duplicated_lines_density" -F "op=LT" -F "error=13.9" $url/api/qualitygates/create_condition
curl -X POST -u $token: -F "gateId=5" -F "metric=vulnerabilities" -F "op=GT" -F "error=0" $url/api/qualitygates/create_condition

curl -X POST -u $token: -F "id=3" $url/api/qualitygates/set_as_default

# projects
curl -X POST -u $token: -F "project=ingestion-processor:development" -F "name=Ingestion Processor development" $url/api/projects/create
curl -X POST -u $token: -F "project=ingestion-processor:master" -F "name=Ingestion Processor master" $url/api/projects/create
curl -X POST -u $token: -F "project=last-mile:master" -F "name=Last Mile master" $url/api/projects/create
curl -X POST -u $token: -F "gateId=1" -F "projectKey=ingestion-processor:development" $url/api/qualitygates/select
curl -X POST -u $token: -F "gateId=1" -F "projectKey=ingestion-processor:master" $url/api/qualitygates/select
curl -X POST -u $token: -F "gateId=1" -F "projectKey=last-mile:master" $url/api/qualitygates/select

curl -X POST -u $token: -F "project=trusted-transformation:development" -F "name=Trusted Transformation development" $url/api/projects/create
curl -X POST -u $token: -F "project=trusted-transformation:master" -F "name=Trusted Transformation master" $url/api/projects/create
curl -X POST -u $token: -F "gateId=2" -F "projectKey=trusted-transformation:development" $url/api/qualitygates/select
curl -X POST -u $token: -F "gateId=2" -F "projectKey=trusted-transformation:master" $url/api/qualitygates/select

while read line; do
	curl -X POST -u $token: -F "project=$line" -F "name=$line" $url/api/projects/create
	curl -X POST -u $token: -F "gateId=4" -F "projectKey=$line" $url/api/qualitygates/select
done < $folder/legacy-projects.txt

while read line; do
	curl -X POST -u $token: -F "project=$line" -F "name=$line" $url/api/projects/create
	curl -X POST -u $token: -F "gateId=5" -F "projectKey=$line" $url/api/qualitygates/select
done < $folder/production-projects.txt
