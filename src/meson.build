pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'getoverhere')
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'populator-entry.blp',
    'window.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('getoverhere',
  'getoverhere.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'getoverhere.in',
  output: 'getoverhere',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

getoverhere_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'restapi.py',
  'populator_entry.py',
  'sourceview.py'
]

install_data(getoverhere_sources, install_dir: moduledir)
