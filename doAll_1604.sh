#!/bin/sh

set -x

export AWS_CONFIG_FILE=/home/liquida/etc/aws_config_file.txt
export PYTHONPATH=/home/liquida/pyliq-packages/:/home/liquida/pyliq-packages/cluster
export LD_LIBRARY_PATH=/usr/lib/libuchardet
CMS_HOME=/home/liquida/gold5/gold5src
WDIR=/home/liquida/gold5/data/workingdir
ARCHIVE_DIR=/home/liquida/gold5/data/archive
LOG_DIR=/home/liquida/gold5/data/logs
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

# call python filter_segments_1.py
echo "Run python"
LAST_DAY_C=`python -c "import sys; print sys.argv[1].replace('-','')" ${LAST_DAY}`
OUTFILE_TMP=outTmp.txt
OUTFILE=banzai_users_segments_${LAST_DAY_C}.txt
cd ${WDIR}
cp ${CMS_HOME}/segmentsg5.txt .
cp ${CMS_HOME}/segmentsg5Dichiarati.csv .
cp ${CMS_HOME}/labels_segmentsg5Peso.json .
cp ${CMS_HOME}/labels_segmentsg5.csv . 
cp ${CMS_HOME}/runSegsAnalysis_with_widgets.R .
cp ${CMS_HOME}/segsAnalysis.Rmd .

# first run
python ${CMS_HOME}/getBestSegs_1.py -i ${ASM_FILE} -o ${OUTFILE_TMP}

# finalize for gold5
python ${CMS_HOME}/finalizeSegs_2.py -i ${OUTFILE_TMP} -o ${OUTFILE}

# call makeStats_3.py -d
LAST_DAY_SEGS_STATS=${LAST_DAY}_segsStats.html
python ${CMS_HOME}/makeStats_3.py -d ${LAST_DAY} -o ${LAST_DAY_SEGS_STATS}

# call Rscript
#/usr/bin/Rscript runSegsAnalysis_with_widgets.R
#LAST_DAY_SEGS_STATS=${LAST_DAY}_segsAnalysis.html
#cp segsAnalysis.html ${LAST_DAY_SEGS_STATS}
cp ${LAST_DAY_SEGS_STATS} ${ARCHIVE_DIR}/
cp ${LAST_DAY_SEGS_STATS} ${WWW_DOC_ROOT}/

#gzip
gzip ${OUTFILE}

# rm huge file
###PAOLO rm ${ASM_FILE}

# copy to gold5 bucket
export AWS_DEFAULT_PROFILE=gold5
aws s3 cp ${OUTFILE}.gz s3://${GOLD5_BUCKET}/


# copy to s3 reports, logs and stats
export AWS_DEFAULT_PROFILE=eni
cp ${LAST_DAY_SEGS_STATS} s3://cppm/bigdata/gold5/reports/
cp  ${CMS_HOME}/*.log ${CMS_HOME}/logs/
cp ${WDIR}/*.log ${CMS_HOME}/logs/
aws s3 cp ${CMS_HOME}/logs/ s3://cppm/bigdata/gold5/logs/${LAST_DAY_S3PATH}/ --recursive --exclude "*" --include "*.log"
aws s3 cp ${WDIR}/ s3://cppm/bigdata/gold5/logs/${LAST_DAY_S3PATH}/ --recursive --exclude "*" --include "stats.csv" --exclude "*/*"

echo "END:"`date`
