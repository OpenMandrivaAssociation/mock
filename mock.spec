# next four lines substituted by autoconf
%define major 0
%define minor 9
%define sub 14
%define extralevel %{nil}
%define release_name mock
%define release_version %{major}.%{minor}.%{sub}%{extralevel}

Summary: Builds packages inside chroots
Name: mock
Version: %{release_version}
Release: %mkrel 1
License: GPLv2+
Group: Development/Other
Source: https://fedorahosted.org/mock/attachment/wiki/MockTarballs/%{name}-%{version}.tar.gz
URL: http://fedoraproject.org/wiki/Projects/Mock
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch
Requires: yum >= 2.4, tar, gzip, python-ctypes, python-decoratortools, python-iniparse, usermode-consoleonly
Requires(pre): shadow-utils
%py_requires -d

%description
Mock takes a srpm and builds it in a chroot

%prep
%setup -q

%build
%{configure2_5x}
%{make}

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install
mkdir -p $RPM_BUILD_ROOT%{_var}/lib/mock
ln -s consolehelper $RPM_BUILD_ROOT/usr/bin/mock

%if 0
# compatibility symlinks
# (probably be nuked in the future)
pushd $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
ln -s epel-4-i386.cfg   fedora-4-i386-epel.cfg
ln -s epel-4-ppc.cfg    fedora-4-ppc-epel.cfg
ln -s epel-4-x86_64.cfg fedora-4-x86_64-epel.cfg
ln -s epel-5-i386.cfg   fedora-5-i386-epel.cfg
ln -s epel-5-ppc.cfg    fedora-5-ppc-epel.cfg
ln -s epel-5-x86_64.cfg fedora-5-x86_64-epel.cfg
# more compat, from devel/rawhide rename
ln -s fedora-rawhide-i386.cfg fedora-devel-i386.cfg
ln -s fedora-rawhide-x86_64.cfg fedora-devel-x86_64.cfg
ln -s fedora-rawhide-ppc.cfg fedora-devel-ppc.cfg
ln -s fedora-rawhide-ppc64.cfg fedora-devel-ppc64.cfg
popd
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ $1 -eq 1 ]; then
    groupadd -r mock >/dev/null 2>&1 || :
fi

%files
%defattr(-, root, root)

# executables
%{_bindir}/mock
%attr(0755, root, root) %{_sbindir}/mock

# python stuff
%{python_sitelib}/*

# config files
%dir  %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.cfg
%config(noreplace) %{_sysconfdir}/%{name}/*.ini
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}

# docs
%{_mandir}/man1/mock.1*
%doc ChangeLog

# build dir
%attr(02775, root, mock) %dir %{_var}/lib/mock
