#!/bin/bash
# Script for updating RDO deps repo on trunk-primary.rdoproject.org
# Usage: update-deps.sh

set -e

MASTER_TAG=${MASTER_TAG:-flamingo}
RELEASE=${RELEASE:-$(echo $USER|cut -d'-' -f2-)}
DEPS_DIR=${DEPS_DIR:-${HOME}/data/repos/deps/}
LATEST_DEPS_DIR=${DEPS_DIR}/latest/
RDOINFO_LOCATION=${RDOINFO_LOCATION:-/home/rdoinfo/rdoinfo}
DATE_VERSION=$(date +%Y%m%d%H%M)
RSYNC_REMOTE=${RSYNC_REMOTE:-0}
TAG_PHASE=${TAG_PHASE:-testing}

# Find CentOS version

case $(echo $USER|cut -d'-' -f1) in
centos9)
  CENTOS_RELEASE=9s
  TAG_PREFFIX="cloud9s"
  ;;
centos10)
  CENTOS_RELEASE=10s
  TAG_PREFFIX="cloud10s"
  ;;
esac

if [ "$TAG_PHASE" = "build" ]; then
    TAG_SUFFIX="el${CENTOS_RELEASE}-$TAG_PHASE"
else
    TAG_SUFFIX=$TAG_PHASE
fi

ARCHES="aarch64 noarch ppc64le ppc64 x86_64"

# rdopkg is installed in the dlrn venv

if [ -f ~/.venv/bin/activate ]; then
    source ~/.venv/bin/activate
fi

# Find remote server to rsync the dependencies
if [ $RSYNC_REMOTE -eq 1 ]; then
    RSYNC_DEST=$(grep rsyncdest /usr/local/share/dlrn/${USER}/projects.ini | awk -F= '{print $2}')
    RSYNC_SERVER=$(echo $RSYNC_DEST | awk -F: '{print $1}')
    RSYNC_PORT=$(grep rsyncport /usr/local/share/dlrn/${USER}/projects.ini | awk -F= '{print $2}')
fi
#

LOCK="/home/${USER}/update-deps.lock"

exec 200>$LOCK
if !  flock -n 200
then
    echo "update-deps.sh for ${USER} is running, please try again later."
    exit 1
fi

echo "INFO: synchronizing dependencies revision $DATE_VERSION to $LATEST_DEPS_DIR"
if [ $RELEASE = "master-uc" ]; then
    CBS_TAG=${CBS_TAG:-"${TAG_PREFFIX}-openstack-${MASTER_TAG}-${TAG_SUFFIX}"}
else
    CBS_TAG=${CBS_TAG:-"${TAG_PREFFIX}-openstack-${RELEASE}-${TAG_SUFFIX}"}
fi

TEMPDIR=$(mktemp -d)

dnf clean all
QUERY_EXTRA_OPTS="--disable-modular-filtering"

repoquery --archlist=x86_64,noarch,ppc64le,aarch64 --repofrompath=deps,file://$LATEST_DEPS_DIR --disablerepo=* --enablerepo=deps -s -q -a $QUERY_EXTRA_OPTS|sort -u|sed 's/.src.rpm//g'>$TEMPDIR/current_deps
rdopkg info -l $RDOINFO_LOCATION "buildsys-tags:$CBS_TAG" "tags:dependency"|grep $CBS_TAG|awk '{print $2}'>$TEMPDIR/required_deps
rdopkg info -l $RDOINFO_LOCATION "name:openstack-macros"|grep $CBS_TAG|awk '{print $2}'>>$TEMPDIR/required_deps

# We only want to download builds for supported arches
ARCH_OPT="-a src"
for arch in $ARCHES
do
ARCH_OPT="$ARCH_OPT -a $arch"
done

cd $LATEST_DEPS_DIR
rm -rf .pending
mkdir .pending
cd .pending
for NVR in $(cat $TEMPDIR/required_deps)
do
  if [ $(grep -c ^$NVR$ $TEMPDIR/current_deps) -eq 0 ]; then
      echo "INFO: adding package $NVR to $LATEST_DEPS_DIR"
      cbs download-build $ARCH_OPT -q $NVR
  fi
done
rm -rf $TEMPDIR
UPDATED=$(ls *.src.*|wc -l)
if [ $UPDATED -ne 0 ];then
    for i in *.src.*
    do
        mv  $i ../SRPMS/
    done
    for arch in $ARCHES
    do
        for i in *.$arch* ; do
            [[ -e "$i" ]] || break
            mv $i ../$arch/
        done
    done
fi

# any leftovers?
ls
cd ..
rmdir .pending
# Repos has a date based revision
if [ $UPDATED -ne 0 ];then
    createrepo --retain-old-md 10 -v --revision $DATE_VERSION --update -x "SRPMS/*" .
    createrepo --retain-old-md 10 -v --revision $DATE_VERSION --update SRPMS
# backup current repodata in a date based repo version
    echo "INFO: Saving current repo in version $DATE_VERSION"
    mkdir ../$DATE_VERSION
    cd ../$DATE_VERSION
    for i in SRPMS $ARCHES
    do
        ln -s ../latest/$i $i
    done
    cp -pr ../latest/repodata .
# Synchronize from primary to public server
    if [ $RSYNC_REMOTE -eq 1 ]; then
        rsync -avz -e "ssh -p ${RSYNC_PORT} -o StrictHostKeyChecking=no" --exclude "repodata" $LATEST_DEPS_DIR ${RSYNC_SERVER}:$LATEST_DEPS_DIR
        rsync -avz -e "ssh -p ${RSYNC_PORT} -o StrictHostKeyChecking=no" $LATEST_DEPS_DIR/repodata/ ${RSYNC_SERVER}:$LATEST_DEPS_DIR/repodata/
        rsync -avz -e "ssh -p ${RSYNC_PORT} -o StrictHostKeyChecking=no" $LATEST_DEPS_DIR/SRPMS/repodata/ ${RSYNC_SERVER}:$LATEST_DEPS_DIR/SRPMS/repodata/
        rsync -avz -e "ssh -p ${RSYNC_PORT} -o StrictHostKeyChecking=no" $DEPS_DIR/$DATE_VERSION/ ${RSYNC_SERVER}:$DEPS_DIR/$DATE_VERSION/
    fi
else
    echo "INFO: No dependencies updates detected"
fi

