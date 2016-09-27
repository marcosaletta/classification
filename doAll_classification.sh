#!/bin/sh

#set -x

export AWS_CONFIG_FILE=/home/liquida/UserSex/aws_config_file.txt
CMS_HOME=/home/liquida/UserSex
WDIR=/home/liquida/UserSex/data/workingdir
SDIR_KRUX=/home/liquida/UserSex/scripts/script_krux
SDIR_KERAS=/home/liquida/UserSex/scripts/script_keras
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
LOG_FILE = ${LOG_DIR}/filter.log
ASM_FILE=ALL_audience_segment_map.txt
LISTS_USERS=lists_users
LISTS_USERS_WITH_SEX=lists_users_WITH_SEX
LISTS_USERS_NO_SEX=lists_users_NO_SEX
LISTS_SELCETED_SEGMENTS=Segments4Class_200916_NO_ALL0.5_list
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

#seguenza SCRIPT
cd $SDIR_KRUX
#create the lists of segments
echo "Preparing lists with the array of 0/1 for the selected segments"
echo "The list of user with sex will be used for evaluation of the models"
echo "The list of user with sex will be used for prediction"
python3 FeaturesArray4Prediction.py -f ${WDIR}/${ASM_FILE} -o ${WDIR}/${LISTS_USERS} -l ${SDIR_KRUX}/${LISTS_SELCETED_SEGMENTS}
echo "Moving to ${SDIR_KERAS}"
cd ${SDIR_KERAS}
echo "EVALUATE model on the users with sex info"
python keras_load_model.py -w ${MODEL_DIR}/${MODEL_WEIGHT} -j ${MODEL_DIR}/${MODEL_JSON} -f ${WDIR}/${LISTS_USERS_WITH_SEX} -o ${WDIR}/${MODEL_EV}
echo "EVALUATE model on the users withOUT sex info"
python keras_load_model.py -w ${MODEL_DIR}/${MODEL_WEIGHT} -j ${MODEL_DIR}/${MODEL_JSON} -f ${WDIR}/${LISTS_USERS_NO_SEX} -o ${WDIR}/${MODEL_PRED}
# copy to keras-class
echo "Exporting to ${KERAS_BUCKET}"
export AWS_DEFAULT_PROFILE=banzaimedia
#aws s3 cp ${WDIR}/${MODEL_EV} ${KERAS_BUCKET}/results
#cp ${LAST_DAY_SEGS_STATS} s3://cppm/bigdata/gold5/reports/
#cp  ${CMS_HOME}/*.log ${CMS_HOME}/logs/
#cp ${WDIR}/*.log ${CMS_HOME}/logs/
#aws s3 cp ${CMS_HOME}/logs/ s3://cppm/bigdata/gold5/logs/${LAST_DAY_S3PATH}/ --recursive --exclude "*" --include "*.log"
#aws s3 cp ${WDIR}/ s3://cppm/bigdata/gold5/logs/${LAST_DAY_S3PATH}/ --recursive --exclude "*" --include "stats.csv" --exclude "*/*"

echo "END:"`date`
