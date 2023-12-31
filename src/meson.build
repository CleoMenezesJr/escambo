moduledir = pkgdatadir / 'escambo'

configure_file(
  input: 'escambo.in',
  output: 'escambo',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

escambo_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  configure_file(
    input: 'define.py.in',
    output: 'define.py',
    configuration: conf
  )
]

install_data(escambo_sources, install_dir: moduledir)
