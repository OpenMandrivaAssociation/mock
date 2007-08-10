Summary: Builds packages inside chroots
Name: mock
Version: 0.7.4
Release: %mkrel 1
License: GPL
Group: Development/Other
Source0: http://fedoraproject.org/projects/mock/releases/%{name}-%{version}.tar.gz
URL: http://fedoraproject.org/wiki/Projects/Mock
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: python, yum >= 2.4
Requires(pre): rpm-helper
BuildRequires: libselinux-devel

%description
Mock takes a srpm and builds it in a chroot

%prep
%setup -q
%{__sed} -i -e "s|/usr/bin|%{_bindir}|g;" -e "s|/usr/libexec|%{_libexecdir}|g;" Makefile

%build
%{make} CFLAGS="%{optflags}"

%install
rm -rf $RPM_BUILD_ROOT
%{makeinstall_std}
# make the default.cfg link
cd $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}

%if 0%{?fedora:1}
if [ -f fedora-%{fedora}-%{_target_cpu}-core.cfg ]; then
        ln -s fedora-%{fedora}-%{_target_cpu}-core.cfg default.cfg
elif [ -f fedora-%{fedora}-%{_target_cpu}.cfg ]; then
        ln -s fedora-%{fedora}-%{_target_cpu}.cfg default.cfg
fi
%endif

# if we haven't created a default link yet, try to do so as devel
if [ ! -f default.cfg ]; then
    if [ -f fedora-development-%{_target_cpu}.cfg ]; then
        ln -s fedora-development-%{_target_cpu}.cfg default.cfg
    elif [ -f fedora-devel-%{_target_cpu}.cfg ]; then
        ln -s fedora-devel-%{_target_cpu}.cfg default.cfg
    elif [ -f fedora-development-i386.cfg ]; then
        ln -s fedora-development-i386.cfg default.cfg
    elif [ -f fedora-devel-i386.cfg ]; then
        ln -s fedora-devel-i386.cfg default.cfg
    fi
fi

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%_pre_groupadd mock

%files
%defattr(-, root, root)
%doc README ChangeLog buildsys-build.spec
%dir  %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*.cfg
%{_bindir}/%{name}
%{_libexecdir}/mock-yum
%{_mandir}/man1/mock.1*
%attr(04750, root, mock) %{_sbindir}/mock-helper
%attr(02775, root, mock) %dir /var/lib/mock
%{_libdir}/libselinux-mock.so
