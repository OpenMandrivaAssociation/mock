# WARNING: This package is synchronized with Mageia and Fedora!
%define _pkgdocdir %{_docdir}/%{name}-%{version}

# mock group id allocate from Fedora
%global mockgid 135

# Fedora release numbers are part of upstream releases
%global origrel %nil

Summary:	Builds packages inside chroots
Name:		mock
Version:	3.5
Release:	3
License:	GPLv2+
Group:		Development/Other
URL:		https://github.com/rpm-software-management/mock/
# Source is created by
# git clone https://github.com/rpm-software-management/mock.git
# cd mock
# git reset --hard %{name}-%{version}-%{origrel}
# tito build --tgz
Source0:	https://github.com/rpm-software-management/mock/releases/download/mock-%{version}-1/mock-%{version}.tar.gz
# (tpg) use sudo these days, especially when /sbin got merged with /bin
Source1:	mock.wrapper
Patch0:		mock-1.4.16-dnf-clean-all-on-builddep-failure.patch
# Remove /bin/rpm hardcode to help during
# usrmerge transition
Patch1:		mock-2.16-usrbinrpm.patch
# Our /usr/bin/tar is bsdtar
Patch2:		mock-3.3-default-bsdtar.patch
# Appending "-d" to an empty compressProgram is a stupid idea
Patch3:		mock-3.3-no-invalid-decompressProgram.patch
# (tpg) this crap was introduced jus to only check is some ancient rpmbuild supports --noclean option
# https://github.com/rpm-software-management/mock/commit/cab12758da074e8af87189bd8f4a11c73a1f1ebf
Patch4:		mock-3.5-stop-calling-rpmbuild-to-discover-noclean-is-supported.patch
# (tpg) patches from upstream
Patch100:	https://github.com/rpm-software-management/mock/commit/adf58f0c172dd8d5493ca5e8dead5ade23caf711.patch
Patch101:	https://github.com/rpm-software-management/mock/commit/a730c331de14ef6c8246ccde3959cc528a75531e.patch
BuildArch:	noarch
BuildRequires:	pkgconfig(bash-completion)
BuildRequires:	pkgconfig(python)
Requires:	python-distro
Requires:	python-jinja2
Requires:	python-requests
Requires:	python-rpm
Requires:	python-pyroute2
Requires:	python-templated-dictionary
Requires:	dnf
Requires:	dnf-plugins-core
Requires:	bsdtar
Requires:	pigz
Requires:	sudo
Requires:	distribution-gpg-keys
Requires:	createrepo_c
Requires:	systemd
Requires:	systemd-container
Requires:	procps-ng
Requires:	util-linux
Requires:	coreutils
Requires(pre):	shadow
Suggests:	iproute2

%description
Mock takes an SRPM and builds it in a chroot.

%package scm
Summary:	Mock SCM integration module
Group:		Development/Other
Requires:	%{name} = %{EVRD}
Recommends:	git
Recommends:	subversion
Recommends:	tar

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

for file in py/mock.py py/mock-parse-buildlog.py; do
    sed -i 1"s|#!/usr/bin/python3 |#!%{__python} |" $file
done

%build
for i in py/mockbuild/constants.py ; do
    sed -i -e 's|^VERSION\s*=.*|VERSION = "%{version}"|' $i
    sed -i -e 's|^SYSCONFDIR\s*=.*|SYSCONFDIR = "%{_sysconfdir}"|' $i
    sed -i -e 's|^PYTHONDIR\s*=.*|PYTHONDIR = "%{python_sitelib}"|' $i
    sed -i -e 's|^PKGPYTHONDIR\s*=.*|PKGPYTHONDIR = "%{python_sitelib}/mockbuild"|' $i
done

for i in docs/mock.1 docs/mock-parse-buildlog.1; do
    sed -i -e 's|\@VERSION\@|%{version}"|' $i
done

%install
#base filesystem
mkdir -p %{buildroot}%{_sysconfdir}/mock/eol/templates
mkdir -p %{buildroot}%{_sysconfdir}/mock/templates

