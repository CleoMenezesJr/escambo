pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

subdir('icons')
subdir('ui')

gnome.compile_resources('escambo',
  configure_file(
    input: 'escambo.gresource.xml.in',
    output: 'escambo.gresource.xml',
    configuration: conf
  ),
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

desktop_file = i18n.merge_file(
        input: configure_file(
          input: 'io.github.cleomenezesjr.Escambo.desktop.in',
          output: app_id + '.desktop.in',
          configuration: conf
        ),
        output: app_id + '.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: configure_file(
          input: 'io.github.cleomenezesjr.Escambo.metainfo.xml.in',
          output: app_id + '.metainfo.xml.in',
          configuration: conf
        ),
       output: app_id + '.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test('Validate appstream file', appstreamcli,
     args: ['validate', '--no-net', '--explain', appstream_file])

install_data(
  configure_file(
    input: 'io.github.cleomenezesjr.Escambo.gschema.xml.in',
    output: app_id + '.gschema.xml',
    configuration: conf
  ),
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test('Validate schema file',
     compile_schemas,
     args: ['--strict', '--dry-run', meson.current_source_dir()])
