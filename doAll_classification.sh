#!/bin/sh

set -x

export AWS_CONFIG_FILE=/home/liquida/UserSex/aws_config_file.txt
CMS_HOME=/home/liquida/UserSex
WDIR=/home/liquida/UserSex/data/workingdir
ARCHIVE_DIR=/home/liquida/UserSex/data/archive
LOG_DIR=/home/liquida/UserSex/data/logs
ASM_DIR=audience-segment-map
UMT_DIR=user-match-tables
K_S3BUCKET=krux-partners/client-banzai/krux-data/exports
GOLD5_BUCKET=gold5-profiles-banzai
LOG_FILE = ${LOG_DIR}/filter.log
ASM_FILE=ALL_audience_segment_map.txt
WWW_DOC_ROOT=/var/www/bigdata/gold5/

echo "BEGIN:"`date`
rm -rf ${WDIR}
mkdir ${WDIR}
cd ${WDIR}

#
# Read from KRUX
#
export AWS_DEFAULT_PROFILE=kruxnew
# AUDIENCE-SEGMENT-MAP
# get the last day available from audience-segment-map
LAST_ASM=`aws s3 ls s3://${K_S3BUCKET}/${ASM_DIR}/ | tail -1`
echo "Last audience-segment-map:" ${LAST_ASM}
LAST_DAY=`python -c "import sys; print sys.argv[2].strip('/')" ${LAST_ASM}`
echo "Last Day:" ${LAST_DAY}

mkdir -p ${ASM_DIR}/${LAST_DAY}

cd ${ASM_DIR}/${LAST_DAY}

#
# get audience-segment-map last-day
#
echo "Copy from s3://${K_S3BUCKET}/${ASM_DIR}/${LAST_DAY}/"
aws s3 cp s3://${K_S3BUCKET}/${ASM_DIR}/${LAST_DAY}/ . --recursive
zcat *.gz > ${ASM_FILE}
mv ${ASM_FILE} ../../

# copy to gold5 bucket
export AWS_DEFAULT_PROFILE=banzaimedia
aws s3 cp ${OUTFILE}.gz s3://${GOLD5_BUCKET}/ #DA SISTEMARE CON I MIEI DATI


# copy to s3 reports, logs and stats
export AWS_DEFAULT_PROFILE=eni
cp ${LAST_DAY_SEGS_STATS} s3://cppm/bigdata/gold5/reports/
cp  ${CMS_HOME}/*.log ${CMS_HOME}/logs/
cp ${WDIR}/*.log ${CMS_HOME}/logs/
aws s3 cp ${CMS_HOME}/logs/ s3://cppm/bigdata/gold5/logs/${LAST_DAY_S3PATH}/ --recursive --exclude "*" --include "*.log"
aws s3 cp ${WDIR}/ s3://cppm/bigdata/gold5/logs/${LAST_DAY_S3PATH}/ --recursive --exclude "*" --include "stats.csv" --exclude "*/*"

echo "END:"`date`
