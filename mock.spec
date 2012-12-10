# next four lines substituted by autoconf
%define major 1
%define minor 1
%define sub 26
%define extralevel %{nil}
%define release_name mock
%define release_version %{major}.%{minor}.%{sub}%{extralevel}

Summary: Builds packages inside chroots
Name: mock
Version: %{release_version}
Release: 1
License: GPLv2+
Group: Development/Other
Source: https://git.fedorahosted.org/cgit/mock.git/snapshot/%{name}-%{version}.tar.gz
Patch0: 0001-add-f18-configs.patch
URL: http://fedoraproject.org/wiki/Projects/Mock
BuildArch: noarch
Requires: yum >= 2.4, tar, gzip, pigz, python-ctypes, python-decoratortools, python-iniparse, usermode
Requires: createrepo
Requires(pre): shadow-utils
Requires(post): coreutils
%py_requires -d

%description
Mock takes a srpm and builds it in a chroot

%prep
%setup -q
%patch0 -p1

%build
%configure
make

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install
mkdir -p $RPM_BUILD_ROOT%{_var}/lib/mock
mkdir -p $RPM_BUILD_ROOT%{_var}/cache/mock
ln -s consolehelper $RPM_BUILD_ROOT%{_bindir}/mock

%if 0
# compatibility symlinks
# (probably be nuked in the future)
pushd $RPM_BUILD_ROOT/etc/mock
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
echo "%defattr(0644, root, mock)" > %{name}.cfgs
find $RPM_BUILD_ROOT%{_sysconfdir}/mock -name "*.cfg" \
    | sed -e "s|^$RPM_BUILD_ROOT|%%config(noreplace) |" >> %{name}.cfgs

# just for %%ghosting purposes
ln -s fedora-rawhide-x86_64.cfg $RPM_BUILD_ROOT%{_sysconfdir}/mock/default.cfg

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ $1 -eq 1 ]; then
    groupadd -r mock >/dev/null 2>&1 || :
fi

%post
# TODO: use dist and version of install system, not build one
if [ ! -e %{_sysconfdir}/%{name}/default.cfg ] ; then
    # in case of dangling symlink
    rm -f %{_sysconfdir}/%{name}/default.cfg
    arch=$(uname -i)
    for ver in %{?fedora}%{?rhel} rawhide ; do
        cfg=%{?fedora:fedora}%{?rhel:epel}-$ver-$arch.cfg
        if [ -e %{_sysconfdir}/%{name}/$cfg ] ; then
            ln -s -f $cfg %{_sysconfdir}/%{name}/default.cfg
            exit 0
        fi
    done
fi
# fix cache permissions from old installs
chmod 2775 %{_var}/cache/mock
:

%files -f %{name}.cfgs
%defattr(-, root, root)

# executables
%{_bindir}/mock
%{_bindir}/mockchain
%attr(0755, root, root) %{_sbindir}/mock

# python stuff
%{python_sitelib}/*

# config files
%dir  %{_sysconfdir}/%{name}
%ghost %config(noreplace,missingok) %{_sysconfdir}/%{name}/default.cfg
%config(noreplace) %{_sysconfdir}/%{name}/*.ini
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}
%{_sysconfdir}/bash_completion.d

# docs
%{_mandir}/man1/mock.1*
%{_mandir}/man1/mockchain.1*
%doc ChangeLog

# cache & build dirs
%defattr(0775, root, mock, 02775)
%dir /var/cache/mock
%dir /var/lib/mock


%changelog
* Tue Aug 28 2012 Paulo Andrade <pcpa@mandriva.com.br> 1.1.26-1
+ Revision: 815929
- Update to latest upstream release.

* Tue Nov 02 2010 Michael Scherer <misc@mandriva.org> 0.9.14-3mdv2011.0
+ Revision: 592412
- rebuild for python 2.7

* Mon Sep 14 2009 Thierry Vignaud <tv@mandriva.org> 0.9.14-2mdv2010.0
+ Revision: 440053
- rebuild

* Wed Feb 18 2009 Jérôme Soyer <saispo@mandriva.org> 0.9.14-1mdv2009.1
+ Revision: 342373
- New upstream release

* Tue Jan 06 2009 Funda Wang <fwang@mandriva.org> 0.9.13-2mdv2009.1
+ Revision: 325765
- rebuild

* Mon Nov 10 2008 David Walluck <walluck@mandriva.org> 0.9.13-1mdv2009.1
+ Revision: 301879
- 0.9.13

* Sat Oct 18 2008 David Walluck <walluck@mandriva.org> 0.9.12-1mdv2009.1
+ Revision: 295157
- 0.9.12

* Mon Aug 18 2008 David Walluck <walluck@mandriva.org> 0.9.10-2mdv2009.0
+ Revision: 273345
- Requires: python-iniparse

* Sun Aug 17 2008 David Walluck <walluck@mandriva.org> 0.9.10-1mdv2009.0
+ Revision: 272850
- 0.9.10

* Tue Jul 29 2008 Thierry Vignaud <tv@mandriva.org> 0.9.7-3mdv2009.0
+ Revision: 252670
- rebuild

* Mon Feb 11 2008 David Walluck <walluck@mandriva.org> 0.9.7-1mdv2008.1
+ Revision: 165006
- 0.9.7

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Sep 19 2007 Guillaume Rousse <guillomovitch@mandriva.org> 0.7.4-2mdv2008.0
+ Revision: 89947
- rebuild

* Sat Aug 11 2007 David Walluck <walluck@mandriva.org> 0.7.4-1mdv2008.0
+ Revision: 61853
- change selinux BuildRequires
- Import mock