install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_libexecdir}/mock
install mockchain %{buildroot}%{_bindir}/mockchain
install py/mock-parse-buildlog.py %{buildroot}%{_bindir}/mock-parse-buildlog
install py/mock.py %{buildroot}%{_libexecdir}/mock/mock
install -m755 %{SOURCE1} %{buildroot}%{_bindir}/mock
install create_default_route_in_container.sh %{buildroot}%{_libexecdir}/mock/

install -d %{buildroot}%{_sysconfdir}/pam.d
cp -a etc/pam/* %{buildroot}%{_sysconfdir}/pam.d/

install -d %{buildroot}%{_sysconfdir}/mock
cp -a etc/mock/* %{buildroot}%{_sysconfdir}/mock/

install -d %{buildroot}%{_sysconfdir}/security/console.apps/
cp -a etc/consolehelper/mock %{buildroot}%{_sysconfdir}/security/console.apps/%{name}

install -d %{buildroot}%{_datadir}/bash-completion/completions/
cp -a etc/bash_completion.d/* %{buildroot}%{_datadir}/bash-completion/completions/
ln -s mock %{buildroot}%{_datadir}/bash-completion/completions/mock-parse-buildlog

install -d %{buildroot}%{_sysconfdir}/pki/mock
cp -a etc/pki/* %{buildroot}%{_sysconfdir}/pki/mock/

install -d %{buildroot}%{python_sitelib}/
cp -a py/mockbuild %{buildroot}%{python_sitelib}/

install -d %{buildroot}%{_mandir}/man1
cp -a docs/mock.1 docs/mock-parse-buildlog.1 %{buildroot}%{_mandir}/man1/
install -d %{buildroot}%{_datadir}/cheat
cp -a docs/mock.cheat %{buildroot}%{_datadir}/cheat/mock

install -d %{buildroot}/var/lib/mock
install -d %{buildroot}/var/cache/mock

mkdir -p %{buildroot}%{_pkgdocdir}
install -p -m 0644 docs/site-defaults.cfg %{buildroot}%{_pkgdocdir}

sed -i 's/^_MOCK_NVR = None$/_MOCK_NVR = "%{name}-%{version}-%{release}"/' \
    %{buildroot}%{_libexecdir}/mock/mock

%pre
# check for existence of mock group, create it if not found
getent group mock > /dev/null || groupadd -f -g %mockgid -r mock
exit 0

%files
%license COPYING
%dir %{_sysconfdir}/mock
%dir %{_sysconfdir}/mock/eol
%dir %{_sysconfdir}/mock/eol/templates
%dir %{_sysconfdir}/mock/templates
%dir %{_datadir}/cheat
%defattr(0644, root, mock)
%doc %{_pkgdocdir}/site-defaults.cfg
%{_datadir}/bash-completion/completions/mock
%{_datadir}/bash-completion/completions/mock-parse-buildlog

%defattr(-, root, root)
# executables
%{_bindir}/mock
%{_bindir}/mockchain
%{_bindir}/mock-parse-buildlog
%{_libexecdir}/mock

# python stuff
%{python_sitelib}/*
%exclude %{python_sitelib}/mockbuild/scm.*
%exclude %{python_sitelib}/mockbuild/plugins/lvm_root.*
# config files
%config(noreplace) %{_sysconfdir}/%{name}/*.ini
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}

# directory for personal gpg keys
%dir %{_sysconfdir}/pki/mock
%config(noreplace) %{_sysconfdir}/pki/mock/*

# docs
%doc %{_mandir}/man1/mock.1.*
%doc %{_mandir}/man1/mock-parse-buildlog.1*
%{_datadir}/cheat/mock

# cache & build dirs
%defattr(0775, root, mock, 02775)
%dir %{_localstatedir}/cache/mock
%dir %{_localstatedir}/lib/mock

%files scm
%{python_sitelib}/mockbuild/scm.py*

%files lvm
%{python_sitelib}/mockbuild/plugins/lvm_root.*
