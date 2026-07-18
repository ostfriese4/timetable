pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'untis'
gnome = import('gnome')

gnome.compile_resources('untis',
  'untis.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'untis.in',
  output: 'untis',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

untis_sources = [
  '__init__.py',
  'absences.py',
  'api.py',
  'credentials.py',
  'create_homework.py',
  'dialog.py',
  'external_page.py',
  'holiday.py',
  'homework.py',
  'homework_api.py',
  'homework_row.py',
  'information.py',
  'lesson.py',
  'login.py',
  'main.py',
  'messages.py',
  'profiles.py',
  'teachers.py',
  'timetable.py',
  'window.py',
]

install_data(untis_sources, install_dir: moduledir)
