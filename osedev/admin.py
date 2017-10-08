from django.contrib.admin import site


site.site_title = 'OSEDev Admin'
site.site_header = 'OSEDev Admin'
site.index_title = 'Main Modules'
original_build_app_dict = site._build_app_dict


def new_build_app_dict(self, request, label=None):
    app_dict = original_build_app_dict(request)

    def move(src, dest):
        if src in app_dict:
            nonlocal label
            app_dict[dest]['models'].extend(app_dict[src]['models'])
            del app_dict[src]
            if label == src:
                label = dest

    move('account', 'user')
    move('socialaccount', 'user')
    move('auth', 'user')
    if 'sites' in app_dict:
        del app_dict['sites']

    if label:
        return app_dict.get(label)

    return app_dict

site._build_app_dict = new_build_app_dict.__get__(site, type(site))