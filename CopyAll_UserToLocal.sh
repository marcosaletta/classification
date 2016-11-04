#!/bin/sh

#set -x

#export PATH=/home/liquida/anaconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export AWS_CONFIG_FILE=/home/marco/progetti_banzai/aws_config_file.txt
CMS_HOME=/home/liquida/UserSex
WDIR=/home/marco/working-dir/Krux/anagrafica_files/ALL_FILES
SDIR_KRUX=/home/liquida/UserSex/scripts/script_krux
SDIR_KERAS=/home/liquida/UserSex/scripts/script_keras/scripts
MODEL_DIR=/home/liquida/UserSex/scripts/script_keras/models
MODEL_WEIGHT=model_10k4training_small_set.h5
MODEL_JSON=model_10k4training_small_set.json
MODEL_EV=model_evaluation
MODEL_PRED=model_predictions
ARCHIVE_DIR=/home/liquida/UserSex/data/archive
LOG_DIR=/home/liquida/UserSex/data/logs
ASM_DIR=audience-segment-map
UMT_DIR=user-match-tables
K_S3BUCKET=krux-partners/client-banzai/krux-data/exports
KERAS_BUCKET=keras-class
LOG_FILE=${LOG_DIR}/filter.log
ASM_FILE=ALL_audience_segment_map.txt
LISTS_USERS=lists_users
LISTS_USERS_WITH_SEX=lists_users_WITH_SEX
LISTS_USERS_NO_SEX=lists_users_NO_SEX
LISTS_SELCETED_SEGMENTS=Segments4Class_200916_NO_ALL0.5_list
WWW_DOC_ROOT=/var/www/bigdata/gold5/

echo "BEGIN:"`date`
echo "IO sono:"`whoami`
cd ${WDIR}
#
# Read from KRUX
#
export AWS_DEFAULT_PROFILE=kruxnew
# AUDIENCE-SEGMENT-MAP
# get the last day available from audience-segment-map
python --version
/home/liquida/anaconda3/bin/aws s3 ls s3://${K_S3BUCKET}/${ASM_DIR}/${LAST_DAY}/
LAST_ASM=`aws s3 ls s3://${K_S3BUCKET}/${ASM_DIR}/ | tail -1`
echo "Last audience-segment-map:" ${LAST_ASM}
LAST_DAY=`python -c "import sys; print(sys.argv[2].strip('/'))" ${LAST_ASM}`
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

cd
