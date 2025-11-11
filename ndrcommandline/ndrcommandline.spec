%global python3_pkgversion 3



Summary:        Epiq Solutions NDR Radio Commandline Utility
Name:           RPM_PKG_NAME
Version:        RPM_PKG_VERSION
Release:        RPM_PKG_OSRPM_PKG_OS_VER
License:        Proprietary
Group:          Applications/Programming
Source:         RPM_PKG_NAME-RPM_PKG_VERSION.tar.gz
URL:            https://www.github.com/CyberRadio/NDRCommandLine.com
Vendor:         Epiq Solutions
Packager:       Brandon.Smith@epiqsolutions.com
BuildArch:      noarch
# Automatically generate BuildRequires for pyproject / setuptools
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

# Don't build a "debuginfo" package
%define debug_package %{nil}

%description
Provides NDR Command Line Utility for communicating to NDR Json Radios.

%prep
%autosetup -n %{name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{name}