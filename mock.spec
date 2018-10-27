# (ngompa) disable rpmlint to avoid terrible cyclic dependency problem in rpm5->rpm4 + python2->python3 transition
# remove after rpm5->rpm4 transition is complete
%undefine _build_pkgcheck_set
%undefine _build_pkgcheck_srpm
%undefine _nonzero_exit_pkgcheck_terminate_build
###

# WARNING: This package is synchronized with Mageia and Fedora!

# mock group id allocate from Fedora
%global mockgid 135

# Fedora release numbers are part of upstream releases
%global origrel 1

Summary:	Builds packages inside chroots
Name:		mock
Version:	1.4.13
Release:	8
License:	GPLv2+
Group:		Development/Other
URL:		https://github.com/rpm-software-management/mock/
# Source is created by
# git clone https://github.com/rpm-software-management/mock.git
# cd mock
# git reset --hard %{name}-%{version}-%{origrel}
# tito build --tgz
Source0:	%{url}/releases/download/%{name}-%{version}-%{origrel}/%{name}-%{version}.tar.gz
Patch0:		mock-1.4.9-bin-paths.patch
# Switch to 32-bit personality when building for armv7*/armv8*
Patch2:		mock-1.4.9-use-32bit-personality-for-armv7armv8.patch
# https://github.com/libarchive/libarchive/issues/1060
Patch3:		remove-compress-option.patch
# https://github.com/rpm-software-management/mock/issues/219
Patch4:		fix-excludes-for-bsdtar.patch

BuildArch:	noarch
Requires:	bsdtar
Requires:	pigz
Requires:	usermode-consoleonly
Recommends:	createrepo_c

# Not yet available
#Requires: mock-core-configs >= 28.2

Requires:	systemd

BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	pkgconfig(bash-completion)
BuildRequires:	pkgconfig(python3)
Requires:	python
Requires:	python-distro
Requires:	python-six >= 1.4.0
Requires:	python-requests
Requires:	python-rpm
Requires:	python-pyroute2
#check
BuildRequires:	python-pylint
BuildRequires:	python-requests
BuildRequires:	python-distro
BuildRequires:	python-six >= 1.4.0
BuildRequires:	python-rpm
BuildRequires:	python-pyroute2

# We need these for the OpenMandriva targets
Requires:	dnf
Requires:	dnf-plugins-core

# For EPEL targets
Recommends:	dnf-yum
Recommends:	dnf-utils

Recommends:	btrfs-progs
BuildRequires:	perl

# hwinfo plugin
Requires(pre):	util-linux
Requires(pre):	coreutils
Requires(pre):	shadow
Requires:	procps-ng

%description
Mock takes an SRPM and builds it in a chroot.

%package scm
Summary:	Mock SCM integration module
Group:		Development/Other
Requires:	%{name} = %{version}-%{release}
Requires:	git
Requires:	subversion
Requires:	tar

%description scm
Mock SCM integration module.

%package lvm
Summary:	LVM plugin for mock
Group:		Development/Other
Requires:	%{name} = %{version}-%{release}
Requires:	lvm2

%description lvm
Mock plugin that enables using LVM as a backend and support creating snapshots
of the buildroot.

%prep
%autosetup -p1

for file in py/mock.py py/mockchain.py; do
  sed -i 1"s|#!/usr/bin/python |#!%{__python} |" $file
done

%build
for i in py/mock.py py/mockchain.py; do
    perl -p -i -e 's|^__VERSION__\s*=.*|__VERSION__="%{version}"|' $i
    perl -p -i -e 's|^SYSCONFDIR\s*=.*|SYSCONFDIR="%{_sysconfdir}"|' $i
    perl -p -i -e 's|^PYTHONDIR\s*=.*|PYTHONDIR="%{python_sitelib}"|' $i
    perl -p -i -e 's|^PKGPYTHONDIR\s*=.*|PKGPYTHONDIR="%{python_sitelib}/mockbuild"|' $i
done
for i in docs/mockchain.1 docs/mock.1; do
    perl -p -i -e 's|"@VERSION@"|"%{version}"|' $i
done


%install
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_libexecdir}/mock
install py/mockchain.py %{buildroot}%{_bindir}/mockchain
install py/mock.py %{buildroot}%{_libexecdir}/mock/mock
ln -s consolehelper %{buildroot}%{_bindir}/mock
install create_default_route_in_container.sh %{buildroot}%{_libexecdir}/mock/

install -d %{buildroot}%{_sysconfdir}/pam.d
cp -a etc/pam/* %{buildroot}%{_sysconfdir}/pam.d/

install -d %{buildroot}%{_sysconfdir}/mock
cp -a etc/mock/* %{buildroot}%{_sysconfdir}/mock/

install -d %{buildroot}%{_sysconfdir}/security/console.apps/
cp -a etc/consolehelper/mock %{buildroot}%{_sysconfdir}/security/console.apps/%{name}

install -d %{buildroot}%{_datadir}/bash-completion/completions/
cp -a etc/bash_completion.d/* %{buildroot}%{_datadir}/bash-completion/completions/
ln -s mock %{buildroot}%{_datadir}/bash-completion/completions/mockchain

install -d %{buildroot}%{_sysconfdir}/pki/mock
cp -a etc/pki/* %{buildroot}%{_sysconfdir}/pki/mock/

install -d %{buildroot}%{python_sitelib}/
cp -a py/mockbuild %{buildroot}%{python_sitelib}/

install -d %{buildroot}%{_mandir}/man1
cp -a docs/mockchain.1 docs/mock.1 %{buildroot}%{_mandir}/man1/

install -d %{buildroot}/var/lib/mock
install -d %{buildroot}/var/cache/mock

# Manually invoke byte compilation
%py_compile %{buildroot}

%pre
# check for existence of mock group, create it if not found
getent group mock > /dev/null || groupadd -f -g %mockgid -r mock
exit 0

%check
# ignore the errors for now, just print them and hopefully somebody will fix it one day
python3-pylint py/mockbuild/ py/*.py py/mockbuild/plugins/* || :

%files
%defattr(0644, root, mock)
%config(noreplace) %{_sysconfdir}/mock/site-defaults.cfg
%{_datadir}/bash-completion/completions/mock
%{_datadir}/bash-completion/completions/mockchain

%defattr(-, root, root)

# executables
%{_bindir}/mock
%{_bindir}/mockchain
%{_libexecdir}/mock

# python stuff
%{python_sitelib}/*
%exclude %{python_sitelib}/mockbuild/scm.*
%exclude %{python_sitelib}/mockbuild/__pycache__/scm.*.py*
%exclude %{python_sitelib}/mockbuild/plugins/lvm_root.*
%exclude %{python_sitelib}/mockbuild/plugins/__pycache__/lvm_root.*.py*
# config files
%dir  %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.ini
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}

# directory for personal gpg keys
%dir %{_sysconfdir}/pki/mock
%config(noreplace) %{_sysconfdir}/pki/mock/*

# docs
%{_mandir}/man1/mock.1.*
%{_mandir}/man1/mockchain.1.*

# license
%license COPYING

# cache & build dirs
%defattr(0775, root, mock, 02775)
%dir %{_localstatedir}/cache/mock
%dir %{_localstatedir}/lib/mock

%files scm
%{python_sitelib}/mockbuild/scm.py*
%{python_sitelib}/mockbuild/__pycache__/scm.*.py*

%files lvm
%{python_sitelib}/mockbuild/plugins/lvm_root.*
%{python_sitelib}/mockbuild/plugins/__pycache__/lvm_root.*.py*
