project('escambo',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
profile = get_option('profile')
if get_option('profile') == 'development'
  app_id = 'io.github.cleomenezesjr.Escambo.Devel'
  prefix = '/io/github/cleomenezesjr/Escambo/Devel'
elif profile == 'release'
  app_id = 'io.github.cleomenezesjr.Escambo'
  prefix = '/io/github/cleomenezesjr/Escambo'
endif

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('APP_ID', app_id)
conf.set('PREFIX', prefix)
conf.set('PROFILE', profile)
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
