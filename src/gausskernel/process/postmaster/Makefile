#
# Copyright (c) 2020 Huawei Technologies Co.,Ltd.
#
# openGauss is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#
#          http://license.coscl.org.cn/MulanPSL2
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
#---------------------------------------------------------------------------------------
#
# IDENTIFICATION
#    src/gausskernel/process/postmaster/Makefile
#
#-------------------------------------------------------------------------

subdir = src/gausskernel/process/postmaster
top_builddir = ../../../..
include $(top_builddir)/src/Makefile.global

override CPPFLAGS := -I$(LIBOPENSSL_INCLUDE_PATH) -I$(LIBCURL_INCLUDE_PATH) $(CPPFLAGS)

ifneq "$(MAKECMDGOALS)" "clean"
  ifneq "$(MAKECMDGOALS)" "distclean"
    ifneq "$(shell which g++ |grep hutaf_llt |wc -l)" "1"
      -include $(DEPEND)
    endif
  endif
endif
OBJS = autovacuum.o bgwriter.o fork_process.o pgarch.o pgstat.o postmaster.o gaussdb_version.o\
	startup.o syslogger.o walwriter.o\
  epochlogicaltimermanager.o epochphysicaltimermanager.o epochmessagecachemanager.o epochmessagemanager.o\
  epochsend.o epochlisten.o epochpack.o epochnotify.o epochunseri.o epochunpack.o epochmerge.o epochcommit.o epochrecordcommit.o tinyxml2.o\
  walwriterauxiliary.o checkpointer.o pgaudit.o alarmchecker.o \
	twophasecleaner.o aiocompleter.o fencedudf.o lwlockmonitor.o cbmwriter.o remoteservice.o pagewriter.o\
	barrier_creator.o $(top_builddir)/src/lib/config/libconfig.a

include $(top_srcdir)/src/gausskernel/common.mk

$(top_builddir)/src/lib/config/libconfig.a:
	$(MAKE) -C $(top_builddir)/src/lib/config libconfig.a
