%{?scl:%scl_package galera}
%{!?scl:%global pkg_name %{name}}

Name:           %{?scl_prefix}galera
Version:        25.3.12
Release:        4%{?dist}
Summary:        Synchronous multi-master wsrep provider (replication engine)

License:        GPLv2
URL:            http://galeracluster.com/
Source0:        http://releases.galeracluster.com/source/%{pkg_name}-3-%{version}.tar.gz

Source1:        garbd.service
Source2:        garbd-wrapper

Patch0:         kill-mtune-native.patch

BuildRequires:  %{?scl_prefix}boost-devel check-devel openssl-devel %{?scl_prefix}scons


%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
Requires:       nmap-ncat
Requires:       systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires:       nc
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(postun): /sbin/service
%endif

%description
Galera is a fast synchronous multi-master wsrep provider (replication engine)
for transactional databases and similar applications. For more information
about wsrep API see http://launchpad.net/wsrep. For a description of Galera
replication engine see http://www.codership.com.

%prep
%setup -q -n %{pkg_name}-3-%{version}
%patch0 -p1

%build
%{?scl:scl enable %{scl} - << "EOF"}
export CPPFLAGS="%{optflags}"
scons %{?_smp_mflags} strict_build_flags=0 extra_sysroot=%{_prefix} \
    bpostatic=%{_libdir}/libboost_program_options.so

%{?scl:EOF}

%install
%{?scl:scl enable %{scl} - << "EOF"}
%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
install -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/garbd.service
install -D -m 755 %{SOURCE2} %{buildroot}%{_sbindir}/garbd-wrapper
%else
install -D -m 755 garb/files/garb.sh %{buildroot}%{_initrddir}/garb
%endif
install -D -m 755 garb/garbd %{buildroot}%{_sbindir}/garbd
install -D -m 755 libgalera_smm.so %{buildroot}%{_libdir}/galera/libgalera_smm.so
install -D -m 644 garb/files/garb.cnf %{buildroot}%{_sysconfdir}/sysconfig/garb
install -D -m 644 COPYING %{buildroot}%{_docdir}/galera/COPYING
install -D -m 644 chromium/LICENSE %{buildroot}%{_docdir}/galera/LICENSE.chromium
install -D -m 644 asio/LICENSE_1_0.txt %{buildroot}%{_docdir}/galera/LICENSE.asio
install -D -m 644 www.evanjones.ca/LICENSE %{buildroot}%{_docdir}/galera/LICENSE.crc32
install -D -m 644 scripts/packages/README %{buildroot}%{_docdir}/galera/README
install -D -m 644 scripts/packages/README-MySQL %{buildroot}%{_docdir}/galera/README-MySQL
%{?scl:EOF}


%post
/sbin/ldconfig
%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%systemd_post garbd.service
%else
/sbin/chkconfig --add garb
%endif


%preun
%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%systemd_preun garbd.service
%else
if [ "$1" -eq 0 ]; then
    /sbin/service garb stop >/dev/null 2>&1
    /sbin/chkconfig --del garb
fi
%endif


%postun
/sbin/ldconfig
%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%systemd_postun_with_restart garbd.service
%else
if [ "$1" -ge 1 ]; then
    /sbin/service garb condrestart >/dev/null 2>&1 || :
fi
%endif

%files
%defattr(-,root,root,-)
%config(noreplace,missingok) %{_sysconfdir}/sysconfig/garb
%dir %{_docdir}/galera
%dir %{_libdir}/galera
%{_sbindir}/garbd
%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%{_sbindir}/garbd-wrapper
%{_unitdir}/garbd.service
%else
%{_initrddir}/garb
%endif
%{_libdir}/galera/libgalera_smm.so
%doc %{_docdir}/galera/COPYING
%doc %{_docdir}/galera/LICENSE.asio
%doc %{_docdir}/galera/LICENSE.crc32
%doc %{_docdir}/galera/LICENSE.chromium
%doc %{_docdir}/galera/README
%doc %{_docdir}/galera/README-MySQL

%changelog
* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 25.3.12-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 15 2016 Jonathan Wakely <jwakely@redhat.com> - 25.3.12-3
- Rebuilt for Boost 1.60

* Wed Sep 30 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 25.3.12-2
- Remove use of -mtune=native which breaks build on secondary architectures

* Fri Sep 25 2015 Richard W.M. Jones <rjones@redhat.com> - 25.3.12-1
- Update to 25.3.12.
- Should fix the build on 32 bit ARM (RHBZ#1241164).
- Remove ExcludeArch (should have read the BZ more closely).

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 25.3.10-5
- Rebuilt for Boost 1.59

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 25.3.10-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 25.3.10-3
- rebuild for Boost 1.58

* Wed Jul 08 2015 Ryan O'Hara <rohara@redhat.com> - 25.3.10-2
- Disable ARM builds (#1241164, #1239516)

* Mon Jul 06 2015 Ryan O'Hara <rohara@redhat.com> - 25.3.10-1
- Update to version 25.3.10

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 25.3.5-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jan 26 2015 Petr Machata <pmachata@redhat.com> - 25.3.5-10
- Rebuild for boost 1.57.0

* Thu Nov 27 2014 Richard W.M. Jones <rjones@redhat.com> - 25.3.5-9
- Add aarch64 support.

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 25.3.5-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 25.3.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 25.3.5-6
- Rebuild for boost 1.55.0

* Wed Apr 30 2014 Dan Horák <dan[at]danny.cz> - 25.3.5-5
- set ExclusiveArch

* Thu Apr 24 2014 Ryan O'Hara <rohara@redhat.com> - 25.3.5-4
- Use strict_build_flags=0 to avoid -Werror
- Remove unnecessary clean section

* Thu Apr 24 2014 Ryan O'Hara <rohara@redhat.com> - 25.3.5-3
- Include galera directories in file list
- Set CPPFLAGS to optflags

* Wed Apr 23 2014 Ryan O'Hara <rohara@redhat.com> - 25.3.5-2
- Fix client certificate verification (#1090604)

* Thu Mar 27 2014 Ryan O'Hara <rohara@redhat.com> - 25.3.5-1
- Update to version 25.3.5

* Mon Mar 24 2014 Ryan O'Hara <rohara@redhat.com> - 25.3.3-2
- Add systemd service

* Sun Mar 09 2014 Ryan O'Hara <rohara@redhat.com> - 25.3.3-1
- Initial build
